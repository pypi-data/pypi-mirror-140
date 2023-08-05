# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs

__all__ = [
    'GetAclRoleResult',
    'AwaitableGetAclRoleResult',
    'get_acl_role',
    'get_acl_role_output',
]

@pulumi.output_type
class GetAclRoleResult:
    """
    A collection of values returned by getAclRole.
    """
    def __init__(__self__, description=None, id=None, name=None, namespace=None, node_identities=None, policies=None, service_identities=None):
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if namespace and not isinstance(namespace, str):
            raise TypeError("Expected argument 'namespace' to be a str")
        pulumi.set(__self__, "namespace", namespace)
        if node_identities and not isinstance(node_identities, list):
            raise TypeError("Expected argument 'node_identities' to be a list")
        pulumi.set(__self__, "node_identities", node_identities)
        if policies and not isinstance(policies, list):
            raise TypeError("Expected argument 'policies' to be a list")
        pulumi.set(__self__, "policies", policies)
        if service_identities and not isinstance(service_identities, list):
            raise TypeError("Expected argument 'service_identities' to be a list")
        pulumi.set(__self__, "service_identities", service_identities)

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        The description of the ACL Role.
        """
        return pulumi.get(self, "description")

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
        The name of the ACL Role.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def namespace(self) -> Optional[str]:
        """
        The namespace to lookup the role.
        """
        return pulumi.get(self, "namespace")

    @property
    @pulumi.getter(name="nodeIdentities")
    def node_identities(self) -> Sequence['outputs.GetAclRoleNodeIdentityResult']:
        """
        The list of node identities associated with the ACL Role. Each entry has a `node_name` and a `datacenter` attributes.
        """
        return pulumi.get(self, "node_identities")

    @property
    @pulumi.getter
    def policies(self) -> Sequence['outputs.GetAclRolePolicyResult']:
        """
        The list of policies associated with the ACL Role. Each entry has an `id` and a `name` attribute.
        """
        return pulumi.get(self, "policies")

    @property
    @pulumi.getter(name="serviceIdentities")
    def service_identities(self) -> Sequence['outputs.GetAclRoleServiceIdentityResult']:
        """
        The list of service identities associated with the ACL Role. Each entry has a `service_name` attribute and a list of `datacenters`.
        """
        return pulumi.get(self, "service_identities")


class AwaitableGetAclRoleResult(GetAclRoleResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAclRoleResult(
            description=self.description,
            id=self.id,
            name=self.name,
            namespace=self.namespace,
            node_identities=self.node_identities,
            policies=self.policies,
            service_identities=self.service_identities)


def get_acl_role(name: Optional[str] = None,
                 namespace: Optional[str] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAclRoleResult:
    """
    The `AclRole` data source returns the information related to a
    [Consul ACL Role](https://www.consul.io/api/acl/roles.html).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_consul as consul

    test = consul.get_acl_role(name="example-role")
    pulumi.export("consulAclRole", test.id)
    ```


    :param str name: The name of the ACL Role.
    :param str namespace: The namespace to lookup the role.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['namespace'] = namespace
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('consul:index/getAclRole:getAclRole', __args__, opts=opts, typ=GetAclRoleResult).value

    return AwaitableGetAclRoleResult(
        description=__ret__.description,
        id=__ret__.id,
        name=__ret__.name,
        namespace=__ret__.namespace,
        node_identities=__ret__.node_identities,
        policies=__ret__.policies,
        service_identities=__ret__.service_identities)


@_utilities.lift_output_func(get_acl_role)
def get_acl_role_output(name: Optional[pulumi.Input[str]] = None,
                        namespace: Optional[pulumi.Input[Optional[str]]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAclRoleResult]:
    """
    The `AclRole` data source returns the information related to a
    [Consul ACL Role](https://www.consul.io/api/acl/roles.html).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_consul as consul

    test = consul.get_acl_role(name="example-role")
    pulumi.export("consulAclRole", test.id)
    ```


    :param str name: The name of the ACL Role.
    :param str namespace: The namespace to lookup the role.
    """
    ...
