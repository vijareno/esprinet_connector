# -*- coding: utf-8 -*-

from odoo import models

class EsprinetCustomerQuotationsService(models.AbstractModel):
    _name = 'esprinet.api.customer_quotations.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Customer Quotations Service'

    def create_quotation(self, quotation_data, headers=None):
        """
        POST /customerQuotations
        """
        return self._make_request('POST', 'customerQuotations', json=quotation_data, headers=headers)

    def get_quotation(self, quotation_id, headers=None):
        """
        GET /customerQuotations/{id}
        """
        return self._make_request('GET', f'customerQuotations/{quotation_id}', headers=headers)
