# -*- coding: utf-8 -*-

from odoo import models

class EsprinetLoginService(models.AbstractModel):
    _name = 'esprinet.api.login.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Login Service'

    def login(self, headers=None):
        """
        POST /login
        This should be used to get a token for subsequent requests.
        The base service needs to be adapted to handle token authentication.
        """
        # The actual login logic will depend on the API's authentication mechanism.
        # This is a placeholder.
        return self._make_request('POST', 'login', headers=headers)
