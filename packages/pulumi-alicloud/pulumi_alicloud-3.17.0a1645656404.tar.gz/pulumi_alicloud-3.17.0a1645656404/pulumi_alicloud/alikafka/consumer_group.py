# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ConsumerGroupArgs', 'ConsumerGroup']

@pulumi.input_type
class ConsumerGroupArgs:
    def __init__(__self__, *,
                 consumer_id: pulumi.Input[str],
                 instance_id: pulumi.Input[str],
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None):
        """
        The set of arguments for constructing a ConsumerGroup resource.
        :param pulumi.Input[str] consumer_id: ID of the consumer group. The length cannot exceed 64 characters.
        :param pulumi.Input[str] instance_id: ID of the ALIKAFKA Instance that owns the groups.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        pulumi.set(__self__, "consumer_id", consumer_id)
        pulumi.set(__self__, "instance_id", instance_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> pulumi.Input[str]:
        """
        ID of the consumer group. The length cannot exceed 64 characters.
        """
        return pulumi.get(self, "consumer_id")

    @consumer_id.setter
    def consumer_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "consumer_id", value)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Input[str]:
        """
        ID of the ALIKAFKA Instance that owns the groups.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_id", value)

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
class _ConsumerGroupState:
    def __init__(__self__, *,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None):
        """
        Input properties used for looking up and filtering ConsumerGroup resources.
        :param pulumi.Input[str] consumer_id: ID of the consumer group. The length cannot exceed 64 characters.
        :param pulumi.Input[str] instance_id: ID of the ALIKAFKA Instance that owns the groups.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        if consumer_id is not None:
            pulumi.set(__self__, "consumer_id", consumer_id)
        if instance_id is not None:
            pulumi.set(__self__, "instance_id", instance_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the consumer group. The length cannot exceed 64 characters.
        """
        return pulumi.get(self, "consumer_id")

    @consumer_id.setter
    def consumer_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "consumer_id", value)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the ALIKAFKA Instance that owns the groups.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "instance_id", value)

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


