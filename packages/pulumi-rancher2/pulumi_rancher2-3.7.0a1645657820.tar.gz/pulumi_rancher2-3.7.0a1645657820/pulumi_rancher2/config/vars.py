# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

import types

__config__ = pulumi.Config('rancher2')


class _ExportableConfig(types.ModuleType):
    @property
    def access_key(self) -> Optional[str]:
        """
        API Key used to authenticate with the rancher server
        """
        return __config__.get('accessKey')

    @property
    def api_url(self) -> Optional[str]:
        """
        The URL to the rancher API
        """
        return __config__.get('apiUrl')

    @property
    def bootstrap(self) -> bool:
        """
        Bootstrap rancher server
        """
        return __config__.get_bool('bootstrap') or (_utilities.get_env_bool('RANCHER_BOOTSTRAP') or False)

    @property
    def ca_certs(self) -> Optional[str]:
        """
        CA certificates used to sign rancher server tls certificates. Mandatory if self signed tls and insecure option false
        """
        return __config__.get('caCerts')

    @property
    def insecure(self) -> bool:
        """
        Allow insecure connections to Rancher. Mandatory if self signed tls and not ca_certs provided
        """
        return __config__.get_bool('insecure') or (_utilities.get_env_bool('RANCHER_INSECURE') or False)

    @property
    def retries(self) -> Optional[int]:
        """
        Rancher connection retries
        """
        return __config__.get_int('retries')

    @property
    def secret_key(self) -> Optional[str]:
        """
        API secret used to authenticate with the rancher server
        """
        return __config__.get('secretKey')

    @property
    def timeout(self) -> Optional[str]:
        """
        Rancher connection timeout (retry every 5s). Golang duration format, ex: "60s"
        """
        return __config__.get('timeout')

    @property
    def token_key(self) -> Optional[str]:
        """
        API token used to authenticate with the rancher server
        """
        return __config__.get('tokenKey')

