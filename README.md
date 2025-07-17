# Esprinet Connector

## Summary

Complete integration module for Esprinet B2B services, providing automated product synchronization and seamless order management between Odoo and Esprinet's platform.

## Description

This comprehensive module enables full integration with Esprinet's webservices, automating both product catalog management and sales order processing. It eliminates manual data entry and ensures real-time synchronization between your Odoo instance and Esprinet's B2B platform.

### Key Features

#### Product Management
- **Automated Product Synchronization**: Scheduled synchronization of products from Esprinet catalog
- **FTP Catalogue Download**: Download complete product catalogue from Esprinet FTP server
- **Large File Processing**: Efficient streaming processing of large catalogue files (200MB+)
- **Real-time Updates**: Automatic updates of product information including prices, stock levels, and descriptions
- **Supplier Association**: Automatic linking of synchronized products to Esprinet as supplier
- **New Product Creation**: Automatic creation of products that don't exist in your Odoo catalog

#### Order Management
- **Smart Order Detection**: Automatic identification of Esprinet products in sales orders
- **Seamless Order Transmission**: Instant order submission to Esprinet upon sales order confirmation
- **Order Tracking**: Visual indicators and tracking of order status with Esprinet reference IDs
- **Error Handling**: Comprehensive error handling with detailed logging for troubleshooting

#### User Interface Enhancements
- **Enhanced Sales Views**: Additional fields in sales order forms showing Esprinet integration status
- **Status Indicators**: Clear visual feedback on order transmission status
- **Configuration Panel**: User-friendly settings interface for API credentials and preferences

#### Technical Excellence
- **SOLID Architecture**: Clean, maintainable code following software engineering best practices
- **Service Layer**: Dedicated service classes for different API endpoints
- **Error Recovery**: Robust error handling that doesn't disrupt normal business operations
- **Logging**: Comprehensive logging for monitoring and debugging

## Installation

1. Copy the `esprinet_connector` folder into your Odoo `addons` directory.
2. Restart the Odoo server.
3. Go to `Apps` in your Odoo instance.
4. Click on `Update Apps List`.
5. Search for "Esprinet Connector" and click `Install`.

**Note**: The module will automatically create an Esprinet supplier record during installation.

## Configuration

### Initial Setup

1. Navigate to `Settings > General Settings > Esprinet Connector`.
2. Enter your Esprinet API credentials:
   - **Username**: Your Esprinet B2B username
   - **Password**: Your Esprinet B2B password
3. Configure FTP access for catalogue download:
   - **FTP Host**: Esprinet FTP server hostname
   - **FTP Username**: Your FTP username
   - **FTP Password**: Your FTP password
   - **Catalogue Path**: Path to Catalogue.json file (e.g., /catalogue/Catalogue.json)
4. Save the configuration.

### Verification

After configuration, verify the setup by:
1. Checking that the Esprinet supplier appears in your vendor list (`Purchases > Vendors`)
2. Running a manual product synchronization to test the connection
3. Confirming that products are properly associated with the Esprinet supplier

## Usage

### Automatic Operations

#### Product Synchronization
- **Scheduled Sync**: Products are automatically synchronized every 2 hours via cron job
- **FTP Catalogue Download**: Complete catalogue is downloaded daily from FTP server
- **New Products**: Products not existing in Odoo are automatically created
- **Updates**: Existing products are updated with latest information from Esprinet
- **Supplier Linking**: All synchronized products are automatically linked to Esprinet supplier
- **Large File Handling**: Efficient processing of large catalogue files using streaming JSON parsing

#### Order Processing
- **Automatic Detection**: When confirming a sales order, the system automatically detects Esprinet products
- **Instant Transmission**: Orders containing Esprinet products are immediately sent to Esprinet
- **Status Tracking**: Order transmission status is visible in the sales order form
- **Error Handling**: Failed transmissions are logged but don't prevent order confirmation

### Manual Operations

#### Manual Product Sync
You can trigger product synchronization manually from:
- Configuration screen: `Settings > General Settings > Esprinet Connector`
- Developer mode: `Settings > Technical > Automation > Scheduled Actions`

#### FTP Catalogue Download
- **Manual Download**: Use the "Download Catalogue Now" button in configuration
- **Scheduled Download**: Enable the daily catalogue download cron job
- **Progress Monitoring**: Check system logs for download and processing progress

#### Order Management
- View Esprinet order status in sales order forms
- Check transmission logs in system logs for troubleshooting
- Retry failed order transmissions if needed

## Workflow

### Product Synchronization Workflow
1. **Cron Trigger**: Scheduled action runs every 2 hours
2. **API Call**: System connects to Esprinet customer depot service
3. **Data Processing**: Retrieved products are processed and mapped to Odoo fields
4. **Database Update**: Products are created or updated in Odoo
5. **Supplier Association**: Products are automatically linked to Esprinet supplier
6. **Logging**: Synchronization results are logged for monitoring

### Order Transmission Workflow
1. **Order Confirmation**: User confirms a sales order in Odoo
2. **Product Analysis**: System analyzes order lines for Esprinet products
3. **Data Preparation**: Order data is formatted for Esprinet API
4. **API Transmission**: Order is sent to Esprinet via orders service
5. **Status Update**: Order record is updated with transmission status and Esprinet ID
6. **Error Handling**: Any errors are logged without blocking the order process

## Troubleshooting

### Common Issues

#### Product Synchronization Issues
- **Authentication Errors**: Verify API credentials in settings
- **Network Issues**: Check server connectivity to Esprinet services
- **Data Mapping**: Review logs for product-specific synchronization errors

#### Order Transmission Issues
- **Missing Supplier**: Ensure Esprinet supplier exists and products are properly linked
- **API Errors**: Check Esprinet API status and credential validity
- **Data Format**: Verify that order data meets Esprinet's requirements

### Logging and Monitoring
- **System Logs**: Check Odoo system logs for detailed error messages
- **Cron Logs**: Monitor scheduled action logs for synchronization status
- **Order Status**: Use sales order views to track transmission status

## Dependencies

This module requires the following Odoo modules:
- `base` - Core Odoo functionality
- `product` - Product management
- `purchase` - Supplier management
- `sale` - Sales order processing

## API Integration

The module integrates with the following Esprinet API endpoints:
- **Customer Depot Service**: For product synchronization
- **Orders Service**: For order transmission and management
- **Authentication Service**: For API access management

## Security

- API credentials are stored securely using Odoo's parameter system
- All API communications use HTTPS
- Error messages don't expose sensitive information in user interfaces

## Support and Maintenance

For technical support or feature requests, please contact:
- **Developer**: Vicente Jareño Molina
- **Website**: [https://www.virunode.es](https://www.virunode.es)

## Version History

- **v1.0**: Initial release with product sync and order transmission capabilities
