# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'GetStocksResult',
    'AwaitableGetStocksResult',
    'get_stocks',
    'get_stocks_output',
]

@pulumi.output_type
class GetStocksResult:
    """
    A collection of values returned by getStocks.
    """
    def __init__(__self__, gateway_class=None, id=None, output_file=None, stocks=None):
        if gateway_class and not isinstance(gateway_class, str):
            raise TypeError("Expected argument 'gateway_class' to be a str")
        pulumi.set(__self__, "gateway_class", gateway_class)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if output_file and not isinstance(output_file, str):
            raise TypeError("Expected argument 'output_file' to be a str")
        pulumi.set(__self__, "output_file", output_file)
        if stocks and not isinstance(stocks, list):
            raise TypeError("Expected argument 'stocks' to be a list")
        pulumi.set(__self__, "stocks", stocks)

    @property
    @pulumi.getter(name="gatewayClass")
    def gateway_class(self) -> Optional[str]:
        return pulumi.get(self, "gateway_class")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="outputFile")
    def output_file(self) -> Optional[str]:
        return pulumi.get(self, "output_file")

    @property
    @pulumi.getter
    def stocks(self) -> Sequence['outputs.GetStocksStockResult']:
        return pulumi.get(self, "stocks")


class AwaitableGetStocksResult(GetStocksResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetStocksResult(
            gateway_class=self.gateway_class,
            id=self.id,
            output_file=self.output_file,
            stocks=self.stocks)


def get_stocks(gateway_class: Optional[str] = None,
               output_file: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetStocksResult:
    """
    This data source provides the Cloud Storage Gateway Stocks of the current Alibaba Cloud user.

    > **NOTE:** Available in v1.144.0+.

    ## Example Usage

    Basic Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    default = alicloud.cloudstoragegateway.get_stocks(gateway_class="Advanced")
    pulumi.export("zoneId", default.stocks[0].zone_id)
    ```


    :param str gateway_class: The gateway class. Valid values: `Basic`, `Standard`,`Enhanced`,`Advanced`.
    """
    __args__ = dict()
    __args__['gatewayClass'] = gateway_class
    __args__['outputFile'] = output_file
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('alicloud:cloudstoragegateway/getStocks:getStocks', __args__, opts=opts, typ=GetStocksResult).value

    return AwaitableGetStocksResult(
        gateway_class=__ret__.gateway_class,
        id=__ret__.id,
        output_file=__ret__.output_file,
        stocks=__ret__.stocks)


@_utilities.lift_output_func(get_stocks)
def get_stocks_output(gateway_class: Optional[pulumi.Input[Optional[str]]] = None,
                      output_file: Optional[pulumi.Input[Optional[str]]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetStocksResult]:
    """
    This data source provides the Cloud Storage Gateway Stocks of the current Alibaba Cloud user.

    > **NOTE:** Available in v1.144.0+.

    ## Example Usage

    Basic Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    default = alicloud.cloudstoragegateway.get_stocks(gateway_class="Advanced")
    pulumi.export("zoneId", default.stocks[0].zone_id)
    ```


    :param str gateway_class: The gateway class. Valid values: `Basic`, `Standard`,`Enhanced`,`Advanced`.
    """
    ...
