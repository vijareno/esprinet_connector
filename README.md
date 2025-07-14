# Esprinet Connector

## Summary

Connector to synchronize products from Esprinet.

## Description

This module allows Odoo to connect to Esprinet's webservices to synchronize products, including their stock levels and prices. It automates the process of keeping your product catalog updated with the information from the supplier.

## Installation

1.  Copy the `esprinet_connector` folder into your Odoo `addons` directory.
2.  Restart the Odoo server.
3.  Go to `Apps` in your Odoo instance.
4.  Click on `Update Apps List`.
5.  Search for "Esprinet Connector" and click `Install`.

## Configuration

To configure the module, please follow these steps:

1.  Go to `Settings > General Settings > Esprinet Connector`.
2.  Here you will need to enter the credentials for the Esprinet API, such as username and password.
3.  You can also configure other settings related to the synchronization process.

## Usage

The synchronization of products is performed automatically by a scheduled action (cron job) that runs periodically.

The module will:
- Create new products that do not exist in Odoo.
- Update existing products with the latest information from Esprinet (e.g., price, stock).

You can also trigger the synchronization manually from the configuration screen if needed.

## Dependencies

This module depends on the following Odoo modules:
- `base`
- `product`

## Author

Your Name
[https://www.yourcompany.com](https://www.yourcompany.com)
