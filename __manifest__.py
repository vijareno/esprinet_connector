# -*- coding: utf-8 -*-
{
    'name': 'Esprinet Connector',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Complete Esprinet integration for products and orders',
    'description': """
Esprinet Connector - Complete Integration Module
===============================================

This module provides a comprehensive integration with Esprinet's B2B webservices, enabling:

**Product Management:**
* Automatic synchronization of products from Esprinet catalog
* Real-time updates of product information (prices, stock, descriptions)
* Automatic supplier association for Esprinet products
* Scheduled synchronization via cron jobs

**Order Management:**
* Automatic detection of Esprinet products in sales orders
* Seamless order transmission to Esprinet upon confirmation
* Order tracking with Esprinet reference IDs
* Error handling and logging for failed transmissions

**Key Features:**
* Automated supplier creation during module installation
* Enhanced sales order views with Esprinet status indicators
* Robust error handling and logging
* Configurable API credentials through Odoo settings
* SOLID principles implementation for maintainable code

**Technical Implementation:**
* RESTful API integration with Esprinet's B2B platform
* Asynchronous processing to avoid blocking user operations
* Comprehensive service layer architecture
* Extended Odoo models with minimal core modifications

This module streamlines the entire procurement and sales process for Esprinet products,
reducing manual work and ensuring data consistency between systems.
    """,
    'author': 'Vicente Jareño Molina',
    'license': 'Other proprietary',
    'website': 'https://www.virunode.es',
    'depends': ['base', 'product', 'purchase', 'sale'],
    'external_dependencies': {
        'python': ['ftplib'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'data/cron.xml',
        'data/res_partner_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
