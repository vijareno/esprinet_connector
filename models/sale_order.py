# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    esprinet_order_sent = fields.Boolean(
        string='Esprinet Order Sent',
        default=False,
        help='Indicates if the order has been sent to Esprinet'
    )
    esprinet_order_id = fields.Char(
        string='Esprinet Order ID',
        help='External order ID from Esprinet'
    )

    def action_confirm(self):
        """Override the confirm action to send orders to Esprinet if applicable"""
        result = super(SaleOrder, self).action_confirm()
        
        for order in self:
            if order._should_send_to_esprinet() and not order.esprinet_order_sent:
                try:
                    order._send_order_to_esprinet()
                except Exception as e:
                    _logger.error(f"Failed to send order {order.name} to Esprinet: {str(e)}")
                    # Continue with the normal flow even if Esprinet fails
                    # You might want to change this behavior based on business requirements
        
        return result

    def _should_send_to_esprinet(self):
        """
        Determine if the order should be sent to Esprinet
        Returns True if the order contains at least one product from Esprinet supplier
        """
        esprinet_supplier = self._get_esprinet_supplier()
        if not esprinet_supplier:
            return False

        for line in self.order_line:
            if line.product_id and line.product_id._is_esprinet_product():
                return True
        
        return False

    def _get_esprinet_supplier(self):
        """Get the Esprinet supplier record"""
        return self.env['res.partner'].search([
            ('ref', '=', 'ESPRINET_SUPPLIER')
        ], limit=1)

    def _send_order_to_esprinet(self):
        """Send the order to Esprinet using the orders service"""
        orders_service = self.env['esprinet.api.orders.service']
        order_data = self._prepare_esprinet_order_data()
        
        response = orders_service.create_order(order_data)
        
        if response.get('success'):
            self.write({
                'esprinet_order_sent': True,
                'esprinet_order_id': response.get('order_id')
            })
            _logger.info(f"Order {self.name} successfully sent to Esprinet with ID: {response.get('order_id')}")
        else:
            error_msg = response.get('error', 'Unknown error occurred')
            _logger.error(f"Failed to send order {self.name} to Esprinet: {error_msg}")
            raise UserError(_("Failed to send order to Esprinet: %s") % error_msg)

    def _prepare_esprinet_order_data(self):
        """
        Prepare order data in the format expected by Esprinet API
        This method should be customized based on Esprinet's API requirements
        """
        esprinet_lines = []
        
        for line in self.order_line:
            if line.product_id and line.product_id._is_esprinet_product():
                esprinet_lines.append({
                    'product_code': line.product_id.default_code or '',
                    'quantity': int(line.product_uom_qty),
                    'price': line.price_unit,
                })

        order_data = {
            'customer_reference': self.name,
            'delivery_address': self._get_delivery_address_data(),
            'lines': esprinet_lines,
            'notes': self.note or '',
        }
        
        return order_data

    def _get_delivery_address_data(self):
        """Prepare delivery address data for Esprinet"""
        partner = self.partner_shipping_id or self.partner_id
        
        return {
            'name': partner.name,
            'street': partner.street or '',
            'street2': partner.street2 or '',
            'city': partner.city or '',
            'zip': partner.zip or '',
            'country_code': partner.country_id.code if partner.country_id else '',
            'phone': partner.phone or '',
            'email': partner.email or '',
        }
