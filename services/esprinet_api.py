# -*- coding: utf-8 -*-

import requests
from odoo import models

class EsprinetApiService(models.AbstractModel):
    _name = 'esprinet.api.service'
    _description = 'Esprinet API Service'

    def _get_credentials(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        username = get_param('esprinet_connector.username')
        password = get_param('esprinet_connector.password')
        return username, password

    def _make_request(self, endpoint, params=None):
        username, password = self._get_credentials()
        if not username or not password:
            # Handle missing credentials
            return None
        
        # This is a placeholder for the actual API endpoint
        base_url = 'https://api.esprinet.com/'
        
        headers = {
            'Content-Type': 'application/json',
        }
        auth = (username, password)
        
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, auth=auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log the error
            return None

    def get_products(self):
        # This is a placeholder for the actual product endpoint
        return self._make_request('products')