class ConsumerGroup(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 __props__=None):
        """
        Provides an ALIKAFKA consumer group resource.

        > **NOTE:** Available in 1.56.0+

        > **NOTE:**  Only the following regions support create alikafka consumer group.
        [`cn-hangzhou`,`cn-beijing`,`cn-shenzhen`,`cn-shanghai`,`cn-qingdao`,`cn-hongkong`,`cn-huhehaote`,`cn-zhangjiakou`,`cn-chengdu`,`cn-heyuan`,`ap-southeast-1`,`ap-southeast-3`,`ap-southeast-5`,`ap-south-1`,`ap-northeast-1`,`eu-central-1`,`eu-west-1`,`us-west-1`,`us-east-1`]

        ## Example Usage

        Basic Usage

        ```python
        import pulumi
        import pulumi_alicloud as alicloud

        config = pulumi.Config()
        consumer_id = config.get("consumerId")
        if consumer_id is None:
            consumer_id = "CID-alikafkaGroupDatasourceName"
        default_zones = alicloud.get_zones(available_resource_creation="VSwitch")
        default_network = alicloud.vpc.Network("defaultNetwork", cidr_block="172.16.0.0/12")
        default_switch = alicloud.vpc.Switch("defaultSwitch",
            vpc_id=default_network.id,
            cidr_block="172.16.0.0/24",
            zone_id=default_zones.zones[0].id)
        default_instance = alicloud.alikafka.Instance("defaultInstance",
            topic_quota=50,
            disk_type=1,
            disk_size=500,
            deploy_type=5,
            io_max=20,
            vswitch_id=default_switch.id)
        default_consumer_group = alicloud.alikafka.ConsumerGroup("defaultConsumerGroup",
            consumer_id=consumer_id,
            instance_id=default_instance.id)
        ```

        ## Import

        ALIKAFKA GROUP can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:alikafka/consumerGroup:ConsumerGroup group alikafka_post-cn-123455abc:consumerId
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] consumer_id: ID of the consumer group. The length cannot exceed 64 characters.
        :param pulumi.Input[str] instance_id: ID of the ALIKAFKA Instance that owns the groups.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ConsumerGroupArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an ALIKAFKA consumer group resource.

        > **NOTE:** Available in 1.56.0+

        > **NOTE:**  Only the following regions support create alikafka consumer group.
        [`cn-hangzhou`,`cn-beijing`,`cn-shenzhen`,`cn-shanghai`,`cn-qingdao`,`cn-hongkong`,`cn-huhehaote`,`cn-zhangjiakou`,`cn-chengdu`,`cn-heyuan`,`ap-southeast-1`,`ap-southeast-3`,`ap-southeast-5`,`ap-south-1`,`ap-northeast-1`,`eu-central-1`,`eu-west-1`,`us-west-1`,`us-east-1`]

        ## Example Usage

        Basic Usage

        ```python
        import pulumi
        import pulumi_alicloud as alicloud

        config = pulumi.Config()
        consumer_id = config.get("consumerId")
        if consumer_id is None:
            consumer_id = "CID-alikafkaGroupDatasourceName"
        default_zones = alicloud.get_zones(available_resource_creation="VSwitch")
        default_network = alicloud.vpc.Network("defaultNetwork", cidr_block="172.16.0.0/12")
        default_switch = alicloud.vpc.Switch("defaultSwitch",
            vpc_id=default_network.id,
            cidr_block="172.16.0.0/24",
            zone_id=default_zones.zones[0].id)
        default_instance = alicloud.alikafka.Instance("defaultInstance",
            topic_quota=50,
            disk_type=1,
            disk_size=500,
            deploy_type=5,
            io_max=20,
            vswitch_id=default_switch.id)
        default_consumer_group = alicloud.alikafka.ConsumerGroup("defaultConsumerGroup",
            consumer_id=consumer_id,
            instance_id=default_instance.id)
        ```

        ## Import

        ALIKAFKA GROUP can be imported using the id, e.g.

        ```sh
         $ pulumi import alicloud:alikafka/consumerGroup:ConsumerGroup group alikafka_post-cn-123455abc:consumerId
        ```

        :param str resource_name: The name of the resource.
        :param ConsumerGroupArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConsumerGroupArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ConsumerGroupArgs.__new__(ConsumerGroupArgs)

            if consumer_id is None and not opts.urn:
                raise TypeError("Missing required property 'consumer_id'")
            __props__.__dict__["consumer_id"] = consumer_id
            if instance_id is None and not opts.urn:
                raise TypeError("Missing required property 'instance_id'")
            __props__.__dict__["instance_id"] = instance_id
            __props__.__dict__["tags"] = tags
        super(ConsumerGroup, __self__).__init__(
            'alicloud:alikafka/consumerGroup:ConsumerGroup',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            consumer_id: Optional[pulumi.Input[str]] = None,
            instance_id: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, Any]]] = None) -> 'ConsumerGroup':
        """
        Get an existing ConsumerGroup resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] consumer_id: ID of the consumer group. The length cannot exceed 64 characters.
        :param pulumi.Input[str] instance_id: ID of the ALIKAFKA Instance that owns the groups.
        :param pulumi.Input[Mapping[str, Any]] tags: A mapping of tags to assign to the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ConsumerGroupState.__new__(_ConsumerGroupState)

        __props__.__dict__["consumer_id"] = consumer_id
        __props__.__dict__["instance_id"] = instance_id
        __props__.__dict__["tags"] = tags
        return ConsumerGroup(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> pulumi.Output[str]:
        """
        ID of the consumer group. The length cannot exceed 64 characters.
        """
        return pulumi.get(self, "consumer_id")

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Output[str]:
        """
        ID of the ALIKAFKA Instance that owns the groups.
        """
        return pulumi.get(self, "instance_id")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, Any]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

