# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['ProviderArgs', 'Provider']

@pulumi.input_type
class ProviderArgs:
    def __init__(__self__, *,
                 kong_admin_uri: pulumi.Input[str],
                 kong_admin_password: Optional[pulumi.Input[str]] = None,
                 kong_admin_token: Optional[pulumi.Input[str]] = None,
                 kong_admin_username: Optional[pulumi.Input[str]] = None,
                 kong_api_key: Optional[pulumi.Input[str]] = None,
                 kong_workspace: Optional[pulumi.Input[str]] = None,
                 strict_plugins_match: Optional[pulumi.Input[bool]] = None,
                 tls_skip_verify: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a Provider resource.
        :param pulumi.Input[str] kong_admin_uri: The address of the kong admin url e.g. http://localhost:8001
        :param pulumi.Input[str] kong_admin_password: An basic auth password for kong admin
        :param pulumi.Input[str] kong_admin_token: API key for the kong api (Enterprise Edition)
        :param pulumi.Input[str] kong_admin_username: An basic auth user for kong admin
        :param pulumi.Input[str] kong_api_key: API key for the kong api (if you have locked it down)
        :param pulumi.Input[str] kong_workspace: Workspace context (Enterprise Edition)
        :param pulumi.Input[bool] strict_plugins_match: Should plugins `config_json` field strictly match plugin configuration
        :param pulumi.Input[bool] tls_skip_verify: Whether to skip tls verify for https kong api endpoint using self signed or untrusted certs
        """
        pulumi.set(__self__, "kong_admin_uri", kong_admin_uri)
        if kong_admin_password is not None:
            pulumi.set(__self__, "kong_admin_password", kong_admin_password)
        if kong_admin_token is not None:
            pulumi.set(__self__, "kong_admin_token", kong_admin_token)
        if kong_admin_username is not None:
            pulumi.set(__self__, "kong_admin_username", kong_admin_username)
        if kong_api_key is not None:
            pulumi.set(__self__, "kong_api_key", kong_api_key)
        if kong_workspace is not None:
            pulumi.set(__self__, "kong_workspace", kong_workspace)
        if strict_plugins_match is None:
            strict_plugins_match = _utilities.get_env_bool('STRICT_PLUGINS_MATCH')
        if strict_plugins_match is not None:
            pulumi.set(__self__, "strict_plugins_match", strict_plugins_match)
        if tls_skip_verify is None:
            tls_skip_verify = (_utilities.get_env_bool('TLS_SKIP_VERIFY') or False)
        if tls_skip_verify is not None:
            pulumi.set(__self__, "tls_skip_verify", tls_skip_verify)

    @property
    @pulumi.getter(name="kongAdminUri")
    def kong_admin_uri(self) -> pulumi.Input[str]:
        """
        The address of the kong admin url e.g. http://localhost:8001
        """
        return pulumi.get(self, "kong_admin_uri")

    @kong_admin_uri.setter
    def kong_admin_uri(self, value: pulumi.Input[str]):
        pulumi.set(self, "kong_admin_uri", value)

    @property
    @pulumi.getter(name="kongAdminPassword")
    def kong_admin_password(self) -> Optional[pulumi.Input[str]]:
        """
        An basic auth password for kong admin
        """
        return pulumi.get(self, "kong_admin_password")

    @kong_admin_password.setter
    def kong_admin_password(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kong_admin_password", value)

    @property
    @pulumi.getter(name="kongAdminToken")
    def kong_admin_token(self) -> Optional[pulumi.Input[str]]:
        """
        API key for the kong api (Enterprise Edition)
        """
        return pulumi.get(self, "kong_admin_token")

    @kong_admin_token.setter
    def kong_admin_token(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kong_admin_token", value)

    @property
    @pulumi.getter(name="kongAdminUsername")
    def kong_admin_username(self) -> Optional[pulumi.Input[str]]:
        """
        An basic auth user for kong admin
        """
        return pulumi.get(self, "kong_admin_username")

    @kong_admin_username.setter
    def kong_admin_username(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kong_admin_username", value)

    @property
    @pulumi.getter(name="kongApiKey")
    def kong_api_key(self) -> Optional[pulumi.Input[str]]:
        """
        API key for the kong api (if you have locked it down)
        """
        return pulumi.get(self, "kong_api_key")

    @kong_api_key.setter
    def kong_api_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kong_api_key", value)

    @property
    @pulumi.getter(name="kongWorkspace")
    def kong_workspace(self) -> Optional[pulumi.Input[str]]:
        """
        Workspace context (Enterprise Edition)
        """
        return pulumi.get(self, "kong_workspace")

    @kong_workspace.setter
    def kong_workspace(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kong_workspace", value)

    @property
    @pulumi.getter(name="strictPluginsMatch")
    def strict_plugins_match(self) -> Optional[pulumi.Input[bool]]:
        """
        Should plugins `config_json` field strictly match plugin configuration
        """
        return pulumi.get(self, "strict_plugins_match")

    @strict_plugins_match.setter
    def strict_plugins_match(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "strict_plugins_match", value)

    @property
    @pulumi.getter(name="tlsSkipVerify")
    def tls_skip_verify(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether to skip tls verify for https kong api endpoint using self signed or untrusted certs
        """
        return pulumi.get(self, "tls_skip_verify")

    @tls_skip_verify.setter
    def tls_skip_verify(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "tls_skip_verify", value)


class Provider(pulumi.ProviderResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 kong_admin_password: Optional[pulumi.Input[str]] = None,
                 kong_admin_token: Optional[pulumi.Input[str]] = None,
                 kong_admin_uri: Optional[pulumi.Input[str]] = None,
                 kong_admin_username: Optional[pulumi.Input[str]] = None,
                 kong_api_key: Optional[pulumi.Input[str]] = None,
                 kong_workspace: Optional[pulumi.Input[str]] = None,
                 strict_plugins_match: Optional[pulumi.Input[bool]] = None,
                 tls_skip_verify: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        The provider type for the kong package. By default, resources use package-wide configuration
        settings, however an explicit `Provider` instance may be created and passed during resource
        construction to achieve fine-grained programmatic control over provider settings. See the
        [documentation](https://www.pulumi.com/docs/reference/programming-model/#providers) for more information.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] kong_admin_password: An basic auth password for kong admin
        :param pulumi.Input[str] kong_admin_token: API key for the kong api (Enterprise Edition)
        :param pulumi.Input[str] kong_admin_uri: The address of the kong admin url e.g. http://localhost:8001
        :param pulumi.Input[str] kong_admin_username: An basic auth user for kong admin
        :param pulumi.Input[str] kong_api_key: API key for the kong api (if you have locked it down)
        :param pulumi.Input[str] kong_workspace: Workspace context (Enterprise Edition)
        :param pulumi.Input[bool] strict_plugins_match: Should plugins `config_json` field strictly match plugin configuration
        :param pulumi.Input[bool] tls_skip_verify: Whether to skip tls verify for https kong api endpoint using self signed or untrusted certs
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProviderArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        The provider type for the kong package. By default, resources use package-wide configuration
        settings, however an explicit `Provider` instance may be created and passed during resource
        construction to achieve fine-grained programmatic control over provider settings. See the
        [documentation](https://www.pulumi.com/docs/reference/programming-model/#providers) for more information.

        :param str resource_name: The name of the resource.
        :param ProviderArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProviderArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 kong_admin_password: Optional[pulumi.Input[str]] = None,
                 kong_admin_token: Optional[pulumi.Input[str]] = None,
                 kong_admin_uri: Optional[pulumi.Input[str]] = None,
                 kong_admin_username: Optional[pulumi.Input[str]] = None,
                 kong_api_key: Optional[pulumi.Input[str]] = None,
                 kong_workspace: Optional[pulumi.Input[str]] = None,
                 strict_plugins_match: Optional[pulumi.Input[bool]] = None,
                 tls_skip_verify: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        if opts is None:
            opts = pulumi.ResourceOptions()
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.version is None:
            opts.version = _utilities.get_version()
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ProviderArgs.__new__(ProviderArgs)

            __props__.__dict__["kong_admin_password"] = kong_admin_password
            __props__.__dict__["kong_admin_token"] = kong_admin_token
            if kong_admin_uri is None and not opts.urn:
                raise TypeError("Missing required property 'kong_admin_uri'")
            __props__.__dict__["kong_admin_uri"] = kong_admin_uri
            __props__.__dict__["kong_admin_username"] = kong_admin_username
            __props__.__dict__["kong_api_key"] = kong_api_key
            __props__.__dict__["kong_workspace"] = kong_workspace
            if strict_plugins_match is None:
                strict_plugins_match = _utilities.get_env_bool('STRICT_PLUGINS_MATCH')
            __props__.__dict__["strict_plugins_match"] = pulumi.Output.from_input(strict_plugins_match).apply(pulumi.runtime.to_json) if strict_plugins_match is not None else None
            if tls_skip_verify is None:
                tls_skip_verify = (_utilities.get_env_bool('TLS_SKIP_VERIFY') or False)
            __props__.__dict__["tls_skip_verify"] = pulumi.Output.from_input(tls_skip_verify).apply(pulumi.runtime.to_json) if tls_skip_verify is not None else None
        super(Provider, __self__).__init__(
            'kong',
            resource_name,
            __props__,
            opts)

    @property
    @pulumi.getter(name="kongAdminPassword")
    def kong_admin_password(self) -> pulumi.Output[Optional[str]]:
        """
        An basic auth password for kong admin
        """
        return pulumi.get(self, "kong_admin_password")

    @property
    @pulumi.getter(name="kongAdminToken")
    def kong_admin_token(self) -> pulumi.Output[Optional[str]]:
        """
        API key for the kong api (Enterprise Edition)
        """
        return pulumi.get(self, "kong_admin_token")

    @property
    @pulumi.getter(name="kongAdminUri")
    def kong_admin_uri(self) -> pulumi.Output[str]:
        """
        The address of the kong admin url e.g. http://localhost:8001
        """
        return pulumi.get(self, "kong_admin_uri")

    @property
    @pulumi.getter(name="kongAdminUsername")
    def kong_admin_username(self) -> pulumi.Output[Optional[str]]:
        """
        An basic auth user for kong admin
        """
        return pulumi.get(self, "kong_admin_username")

    @property
    @pulumi.getter(name="kongApiKey")
    def kong_api_key(self) -> pulumi.Output[Optional[str]]:
        """
        API key for the kong api (if you have locked it down)
        """
        return pulumi.get(self, "kong_api_key")

    @property
    @pulumi.getter(name="kongWorkspace")
    def kong_workspace(self) -> pulumi.Output[Optional[str]]:
        """
        Workspace context (Enterprise Edition)
        """
        return pulumi.get(self, "kong_workspace")

