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
    'GetServiceResult',
    'AwaitableGetServiceResult',
    'get_service',
    'get_service_output',
]

@pulumi.output_type
class GetServiceResult:
    """
    A collection of values returned by getService.
    """
    def __init__(__self__, datacenter=None, filter=None, id=None, name=None, query_options=None, services=None, tag=None):
        if datacenter and not isinstance(datacenter, str):
            raise TypeError("Expected argument 'datacenter' to be a str")
        pulumi.set(__self__, "datacenter", datacenter)
        if filter and not isinstance(filter, str):
            raise TypeError("Expected argument 'filter' to be a str")
        pulumi.set(__self__, "filter", filter)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if query_options and not isinstance(query_options, list):
            raise TypeError("Expected argument 'query_options' to be a list")
        pulumi.set(__self__, "query_options", query_options)
        if services and not isinstance(services, list):
            raise TypeError("Expected argument 'services' to be a list")
        pulumi.set(__self__, "services", services)
        if tag and not isinstance(tag, str):
            raise TypeError("Expected argument 'tag' to be a str")
        pulumi.set(__self__, "tag", tag)

    @property
    @pulumi.getter
    def datacenter(self) -> Optional[str]:
        """
        The datacenter the keys are being read from to.
        """
        return pulumi.get(self, "datacenter")

    @property
    @pulumi.getter
    def filter(self) -> Optional[str]:
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the service
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="queryOptions")
    def query_options(self) -> Optional[Sequence['outputs.GetServiceQueryOptionResult']]:
        return pulumi.get(self, "query_options")

    @property
    @pulumi.getter
    def services(self) -> Sequence['outputs.GetServiceServiceResult']:
        """
        A list of nodes and details about each endpoint advertising a
        service.  Each element in the list is a map of attributes that correspond to
        each individual node.  The list of per-node attributes is detailed below.
        """
        return pulumi.get(self, "services")

    @property
    @pulumi.getter
    def tag(self) -> Optional[str]:
        """
        The name of the tag used to filter the list of nodes in `service`.
        """
        return pulumi.get(self, "tag")


class AwaitableGetServiceResult(GetServiceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetServiceResult(
            datacenter=self.datacenter,
            filter=self.filter,
            id=self.id,
            name=self.name,
            query_options=self.query_options,
            services=self.services,
            tag=self.tag)


def get_service(datacenter: Optional[str] = None,
                filter: Optional[str] = None,
                name: Optional[str] = None,
                query_options: Optional[Sequence[pulumi.InputType['GetServiceQueryOptionArgs']]] = None,
                tag: Optional[str] = None,
                opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetServiceResult:
    """
    `Service` provides details about a specific Consul service in a
    given datacenter.  The results include a list of nodes advertising the specified
    service, the node's IP address, port number, node ID, etc.  By specifying a
    different datacenter in the `query_options` it is possible to retrieve a list of
    services from a different WAN-attached Consul datacenter.

    This data source is different from the `get_services` (plural) data
    source, which provides a summary of the current Consul services.


    :param str datacenter: The Consul datacenter to query.  Defaults to the
           same value found in `query_options` parameter specified below, or if that is
           empty, the `datacenter` value found in the Consul agent that this provider is
           configured to talk to.
    :param str filter: A filter expression to refine the query, see https://www.consul.io/api-docs/features/filtering
           and https://www.consul.io/api-docs/catalog#filtering-1.
    :param str name: The service name to select.
    :param Sequence[pulumi.InputType['GetServiceQueryOptionArgs']] query_options: See below.
    :param str tag: A single tag that can be used to filter the list of nodes
           to return based on a single matching tag..
    """
    __args__ = dict()
    __args__['datacenter'] = datacenter
    __args__['filter'] = filter
    __args__['name'] = name
    __args__['queryOptions'] = query_options
    __args__['tag'] = tag
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('consul:index/getService:getService', __args__, opts=opts, typ=GetServiceResult).value

    return AwaitableGetServiceResult(
        datacenter=__ret__.datacenter,
        filter=__ret__.filter,
        id=__ret__.id,
        name=__ret__.name,
        query_options=__ret__.query_options,
        services=__ret__.services,
        tag=__ret__.tag)


@_utilities.lift_output_func(get_service)
def get_service_output(datacenter: Optional[pulumi.Input[Optional[str]]] = None,
                       filter: Optional[pulumi.Input[Optional[str]]] = None,
                       name: Optional[pulumi.Input[str]] = None,
                       query_options: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetServiceQueryOptionArgs']]]]] = None,
                       tag: Optional[pulumi.Input[Optional[str]]] = None,
                       opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetServiceResult]:
    """
    `Service` provides details about a specific Consul service in a
    given datacenter.  The results include a list of nodes advertising the specified
    service, the node's IP address, port number, node ID, etc.  By specifying a
    different datacenter in the `query_options` it is possible to retrieve a list of
    services from a different WAN-attached Consul datacenter.

    This data source is different from the `get_services` (plural) data
    source, which provides a summary of the current Consul services.


    :param str datacenter: The Consul datacenter to query.  Defaults to the
           same value found in `query_options` parameter specified below, or if that is
           empty, the `datacenter` value found in the Consul agent that this provider is
           configured to talk to.
    :param str filter: A filter expression to refine the query, see https://www.consul.io/api-docs/features/filtering
           and https://www.consul.io/api-docs/catalog#filtering-1.
    :param str name: The service name to select.
    :param Sequence[pulumi.InputType['GetServiceQueryOptionArgs']] query_options: See below.
    :param str tag: A single tag that can be used to filter the list of nodes
           to return based on a single matching tag..
    """
    ...
