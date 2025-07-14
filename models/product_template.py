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
                _logger.debug("Updated product with SKU %s", sku)
            else:
                self.create(product_values)
                _logger.debug("Created product with SKU %s", sku)
            processed_count += 1
        
        _logger.info("Finished Esprinet products synchronization. Processed %d products.", processed_count)
