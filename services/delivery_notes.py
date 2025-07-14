# -*- coding: utf-8 -*-

from odoo import models

class EsprinetDeliveryNotesService(models.AbstractModel):
    _name = 'esprinet.api.delivery_notes.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Delivery Notes Service'

    def get_delivery_notes(self, headers=None):
        """
        GET /deliveryNotes
        """
        return self._make_request('GET', 'deliveryNotes', headers=headers)

    def get_delivery_note(self, note_id, headers=None):
        """
        GET /deliveryNotes/{id}
        """
        return self._make_request('GET', f'deliveryNotes/{note_id}', headers=headers)
