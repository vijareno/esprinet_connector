# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    supplier_stock_qty = fields.Float(
        string='Stock del proveedor',
        help='Cantidad de stock disponible en el proveedor externo (dropshipping).',
        digits='Product Unit of Measure',
        readonly=False,
        store=True,
    )
    display_supplier_stock_in_website = fields.Boolean(
        string='Mostrar stock proveedor en web',
        help='Mostrar la cantidad de stock del proveedor en el sitio web (eCommerce).',
        default=False,
    )
