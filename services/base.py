# -*- coding: utf-8 -*-

import requests
import logging
from odoo import models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EsprinetApiBaseService(models.AbstractModel):
    _name = 'esprinet.api.base.service'
    _description = 'Esprinet API Base Service'

    def _get_base_url(self):
        return 'https://ws-uat.esprinet.com/b2b/api/v2.0'

    def _get_session(self):
        """
        Manages the session and token.
        For now, we use basic auth. A real implementation should handle a login
        and token management.
        """
        session = requests.Session()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        username = get_param('esprinet_connector.username')
        password = get_param('esprinet_connector.password')

        if not username or not password:
            raise UserError(_('Esprinet username and password are not configured.'))

        session.auth = (username, password)
        return session

    def _make_request(self, method, endpoint, params=None, json=None, headers=None):
        base_url = self._get_base_url()
        url = f"{base_url}/{endpoint}"
        session = self._get_session()

        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if headers:
            default_headers.update(headers)

        try:
            response = session.request(method, url, params=params, json=json, headers=default_headers, timeout=30)
            response.raise_for_status()
            if response.status_code == 204:  # No Content
                return True
            return response.json()
        except requests.exceptions.HTTPError as e:
            _logger.error("HTTP Error for %s: %s", url, e.response.text)
            # You could raise a specific exception here
            return None
        except requests.exceptions.RequestException as e:
            _logger.error("Request Exception for %s: %s", url, e)
            return None
