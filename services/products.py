# -*- coding: utf-8 -*-

from odoo import models

class EsprinetProductsService(models.AbstractModel):
    _name = 'esprinet.api.products.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Products Service'

    def get_availability(self, esprinet_product_code=None, customer_product_code=None, headers=None):
        """
        GET /products/availability
        """
        params = {}
        if esprinet_product_code:
            params['esprinetProductCode'] = esprinet_product_code
        if customer_product_code:
            params['customerProductCode'] = customer_product_code
        
        return self._make_request('GET', 'products/availability', params=params, headers=headers)

    def get_pricing(self, esprinet_product_code=None, customer_product_code=None, headers=None):
        """
        GET /products/pricing
        """
        params = {}
        if esprinet_product_code:
            params['esprinetProductCode'] = esprinet_product_code
        if customer_product_code:
            params['customerProductCode'] = customer_product_code
            
        return self._make_request('GET', 'products/pricing', params=params, headers=headers)
