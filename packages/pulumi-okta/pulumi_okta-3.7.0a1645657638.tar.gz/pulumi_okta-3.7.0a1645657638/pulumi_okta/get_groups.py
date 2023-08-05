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
    'GetGroupsResult',
    'AwaitableGetGroupsResult',
    'get_groups',
    'get_groups_output',
]

@pulumi.output_type
class GetGroupsResult:
    """
    A collection of values returned by getGroups.
    """
    def __init__(__self__, groups=None, id=None, q=None, search=None, type=None):
        if groups and not isinstance(groups, list):
            raise TypeError("Expected argument 'groups' to be a list")
        pulumi.set(__self__, "groups", groups)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if q and not isinstance(q, str):
            raise TypeError("Expected argument 'q' to be a str")
        pulumi.set(__self__, "q", q)
        if search and not isinstance(search, str):
            raise TypeError("Expected argument 'search' to be a str")
        pulumi.set(__self__, "search", search)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def groups(self) -> Sequence['outputs.GetGroupsGroupResult']:
        """
        collection of groups retrieved from Okta with the following properties.
        """
        return pulumi.get(self, "groups")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def q(self) -> Optional[str]:
        return pulumi.get(self, "q")

    @property
    @pulumi.getter
    def search(self) -> Optional[str]:
        return pulumi.get(self, "search")

    @property
    @pulumi.getter
    def type(self) -> Optional[str]:
        """
        Group type.
        """
        return pulumi.get(self, "type")


class AwaitableGetGroupsResult(GetGroupsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetGroupsResult(
            groups=self.groups,
            id=self.id,
            q=self.q,
            search=self.search,
            type=self.type)


def get_groups(q: Optional[str] = None,
               search: Optional[str] = None,
               type: Optional[str] = None,
               opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetGroupsResult:
    """
    Use this data source to retrieve a list of groups from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    example = okta.get_groups(q="Engineering - ")
    ```


    :param str q: Searches the name property of groups for matching value.
    :param str search: Searches for groups with a
           supported [filtering](https://developer.okta.com/docs/reference/api-overview/#filtering) expression for
           all [attributes](https://developer.okta.com/docs/reference/api/groups/#group-attributes)
           except for `"_embedded"`, `"_links"`, and `"objectClass"`
    :param str type: type of the group to retrieve. Can only be one of `OKTA_GROUP` (Native Okta Groups), `APP_GROUP`
           (Imported App Groups), or `BUILT_IN` (Okta System Groups).
    """
    __args__ = dict()
    __args__['q'] = q
    __args__['search'] = search
    __args__['type'] = type
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('okta:index/getGroups:getGroups', __args__, opts=opts, typ=GetGroupsResult).value

    return AwaitableGetGroupsResult(
        groups=__ret__.groups,
        id=__ret__.id,
        q=__ret__.q,
        search=__ret__.search,
        type=__ret__.type)


@_utilities.lift_output_func(get_groups)
def get_groups_output(q: Optional[pulumi.Input[Optional[str]]] = None,
                      search: Optional[pulumi.Input[Optional[str]]] = None,
                      type: Optional[pulumi.Input[Optional[str]]] = None,
                      opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetGroupsResult]:
    """
    Use this data source to retrieve a list of groups from Okta.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    example = okta.get_groups(q="Engineering - ")
    ```


    :param str q: Searches the name property of groups for matching value.
    :param str search: Searches for groups with a
           supported [filtering](https://developer.okta.com/docs/reference/api-overview/#filtering) expression for
           all [attributes](https://developer.okta.com/docs/reference/api/groups/#group-attributes)
           except for `"_embedded"`, `"_links"`, and `"objectClass"`
    :param str type: type of the group to retrieve. Can only be one of `OKTA_GROUP` (Native Okta Groups), `APP_GROUP`
           (Imported App Groups), or `BUILT_IN` (Okta System Groups).
    """
    ...
