# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs

__all__ = [
    'GetFloatingIpsResult',
    'AwaitableGetFloatingIpsResult',
    'get_floating_ips',
    'get_floating_ips_output',
]

@pulumi.output_type
class GetFloatingIpsResult:
    """
    A collection of values returned by getFloatingIps.
    """
    def __init__(__self__, floating_ips=None, id=None, with_selector=None):
        if floating_ips and not isinstance(floating_ips, list):
            raise TypeError("Expected argument 'floating_ips' to be a list")
        pulumi.set(__self__, "floating_ips", floating_ips)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if with_selector and not isinstance(with_selector, str):
            raise TypeError("Expected argument 'with_selector' to be a str")
        pulumi.set(__self__, "with_selector", with_selector)

    @property
    @pulumi.getter(name="floatingIps")
    def floating_ips(self) -> Sequence['outputs.GetFloatingIpsFloatingIpResult']:
        """
        (list) List of all matching floating ips. See `data.hcloud_floating_ip` for schema.
        """
        return pulumi.get(self, "floating_ips")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="withSelector")
    def with_selector(self) -> Optional[str]:
        return pulumi.get(self, "with_selector")


class AwaitableGetFloatingIpsResult(GetFloatingIpsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetFloatingIpsResult(
            floating_ips=self.floating_ips,
            id=self.id,
            with_selector=self.with_selector)


def get_floating_ips(with_selector: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetFloatingIpsResult:
    """
    Provides details about multiple Hetzner Cloud Floating IPs.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_hcloud as hcloud

    ip2 = hcloud.get_floating_ips(with_selector="key=value")
    ```


    :param str with_selector: [Label selector](https://docs.hetzner.cloud/#overview-label-selector)
    """
    __args__ = dict()
    __args__['withSelector'] = with_selector
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('hcloud:index/getFloatingIps:getFloatingIps', __args__, opts=opts, typ=GetFloatingIpsResult).value

    return AwaitableGetFloatingIpsResult(
        floating_ips=__ret__.floating_ips,
        id=__ret__.id,
        with_selector=__ret__.with_selector)


@_utilities.lift_output_func(get_floating_ips)
def get_floating_ips_output(with_selector: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetFloatingIpsResult]:
    """
    Provides details about multiple Hetzner Cloud Floating IPs.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_hcloud as hcloud

    ip2 = hcloud.get_floating_ips(with_selector="key=value")
    ```


    :param str with_selector: [Label selector](https://docs.hetzner.cloud/#overview-label-selector)
    """
    ...
