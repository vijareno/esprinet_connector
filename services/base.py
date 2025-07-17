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

    def _get_credentials(self):
        """Get configured credentials"""
        get_param = self.env['ir.config_parameter'].sudo().get_param
        username = get_param('esprinet_connector.username')
        password = get_param('esprinet_connector.password')

        if not username or not password:
            raise UserError(_('Esprinet username and password are not configured.'))
        
        return username, password

    def _perform_login(self):
        """
        Performs login to get authentication token
        """
        username, password = self._get_credentials()
        login_url = f"{self._get_base_url()}/login"
        
        login_data = {
            'username': username,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        try:
            response = requests.post(login_url, json=login_data, headers=headers, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            auth_token = response_data.get('authenticationToken')

            if not auth_token or auth_token is None:
                resultDetails = response_data.get('resultDetails', {})
                if resultDetails:
                    error_code = resultDetails.get('resultCode', 'Unknown error')
                    error_message = resultDetails.get('resultMessage', 'No authentication token received')
                    _logger.error("Login failed: %s - %s", error_code, error_message)
                    raise UserError(_('Authentication failed: %s - %s') % (error_code, error_message))
                _logger.error("Login successful but no authenticationToken received")
                raise UserError(_('Authentication failed: No token received from Esprinet API'))
            
            _logger.info("Successfully logged in to Esprinet API")
            return auth_token
            
        except requests.exceptions.HTTPError as e:
            _logger.error("Login HTTP Error: %s - %s", e.response.status_code, e.response.text)
            raise UserError(_('Login failed: %s') % e.response.text)
        except requests.exceptions.RequestException as e:
            _logger.error("Login Request Exception: %s", e)
            raise UserError(_('Login failed: Connection error'))

    def _get_auth_token(self):
        """
        Get authentication token with caching mechanism
        """
        # Check if we have a cached token that's still valid
        cache_key = 'esprinet_connector.auth_token'
        cache_expiry_key = 'esprinet_connector.auth_token_expiry'
        
        cached_token = self.env['ir.config_parameter'].sudo().get_param(cache_key)
        token_expiry = self.env['ir.config_parameter'].sudo().get_param(cache_expiry_key)
        
        if cached_token and token_expiry:
            import time
            if time.time() < float(token_expiry):
                return cached_token
        
        # Token expired or doesn't exist, get a new one
        auth_token = self._perform_login()
        
        # Cache the token for 1 hour (you may need to adjust based on Esprinet's token expiry)
        import time
        expiry_time = time.time() + 3600  # 1 hour from now
        
        self.env['ir.config_parameter'].sudo().set_param(cache_key, auth_token)
        self.env['ir.config_parameter'].sudo().set_param(cache_expiry_key, str(expiry_time))
        
        return auth_token

    def _get_session(self):
        """
        Creates a session with authentication token
        """
        session = requests.Session()
        auth_token = self._get_auth_token()
        
        # Set the Authorization header with the token
        session.headers.update({
            'Authorization': f'Bearer {auth_token}'
        })
        
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
