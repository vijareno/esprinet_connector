# -*- coding: utf-8 -*-

import logging
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def cron_synchronize_esprinet_products(self):
        _logger.info("Starting Esprinet products synchronization cron job.")
        try:
            # Use the specific service for customer depot products
            product_service = self.env['esprinet.api.customer_depot.service']
            # Assuming get_all_products returns a list of all products to sync
            # The actual response structure needs to be verified against the API documentation
            products_data = product_service.get_all_products()
        except UserError as e:
            _logger.error("Could not synchronize Esprinet products: %s", e)
            return
        except Exception as e:
            _logger.error("An unexpected error occurred during Esprinet product synchronization: %s", e)
            return

        if not products_data:
            _logger.info("No products returned from Esprinet API.")
            return

        # The key containing the list of products might be different.
        # This needs to be adapted based on the actual API response.
        product_list = products_data.get('products', [])
        
        processed_count = 0
        for product_data in product_list:
            # The fields (sku, name, price, etc.) must be mapped according to the
            # actual names in the API response.
            sku = product_data.get('sku')
            if not sku:
                _logger.warning("Skipping product with no SKU: %s", product_data)
                continue

            product_values = {
                'name': product_data.get('name', 'No Name'),
                'default_code': sku,
                'list_price': product_data.get('price', 0.0),
                'standard_price': product_data.get('cost', 0.0),
                'weight': product_data.get('weight', 0.0),
                # TODO: Map other fields as needed (e.g., description, stock)
            }
            
            product = self.search([('default_code', '=', sku)], limit=1)
            if product:
                product.write(product_values)
                # Ensure Esprinet is added as supplier if not already present
                product._ensure_esprinet_supplier()
                _logger.debug("Updated product with SKU %s", sku)
            else:
                product = self.create(product_values)
                # Add Esprinet as supplier for new products
                product._ensure_esprinet_supplier()
                _logger.debug("Created product with SKU %s", sku)
            processed_count += 1
        
        _logger.info("Finished Esprinet products synchronization. Processed %d products.", processed_count)

    def _is_esprinet_product(self):
        """
        Check if this product is supplied by Esprinet
        Returns True if Esprinet is in the product's supplier list
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
                'delay': 1,  # Lead time in days
            })
            _logger.debug("Added Esprinet as supplier for product %s", self.name)
