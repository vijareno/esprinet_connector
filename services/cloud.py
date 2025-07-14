# -*- coding: utf-8 -*-

from odoo import models

class EsprinetCloudService(models.AbstractModel):
    _name = 'esprinet.api.cloud.service'
    _inherit = 'esprinet.api.base.service'
    _description = 'Esprinet API Cloud Service'

    def get_tenants(self, headers=None):
        """
        GET /cloud/tenants
        """
        return self._make_request('GET', 'cloud/tenants', headers=headers)

    def create_tenant(self, tenant_data, headers=None):
        """
        POST /cloud/tenants
        """
        return self._make_request('POST', 'cloud/tenants', json=tenant_data, headers=headers)

    def get_tenant_subscriptions(self, tenant_id, headers=None):
        """
        GET /cloud/tenants/{id}/subscriptions
        """
        return self._make_request('GET', f'cloud/tenants/{tenant_id}/subscriptions', headers=headers)

    def update_tenant(self, tenant_id, tenant_data, headers=None):
        """
        PUT /cloud/tenants/{id}
        """
        return self._make_request('PUT', f'cloud/tenants/{tenant_id}', json=tenant_data, headers=headers)

    def check_domain(self, mpn_id, domain_id, headers=None):
        """
        POST /cloud/ms-csp/{mpnid}/domains/{id}
        """
        return self._make_request('POST', f'cloud/ms-csp/{mpn_id}/domains/{domain_id}', headers=headers)

    def get_domains(self, mpn_id, headers=None):
        """
        GET /cloud/ms-csp/{mpnid}/domains
        """
        return self._make_request('GET', f'cloud/ms-csp/{mpn_id}/domains', headers=headers)

    def get_delegations(self, mpn_id, headers=None):
        """
        GET /cloud/ms-csp/{mpnid}/delegations
        """
        return self._make_request('GET', f'cloud/ms-csp/{mpn_id}/delegations', headers=headers)

    def get_product_metadata(self, headers=None):
        """
        GET /cloud/product-metadata
        """
        return self._make_request('GET', 'cloud/product-metadata', headers=headers)

    def get_service_providers_info(self, headers=None):
        """
        GET /cloud/serviceprovidersinfo
        """
        return self._make_request('GET', 'cloud/serviceprovidersinfo', headers=headers)

    def search_subscriptions(self, headers=None):
        """
        GET /cloud/subscriptions/search
        """
        return self._make_request('GET', 'cloud/subscriptions/search', headers=headers)

    def get_subscription(self, subscription_id, headers=None):
        """
        GET /cloud/subscriptions/{id}
        """
        return self._make_request('GET', f'cloud/subscriptions/{subscription_id}', headers=headers)
