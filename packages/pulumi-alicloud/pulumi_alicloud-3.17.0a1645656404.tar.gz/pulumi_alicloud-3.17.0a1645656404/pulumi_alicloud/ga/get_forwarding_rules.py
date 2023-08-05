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
    'GetForwardingRulesResult',
    'AwaitableGetForwardingRulesResult',
    'get_forwarding_rules',
    'get_forwarding_rules_output',
]

@pulumi.output_type
class GetForwardingRulesResult:
    """
    A collection of values returned by getForwardingRules.
    """
    def __init__(__self__, accelerator_id=None, forwarding_rules=None, id=None, ids=None, listener_id=None, output_file=None, status=None):
        if accelerator_id and not isinstance(accelerator_id, str):
            raise TypeError("Expected argument 'accelerator_id' to be a str")
        pulumi.set(__self__, "accelerator_id", accelerator_id)
        if forwarding_rules and not isinstance(forwarding_rules, list):
            raise TypeError("Expected argument 'forwarding_rules' to be a list")
        pulumi.set(__self__, "forwarding_rules", forwarding_rules)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ids and not isinstance(ids, list):
            raise TypeError("Expected argument 'ids' to be a list")
        pulumi.set(__self__, "ids", ids)
        if listener_id and not isinstance(listener_id, str):
            raise TypeError("Expected argument 'listener_id' to be a str")
        pulumi.set(__self__, "listener_id", listener_id)
        if output_file and not isinstance(output_file, str):
            raise TypeError("Expected argument 'output_file' to be a str")
        pulumi.set(__self__, "output_file", output_file)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="acceleratorId")
    def accelerator_id(self) -> str:
        return pulumi.get(self, "accelerator_id")

    @property
    @pulumi.getter(name="forwardingRules")
    def forwarding_rules(self) -> Sequence['outputs.GetForwardingRulesForwardingRuleResult']:
        return pulumi.get(self, "forwarding_rules")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def ids(self) -> Sequence[str]:
        return pulumi.get(self, "ids")

    @property
    @pulumi.getter(name="listenerId")
    def listener_id(self) -> str:
        return pulumi.get(self, "listener_id")

    @property
    @pulumi.getter(name="outputFile")
    def output_file(self) -> Optional[str]:
        return pulumi.get(self, "output_file")

    @property
    @pulumi.getter
    def status(self) -> Optional[str]:
        return pulumi.get(self, "status")


class AwaitableGetForwardingRulesResult(GetForwardingRulesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetForwardingRulesResult(
            accelerator_id=self.accelerator_id,
            forwarding_rules=self.forwarding_rules,
            id=self.id,
            ids=self.ids,
            listener_id=self.listener_id,
            output_file=self.output_file,
            status=self.status)


def get_forwarding_rules(accelerator_id: Optional[str] = None,
                         ids: Optional[Sequence[str]] = None,
                         listener_id: Optional[str] = None,
                         output_file: Optional[str] = None,
                         status: Optional[str] = None,
                         opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetForwardingRulesResult:
    """
    This data source provides the Global Accelerator (GA) Forwarding Rules of the current Alibaba Cloud user.

    > **NOTE:** Available in v1.120.0+.

    ## Example Usage

    Basic Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    example = alicloud.ga.get_forwarding_rules(accelerator_id="example_value",
        listener_id="example_value",
        ids=["example_value"])
    pulumi.export("firstGaForwardingRuleId", example.forwarding_rules[0].id)
    ```


    :param str accelerator_id: The ID of the Global Accelerator instance.
    :param Sequence[str] ids: A list of Forwarding Rule IDs.
    :param str listener_id: The ID of the listener.
    :param str status: The status of the acceleration region. Valid values: `active`, `configuring`.
    """
    __args__ = dict()
    __args__['acceleratorId'] = accelerator_id
    __args__['ids'] = ids
    __args__['listenerId'] = listener_id
    __args__['outputFile'] = output_file
    __args__['status'] = status
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('alicloud:ga/getForwardingRules:getForwardingRules', __args__, opts=opts, typ=GetForwardingRulesResult).value

    return AwaitableGetForwardingRulesResult(
        accelerator_id=__ret__.accelerator_id,
        forwarding_rules=__ret__.forwarding_rules,
        id=__ret__.id,
        ids=__ret__.ids,
        listener_id=__ret__.listener_id,
        output_file=__ret__.output_file,
        status=__ret__.status)


@_utilities.lift_output_func(get_forwarding_rules)
def get_forwarding_rules_output(accelerator_id: Optional[pulumi.Input[str]] = None,
                                ids: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                                listener_id: Optional[pulumi.Input[str]] = None,
                                output_file: Optional[pulumi.Input[Optional[str]]] = None,
                                status: Optional[pulumi.Input[Optional[str]]] = None,
                                opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetForwardingRulesResult]:
    """
    This data source provides the Global Accelerator (GA) Forwarding Rules of the current Alibaba Cloud user.

    > **NOTE:** Available in v1.120.0+.

    ## Example Usage

    Basic Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    example = alicloud.ga.get_forwarding_rules(accelerator_id="example_value",
        listener_id="example_value",
        ids=["example_value"])
    pulumi.export("firstGaForwardingRuleId", example.forwarding_rules[0].id)
    ```


    :param str accelerator_id: The ID of the Global Accelerator instance.
    :param Sequence[str] ids: A list of Forwarding Rule IDs.
    :param str listener_id: The ID of the listener.
    :param str status: The status of the acceleration region. Valid values: `active`, `configuring`.
    """
    ...
