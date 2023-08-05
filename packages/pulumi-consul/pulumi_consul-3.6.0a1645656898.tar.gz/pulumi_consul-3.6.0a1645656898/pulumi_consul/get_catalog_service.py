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
    'GetCatalogServiceResult',
    'AwaitableGetCatalogServiceResult',
    'get_catalog_service',
    'get_catalog_service_output',
]

@pulumi.output_type
class GetCatalogServiceResult:
    """
    A collection of values returned by getCatalogService.
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
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="queryOptions")
    def query_options(self) -> Optional[Sequence['outputs.GetCatalogServiceQueryOptionResult']]:
        return pulumi.get(self, "query_options")

    @property
    @pulumi.getter
    def services(self) -> Sequence['outputs.GetCatalogServiceServiceResult']:
        return pulumi.get(self, "services")

    @property
    @pulumi.getter
    def tag(self) -> Optional[str]:
        return pulumi.get(self, "tag")


class AwaitableGetCatalogServiceResult(GetCatalogServiceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetCatalogServiceResult(
            datacenter=self.datacenter,
            filter=self.filter,
            id=self.id,
            name=self.name,
            query_options=self.query_options,
            services=self.services,
            tag=self.tag)


def get_catalog_service(datacenter: Optional[str] = None,
                        filter: Optional[str] = None,
                        name: Optional[str] = None,
                        query_options: Optional[Sequence[pulumi.InputType['GetCatalogServiceQueryOptionArgs']]] = None,
                        tag: Optional[str] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetCatalogServiceResult:
    """
    Use this data source to access information about an existing resource.
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
    __ret__ = pulumi.runtime.invoke('consul:index/getCatalogService:getCatalogService', __args__, opts=opts, typ=GetCatalogServiceResult).value

    return AwaitableGetCatalogServiceResult(
        datacenter=__ret__.datacenter,
        filter=__ret__.filter,
        id=__ret__.id,
        name=__ret__.name,
        query_options=__ret__.query_options,
        services=__ret__.services,
        tag=__ret__.tag)


@_utilities.lift_output_func(get_catalog_service)
def get_catalog_service_output(datacenter: Optional[pulumi.Input[Optional[str]]] = None,
                               filter: Optional[pulumi.Input[Optional[str]]] = None,
                               name: Optional[pulumi.Input[str]] = None,
                               query_options: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetCatalogServiceQueryOptionArgs']]]]] = None,
                               tag: Optional[pulumi.Input[Optional[str]]] = None,
                               opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetCatalogServiceResult]:
    """
    Use this data source to access information about an existing resource.
    """
    ...
