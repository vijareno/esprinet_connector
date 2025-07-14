# -*- coding: utf-8 -*-
{
    'name': 'Esprinet Connector',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Connector to synchronize products from Esprinet',
    'description': """
This module allows to connect to Esprinet webservices to synchronize products.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
