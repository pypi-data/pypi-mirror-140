# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs
from ._inputs import *

__all__ = [
    'GetServicesResult',
    'AwaitableGetServicesResult',
    'get_services',
    'get_services_output',
]

@pulumi.output_type
class GetServicesResult:
    """
    A collection of values returned by getServices.
    """
    def __init__(__self__, datacenter=None, id=None, names=None, query_options=None, services=None, tags=None):
        if datacenter and not isinstance(datacenter, str):
            raise TypeError("Expected argument 'datacenter' to be a str")
        pulumi.set(__self__, "datacenter", datacenter)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if names and not isinstance(names, list):
            raise TypeError("Expected argument 'names' to be a list")
        pulumi.set(__self__, "names", names)
        if query_options and not isinstance(query_options, list):
            raise TypeError("Expected argument 'query_options' to be a list")
        pulumi.set(__self__, "query_options", query_options)
        if services and not isinstance(services, dict):
            raise TypeError("Expected argument 'services' to be a dict")
        pulumi.set(__self__, "services", services)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def datacenter(self) -> str:
        """
        The datacenter the keys are being read from to.
        """
        return pulumi.get(self, "datacenter")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def names(self) -> Sequence[str]:
        return pulumi.get(self, "names")

    @property
    @pulumi.getter(name="queryOptions")
    def query_options(self) -> Optional[Sequence['outputs.GetServicesQueryOptionResult']]:
        return pulumi.get(self, "query_options")

    @property
    @pulumi.getter
    def services(self) -> Mapping[str, str]:
        return pulumi.get(self, "services")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        A map of the tags found for each service.  If more than one service
        shares the same tag, unique service names will be joined by whitespace (this
        is the inverse of `services` and can be used to lookup the services that match
        a single tag).
        """
        return pulumi.get(self, "tags")


class AwaitableGetServicesResult(GetServicesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetServicesResult(
            datacenter=self.datacenter,
            id=self.id,
            names=self.names,
            query_options=self.query_options,
            services=self.services,
            tags=self.tags)


def get_services(query_options: Optional[Sequence[pulumi.InputType['GetServicesQueryOptionArgs']]] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetServicesResult:
    """
    The `get_services` data source returns a list of Consul services that
    have been registered with the Consul cluster in a given datacenter.  By
    specifying a different datacenter in the `query_options` it is possible to
    retrieve a list of services from a different WAN-attached Consul datacenter.

    This data source is different from the `Service` (singular) data
    source, which provides a detailed response about a specific Consul service.


    :param Sequence[pulumi.InputType['GetServicesQueryOptionArgs']] query_options: See below.
    """
    __args__ = dict()
    __args__['queryOptions'] = query_options
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('consul:index/getServices:getServices', __args__, opts=opts, typ=GetServicesResult).value

    return AwaitableGetServicesResult(
        datacenter=__ret__.datacenter,
        id=__ret__.id,
        names=__ret__.names,
        query_options=__ret__.query_options,
        services=__ret__.services,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_services)
def get_services_output(query_options: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetServicesQueryOptionArgs']]]]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetServicesResult]:
    """
    The `get_services` data source returns a list of Consul services that
    have been registered with the Consul cluster in a given datacenter.  By
    specifying a different datacenter in the `query_options` it is possible to
    retrieve a list of services from a different WAN-attached Consul datacenter.

    This data source is different from the `Service` (singular) data
    source, which provides a detailed response about a specific Consul service.


    :param Sequence[pulumi.InputType['GetServicesQueryOptionArgs']] query_options: See below.
    """
    ...
