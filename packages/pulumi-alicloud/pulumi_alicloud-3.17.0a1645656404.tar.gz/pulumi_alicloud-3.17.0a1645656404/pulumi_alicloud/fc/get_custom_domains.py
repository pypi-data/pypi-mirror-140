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
    'GetCustomDomainsResult',
    'AwaitableGetCustomDomainsResult',
    'get_custom_domains',
    'get_custom_domains_output',
]

@pulumi.output_type
class GetCustomDomainsResult:
    """
    A collection of values returned by getCustomDomains.
    """
    def __init__(__self__, domains=None, id=None, ids=None, name_regex=None, names=None, output_file=None):
        if domains and not isinstance(domains, list):
            raise TypeError("Expected argument 'domains' to be a list")
        pulumi.set(__self__, "domains", domains)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ids and not isinstance(ids, list):
            raise TypeError("Expected argument 'ids' to be a list")
        pulumi.set(__self__, "ids", ids)
        if name_regex and not isinstance(name_regex, str):
            raise TypeError("Expected argument 'name_regex' to be a str")
        pulumi.set(__self__, "name_regex", name_regex)
        if names and not isinstance(names, list):
            raise TypeError("Expected argument 'names' to be a list")
        pulumi.set(__self__, "names", names)
        if output_file and not isinstance(output_file, str):
            raise TypeError("Expected argument 'output_file' to be a str")
        pulumi.set(__self__, "output_file", output_file)

    @property
    @pulumi.getter
    def domains(self) -> Sequence['outputs.GetCustomDomainsDomainResult']:
        """
        A list of custom domains, including the following attributes:
        """
        return pulumi.get(self, "domains")

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
        A list of custom domain ids.
        """
        return pulumi.get(self, "ids")

    @property
    @pulumi.getter(name="nameRegex")
    def name_regex(self) -> Optional[str]:
        return pulumi.get(self, "name_regex")

    @property
    @pulumi.getter
    def names(self) -> Sequence[str]:
        """
        A list of custom domain names.
        """
        return pulumi.get(self, "names")

    @property
    @pulumi.getter(name="outputFile")
    def output_file(self) -> Optional[str]:
        return pulumi.get(self, "output_file")


class AwaitableGetCustomDomainsResult(GetCustomDomainsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetCustomDomainsResult(
            domains=self.domains,
            id=self.id,
            ids=self.ids,
            name_regex=self.name_regex,
            names=self.names,
            output_file=self.output_file)


def get_custom_domains(ids: Optional[Sequence[str]] = None,
                       name_regex: Optional[str] = None,
                       output_file: Optional[str] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetCustomDomainsResult:
    """
    This data source provides the Function Compute custom domains of the current Alibaba Cloud user.

    > **NOTE:** Available in 1.98.0+

    ## Example Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    fc_domains = alicloud.fc.get_custom_domains(name_regex="sample_fc_custom_domain")
    pulumi.export("firstFcCustomDomainName", data["alicloud_fc_custom_domains"]["fc_domains_ds"]["domains"][0]["domain_name"])
    ```


    :param Sequence[str] ids: A list of functions ids.
    :param str name_regex: A regex string to filter results by Function Compute custom domain name.
    """
    __args__ = dict()
    __args__['ids'] = ids
    __args__['nameRegex'] = name_regex
    __args__['outputFile'] = output_file
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('alicloud:fc/getCustomDomains:getCustomDomains', __args__, opts=opts, typ=GetCustomDomainsResult).value

    return AwaitableGetCustomDomainsResult(
        domains=__ret__.domains,
        id=__ret__.id,
        ids=__ret__.ids,
        name_regex=__ret__.name_regex,
        names=__ret__.names,
        output_file=__ret__.output_file)


@_utilities.lift_output_func(get_custom_domains)
def get_custom_domains_output(ids: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                              name_regex: Optional[pulumi.Input[Optional[str]]] = None,
                              output_file: Optional[pulumi.Input[Optional[str]]] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetCustomDomainsResult]:
    """
    This data source provides the Function Compute custom domains of the current Alibaba Cloud user.

    > **NOTE:** Available in 1.98.0+

    ## Example Usage

    ```python
    import pulumi
    import pulumi_alicloud as alicloud

    fc_domains = alicloud.fc.get_custom_domains(name_regex="sample_fc_custom_domain")
    pulumi.export("firstFcCustomDomainName", data["alicloud_fc_custom_domains"]["fc_domains_ds"]["domains"][0]["domain_name"])
    ```


    :param Sequence[str] ids: A list of functions ids.
    :param str name_regex: A regex string to filter results by Function Compute custom domain name.
    """
    ...
