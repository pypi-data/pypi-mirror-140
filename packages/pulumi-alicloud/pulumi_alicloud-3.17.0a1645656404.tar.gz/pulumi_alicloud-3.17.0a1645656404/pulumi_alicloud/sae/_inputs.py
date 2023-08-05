# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'ApplicationInternetArgs',
    'ApplicationIntranetArgs',
    'IngressDefaultRuleArgs',
    'IngressRuleArgs',
]

@pulumi.input_type
class ApplicationInternetArgs:
    def __init__(__self__, *,
                 https_cert_id: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 target_port: Optional[pulumi.Input[int]] = None):
        """
        :param pulumi.Input[str] https_cert_id: SSL certificate. `https_cert_id` is required when HTTPS is selected
        :param pulumi.Input[int] port: SLB Port.
        :param pulumi.Input[str] protocol: Network protocol. Valid values: `TCP` ,`HTTP`,`HTTPS`.
        :param pulumi.Input[int] target_port: Container port.
        """
        if https_cert_id is not None:
            pulumi.set(__self__, "https_cert_id", https_cert_id)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if protocol is not None:
            pulumi.set(__self__, "protocol", protocol)
        if target_port is not None:
            pulumi.set(__self__, "target_port", target_port)

    @property
    @pulumi.getter(name="httpsCertId")
    def https_cert_id(self) -> Optional[pulumi.Input[str]]:
        """
        SSL certificate. `https_cert_id` is required when HTTPS is selected
        """
        return pulumi.get(self, "https_cert_id")

    @https_cert_id.setter
    def https_cert_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "https_cert_id", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        """
        SLB Port.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter
    def protocol(self) -> Optional[pulumi.Input[str]]:
        """
        Network protocol. Valid values: `TCP` ,`HTTP`,`HTTPS`.
        """
        return pulumi.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protocol", value)

    @property
    @pulumi.getter(name="targetPort")
    def target_port(self) -> Optional[pulumi.Input[int]]:
        """
        Container port.
        """
        return pulumi.get(self, "target_port")

    @target_port.setter
    def target_port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_port", value)


@pulumi.input_type
class ApplicationIntranetArgs:
    def __init__(__self__, *,
                 https_cert_id: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 target_port: Optional[pulumi.Input[int]] = None):
        """
        :param pulumi.Input[str] https_cert_id: SSL certificate. `https_cert_id` is required when HTTPS is selected
        :param pulumi.Input[int] port: SLB Port.
        :param pulumi.Input[str] protocol: Network protocol. Valid values: `TCP` ,`HTTP`,`HTTPS`.
        :param pulumi.Input[int] target_port: Container port.
        """
        if https_cert_id is not None:
            pulumi.set(__self__, "https_cert_id", https_cert_id)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if protocol is not None:
            pulumi.set(__self__, "protocol", protocol)
        if target_port is not None:
            pulumi.set(__self__, "target_port", target_port)

    @property
    @pulumi.getter(name="httpsCertId")
    def https_cert_id(self) -> Optional[pulumi.Input[str]]:
        """
        SSL certificate. `https_cert_id` is required when HTTPS is selected
        """
        return pulumi.get(self, "https_cert_id")

    @https_cert_id.setter
    def https_cert_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "https_cert_id", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        """
        SLB Port.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter
    def protocol(self) -> Optional[pulumi.Input[str]]:
        """
        Network protocol. Valid values: `TCP` ,`HTTP`,`HTTPS`.
        """
        return pulumi.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protocol", value)

    @property
    @pulumi.getter(name="targetPort")
    def target_port(self) -> Optional[pulumi.Input[int]]:
        """
        Container port.
        """
        return pulumi.get(self, "target_port")

    @target_port.setter
    def target_port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_port", value)


@pulumi.input_type
class IngressDefaultRuleArgs:
    def __init__(__self__, *,
                 app_id: Optional[pulumi.Input[str]] = None,
                 app_name: Optional[pulumi.Input[str]] = None,
                 container_port: Optional[pulumi.Input[int]] = None):
        """
        :param pulumi.Input[str] app_id: Target application ID.
        :param pulumi.Input[str] app_name: Target application name.
        :param pulumi.Input[int] container_port: Application backend port.
        """
        if app_id is not None:
            pulumi.set(__self__, "app_id", app_id)
        if app_name is not None:
            pulumi.set(__self__, "app_name", app_name)
        if container_port is not None:
            pulumi.set(__self__, "container_port", container_port)

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> Optional[pulumi.Input[str]]:
        """
        Target application ID.
        """
        return pulumi.get(self, "app_id")

    @app_id.setter
    def app_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_id", value)

    @property
    @pulumi.getter(name="appName")
    def app_name(self) -> Optional[pulumi.Input[str]]:
        """
        Target application name.
        """
        return pulumi.get(self, "app_name")

    @app_name.setter
    def app_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "app_name", value)

    @property
    @pulumi.getter(name="containerPort")
    def container_port(self) -> Optional[pulumi.Input[int]]:
        """
        Application backend port.
        """
        return pulumi.get(self, "container_port")

    @container_port.setter
    def container_port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "container_port", value)


@pulumi.input_type
class IngressRuleArgs:
    def __init__(__self__, *,
                 app_id: pulumi.Input[str],
                 app_name: pulumi.Input[str],
                 container_port: pulumi.Input[int],
                 domain: pulumi.Input[str],
                 path: pulumi.Input[str]):
        """
        :param pulumi.Input[str] app_id: Target application ID.
        :param pulumi.Input[str] app_name: Target application name.
        :param pulumi.Input[int] container_port: Application backend port.
        :param pulumi.Input[str] domain: Application domain name.
        :param pulumi.Input[str] path: URL path.
        """
        pulumi.set(__self__, "app_id", app_id)
        pulumi.set(__self__, "app_name", app_name)
        pulumi.set(__self__, "container_port", container_port)
        pulumi.set(__self__, "domain", domain)
        pulumi.set(__self__, "path", path)

    @property
    @pulumi.getter(name="appId")
    def app_id(self) -> pulumi.Input[str]:
        """
        Target application ID.
        """
        return pulumi.get(self, "app_id")

    @app_id.setter
    def app_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "app_id", value)

    @property
    @pulumi.getter(name="appName")
    def app_name(self) -> pulumi.Input[str]:
        """
        Target application name.
        """
        return pulumi.get(self, "app_name")

    @app_name.setter
    def app_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "app_name", value)

    @property
    @pulumi.getter(name="containerPort")
    def container_port(self) -> pulumi.Input[int]:
        """
        Application backend port.
        """
        return pulumi.get(self, "container_port")

    @container_port.setter
    def container_port(self, value: pulumi.Input[int]):
        pulumi.set(self, "container_port", value)

    @property
    @pulumi.getter
    def domain(self) -> pulumi.Input[str]:
        """
        Application domain name.
        """
        return pulumi.get(self, "domain")

    @domain.setter
    def domain(self, value: pulumi.Input[str]):
        pulumi.set(self, "domain", value)

    @property
    @pulumi.getter
    def path(self) -> pulumi.Input[str]:
        """
        URL path.
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: pulumi.Input[str]):
        pulumi.set(self, "path", value)


