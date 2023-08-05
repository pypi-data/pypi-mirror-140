# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetAclTokenSecretIdResult',
    'AwaitableGetAclTokenSecretIdResult',
    'get_acl_token_secret_id',
    'get_acl_token_secret_id_output',
]

@pulumi.output_type
class GetAclTokenSecretIdResult:
    """
    A collection of values returned by getAclTokenSecretId.
    """
    def __init__(__self__, accessor_id=None, encrypted_secret_id=None, id=None, namespace=None, pgp_key=None, secret_id=None):
        if accessor_id and not isinstance(accessor_id, str):
            raise TypeError("Expected argument 'accessor_id' to be a str")
        pulumi.set(__self__, "accessor_id", accessor_id)
        if encrypted_secret_id and not isinstance(encrypted_secret_id, str):
            raise TypeError("Expected argument 'encrypted_secret_id' to be a str")
        pulumi.set(__self__, "encrypted_secret_id", encrypted_secret_id)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if namespace and not isinstance(namespace, str):
            raise TypeError("Expected argument 'namespace' to be a str")
        pulumi.set(__self__, "namespace", namespace)
        if pgp_key and not isinstance(pgp_key, str):
            raise TypeError("Expected argument 'pgp_key' to be a str")
        pulumi.set(__self__, "pgp_key", pgp_key)
        if secret_id and not isinstance(secret_id, str):
            raise TypeError("Expected argument 'secret_id' to be a str")
        pulumi.set(__self__, "secret_id", secret_id)

    @property
    @pulumi.getter(name="accessorId")
    def accessor_id(self) -> str:
        return pulumi.get(self, "accessor_id")

    @property
    @pulumi.getter(name="encryptedSecretId")
    def encrypted_secret_id(self) -> str:
        return pulumi.get(self, "encrypted_secret_id")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def namespace(self) -> Optional[str]:
        return pulumi.get(self, "namespace")

    @property
    @pulumi.getter(name="pgpKey")
    def pgp_key(self) -> Optional[str]:
        return pulumi.get(self, "pgp_key")

    @property
    @pulumi.getter(name="secretId")
    def secret_id(self) -> str:
        """
        The secret ID of the ACL token if `pgp_key` has not been set.
        """
        return pulumi.get(self, "secret_id")


class AwaitableGetAclTokenSecretIdResult(GetAclTokenSecretIdResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAclTokenSecretIdResult(
            accessor_id=self.accessor_id,
            encrypted_secret_id=self.encrypted_secret_id,
            id=self.id,
            namespace=self.namespace,
            pgp_key=self.pgp_key,
            secret_id=self.secret_id)


def get_acl_token_secret_id(accessor_id: Optional[str] = None,
                            namespace: Optional[str] = None,
                            pgp_key: Optional[str] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAclTokenSecretIdResult:
    """
    Use this data source to access information about an existing resource.

    :param str accessor_id: The accessor ID of the ACL token.
    :param str namespace: The namespace to lookup the token.
    """
    __args__ = dict()
    __args__['accessorId'] = accessor_id
    __args__['namespace'] = namespace
    __args__['pgpKey'] = pgp_key
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('consul:index/getAclTokenSecretId:getAclTokenSecretId', __args__, opts=opts, typ=GetAclTokenSecretIdResult).value

    return AwaitableGetAclTokenSecretIdResult(
        accessor_id=__ret__.accessor_id,
        encrypted_secret_id=__ret__.encrypted_secret_id,
        id=__ret__.id,
        namespace=__ret__.namespace,
        pgp_key=__ret__.pgp_key,
        secret_id=__ret__.secret_id)


@_utilities.lift_output_func(get_acl_token_secret_id)
def get_acl_token_secret_id_output(accessor_id: Optional[pulumi.Input[str]] = None,
                                   namespace: Optional[pulumi.Input[Optional[str]]] = None,
                                   pgp_key: Optional[pulumi.Input[Optional[str]]] = None,
                                   opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAclTokenSecretIdResult]:
    """
    Use this data source to access information about an existing resource.

    :param str accessor_id: The accessor ID of the ACL token.
    :param str namespace: The namespace to lookup the token.
    """
    ...
