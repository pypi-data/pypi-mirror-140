# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetServiceResult',
    'AwaitableGetServiceResult',
    'get_service',
    'get_service_output',
]

@pulumi.output_type
class GetServiceResult:
    """
    A collection of values returned by getService.
    """
    def __init__(__self__, changing_affect_time=None, changing_charge_type=None, enable=None, id=None, internet_charge_type=None, opening_time=None, status=None):
        if changing_affect_time and not isinstance(changing_affect_time, str):
            raise TypeError("Expected argument 'changing_affect_time' to be a str")
        pulumi.set(__self__, "changing_affect_time", changing_affect_time)
        if changing_charge_type and not isinstance(changing_charge_type, str):
            raise TypeError("Expected argument 'changing_charge_type' to be a str")
        pulumi.set(__self__, "changing_charge_type", changing_charge_type)
        if enable and not isinstance(enable, str):
            raise TypeError("Expected argument 'enable' to be a str")
        pulumi.set(__self__, "enable", enable)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if internet_charge_type and not isinstance(internet_charge_type, str):
            raise TypeError("Expected argument 'internet_charge_type' to be a str")
        pulumi.set(__self__, "internet_charge_type", internet_charge_type)
        if opening_time and not isinstance(opening_time, str):
            raise TypeError("Expected argument 'opening_time' to be a str")
        pulumi.set(__self__, "opening_time", opening_time)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="changingAffectTime")
    def changing_affect_time(self) -> str:
        """
        The time when the change of the billing method starts to take effect. The time is displayed in GMT.
        """
        return pulumi.get(self, "changing_affect_time")

    @property
    @pulumi.getter(name="changingChargeType")
    def changing_charge_type(self) -> str:
        """
        The billing method to be effective.
        """
        return pulumi.get(self, "changing_charge_type")

    @property
    @pulumi.getter
    def enable(self) -> Optional[str]:
        return pulumi.get(self, "enable")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="internetChargeType")
    def internet_charge_type(self) -> Optional[str]:
        return pulumi.get(self, "internet_charge_type")

    @property
    @pulumi.getter(name="openingTime")
    def opening_time(self) -> str:
        """
        The time when the CDN service was activated. The time follows the ISO 8601 standard in the yyyy-MM-ddThh:mmZ format.
        """
        return pulumi.get(self, "opening_time")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        The current service enable status.
        """
        return pulumi.get(self, "status")


class AwaitableGetServiceResult(GetServiceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetServiceResult(
            changing_affect_time=self.changing_affect_time,
            changing_charge_type=self.changing_charge_type,
            enable=self.enable,
            id=self.id,
            internet_charge_type=self.internet_charge_type,
            opening_time=self.opening_time,
            status=self.status)


def get_service(enable: Optional[str] = None,
                internet_charge_type: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetServiceResult:
    """
    Using this data source can enable CDN service automatically. If the service has been enabled, it will return `Opened`.

    For information about CDN and how to use it, see [What is CDN](https://www.alibabacloud.com/help/product/27099.htm).

    > **NOTE:** Available in v1.98.0+

    ## Example Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    open = alicloud.cdn.get_service(enable="On",
        internet_charge_type="PayByTraffic")
    ```


    :param str enable: Setting the value to `On` to enable the service. If has been enabled, return the result. Valid values: "On" or "Off". Default to "Off".
    :param str internet_charge_type: The new billing method. Valid values: `PayByTraffic` and `PayByBandwidth`. Default value: `PayByTraffic`.
           It is required when `enable = on`. If the CDN service has been opened and you can update its internet charge type by modifying the filed `internet_charge_type`.
           As a note, the updated internet charge type will be effective in the next day zero time.
    """
    __args__ = dict()
    __args__['enable'] = enable
    __args__['internetChargeType'] = internet_charge_type
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('alicloud:cdn/getService:getService', __args__, opts=opts, typ=GetServiceResult).value

    return AwaitableGetServiceResult(
        changing_affect_time=__ret__.changing_affect_time,
        changing_charge_type=__ret__.changing_charge_type,
        enable=__ret__.enable,
        id=__ret__.id,
        internet_charge_type=__ret__.internet_charge_type,
        opening_time=__ret__.opening_time,
        status=__ret__.status)


@_utilities.lift_output_func(get_service)
def get_service_output(enable: Optional[pulumi.Input[Optional[str]]] = None,
                       internet_charge_type: Optional[pulumi.Input[Optional[str]]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetServiceResult]:
    """
    Using this data source can enable CDN service automatically. If the service has been enabled, it will return `Opened`.

    For information about CDN and how to use it, see [What is CDN](https://www.alibabacloud.com/help/product/27099.htm).

    > **NOTE:** Available in v1.98.0+

    ## Example Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    open = alicloud.cdn.get_service(enable="On",
        internet_charge_type="PayByTraffic")
    ```


    :param str enable: Setting the value to `On` to enable the service. If has been enabled, return the result. Valid values: "On" or "Off". Default to "Off".
    :param str internet_charge_type: The new billing method. Valid values: `PayByTraffic` and `PayByBandwidth`. Default value: `PayByTraffic`.
           It is required when `enable = on`. If the CDN service has been opened and you can update its internet charge type by modifying the filed `internet_charge_type`.
           As a note, the updated internet charge type will be effective in the next day zero time.
    """
    ...
