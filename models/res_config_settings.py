# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esprinet_username = fields.Char(string='Esprinet Username', config_parameter='esprinet_connector.username')
    esprinet_password = fields.Char(string='Esprinet Password', config_parameter='esprinet_connector.password', widget='password')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('esprinet_connector.username', self.esprinet_username or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.password', self.esprinet_password or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            esprinet_username=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.username'),
            esprinet_password=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.password'),
        )
        return res
