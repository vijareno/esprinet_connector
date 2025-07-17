# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esprinet_username = fields.Char(string='Usuario', config_parameter='esprinet_connector.username')
    esprinet_password = fields.Char(string='Contraseña', config_parameter='esprinet_connector.password')

    # FTP Configuration
    esprinet_ftp_host = fields.Char(string='Host FTP', config_parameter='esprinet_connector.ftp_host')
    esprinet_ftp_username = fields.Char(string='Usuario FTP', config_parameter='esprinet_connector.ftp_username')
    esprinet_ftp_password = fields.Char(string='Contraseña FTP', config_parameter='esprinet_connector.ftp_password')
    esprinet_ftp_path = fields.Char(string='Ruta del archivo de catálogo', config_parameter='esprinet_connector.ftp_path', 
                                   help='Ruta al archivo Catalogue.json en el servidor FTP (por ejemplo, Catalogue.json)')

    # Margen de venta
    esprinet_sale_margin = fields.Float(string='Porcentaje margen venta (%)', config_parameter='esprinet_connector.sale_margin',
        help='Porcentaje de margen a aplicar sobre el precio de coste para calcular el precio de venta.', default=10.0)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('esprinet_connector.username', self.esprinet_username or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.password', self.esprinet_password or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_host', self.esprinet_ftp_host or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_username', self.esprinet_ftp_username or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_password', self.esprinet_ftp_password or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.ftp_path', self.esprinet_ftp_path or '')
        self.env['ir.config_parameter'].set_param('esprinet_connector.sale_margin', self.esprinet_sale_margin or 0.0)

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
            esprinet_sale_margin=float(self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.sale_margin', default=0.0)),
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
