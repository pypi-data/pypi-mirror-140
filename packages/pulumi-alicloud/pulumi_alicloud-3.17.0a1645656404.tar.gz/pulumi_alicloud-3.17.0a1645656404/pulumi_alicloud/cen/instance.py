# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['InstanceArgs', 'Instance']

@pulumi.input_type
class InstanceArgs:
    def __init__(__self__, *,
                 cen_instance_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 protection_level: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None):
        """
        The set of arguments for constructing a Instance resource.
        :param pulumi.Input[str] cen_instance_name: The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        :param pulumi.Input[str] description: The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        :param pulumi.Input[str] name: Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        :param pulumi.Input[str] protection_level: Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        if cen_instance_name is not None:
            pulumi.set(__self__, "cen_instance_name", cen_instance_name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            warnings.warn("""Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""", DeprecationWarning)
            pulumi.log.warn("""name is deprecated: Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""")
        if name is not None:
            pulumi.set(__self__, "name", name)
        if protection_level is not None:
            pulumi.set(__self__, "protection_level", protection_level)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="cenInstanceName")
    def cen_instance_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        """
        return pulumi.get(self, "cen_instance_name")

    @cen_instance_name.setter
    def cen_instance_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cen_instance_name", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="protectionLevel")
    def protection_level(self) -> Optional[pulumi.Input[str]]:
        """
        Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        """
        return pulumi.get(self, "protection_level")

    @protection_level.setter
    def protection_level(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protection_level", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _InstanceState:
    def __init__(__self__, *,
                 cen_instance_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 protection_level: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None):
        """
        Input properties used for looking up and filtering Instance resources.
        :param pulumi.Input[str] cen_instance_name: The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        :param pulumi.Input[str] description: The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        :param pulumi.Input[str] name: Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        :param pulumi.Input[str] protection_level: Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        :param pulumi.Input[str] status: The Cen Instance current status.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        if cen_instance_name is not None:
            pulumi.set(__self__, "cen_instance_name", cen_instance_name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            warnings.warn("""Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""", DeprecationWarning)
            pulumi.log.warn("""name is deprecated: Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""")
        if name is not None:
            pulumi.set(__self__, "name", name)
        if protection_level is not None:
            pulumi.set(__self__, "protection_level", protection_level)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="cenInstanceName")
    def cen_instance_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        """
        return pulumi.get(self, "cen_instance_name")

    @cen_instance_name.setter
    def cen_instance_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cen_instance_name", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="protectionLevel")
    def protection_level(self) -> Optional[pulumi.Input[str]]:
        """
        Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        """
        return pulumi.get(self, "protection_level")

    @protection_level.setter
    def protection_level(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protection_level", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        The Cen Instance current status.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "tags", value)


class Instance(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cen_instance_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 protection_level: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 __props__=None):
        """
        Provides a CEN instance resource. Cloud Enterprise Network (CEN) is a service that allows you to create a global network for rapidly building a distributed business system with a hybrid cloud computing solution. CEN enables you to build a secure, private, and enterprise-class interconnected network between VPCs in different regions and your local data centers. CEN provides enterprise-class scalability that automatically responds to your dynamic computing requirements.

        For information about CEN and how to use it, see [What is Cloud Enterprise Network](https://www.alibabacloud.com/help/doc-detail/59870.htm).

        ## Example Usage

        Basic Usage

        ```python
        import pulumi
        import pulumi_alicloud as alicloud

        example = alicloud.cen.Instance("example",
            cen_instance_name="tf_test_foo",
            description="an example for cen")
        ```

        ## Import

        CEN instance can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:cen/instance:Instance example cen-abc123456
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cen_instance_name: The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        :param pulumi.Input[str] description: The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        :param pulumi.Input[str] name: Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        :param pulumi.Input[str] protection_level: Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[InstanceArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a CEN instance resource. Cloud Enterprise Network (CEN) is a service that allows you to create a global network for rapidly building a distributed business system with a hybrid cloud computing solution. CEN enables you to build a secure, private, and enterprise-class interconnected network between VPCs in different regions and your local data centers. CEN provides enterprise-class scalability that automatically responds to your dynamic computing requirements.

        For information about CEN and how to use it, see [What is Cloud Enterprise Network](https://www.alibabacloud.com/help/doc-detail/59870.htm).

        ## Example Usage

        Basic Usage

        ```python
        import pulumi
        import pulumi_alicloud as alicloud

        example = alicloud.cen.Instance("example",
            cen_instance_name="tf_test_foo",
            description="an example for cen")
        ```

        ## Import

        CEN instance can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:cen/instance:Instance example cen-abc123456
        ```

        :param str resource_name: The name of the resource.
        :param InstanceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InstanceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cen_instance_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 protection_level: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None,
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
            __props__ = InstanceArgs.__new__(InstanceArgs)

            __props__.__dict__["cen_instance_name"] = cen_instance_name
            __props__.__dict__["description"] = description
            if name is not None and not opts.urn:
                warnings.warn("""Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""", DeprecationWarning)
                pulumi.log.warn("""name is deprecated: Field 'name' has been deprecated from version 1.98.0. Use 'cen_instance_name' instead.""")
            __props__.__dict__["name"] = name
            __props__.__dict__["protection_level"] = protection_level
            __props__.__dict__["tags"] = tags
            __props__.__dict__["status"] = None
        super(Instance, __self__).__init__(
            'alicloud:cen/instance:Instance',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            cen_instance_name: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            protection_level: Optional[pulumi.Input[str]] = None,
            status: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, Any]]] = None) -> 'Instance':
        """
        Get an existing Instance resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cen_instance_name: The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        :param pulumi.Input[str] description: The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        :param pulumi.Input[str] name: Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        :param pulumi.Input[str] protection_level: Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        :param pulumi.Input[str] status: The Cen Instance current status.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _InstanceState.__new__(_InstanceState)

        __props__.__dict__["cen_instance_name"] = cen_instance_name
        __props__.__dict__["description"] = description
        __props__.__dict__["name"] = name
        __props__.__dict__["protection_level"] = protection_level
        __props__.__dict__["status"] = status
        __props__.__dict__["tags"] = tags
        return Instance(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="cenInstanceName")
    def cen_instance_name(self) -> pulumi.Output[str]:
        """
        The name of the CEN instance. Defaults to null. The name must be 2 to 128 characters in length and can contain letters, numbers, periods (.), underscores (_), and hyphens (-). The name must start with a letter, but cannot start with http:// or https://.
        """
        return pulumi.get(self, "cen_instance_name")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description of the CEN instance. Defaults to null. The description must be 2 to 256 characters in length. It must start with a letter, and cannot start with http:// or https://.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Field `name` has been deprecated from version 1.98.0. Use `cen_instance_name` instead.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="protectionLevel")
    def protection_level(self) -> pulumi.Output[str]:
        """
        Indicates the allowed level of CIDR block overlapping. Default value: `REDUCE`: Overlapping CIDR blocks are allowed. However, the overlapping CIDR blocks cannot be identical.
        """
        return pulumi.get(self, "protection_level")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        The Cen Instance current status.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, Any]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

