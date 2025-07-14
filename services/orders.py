# -*- coding: utf-8 -*-

from odoo import models

class EsprinetOrdersService(models.AbstractModel):
    _name = 'esprinet.api.orders.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Orders Service'

    def get_orders(self, headers=None):
        """
        GET /orders
        """
        return self._make_request('GET', 'orders', headers=headers)

    def create_order(self, order_data, headers=None):
        """
        POST /orders
        """
        return self._make_request('POST', 'orders', json=order_data, headers=headers)

    def get_order(self, order_id, headers=None):
        """
        GET /orders/{id}
        """
        return self._make_request('GET', f'orders/{order_id}', headers=headers)

    def delete_order(self, order_id, headers=None):
        """
        DELETE /orders/{id}
        """
        return self._make_request('DELETE', f'orders/{order_id}', headers=headers)

    def update_order(self, order_id, order_data, headers=None):
        """
        PUT /orders/{id}
        """
        return self._make_request('PUT', f'orders/{order_id}', json=order_data, headers=headers)

    def patch_order(self, order_id, order_data, headers=None):
        """
        PATCH /orders/{id}
        """
        return self._make_request('PATCH', f'orders/{order_id}', json=order_data, headers=headers)

    def get_order_summary(self, headers=None):
        """
        GET /orders/summary
        """
        return self._make_request('GET', 'orders/summary', headers=headers)

    def get_order_transaction(self, transaction_id, headers=None):
        """
        GET /orders/transactions/{id}
        """
        return self._make_request('GET', f'orders/transactions/{transaction_id}', headers=headers)

    def delete_order_line(self, order_id, order_line_id, headers=None):
        """
        DELETE /orders/{orderId}/lines/{orderLineId}
        """
        return self._make_request('DELETE', f'orders/{order_id}/lines/{order_line_id}', headers=headers)

    def get_shippers(self, headers=None):
        """
        GET /orders/freightForwading/Shippers
        """
        return self._make_request('GET', 'orders/freightForwading/Shippers', headers=headers)

    def validate_apple_order(self, validation_data, headers=None):
        """
        POST /orders/apple-validate
        """
        return self._make_request('POST', 'orders/apple-validate', json=validation_data, headers=headers)
