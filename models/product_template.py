# -*- coding: utf-8 -*-

import logging
from odoo import models, api, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    supplier_stock_qty = fields.Float(
        string='Stock del proveedor',
        help='Cantidad de stock disponible en el proveedor externo (dropshipping).',
        digits='Product Unit of Measure',
        readonly=False,
        store=True,
    )
    display_supplier_stock_in_website = fields.Boolean(
        string='Mostrar stock proveedor en web',
        help='Mostrar la cantidad de stock del proveedor en el sitio web (eCommerce).',
        default=True,
    )

    @api.model
    def cron_synchronize_esprinet_products(self):
        """
        Sincroniza los datos de productos desde la API de Esprinet para un lote de productos.

        Este método está diseñado para ejecutarse como una tarea programada (cron). Recupera una lista de productos,
        obtiene su información más reciente de precios y disponibilidad desde la API de Esprinet, y actualiza
        los campos correspondientes en los registros de productos de Odoo.

        Pasos realizados:
            1. Recupera hasta 100 productos para actualizar.
            2. Para cada producto (del modelo `product.template`):
            - Obtiene precios y disponibilidad desde la API de Esprinet usando el SKU del producto.
            - Actualiza el precio de coste, el precio de venta (con el margen configurado) y la cantidad de stock del proveedor si se detectan cambios.
            - Registra advertencias para datos faltantes o inválidos.
            3. Registra el número de productos procesados.

        Argumentos:
            self (models.Model): Instancia del modelo Odoo. El método opera sobre el modelo `product.template`.

        Notas:
            - La variable `product` en el bucle se refiere a un registro del modelo `product.template`.
            - Utiliza el parámetro de configuración 'esprinet_connector.margin' para calcular el precio de venta.
            - Maneja y registra excepciones para errores de la API y problemas inesperados.
        """
        _logger.info("Starting Esprinet products synchronization cron job.")
        try:
            products_list = self.get_firsts_products_write()
        except UserError as e:
            _logger.error("No se pudieron sincronizar los productos de Esprinet: %s", e)
            return
        except Exception as e:
            _logger.error("Ocurrió un error inesperado durante la sincronización de productos de Esprinet: %s", e)
            return

        if not products_list:
            _logger.info("No se devolvieron productos desde la API de Esprinet.")
            return

        margin = self.env['ir.config_parameter'].sudo().get_param(
            'esprinet_connector.margin',
            default=25.0
        )
        processed_count = 0
        # product: product.template
        for product in products_list:
            sku = product.default_code
            product_values = {}
            if not product._is_esprinet_product():
                _logger.warning("El producto %s no es un producto de Esprinet, se omite.", sku)
                product.write(product_values)
                continue
            if not sku:
                _logger.warning("Este producto no tiene SKU: %s", product.id)
                product.write(product_values)
                continue
            response_pricing = self.env['esprinet.api.products.service'].get_pricing(esprinet_product_code=sku)
            if not response_pricing:
                _logger.warning("No se pudo obtener el precio para el producto con SKU %s", sku)
                product.write(product_values)
                continue
            pricing_data = response_pricing.get('productPricingByCode', {})
            if not pricing_data:
                _logger.warning("No se pudo obtener la información de precios para el producto con SKU %s", sku)
                product.write(product_values)
                continue
            standard_price = pricing_data.get('sellPrice', 0.0)
            fees = pricing_data.get('fees', 0.0)
            standard_price = float(standard_price) + float(fees)
            if standard_price <= 0:
                _logger.warning("El precio estándar para el producto con SKU %s es inválido: %s", sku, standard_price)
                product.write(product_values)
                continue
            if standard_price != product.standard_price:
                product_values['standard_price'] = standard_price
                product_values['list_price'] = standard_price * (1 + margin / 100.0)

            response_availability = self.env['esprinet.api.products.service'].get_availability(esprinet_product_code=sku)
            if not response_availability:
                _logger.warning("No se pudo obtener la disponibilidad para el producto con SKU %s", sku)
                product.write(product_values)
                continue
            availability_data = response_availability.get('productAvailabilityByCode', {})
            if not availability_data:
                _logger.warning("No se pudo obtener la información de disponibilidad para el producto con SKU %s", sku)
                product.write(product_values)
                continue
            stock_qty = availability_data.get('stock', 0.0)
            if stock_qty != product.supplier_stock_qty:
                product_values['stock_qty'] = stock_qty

            if product_values:
                product.write(product_values)
                if product_values['standard_price']:
                    self._update_product_supplier_info(product_values['standard_price'])
                _logger.debug("Actualizado el producto con SKU %s", sku)
                processed_count += 1

        _logger.info("Sincronización de productos de Esprinet finalizada. Se procesaron %d productos.", processed_count)

    def _is_esprinet_product(self):
        """
        Verifica si este producto es suministrado por Esprinet.
        Devuelve True si Esprinet está en la lista de proveedores del producto.
        """
        esprinet_supplier = self.env['res.partner'].search([
            ('ref', '=', 'ESPRINET_SUPPLIER')
        ], limit=1)

        if not esprinet_supplier:
            return False

        # Check if Esprinet is in the product's supplier info
        return bool(self.seller_ids.filtered(lambda s: s.partner_id == esprinet_supplier))

    def _ensure_esprinet_supplier(self):
        """
        Ensure that Esprinet is added as a supplier for this product
        """
        esprinet_supplier = self.env['res.partner'].search([
            ('ref', '=', 'ESPRINET_SUPPLIER')
        ], limit=1)

        if not esprinet_supplier:
            _logger.warning("Esprinet supplier not found. Please ensure the supplier is properly configured.")
            return

        # Check if Esprinet is already a supplier for this product
        existing_supplier = self.seller_ids.filtered(lambda s: s.partner_id == esprinet_supplier)

        if not existing_supplier:
            # Add Esprinet as a supplier
            self.env['product.supplierinfo'].create({
                'partner_id': esprinet_supplier.id,
                'product_tmpl_id': self.id,
                'min_qty': 1.0,
                'delay': 2,
            })
            _logger.debug("Added Esprinet as supplier for product %s", self.name)

    def _update_product_supplier_info(self, price):
        """
        Update the supplier information for this product
        """
        try:
            existing_supplierinfo = self.env['product.supplierinfo'].search(
                [
                    ('product_tmpl_id', '=', self.id),
                ],
                limit=1,
            )

            supplierinfo_vals = {
                'price': float(price) if price else 0.0,
            }

            if existing_supplierinfo:
                existing_supplierinfo.write(supplierinfo_vals)

        except Exception as e:
            _logger.error("Error updating supplier info: %s", str(e))
            raise

    def get_firsts_products_write(self, limit=100):
        """
        Obtener los primeros productos ordenados por write_date en orden ascendente.
        :param limit: Número de productos a recuperar (por defecto es 100).
        :return: Conjunto de registros de productos.
        """
        return self.search([], order='write_date asc', limit=limit)
