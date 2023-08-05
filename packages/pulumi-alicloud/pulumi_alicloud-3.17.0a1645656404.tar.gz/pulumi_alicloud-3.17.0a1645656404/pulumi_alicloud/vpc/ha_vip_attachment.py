# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['HAVipAttachmentArgs', 'HAVipAttachment']

@pulumi.input_type
class HAVipAttachmentArgs:
    def __init__(__self__, *,
                 havip_id: pulumi.Input[str],
                 instance_id: pulumi.Input[str]):
        """
        The set of arguments for constructing a HAVipAttachment resource.
        :param pulumi.Input[str] havip_id: The havip_id of the havip attachment, the field can't be changed.
        :param pulumi.Input[str] instance_id: The instance_id of the havip attachment, the field can't be changed.
        """
        pulumi.set(__self__, "havip_id", havip_id)
        pulumi.set(__self__, "instance_id", instance_id)

    @property
    @pulumi.getter(name="havipId")
    def havip_id(self) -> pulumi.Input[str]:
        """
        The havip_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "havip_id")

    @havip_id.setter
    def havip_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "havip_id", value)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Input[str]:
        """
        The instance_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_id", value)


@pulumi.input_type
class _HAVipAttachmentState:
    def __init__(__self__, *,
                 havip_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering HAVipAttachment resources.
        :param pulumi.Input[str] havip_id: The havip_id of the havip attachment, the field can't be changed.
        :param pulumi.Input[str] instance_id: The instance_id of the havip attachment, the field can't be changed.
        """
        if havip_id is not None:
            pulumi.set(__self__, "havip_id", havip_id)
        if instance_id is not None:
            pulumi.set(__self__, "instance_id", instance_id)

    @property
    @pulumi.getter(name="havipId")
    def havip_id(self) -> Optional[pulumi.Input[str]]:
        """
        The havip_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "havip_id")

    @havip_id.setter
    def havip_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "havip_id", value)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> Optional[pulumi.Input[str]]:
        """
        The instance_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "instance_id", value)


class HAVipAttachment(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 havip_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        ## Import

        The havip attachment can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:vpc/hAVipAttachment:HAVipAttachment foo havip-abc123456:i-abc123456
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] havip_id: The havip_id of the havip attachment, the field can't be changed.
        :param pulumi.Input[str] instance_id: The instance_id of the havip attachment, the field can't be changed.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: HAVipAttachmentArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Import

        The havip attachment can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:vpc/hAVipAttachment:HAVipAttachment foo havip-abc123456:i-abc123456
        ```

        :param str resource_name: The name of the resource.
        :param HAVipAttachmentArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(HAVipAttachmentArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 havip_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = HAVipAttachmentArgs.__new__(HAVipAttachmentArgs)

            if havip_id is None and not opts.urn:
                raise TypeError("Missing required property 'havip_id'")
            __props__.__dict__["havip_id"] = havip_id
            if instance_id is None and not opts.urn:
                raise TypeError("Missing required property 'instance_id'")
            __props__.__dict__["instance_id"] = instance_id
        super(HAVipAttachment, __self__).__init__(
            'alicloud:vpc/hAVipAttachment:HAVipAttachment',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            havip_id: Optional[pulumi.Input[str]] = None,
            instance_id: Optional[pulumi.Input[str]] = None) -> 'HAVipAttachment':
        """
        Get an existing HAVipAttachment resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] havip_id: The havip_id of the havip attachment, the field can't be changed.
        :param pulumi.Input[str] instance_id: The instance_id of the havip attachment, the field can't be changed.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _HAVipAttachmentState.__new__(_HAVipAttachmentState)

        __props__.__dict__["havip_id"] = havip_id
        __props__.__dict__["instance_id"] = instance_id
        return HAVipAttachment(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="havipId")
    def havip_id(self) -> pulumi.Output[str]:
        """
        The havip_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "havip_id")

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Output[str]:
        """
        The instance_id of the havip attachment, the field can't be changed.
        """
        return pulumi.get(self, "instance_id")

