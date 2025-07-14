# -*- coding: utf-8 -*-

from odoo import models

class EsprinetCustomerDepotService(models.AbstractModel):
    _name = 'esprinet.api.customer_depot.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Customer Depot Service'

    def get_delivery_notes(self, headers=None):
        """
        GET /customerDepot/deliverynotes
        """
        return self._make_request('GET', 'customerDepot/deliverynotes', headers=headers)

    def get_delivery_note(self, note_id, headers=None):
        """
        GET /customerDepot/deliverynotes/{id}
        """
        return self._make_request('GET', f'customerDepot/deliverynotes/{note_id}', headers=headers)

    def get_all_products(self, headers=None):
        """
        GET /customerDepot/products/all
        """
        return self._make_request('GET', 'customerDepot/products/all', headers=headers)

    def get_products(self, headers=None):
        """
        GET /customerDepot/products
        """
        return self._make_request('GET', 'customerDepot/products', headers=headers)

    def get_product(self, product_id, headers=None):
        """
        GET /customerDepot/products/{id}
        """
        return self._make_request('GET', f'customerDepot/products/{product_id}', headers=headers)

    def get_orders(self, headers=None):
        """
        GET /customerDepot/orders
        """
        return self._make_request('GET', 'customerDepot/orders', headers=headers)

    def create_order(self, order_data, headers=None):
        """
        POST /customerDepot/orders
        """
        return self._make_request('POST', 'customerDepot/orders', json=order_data, headers=headers)

    def get_order(self, order_id, headers=None):
        """
        GET /customerDepot/orders/{id}
        """
        return self._make_request('GET', f'customerDepot/orders/{order_id}', headers=headers)
