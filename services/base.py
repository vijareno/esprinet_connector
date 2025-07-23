# -*- coding: utf-8 -*-

import requests
import logging
from odoo import models, _
from odoo.exceptions import UserError
import time
from datetime import datetime

_logger = logging.getLogger(__name__)

class EsprinetApiBaseService(models.AbstractModel):
    _name = 'esprinet.api.base.service'
    _description = 'Esprinet API Base Service'

    def _get_base_url(self):
        """
        Obtiene la URL de la API de Esprinet desde la configuración.
        """
        return self.env['ir.config_parameter'].sudo().get_param(
            'esprinet_connector.url_api',
            default='https://ws-uat.esprinet.com/b2b/api/v2.0'
        )

    def _get_credentials(self):
        """
        Obtiene las credenciales configuradas.
        """
        get_param = self.env['ir.config_parameter'].sudo().get_param
        username = get_param('esprinet_connector.username')
        password = get_param('esprinet_connector.password')

        if not username or not password:
            raise UserError(_('Esprinet username and password are not configured.'))

        return username, password

    def _perform_login(self):
        """
        Realiza el inicio de sesión para obtener el token de autenticación.
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
            expiresUtc = response_data.get('expiresUtc')

            if not auth_token or auth_token is None:
                resultDetails = response_data.get('resultDetails', {})
                if resultDetails:
                    error_code = resultDetails.get(
                        'resultCode',
                        'Unknown error'
                    )
                    error_message = resultDetails.get(
                        'resultMessage',
                        'No authentication token received'
                    )
                    _logger.error(
                        "Login failed: %s - %s",
                        error_code,
                        error_message
                    )
                    raise UserError(_('Authentication failed: %s - %s') % (error_code, error_message))

                _logger.error("Login successful but no authenticationToken received")
                raise UserError(_('Authentication failed: No token received from Esprinet API'))

            _logger.info("Successfully logged in to Esprinet API")

            return auth_token, expiresUtc

        except requests.exceptions.HTTPError as e:
            _logger.error("Login HTTP Error: %s - %s", e.response.status_code, e.response.text)
            self.env['ir.config_parameter'].sudo().set_param(
                'esprinet_connector.auth_token',
                None
            )
            raise UserError(_('Login failed: %s') % e.response.text)
        except requests.exceptions.RequestException as e:
            _logger.error("Login Request Exception: %s", e)
            raise UserError(_('Login failed: Connection error'))

    def _get_auth_token(self):
        """
        Obtiene el token de autenticación con un mecanismo de caché.
        """
        # Check if we have a cached token that's still valid
        cache_key = 'esprinet_connector.auth_token'
        cache_expiry_key = 'esprinet_connector.auth_token_expiry'

        cached_token = self.env['ir.config_parameter'].sudo().get_param(cache_key)
        token_expiry = self.env['ir.config_parameter'].sudo().get_param(cache_expiry_key)

        if cached_token and token_expiry:
            try:
                # Ajustar para manejar precisión adicional en el formato ISO 8601
                token_expiry_time = datetime.strptime(token_expiry.split('.')[0], "%Y-%m-%dT%H:%M:%S").timestamp()
                if time.time() < token_expiry_time:
                    return cached_token
            except ValueError:
                _logger.error("Invalid token expiry format: %s", token_expiry)

        auth_token, expires_utc = self._perform_login()

        self.env['ir.config_parameter'].sudo().set_param(
            cache_key,
            auth_token
        )
        self.env['ir.config_parameter'].sudo().set_param(
            cache_expiry_key,
            expires_utc
        )

        return auth_token

    def _get_session(self):
        """
        Crea una sesión con el token de autenticación.
        """
        session = requests.Session()
        auth_token = self._get_auth_token()

        # Set the Authorization header with the token
        session.headers.update({
            'Authorization': f'Bearer {auth_token}'
        })

        return session

    def _make_request(self, method, endpoint, params=None, json=None, headers=None):
        """
        Realiza una solicitud HTTP a la API de Esprinet.

        :param method: Método HTTP (GET, POST, etc.).
        :param endpoint: Endpoint de la API.
        :param params: Parámetros de consulta.
        :param json: Datos en formato JSON.
        :param headers: Encabezados adicionales.
        :return: Respuesta de la API en formato JSON o None en caso de error.
        """
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
            response = session.request(
                method,
                url,
                params=params,
                json=json,
                headers=default_headers,
                timeout=30
            )
            response.raise_for_status()
            if response.status_code == 204:  # No Content
                return True
            return response.json()
        except requests.exceptions.HTTPError as e:
            _logger.error("HTTP Error for %s: %s", url, e.response.text)
            self.env['ir.config_parameter'].sudo().set_param(
                'esprinet_connector.auth_token',
                None
            )
            return None
        except requests.exceptions.RequestException as e:
            _logger.error("Request Exception for %s: %s", url, e)
            return None
