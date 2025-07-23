# -*- coding: utf-8 -*-

import ftplib
import json
import tempfile
import os
import logging
from odoo import models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class EsprinetCatalogueService(models.AbstractModel):
    _name = 'esprinet.catalogue.service'
    _description = 'Esprinet Catalogue FTP Service'

    def _get_ftp_config(self):
        """Get FTP configuration parameters"""
        get_param = self.env['ir.config_parameter'].sudo().get_param

        config = {
            'host': get_param('esprinet_connector.ftp_host'),
            'username': get_param('esprinet_connector.ftp_username'),
            'password': get_param('esprinet_connector.ftp_password'),
            'file_path': get_param('esprinet_connector.ftp_path'),
        }

        missing_params = [k for k, v in config.items() if not v]
        if missing_params:
            raise UserError(_('FTP configuration incomplete. Missing: %s') % ', '.join(missing_params))

        return config

    def _download_catalogue_file(self):
        """Download Catalogue.json from FTP server"""
        config = self._get_ftp_config()

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json')
        temp_file_path = temp_file.name

        try:
            _logger.info("Connecting to FTP server: %s", config['host'])

            # Connect to FTP server
            with ftplib.FTP(config['host']) as ftp:
                ftp.login(config['username'], config['password'])

                # Get file size for progress tracking
                try:
                    file_size = ftp.size(config['file_path'])
                    _logger.info("Catalogue file size: %s bytes", file_size)
                except:
                    file_size = None
                    _logger.warning("Could not determine file size")

                # Download file
                _logger.info("Starting download of %s", config['file_path'])

                def write_chunk(chunk):
                    temp_file.write(chunk)

                ftp.retrbinary(f"RETR {config['file_path']}", write_chunk)
                temp_file.close()

                _logger.info("Download completed successfully to %s", temp_file_path)
                return temp_file_path

        except ftplib.all_errors as e:
            temp_file.close()
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            _logger.error("FTP Error: %s", str(e))
            raise UserError(_('FTP download failed: %s') % str(e))
        except Exception as e:
            temp_file.close()
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            _logger.error("Download Error: %s", str(e))
            raise UserError(_('Download failed: %s') % str(e))

    def _debug_json_structure(self, file_path):
        """Debug the JSON structure to understand the format"""
        try:
            _logger.info("Debugging JSON structure...")

            # Read first few KB to understand structure
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(2048)  # Read first 2KB
                _logger.info("JSON sample (first 2KB): %s", sample[:500] + "..." if len(sample) > 500 else sample)

            _logger.info("JSON structure: Direct array of product objects")

        except Exception as e:
            _logger.error("Error debugging JSON structure: %s", str(e))

    def _process_catalogue_file(self, file_path):
        """Process the downloaded JSON file with streaming to handle large files"""
        try:
            _logger.info("Starting to process catalogue file: %s", file_path)

            # First, let's examine the JSON structure
            self._debug_json_structure(file_path)

            # Get or create Esprinet supplier
            esprinet_supplier = self._get_or_create_esprinet_supplier()

            products_processed = 0
            products_created = 0
            products_updated = 0

            # Stream process the JSON file to handle large files efficiently
            if not os.path.exists(file_path):
                _logger.error("File does not exist: %s", file_path)
                return {'processed': 0, 'created': 0, 'updated': 0}

            if os.path.getsize(file_path) == 0:
                _logger.error("File is empty: %s", file_path)
                return {'processed': 0, 'created': 0, 'updated': 0}

            if not os.access(file_path, os.R_OK):
                _logger.error("No read permissions for file: %s", file_path)
                return {'processed': 0, 'created': 0, 'updated': 0}

            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    # Load the JSON file - we know it's a direct array of products
                    _logger.info("Loading JSON file...")
                    products_data = json.load(file)

                    if not isinstance(products_data, list):
                        _logger.error("Expected JSON array, got %s", type(products_data))
                        return {'processed': 0, 'created': 0, 'updated': 0}

                    _logger.info("Processing JSON array of %s products...", len(products_data))

                    # Process each product
                    for product_data in products_data:
                        try:
                            result = self._process_single_product(product_data, esprinet_supplier)
                            products_processed += 1

                            if result == 'created':
                                products_created += 1
                            elif result == 'updated':
                                products_updated += 1

                            # Commit every 500 products to avoid memory issues
                            if products_processed % 500 == 0:
                                self.env.cr.commit()
                                _logger.info("Processed %s products...", products_processed)

                        except Exception as e:
                            _logger.error("Error processing product %s: %s", products_processed, str(e))
                            continue

                    if products_processed == 0:
                        _logger.error("No products processed from JSON")
                        return {'processed': 0, 'created': 0, 'updated': 0}

                except json.JSONDecodeError as e:
                    _logger.error("Invalid JSON file: %s", str(e))
                    return {'processed': 0, 'created': 0, 'updated': 0}
                except Exception as e:
                    _logger.error("Error processing JSON file: %s", str(e))
                    return {'processed': 0, 'created': 0, 'updated': 0}

            # Final commit only if we processed products successfully
            if products_processed > 0:
                try:
                    self.env.cr.commit()
                    _logger.info("Final commit completed successfully")
                except Exception as e:
                    _logger.error("Error in final commit: %s", str(e))
                    self.env.cr.rollback()

            _logger.info("Catalogue processing completed. Processed: %s, Created: %s, Updated: %s",
                        products_processed, products_created, products_updated)

            return {
                'processed': products_processed,
                'created': products_created,
                'updated': products_updated
            }

        except Exception as e:
            _logger.error("Error processing catalogue file: %s", str(e))
            raise UserError(_('Catalogue processing failed: %s') % str(e))

    def _process_single_product(self, product_data, supplier):
        """Process a single product from the catalogue"""
        try:
            _logger.debug("Processing product data: %s", str(product_data)[:300])

            # Extract product information - based on actual JSON structure
            sku = product_data.get('SKU')  # Confirmed field name
            name = product_data.get('Description')  # Using Description as primary name
            barcode = product_data.get('EAN')  # Confirmed field name
            part_number = product_data.get('PartNumber')  # Additional identifier

            # Use PartNumber as fallback for SKU if SKU is empty
            if not sku and part_number:
                sku = part_number

            supplier_price = product_data.get('StandardDealerPrice', 0.0)  # Confirmed field name
            price = product_data.get('ListPrice', 0.0)  # Confirmed field name

            if not sku:
                _logger.warning("Product without SKU found, available keys: %s", list(product_data.keys()) if isinstance(product_data, dict) else "Not a dict")
                return 'skipped'

            _logger.debug("Processing product SKU: %s, Name: %s", sku, name)

            # Search for existing product by default_code (SKU) or barcode
            existing_product = self.env['product.product'].search([
                '|',
                ('default_code', '=', sku),
                ('barcode', '=', barcode)
            ], limit=1)

            # Obtener margen de venta desde la configuración
            margin = 10.0
            try:
                margin = float(self.env['ir.config_parameter'].sudo().get_param('esprinet_connector.sale_margin', default=0.0))
            except Exception:
                margin = 10.0

            cost = float(supplier_price) if supplier_price else 0.0
            list_price = cost * (1 + margin / 100.0)
            volume = (float(product_data.get('Depth')) * float(product_data.get('Length')) * float(product_data.get('Height'))) / 1000
            product_vals = {
                'name': name or f'Product {sku}',
                'default_code': sku,
                'barcode': barcode,
                'standard_price': cost,
                'list_price': list_price,
                'volume': volume,
                'type': 'product',
                'purchase_ok': True,
                'sale_ok': True,
            }

            # Add more fields based on catalogue structure
            grouping = product_data.get('Grouping')  # Confirmed field name

            if grouping:
                product_vals['categ_id'] = self._get_or_create_category(grouping)

            weight = product_data.get('GrossWeight')  # Confirmed field name

            if weight:
                try:
                    product_vals['weight'] = float(weight)
                except (ValueError, TypeError):
                    _logger.warning("Invalid weight value for product %s: %s", sku, weight)

            description = product_data.get('ExtendedDescription')  # Confirmed field name

            if description:
                product_vals['description'] = description
                product_vals['description_sale'] = description
                product_vals['description_purchase'] = description

            # Add additional fields that might be useful
            if product_data.get('PartNumber'):
                # Store PartNumber in internal reference if different from SKU
                if product_data.get('PartNumber') != sku:
                    product_vals['default_code'] = product_data.get('PartNumber')

            tax_supplier_id = self._get_or_create_tax(product_data.get('VatRate'), type='purchase')
            tax_sale_id = self._get_or_create_tax(product_data.get('VatRate'), type='sale')
            # Forzar actualización de impuestos en productos existentes
            product_vals['supplier_taxes_id'] = [(6, 0, [tax_supplier_id])] if tax_supplier_id else [(6, 0, [])]
            product_vals['taxes_id'] = [(6, 0, [tax_sale_id])] if tax_sale_id else [(6, 0, [])]

            if existing_product:
                return 'skipped'

            new_product = self.env['product.product'].create(product_vals)
            self._update_supplier_info(new_product, supplier, price)
            stock_qty = product_data.get('StockQty', 0.0)

            new_product.sudo().supplier_stock_qty = float(stock_qty)
            new_product.sudo().display_supplier_stock_in_website = True

            return 'created'

        except Exception as e:
            _logger.error("Error in _process_single_product: %s", str(e))
            return 'error'

    def _set_stock_quant(self, sku, product, stock_qty):
        try:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
            if not warehouse:
                _logger.warning("No stock.warehouse found for company_id %s. Cannot update stock for product %s.", self.env.company.id, sku)
                return
            location = warehouse.lot_stock_id
            quant = self.env['stock.quant'].with_context(inventory_mode=True).search([
                ('product_id', '=', product.id),
                ('location_id', '=', location.id)
            ], limit=1)
            if quant:
                _logger.debug(
                    "Actualizando quant para producto %s (ID: %s, type: %s, detailed_type: %s, company_id: %s) en almacén %s (ID: %s)",
                    sku, product.id, getattr(product, 'type', None), getattr(product, 'detailed_type', None), getattr(product, 'company_id', None), warehouse.name, warehouse.id
                )
                quant.inventory_quantity = float(stock_qty)
                quant._set_inventory_quantity()
            else:
                new_quant = self.env['stock.quant'].with_context(inventory_mode=True).create({
                    'product_id': product.id,
                    'location_id': location.id,
                    'inventory_quantity': float(stock_qty),
                })
                new_quant._set_inventory_quantity()

        except Exception as e:
            _logger.error("Error updating stock for product %s: %s", sku, str(e))

    def _search_tax_id(self, amount, type='purchase'):
        """Search for tax ID based on amount"""
        try:
            tax = self.env['account.tax'].search([
                ('amount', '=', amount),
                ('type_tax_use', '=', type)
            ], limit=1)
            if not tax:
                _logger.warning("No tax found for amount: %s", amount)
                return False
            return tax.id
        except Exception as e:
            _logger.error("Error searching tax ID: %s", str(e))
            return False

    def _create_supplier_tax(self, amount):
        """Create a new supplier tax record"""
        try:
            tax = self.env['account.tax'].create({
                'name': f"{amount} %",
                'amount': float(amount),
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
            })
            _logger.info("Created new tax: %s", tax.name)
            return tax.id
        except Exception as e:
            _logger.error("Error creating supplier tax: %s", str(e))
            return False

    def _create_sale_tax(self, amount):
        """Create a new sale tax record"""
        try:
            tax = self.env['account.tax'].create({
                'name': f"{amount} %",
                'amount': float(amount),
                'amount_type': 'percent',
                'type_tax_use': 'sale',
                'company_id': self.env.company.id,
            })
            _logger.info("Created new tax: %s", tax.name)
            return tax.id
        except Exception as e:
            _logger.error("Error creating sale tax: %s", str(e))
            return False

    def _get_or_create_tax(self, amount, type='purchase'):
        """Get or create a tax based on amount and type"""
        tax_id = self._search_tax_id(amount, type)
        if not tax_id:
            if type == 'purchase':
                tax_id = self._create_supplier_tax(amount)
            else:
                tax_id = self._create_sale_tax(amount)
        return tax_id if tax_id else False

    def _update_supplier_info(self, product, supplier, price):
        """Update or create supplier info for the product"""
        try:
            existing_supplierinfo = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('partner_id', '=', supplier.id)
            ], limit=1)

            supplierinfo_vals = {
                'partner_id': supplier.id,
                'product_tmpl_id': product.product_tmpl_id.id,
                'price': float(price) if price else 0.0,
                'min_qty': 1,
            }

            if existing_supplierinfo:
                existing_supplierinfo.write(supplierinfo_vals)
            else:
                self.env['product.supplierinfo'].create(supplierinfo_vals)

        except Exception as e:
            _logger.error("Error updating supplier info: %s", str(e))
            raise

    def _get_or_create_category(self, category_name):
        """Get or create product category"""
        category = self.env['product.category'].search([('name', '=', category_name)], limit=1)
        if not category:
            category = self.env['product.category'].create({'name': category_name})
        return category.id

    def _get_or_create_esprinet_supplier(self):
        """Get or create Esprinet supplier"""
        supplier = self.env['res.partner'].search([('name', '=', 'Esprinet')], limit=1)
        if not supplier:
            supplier = self.env['res.partner'].create({
                'name': 'Esprinet',
                'is_company': True,
                'supplier_rank': 1,
                'customer_rank': 0,
            })
        return supplier

    def download_and_process_catalogue(self):
        """Main method to download and process catalogue"""
        temp_file_path = None
        try:
            # Download file
            temp_file_path = self._download_catalogue_file()
            _logger.info("Catalogue file downloaded to: %s", temp_file_path)
            # Process file
            result = self._process_catalogue_file(temp_file_path)

            _logger.info("Catalogue sync completed successfully: %s", result)
            return result

        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    _logger.info("Temporary file cleaned up: %s", temp_file_path)
                except Exception as e:
                    _logger.warning("Could not clean up temporary file %s: %s", temp_file_path, str(e))
            pass
