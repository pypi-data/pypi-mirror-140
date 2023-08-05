# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'ApplicationInfoDimensionArgs',
    'QuotaAlarmQuotaDimensionArgs',
    'QuotaApplicationDimensionArgs',
    'GetApplicationInfosDimensionArgs',
    'GetQuotaAlarmsQuotaDimensionArgs',
    'GetQuotaApplicationsDimensionArgs',
    'GetQuotasDimensionArgs',
]

@pulumi.input_type
class ApplicationInfoDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None):
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class QuotaAlarmQuotaDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] key: The Key of quota_dimensions.
        :param pulumi.Input[str] value: The Value of quota_dimensions.
        """
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        """
        The Key of quota_dimensions.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[pulumi.Input[str]]:
        """
        The Value of quota_dimensions.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class QuotaApplicationDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[pulumi.Input[str]] = None,
                 value: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] key: The key of dimensions.
        :param pulumi.Input[str] value: The value of dimensions.
        """
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        """
        The key of dimensions.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[pulumi.Input[str]]:
        """
        The value of dimensions.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class GetApplicationInfosDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class GetQuotaAlarmsQuotaDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        """
        :param str key: The key of quota_dimensions.
        :param str value: The value of quota_dimensions.
        """
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        """
        The key of quota_dimensions.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        """
        The value of quota_dimensions.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class GetQuotaApplicationsDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        """
        :param str key: The key of dimensions.
        :param str value: The value of dimensions.
        """
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        """
        The key of dimensions.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        """
        The value of dimensions.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[str]):
        pulumi.set(self, "value", value)


@pulumi.input_type
class GetQuotasDimensionArgs:
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        """
        :param str key: The key of dimensions.
        :param str value: The value of dimensions.
        """
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        """
        The key of dimensions.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[str]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        """
        The value of dimensions.
        """
        return pulumi.get(self, "value")

    @value.setter
    def value(self, value: Optional[str]):
        pulumi.set(self, "value", value)


