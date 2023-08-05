# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetAppUserAssignmentsResult',
    'AwaitableGetAppUserAssignmentsResult',
    'get_app_user_assignments',
    'get_app_user_assignments_output',
]

@pulumi.output_type
class GetAppUserAssignmentsResult:
    """
    A collection of values returned by getAppUserAssignments.
    """
    def __init__(__self__, id=None, users=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if users and not isinstance(users, list):
            raise TypeError("Expected argument 'users' to be a list")
        pulumi.set(__self__, "users", users)

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        ID of application.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def users(self) -> Sequence[str]:
        """
        List of user IDs assigned to the application.
        """
        return pulumi.get(self, "users")


class AwaitableGetAppUserAssignmentsResult(GetAppUserAssignmentsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAppUserAssignmentsResult(
            id=self.id,
            users=self.users)


def get_app_user_assignments(id: Optional[str] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAppUserAssignmentsResult:
    """
    Use this data source to retrieve the list of users assigned to the given Okta application (by ID).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    test = okta.get_app_user_assignments(id=okta_app_oauth["test"]["id"])
    ```


    :param str id: The ID of the Okta application you want to retrieve the groups for.
    """
    __args__ = dict()
    __args__['id'] = id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('okta:index/getAppUserAssignments:getAppUserAssignments', __args__, opts=opts, typ=GetAppUserAssignmentsResult).value

    return AwaitableGetAppUserAssignmentsResult(
        id=__ret__.id,
        users=__ret__.users)


@_utilities.lift_output_func(get_app_user_assignments)
def get_app_user_assignments_output(id: Optional[pulumi.Input[str]] = None,
                                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAppUserAssignmentsResult]:
    """
    Use this data source to retrieve the list of users assigned to the given Okta application (by ID).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_okta as okta

    test = okta.get_app_user_assignments(id=okta_app_oauth["test"]["id"])
    ```


    :param str id: The ID of the Okta application you want to retrieve the groups for.
    """
    ...
