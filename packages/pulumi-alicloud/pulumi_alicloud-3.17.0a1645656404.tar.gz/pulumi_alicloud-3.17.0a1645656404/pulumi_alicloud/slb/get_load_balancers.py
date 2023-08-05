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
    'GetLoadBalancersResult',
    'AwaitableGetLoadBalancersResult',
    'get_load_balancers',
    'get_load_balancers_output',
]

@pulumi.output_type
class GetLoadBalancersResult:
    """
    A collection of values returned by getLoadBalancers.
    """
    def __init__(__self__, address=None, address_ip_version=None, address_type=None, balancers=None, enable_details=None, id=None, ids=None, internet_charge_type=None, load_balancer_name=None, master_zone_id=None, name_regex=None, names=None, network_type=None, output_file=None, page_number=None, page_size=None, payment_type=None, resource_group_id=None, server_id=None, server_intranet_address=None, slave_zone_id=None, slbs=None, status=None, tags=None, total_count=None, vpc_id=None, vswitch_id=None):
        if address and not isinstance(address, str):
            raise TypeError("Expected argument 'address' to be a str")
        pulumi.set(__self__, "address", address)
        if address_ip_version and not isinstance(address_ip_version, str):
            raise TypeError("Expected argument 'address_ip_version' to be a str")
        pulumi.set(__self__, "address_ip_version", address_ip_version)
        if address_type and not isinstance(address_type, str):
            raise TypeError("Expected argument 'address_type' to be a str")
        pulumi.set(__self__, "address_type", address_type)
        if balancers and not isinstance(balancers, list):
            raise TypeError("Expected argument 'balancers' to be a list")
        pulumi.set(__self__, "balancers", balancers)
        if enable_details and not isinstance(enable_details, bool):
            raise TypeError("Expected argument 'enable_details' to be a bool")
        pulumi.set(__self__, "enable_details", enable_details)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ids and not isinstance(ids, list):
            raise TypeError("Expected argument 'ids' to be a list")
        pulumi.set(__self__, "ids", ids)
        if internet_charge_type and not isinstance(internet_charge_type, str):
            raise TypeError("Expected argument 'internet_charge_type' to be a str")
        pulumi.set(__self__, "internet_charge_type", internet_charge_type)
        if load_balancer_name and not isinstance(load_balancer_name, str):
            raise TypeError("Expected argument 'load_balancer_name' to be a str")
        pulumi.set(__self__, "load_balancer_name", load_balancer_name)
        if master_zone_id and not isinstance(master_zone_id, str):
            raise TypeError("Expected argument 'master_zone_id' to be a str")
        pulumi.set(__self__, "master_zone_id", master_zone_id)
        if name_regex and not isinstance(name_regex, str):
            raise TypeError("Expected argument 'name_regex' to be a str")
        pulumi.set(__self__, "name_regex", name_regex)
        if names and not isinstance(names, list):
            raise TypeError("Expected argument 'names' to be a list")
        pulumi.set(__self__, "names", names)
        if network_type and not isinstance(network_type, str):
            raise TypeError("Expected argument 'network_type' to be a str")
        pulumi.set(__self__, "network_type", network_type)
        if output_file and not isinstance(output_file, str):
            raise TypeError("Expected argument 'output_file' to be a str")
        pulumi.set(__self__, "output_file", output_file)
        if page_number and not isinstance(page_number, int):
            raise TypeError("Expected argument 'page_number' to be a int")
        pulumi.set(__self__, "page_number", page_number)
        if page_size and not isinstance(page_size, int):
            raise TypeError("Expected argument 'page_size' to be a int")
        pulumi.set(__self__, "page_size", page_size)
        if payment_type and not isinstance(payment_type, str):
            raise TypeError("Expected argument 'payment_type' to be a str")
        pulumi.set(__self__, "payment_type", payment_type)
        if resource_group_id and not isinstance(resource_group_id, str):
            raise TypeError("Expected argument 'resource_group_id' to be a str")
        pulumi.set(__self__, "resource_group_id", resource_group_id)
        if server_id and not isinstance(server_id, str):
            raise TypeError("Expected argument 'server_id' to be a str")
        pulumi.set(__self__, "server_id", server_id)
        if server_intranet_address and not isinstance(server_intranet_address, str):
            raise TypeError("Expected argument 'server_intranet_address' to be a str")
        pulumi.set(__self__, "server_intranet_address", server_intranet_address)
        if slave_zone_id and not isinstance(slave_zone_id, str):
            raise TypeError("Expected argument 'slave_zone_id' to be a str")
        pulumi.set(__self__, "slave_zone_id", slave_zone_id)
        if slbs and not isinstance(slbs, list):
            raise TypeError("Expected argument 'slbs' to be a list")
        if slbs is not None:
            warnings.warn("""Field 'slbs' has deprecated from v1.123.1 and replace by 'balancers'.""", DeprecationWarning)
            pulumi.log.warn("""slbs is deprecated: Field 'slbs' has deprecated from v1.123.1 and replace by 'balancers'.""")

        pulumi.set(__self__, "slbs", slbs)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if total_count and not isinstance(total_count, int):
            raise TypeError("Expected argument 'total_count' to be a int")
        pulumi.set(__self__, "total_count", total_count)
        if vpc_id and not isinstance(vpc_id, str):
            raise TypeError("Expected argument 'vpc_id' to be a str")
        pulumi.set(__self__, "vpc_id", vpc_id)
        if vswitch_id and not isinstance(vswitch_id, str):
            raise TypeError("Expected argument 'vswitch_id' to be a str")
        pulumi.set(__self__, "vswitch_id", vswitch_id)

    @property
    @pulumi.getter
    def address(self) -> Optional[str]:
        """
        Service address of the SLB.
        """
        return pulumi.get(self, "address")

    @property
    @pulumi.getter(name="addressIpVersion")
    def address_ip_version(self) -> Optional[str]:
        return pulumi.get(self, "address_ip_version")

    @property
    @pulumi.getter(name="addressType")
    def address_type(self) -> Optional[str]:
        return pulumi.get(self, "address_type")

    @property
    @pulumi.getter
    def balancers(self) -> Sequence['outputs.GetLoadBalancersBalancerResult']:
        return pulumi.get(self, "balancers")

    @property
    @pulumi.getter(name="enableDetails")
    def enable_details(self) -> Optional[bool]:
        return pulumi.get(self, "enable_details")

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
        """
        A list of slb IDs.
        """
        return pulumi.get(self, "ids")

    @property
    @pulumi.getter(name="internetChargeType")
    def internet_charge_type(self) -> Optional[str]:
        return pulumi.get(self, "internet_charge_type")

    @property
    @pulumi.getter(name="loadBalancerName")
    def load_balancer_name(self) -> Optional[str]:
        return pulumi.get(self, "load_balancer_name")

    @property
    @pulumi.getter(name="masterZoneId")
    def master_zone_id(self) -> Optional[str]:
        return pulumi.get(self, "master_zone_id")

    @property
    @pulumi.getter(name="nameRegex")
    def name_regex(self) -> Optional[str]:
        return pulumi.get(self, "name_regex")

    @property
    @pulumi.getter
    def names(self) -> Sequence[str]:
        """
        A list of slb names.
        """
        return pulumi.get(self, "names")

    @property
    @pulumi.getter(name="networkType")
    def network_type(self) -> Optional[str]:
        """
        Network type of the SLB. Possible values: `vpc` and `classic`.
        """
        return pulumi.get(self, "network_type")

    @property
    @pulumi.getter(name="outputFile")
    def output_file(self) -> Optional[str]:
        return pulumi.get(self, "output_file")

    @property
    @pulumi.getter(name="pageNumber")
    def page_number(self) -> Optional[int]:
        return pulumi.get(self, "page_number")

    @property
    @pulumi.getter(name="pageSize")
    def page_size(self) -> Optional[int]:
        return pulumi.get(self, "page_size")

    @property
    @pulumi.getter(name="paymentType")
    def payment_type(self) -> Optional[str]:
        return pulumi.get(self, "payment_type")

    @property
    @pulumi.getter(name="resourceGroupId")
    def resource_group_id(self) -> Optional[str]:
        return pulumi.get(self, "resource_group_id")

    @property
    @pulumi.getter(name="serverId")
    def server_id(self) -> Optional[str]:
        return pulumi.get(self, "server_id")

    @property
    @pulumi.getter(name="serverIntranetAddress")
    def server_intranet_address(self) -> Optional[str]:
        return pulumi.get(self, "server_intranet_address")

    @property
    @pulumi.getter(name="slaveZoneId")
    def slave_zone_id(self) -> Optional[str]:
        return pulumi.get(self, "slave_zone_id")

    @property
    @pulumi.getter
    def slbs(self) -> Sequence['outputs.GetLoadBalancersSlbResult']:
        """
        A list of SLBs. Each element contains the following attributes:
        """
        return pulumi.get(self, "slbs")

    @property
    @pulumi.getter
    def status(self) -> Optional[str]:
        """
        SLB current status. Possible values: `inactive`, `active` and `locked`.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Mapping[str, Any]]:
        """
        A map of tags assigned to the SLB instance.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="totalCount")
    def total_count(self) -> int:
        return pulumi.get(self, "total_count")

    @property
    @pulumi.getter(name="vpcId")
    def vpc_id(self) -> Optional[str]:
        """
        ID of the VPC the SLB belongs to.
        """
        return pulumi.get(self, "vpc_id")

    @property
    @pulumi.getter(name="vswitchId")
    def vswitch_id(self) -> Optional[str]:
        """
        ID of the VSwitch the SLB belongs to.
        """
        return pulumi.get(self, "vswitch_id")


