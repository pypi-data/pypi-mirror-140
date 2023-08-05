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
                 endpoint: pulumi.Input[str],
                 username: pulumi.Input[str],
                 authentication_plugin: Optional[pulumi.Input[str]] = None,
                 max_conn_lifetime_sec: Optional[pulumi.Input[int]] = None,
                 max_open_conns: Optional[pulumi.Input[int]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 proxy: Optional[pulumi.Input[str]] = None,
                 tls: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Provider resource.
        """
        pulumi.set(__self__, "endpoint", endpoint)
        pulumi.set(__self__, "username", username)
        if authentication_plugin is not None:
            pulumi.set(__self__, "authentication_plugin", authentication_plugin)
        if max_conn_lifetime_sec is not None:
            pulumi.set(__self__, "max_conn_lifetime_sec", max_conn_lifetime_sec)
        if max_open_conns is not None:
            pulumi.set(__self__, "max_open_conns", max_open_conns)
        if password is not None:
            pulumi.set(__self__, "password", password)
        if proxy is None:
            proxy = _utilities.get_env('ALL_PROXY', 'all_proxy')
        if proxy is not None:
            pulumi.set(__self__, "proxy", proxy)
        if tls is None:
            tls = (_utilities.get_env('MYSQL_TLS_CONFIG') or 'false')
        if tls is not None:
            pulumi.set(__self__, "tls", tls)

    @property
    @pulumi.getter
    def endpoint(self) -> pulumi.Input[str]:
        return pulumi.get(self, "endpoint")

    @endpoint.setter
    def endpoint(self, value: pulumi.Input[str]):
        pulumi.set(self, "endpoint", value)

    @property
    @pulumi.getter
    def username(self) -> pulumi.Input[str]:
        return pulumi.get(self, "username")

    @username.setter
    def username(self, value: pulumi.Input[str]):
        pulumi.set(self, "username", value)

    @property
    @pulumi.getter(name="authenticationPlugin")
    def authentication_plugin(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "authentication_plugin")

    @authentication_plugin.setter
    def authentication_plugin(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "authentication_plugin", value)

    @property
    @pulumi.getter(name="maxConnLifetimeSec")
    def max_conn_lifetime_sec(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "max_conn_lifetime_sec")

    @max_conn_lifetime_sec.setter
    def max_conn_lifetime_sec(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_conn_lifetime_sec", value)

    @property
    @pulumi.getter(name="maxOpenConns")
    def max_open_conns(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "max_open_conns")

    @max_open_conns.setter
    def max_open_conns(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_open_conns", value)

    @property
    @pulumi.getter
    def password(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "password")

    @password.setter
    def password(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password", value)

    @property
    @pulumi.getter
    def proxy(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "proxy")

    @proxy.setter
    def proxy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "proxy", value)

    @property
    @pulumi.getter
    def tls(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "tls")

    @tls.setter
    def tls(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tls", value)


class Provider(pulumi.ProviderResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 authentication_plugin: Optional[pulumi.Input[str]] = None,
                 endpoint: Optional[pulumi.Input[str]] = None,
                 max_conn_lifetime_sec: Optional[pulumi.Input[int]] = None,
                 max_open_conns: Optional[pulumi.Input[int]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 proxy: Optional[pulumi.Input[str]] = None,
                 tls: Optional[pulumi.Input[str]] = None,
                 username: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        The provider type for the mysql package. By default, resources use package-wide configuration
        settings, however an explicit `Provider` instance may be created and passed during resource
        construction to achieve fine-grained programmatic control over provider settings. See the
        [documentation](https://www.pulumi.com/docs/reference/programming-model/#providers) for more information.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProviderArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        The provider type for the mysql package. By default, resources use package-wide configuration
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
                 authentication_plugin: Optional[pulumi.Input[str]] = None,
                 endpoint: Optional[pulumi.Input[str]] = None,
                 max_conn_lifetime_sec: Optional[pulumi.Input[int]] = None,
                 max_open_conns: Optional[pulumi.Input[int]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 proxy: Optional[pulumi.Input[str]] = None,
                 tls: Optional[pulumi.Input[str]] = None,
                 username: Optional[pulumi.Input[str]] = None,
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

            __props__.__dict__["authentication_plugin"] = authentication_plugin
            if endpoint is None and not opts.urn:
                raise TypeError("Missing required property 'endpoint'")
            __props__.__dict__["endpoint"] = endpoint
            __props__.__dict__["max_conn_lifetime_sec"] = pulumi.Output.from_input(max_conn_lifetime_sec).apply(pulumi.runtime.to_json) if max_conn_lifetime_sec is not None else None
            __props__.__dict__["max_open_conns"] = pulumi.Output.from_input(max_open_conns).apply(pulumi.runtime.to_json) if max_open_conns is not None else None
            __props__.__dict__["password"] = password
            if proxy is None:
                proxy = _utilities.get_env('ALL_PROXY', 'all_proxy')
            __props__.__dict__["proxy"] = proxy
            if tls is None:
                tls = (_utilities.get_env('MYSQL_TLS_CONFIG') or 'false')
            __props__.__dict__["tls"] = tls
            if username is None and not opts.urn:
                raise TypeError("Missing required property 'username'")
            __props__.__dict__["username"] = username
        super(Provider, __self__).__init__(
            'mysql',
            resource_name,
            __props__,
            opts)

    @property
    @pulumi.getter(name="authenticationPlugin")
    def authentication_plugin(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "authentication_plugin")

    @property
    @pulumi.getter
    def endpoint(self) -> pulumi.Output[str]:
        return pulumi.get(self, "endpoint")

    @property
    @pulumi.getter
    def password(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "password")

    @property
    @pulumi.getter
    def proxy(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "proxy")

    @property
    @pulumi.getter
    def tls(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "tls")

    @property
    @pulumi.getter
    def username(self) -> pulumi.Output[str]:
        return pulumi.get(self, "username")

