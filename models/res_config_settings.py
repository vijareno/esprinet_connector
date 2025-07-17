# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esprinet_username = fields.Char(string='Esprinet Username', config_parameter='esprinet_connector.username')
    esprinet_password = fields.Char(string='Esprinet Password', config_parameter='esprinet_connector.password', widget='password')
    
    # FTP Configuration
    esprinet_ftp_host = fields.Char(string='FTP Host', config_parameter='esprinet_connector.ftp_host')
    esprinet_ftp_username = fields.Char(string='FTP Username', config_parameter='esprinet_connector.ftp_username')
    esprinet_ftp_password = fields.Char(string='FTP Password', config_parameter='esprinet_connector.ftp_password', widget='password')
    esprinet_ftp_path = fields.Char(string='Catalogue File Path', config_parameter='esprinet_connector.ftp_path', 
                                   help='Path to Catalogue.json file on FTP server (e.g., /catalogue/Catalogue.json)')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('esprinet_connector.username', self.esprinet_username or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.password', self.esprinet_password or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_host', self.esprinet_ftp_host or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_username', self.esprinet_ftp_username or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_password', self.esprinet_ftp_password or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_path', self.esprinet_ftp_path or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            esprinet_username=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.username'),
            esprinet_password=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.password'),
            esprinet_ftp_host=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.ftp_host'),
            esprinet_ftp_username=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.ftp_username'),
            esprinet_ftp_password=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.ftp_password'),
            esprinet_ftp_path=self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.ftp_path'),
        )
        return res
    
    def action_download_catalogue(self):
        """Manual action to download and process catalogue"""
        try:
            catalogue_service = self.env['esprinet.catalogue.service']
            catalogue_service.download_and_process_catalogue()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Catalogue download and processing started successfully',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Failed to start catalogue processing: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
