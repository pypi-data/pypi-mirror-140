# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetPluginResult',
    'AwaitableGetPluginResult',
    'get_plugin',
    'get_plugin_output',
]

@pulumi.output_type
class GetPluginResult:
    """
    A collection of values returned by getPlugin.
    """
    def __init__(__self__, alias=None, enabled=None, envs=None, grant_all_permissions=None, id=None, name=None, plugin_reference=None):
        if alias and not isinstance(alias, str):
            raise TypeError("Expected argument 'alias' to be a str")
        pulumi.set(__self__, "alias", alias)
        if enabled and not isinstance(enabled, bool):
            raise TypeError("Expected argument 'enabled' to be a bool")
        pulumi.set(__self__, "enabled", enabled)
        if envs and not isinstance(envs, list):
            raise TypeError("Expected argument 'envs' to be a list")
        pulumi.set(__self__, "envs", envs)
        if grant_all_permissions and not isinstance(grant_all_permissions, bool):
            raise TypeError("Expected argument 'grant_all_permissions' to be a bool")
        pulumi.set(__self__, "grant_all_permissions", grant_all_permissions)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if plugin_reference and not isinstance(plugin_reference, str):
            raise TypeError("Expected argument 'plugin_reference' to be a str")
        pulumi.set(__self__, "plugin_reference", plugin_reference)

    @property
    @pulumi.getter
    def alias(self) -> Optional[str]:
        """
        The alias of the Docker plugin. If the tag is omitted, `:latest` is complemented to the attribute value.
        """
        return pulumi.get(self, "alias")

    @property
    @pulumi.getter
    def enabled(self) -> bool:
        """
        If `true` the plugin is enabled
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter
    def envs(self) -> Sequence[str]:
        """
        The environment variables in the form of `KEY=VALUE`, e.g. `DEBUG=0`
        """
        return pulumi.get(self, "envs")

    @property
    @pulumi.getter(name="grantAllPermissions")
    def grant_all_permissions(self) -> bool:
        """
        If true, grant all permissions necessary to run the plugin
        """
        return pulumi.get(self, "grant_all_permissions")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        """
        The ID of the plugin, which has precedence over the `alias` of both are given
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The plugin name. If the tag is omitted, `:latest` is complemented to the attribute value.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="pluginReference")
    def plugin_reference(self) -> str:
        """
        The Docker Plugin Reference
        """
        return pulumi.get(self, "plugin_reference")


class AwaitableGetPluginResult(GetPluginResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetPluginResult(
            alias=self.alias,
            enabled=self.enabled,
            envs=self.envs,
            grant_all_permissions=self.grant_all_permissions,
            id=self.id,
            name=self.name,
            plugin_reference=self.plugin_reference)


def get_plugin(alias: Optional[str] = None,
               id: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetPluginResult:
    """
    Reads the local Docker plugin. The plugin must be installed locally.

    ## Example Usage

    ### With alias
    data "Plugin" "by_alias" {
      alias = "sample-volume-plugin:latest"
    }


    :param str alias: The alias of the Docker plugin. If the tag is omitted, `:latest` is complemented to the attribute value.
    :param str id: The ID of the plugin, which has precedence over the `alias` of both are given
    """
    __args__ = dict()
    __args__['alias'] = alias
    __args__['id'] = id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('docker:index/getPlugin:getPlugin', __args__, opts=opts, typ=GetPluginResult).value

    return AwaitableGetPluginResult(
        alias=__ret__.alias,
        enabled=__ret__.enabled,
        envs=__ret__.envs,
        grant_all_permissions=__ret__.grant_all_permissions,
        id=__ret__.id,
        name=__ret__.name,
        plugin_reference=__ret__.plugin_reference)


@_utilities.lift_output_func(get_plugin)
def get_plugin_output(alias: Optional[pulumi.Input[Optional[str]]] = None,
                      id: Optional[pulumi.Input[Optional[str]]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetPluginResult]:
    """
    Reads the local Docker plugin. The plugin must be installed locally.

    ## Example Usage

    ### With alias
    data "Plugin" "by_alias" {
      alias = "sample-volume-plugin:latest"
    }


    :param str alias: The alias of the Docker plugin. If the tag is omitted, `:latest` is complemented to the attribute value.
    :param str id: The ID of the plugin, which has precedence over the `alias` of both are given
    """
    ...
