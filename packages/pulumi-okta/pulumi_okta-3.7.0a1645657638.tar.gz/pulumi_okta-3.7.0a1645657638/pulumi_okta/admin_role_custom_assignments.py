# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['AdminRoleCustomAssignmentsArgs', 'AdminRoleCustomAssignments']

@pulumi.input_type
class AdminRoleCustomAssignmentsArgs:
    def __init__(__self__, *,
                 custom_role_id: pulumi.Input[str],
                 resource_set_id: pulumi.Input[str],
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a AdminRoleCustomAssignments resource.
        :param pulumi.Input[str] custom_role_id: ID of the Custom Role.
        :param pulumi.Input[str] resource_set_id: ID of the target Resource Set.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
               permission must be specified when creating custom role.
        """
        pulumi.set(__self__, "custom_role_id", custom_role_id)
        pulumi.set(__self__, "resource_set_id", resource_set_id)
        if members is not None:
            pulumi.set(__self__, "members", members)

    @property
    @pulumi.getter(name="customRoleId")
    def custom_role_id(self) -> pulumi.Input[str]:
        """
        ID of the Custom Role.
        """
        return pulumi.get(self, "custom_role_id")

    @custom_role_id.setter
    def custom_role_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "custom_role_id", value)

    @property
    @pulumi.getter(name="resourceSetId")
    def resource_set_id(self) -> pulumi.Input[str]:
        """
        ID of the target Resource Set.
        """
        return pulumi.get(self, "resource_set_id")

    @resource_set_id.setter
    def resource_set_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_set_id", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
        permission must be specified when creating custom role.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "members", value)


@pulumi.input_type
class _AdminRoleCustomAssignmentsState:
    def __init__(__self__, *,
                 custom_role_id: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_set_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering AdminRoleCustomAssignments resources.
        :param pulumi.Input[str] custom_role_id: ID of the Custom Role.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
               permission must be specified when creating custom role.
        :param pulumi.Input[str] resource_set_id: ID of the target Resource Set.
        """
        if custom_role_id is not None:
            pulumi.set(__self__, "custom_role_id", custom_role_id)
        if members is not None:
            pulumi.set(__self__, "members", members)
        if resource_set_id is not None:
            pulumi.set(__self__, "resource_set_id", resource_set_id)

    @property
    @pulumi.getter(name="customRoleId")
    def custom_role_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the Custom Role.
        """
        return pulumi.get(self, "custom_role_id")

    @custom_role_id.setter
    def custom_role_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "custom_role_id", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
        permission must be specified when creating custom role.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter(name="resourceSetId")
    def resource_set_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the target Resource Set.
        """
        return pulumi.get(self, "resource_set_id")

    @resource_set_id.setter
    def resource_set_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_set_id", value)


class AdminRoleCustomAssignments(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 custom_role_id: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_set_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        This resource allows the assignment and unassignment of Custom Roles. The `members` field supports these type of resources:
         - Groups
         - Users

        > **NOTE:** This an `Early Access` feature.

        ## Import

        Okta Custom Admin Role Assignments can be imported via the Okta ID.

        ```sh
         $ pulumi import okta:index/adminRoleCustomAssignments:AdminRoleCustomAssignments example <resource_set_id>/<custom_role_id>
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] custom_role_id: ID of the Custom Role.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
               permission must be specified when creating custom role.
        :param pulumi.Input[str] resource_set_id: ID of the target Resource Set.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: AdminRoleCustomAssignmentsArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        This resource allows the assignment and unassignment of Custom Roles. The `members` field supports these type of resources:
         - Groups
         - Users

        > **NOTE:** This an `Early Access` feature.

        ## Import

        Okta Custom Admin Role Assignments can be imported via the Okta ID.

        ```sh
         $ pulumi import okta:index/adminRoleCustomAssignments:AdminRoleCustomAssignments example <resource_set_id>/<custom_role_id>
        ```

        :param str resource_name: The name of the resource.
        :param AdminRoleCustomAssignmentsArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AdminRoleCustomAssignmentsArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 custom_role_id: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_set_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = AdminRoleCustomAssignmentsArgs.__new__(AdminRoleCustomAssignmentsArgs)

            if custom_role_id is None and not opts.urn:
                raise TypeError("Missing required property 'custom_role_id'")
            __props__.__dict__["custom_role_id"] = custom_role_id
            __props__.__dict__["members"] = members
            if resource_set_id is None and not opts.urn:
                raise TypeError("Missing required property 'resource_set_id'")
            __props__.__dict__["resource_set_id"] = resource_set_id
        super(AdminRoleCustomAssignments, __self__).__init__(
            'okta:index/adminRoleCustomAssignments:AdminRoleCustomAssignments',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            custom_role_id: Optional[pulumi.Input[str]] = None,
            members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            resource_set_id: Optional[pulumi.Input[str]] = None) -> 'AdminRoleCustomAssignments':
        """
        Get an existing AdminRoleCustomAssignments resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] custom_role_id: ID of the Custom Role.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
               permission must be specified when creating custom role.
        :param pulumi.Input[str] resource_set_id: ID of the target Resource Set.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AdminRoleCustomAssignmentsState.__new__(_AdminRoleCustomAssignmentsState)

        __props__.__dict__["custom_role_id"] = custom_role_id
        __props__.__dict__["members"] = members
        __props__.__dict__["resource_set_id"] = resource_set_id
        return AdminRoleCustomAssignments(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="customRoleId")
    def custom_role_id(self) -> pulumi.Output[str]:
        """
        ID of the Custom Role.
        """
        return pulumi.get(self, "custom_role_id")

    @property
    @pulumi.getter
    def members(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        The hrefs that point to User(s) and/or Group(s) that receive the Role. At least one
        permission must be specified when creating custom role.
        """
        return pulumi.get(self, "members")

    @property
    @pulumi.getter(name="resourceSetId")
    def resource_set_id(self) -> pulumi.Output[str]:
        """
        ID of the target Resource Set.
        """
        return pulumi.get(self, "resource_set_id")