class AwaitableGetLoadBalancersResult(GetLoadBalancersResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetLoadBalancersResult(
            address=self.address,
            address_ip_version=self.address_ip_version,
            address_type=self.address_type,
            balancers=self.balancers,
            enable_details=self.enable_details,
            id=self.id,
            ids=self.ids,
            internet_charge_type=self.internet_charge_type,
            load_balancer_name=self.load_balancer_name,
            master_zone_id=self.master_zone_id,
            name_regex=self.name_regex,
            names=self.names,
            network_type=self.network_type,
            output_file=self.output_file,
            page_number=self.page_number,
            page_size=self.page_size,
            payment_type=self.payment_type,
            resource_group_id=self.resource_group_id,
            server_id=self.server_id,
            server_intranet_address=self.server_intranet_address,
            slave_zone_id=self.slave_zone_id,
            slbs=self.slbs,
            status=self.status,
            tags=self.tags,
            total_count=self.total_count,
            vpc_id=self.vpc_id,
            vswitch_id=self.vswitch_id)


def get_load_balancers(address: Optional[str] = None,
                       address_ip_version: Optional[str] = None,
                       address_type: Optional[str] = None,
                       enable_details: Optional[bool] = None,
                       ids: Optional[Sequence[str]] = None,
                       internet_charge_type: Optional[str] = None,
                       load_balancer_name: Optional[str] = None,
                       master_zone_id: Optional[str] = None,
                       name_regex: Optional[str] = None,
                       network_type: Optional[str] = None,
                       output_file: Optional[str] = None,
                       page_number: Optional[int] = None,
                       page_size: Optional[int] = None,
                       payment_type: Optional[str] = None,
                       resource_group_id: Optional[str] = None,
                       server_id: Optional[str] = None,
                       server_intranet_address: Optional[str] = None,
                       slave_zone_id: Optional[str] = None,
                       status: Optional[str] = None,
                       tags: Optional[Mapping[str, Any]] = None,
                       vpc_id: Optional[str] = None,
                       vswitch_id: Optional[str] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetLoadBalancersResult:
    """
    Use this data source to access information about an existing resource.

    :param str address: Service address of the SLBs.
    :param Sequence[str] ids: A list of SLBs IDs.
    :param str name_regex: A regex string to filter results by SLB name.
    :param str network_type: Network type of the SLBs. Valid values: `vpc` and `classic`.
    :param str resource_group_id: The Id of resource group which SLB belongs.
    :param str status: SLB current status. Possible values: `inactive`, `active` and `locked`.
    :param Mapping[str, Any] tags: A map of tags assigned to the SLB instances. The `tags` can have a maximum of 5 tag. It must be in the format:
           ```python
           import pulumi
           import pulumi_alicloud as alicloud
           
           tagged_instances = alicloud.slb.get_load_balancers(tags={
               "tagKey1": "tagValue1",
               "tagKey2": "tagValue2",
           })
           ```
    :param str vpc_id: ID of the VPC linked to the SLBs.
    :param str vswitch_id: ID of the VSwitch linked to the SLBs.
    """
    __args__ = dict()
    __args__['address'] = address
    __args__['addressIpVersion'] = address_ip_version
    __args__['addressType'] = address_type
    __args__['enableDetails'] = enable_details
    __args__['ids'] = ids
    __args__['internetChargeType'] = internet_charge_type
    __args__['loadBalancerName'] = load_balancer_name
    __args__['masterZoneId'] = master_zone_id
    __args__['nameRegex'] = name_regex
    __args__['networkType'] = network_type
    __args__['outputFile'] = output_file
    __args__['pageNumber'] = page_number
    __args__['pageSize'] = page_size
    __args__['paymentType'] = payment_type
    __args__['resourceGroupId'] = resource_group_id
    __args__['serverId'] = server_id
    __args__['serverIntranetAddress'] = server_intranet_address
    __args__['slaveZoneId'] = slave_zone_id
    __args__['status'] = status
    __args__['tags'] = tags
    __args__['vpcId'] = vpc_id
    __args__['vswitchId'] = vswitch_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('alicloud:slb/getLoadBalancers:getLoadBalancers', __args__, opts=opts, typ=GetLoadBalancersResult).value

    return AwaitableGetLoadBalancersResult(
        address=__ret__.address,
        address_ip_version=__ret__.address_ip_version,
        address_type=__ret__.address_type,
        balancers=__ret__.balancers,
        enable_details=__ret__.enable_details,
        id=__ret__.id,
        ids=__ret__.ids,
        internet_charge_type=__ret__.internet_charge_type,
        load_balancer_name=__ret__.load_balancer_name,
        master_zone_id=__ret__.master_zone_id,
        name_regex=__ret__.name_regex,
        names=__ret__.names,
        network_type=__ret__.network_type,
        output_file=__ret__.output_file,
        page_number=__ret__.page_number,
        page_size=__ret__.page_size,
        payment_type=__ret__.payment_type,
        resource_group_id=__ret__.resource_group_id,
        server_id=__ret__.server_id,
        server_intranet_address=__ret__.server_intranet_address,
        slave_zone_id=__ret__.slave_zone_id,
        slbs=__ret__.slbs,
        status=__ret__.status,
        tags=__ret__.tags,
        total_count=__ret__.total_count,
        vpc_id=__ret__.vpc_id,
        vswitch_id=__ret__.vswitch_id)


@_utilities.lift_output_func(get_load_balancers)
def get_load_balancers_output(address: Optional[pulumi.Input[Optional[str]]] = None,
                              address_ip_version: Optional[pulumi.Input[Optional[str]]] = None,
                              address_type: Optional[pulumi.Input[Optional[str]]] = None,
                              enable_details: Optional[pulumi.Input[Optional[bool]]] = None,
                              ids: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                              internet_charge_type: Optional[pulumi.Input[Optional[str]]] = None,
                              load_balancer_name: Optional[pulumi.Input[Optional[str]]] = None,
                              master_zone_id: Optional[pulumi.Input[Optional[str]]] = None,
                              name_regex: Optional[pulumi.Input[Optional[str]]] = None,
                              network_type: Optional[pulumi.Input[Optional[str]]] = None,
                              output_file: Optional[pulumi.Input[Optional[str]]] = None,
                              page_number: Optional[pulumi.Input[Optional[int]]] = None,
                              page_size: Optional[pulumi.Input[Optional[int]]] = None,
                              payment_type: Optional[pulumi.Input[Optional[str]]] = None,
                              resource_group_id: Optional[pulumi.Input[Optional[str]]] = None,
                              server_id: Optional[pulumi.Input[Optional[str]]] = None,
                              server_intranet_address: Optional[pulumi.Input[Optional[str]]] = None,
                              slave_zone_id: Optional[pulumi.Input[Optional[str]]] = None,
                              status: Optional[pulumi.Input[Optional[str]]] = None,
                              tags: Optional[pulumi.Input[Optional[Mapping[str, Any]]]] = None,
                              vpc_id: Optional[pulumi.Input[Optional[str]]] = None,
                              vswitch_id: Optional[pulumi.Input[Optional[str]]] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetLoadBalancersResult]:
    """
    Use this data source to access information about an existing resource.

    :param str address: Service address of the SLBs.
    :param Sequence[str] ids: A list of SLBs IDs.
    :param str name_regex: A regex string to filter results by SLB name.
    :param str network_type: Network type of the SLBs. Valid values: `vpc` and `classic`.
    :param str resource_group_id: The Id of resource group which SLB belongs.
    :param str status: SLB current status. Possible values: `inactive`, `active` and `locked`.
    :param Mapping[str, Any] tags: A map of tags assigned to the SLB instances. The `tags` can have a maximum of 5 tag. It must be in the format:
           ```python
           import pulumi
           import pulumi_alicloud as alicloud
           
           tagged_instances = alicloud.slb.get_load_balancers(tags={
               "tagKey1": "tagValue1",
               "tagKey2": "tagValue2",
           })
           ```
    :param str vpc_id: ID of the VPC linked to the SLBs.
    :param str vswitch_id: ID of the VSwitch linked to the SLBs.
    """
    ...
