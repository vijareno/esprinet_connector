# -*- coding: utf-8 -*-

from odoo import models

class EsprinetCashAndCarriesService(models.AbstractModel):
    _name = 'esprinet.api.cashandcarries.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Cash and Carries Service'

    def get_products_availability(self, headers=None):
        """
        GET /cashandcarries/products/availability
        """
        return self._make_request('GET', 'cashandcarries/products/availability', headers=headers)

    def get_cash_products_availability(self, cash_id, headers=None):
        """
        GET /cashandcarries/{cashId}/products/availability
        """
        return self._make_request('GET', f'cashandcarries/{cash_id}/products/availability', headers=headers)

    def get_products_pricing(self, headers=None):
        """
        GET /cashandcarries/products/pricing
        """
        return self._make_request('GET', 'cashandcarries/products/pricing', headers=headers)

    def get_cash_products_pricing(self, cash_id, headers=None):
        """
        GET /cashandcarries/{cashId}/products/pricing
        """
        return self._make_request('GET', f'cashandcarries/{cash_id}/products/pricing', headers=headers)
