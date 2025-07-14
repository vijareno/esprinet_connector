# -*- coding: utf-8 -*-

from odoo import models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _is_esprinet_product(self):
        """
        Check if this product is supplied by Esprinet
        Returns True if Esprinet is in the product's supplier list
        """
        return self.product_tmpl_id._is_esprinet_product()
