# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['ProjectRoleTemplateBindingArgs', 'ProjectRoleTemplateBinding']

@pulumi.input_type
class ProjectRoleTemplateBindingArgs:
    def __init__(__self__, *,
                 project_id: pulumi.Input[str],
                 role_template_id: pulumi.Input[str],
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_principal_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 user_principal_id: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ProjectRoleTemplateBinding resource.
        :param pulumi.Input[str] project_id: The project id where bind project role template (string)
        :param pulumi.Input[str] role_template_id: The role template id from create project role template binding (string)
        :param pulumi.Input[Mapping[str, Any]] annotations: Annotations of the resource (map)
        :param pulumi.Input[str] group_id: The group ID to assign project role template binding (string)
        :param pulumi.Input[str] group_principal_id: The group_principal ID to assign project role template binding (string)
        :param pulumi.Input[Mapping[str, Any]] labels: Labels of the resource (map)
        :param pulumi.Input[str] name: The name of the project role template binding (string)
        :param pulumi.Input[str] user_id: The user ID to assign project role template binding (string)
        :param pulumi.Input[str] user_principal_id: The user_principal ID to assign project role template binding (string)
        """
        pulumi.set(__self__, "project_id", project_id)
        pulumi.set(__self__, "role_template_id", role_template_id)
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if group_id is not None:
            pulumi.set(__self__, "group_id", group_id)
        if group_principal_id is not None:
            pulumi.set(__self__, "group_principal_id", group_principal_id)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if user_id is not None:
            pulumi.set(__self__, "user_id", user_id)
        if user_principal_id is not None:
            pulumi.set(__self__, "user_principal_id", user_principal_id)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Input[str]:
        """
        The project id where bind project role template (string)
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter(name="roleTemplateId")
    def role_template_id(self) -> pulumi.Input[str]:
        """
        The role template id from create project role template binding (string)
        """
        return pulumi.get(self, "role_template_id")

    @role_template_id.setter
    def role_template_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "role_template_id", value)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Annotations of the resource (map)
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The group ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="groupPrincipalId")
    def group_principal_id(self) -> Optional[pulumi.Input[str]]:
        """
        The group_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_principal_id")

    @group_principal_id.setter
    def group_principal_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "group_principal_id", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Labels of the resource (map)
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the project role template binding (string)
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="userId")
    def user_id(self) -> Optional[pulumi.Input[str]]:
        """
        The user ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_id")

    @user_id.setter
    def user_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_id", value)

    @property
    @pulumi.getter(name="userPrincipalId")
    def user_principal_id(self) -> Optional[pulumi.Input[str]]:
        """
        The user_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_principal_id")

    @user_principal_id.setter
    def user_principal_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_principal_id", value)


@pulumi.input_type
class _ProjectRoleTemplateBindingState:
    def __init__(__self__, *,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_principal_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 role_template_id: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 user_principal_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ProjectRoleTemplateBinding resources.
        :param pulumi.Input[Mapping[str, Any]] annotations: Annotations of the resource (map)
        :param pulumi.Input[str] group_id: The group ID to assign project role template binding (string)
        :param pulumi.Input[str] group_principal_id: The group_principal ID to assign project role template binding (string)
        :param pulumi.Input[Mapping[str, Any]] labels: Labels of the resource (map)
        :param pulumi.Input[str] name: The name of the project role template binding (string)
        :param pulumi.Input[str] project_id: The project id where bind project role template (string)
        :param pulumi.Input[str] role_template_id: The role template id from create project role template binding (string)
        :param pulumi.Input[str] user_id: The user ID to assign project role template binding (string)
        :param pulumi.Input[str] user_principal_id: The user_principal ID to assign project role template binding (string)
        """
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if group_id is not None:
            pulumi.set(__self__, "group_id", group_id)
        if group_principal_id is not None:
            pulumi.set(__self__, "group_principal_id", group_principal_id)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project_id is not None:
            pulumi.set(__self__, "project_id", project_id)
        if role_template_id is not None:
            pulumi.set(__self__, "role_template_id", role_template_id)
        if user_id is not None:
            pulumi.set(__self__, "user_id", user_id)
        if user_principal_id is not None:
            pulumi.set(__self__, "user_principal_id", user_principal_id)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Annotations of the resource (map)
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The group ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="groupPrincipalId")
    def group_principal_id(self) -> Optional[pulumi.Input[str]]:
        """
        The group_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_principal_id")

    @group_principal_id.setter
    def group_principal_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "group_principal_id", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Labels of the resource (map)
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the project role template binding (string)
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> Optional[pulumi.Input[str]]:
        """
        The project id where bind project role template (string)
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter(name="roleTemplateId")
    def role_template_id(self) -> Optional[pulumi.Input[str]]:
        """
        The role template id from create project role template binding (string)
        """
        return pulumi.get(self, "role_template_id")

    @role_template_id.setter
    def role_template_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "role_template_id", value)

    @property
    @pulumi.getter(name="userId")
    def user_id(self) -> Optional[pulumi.Input[str]]:
        """
        The user ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_id")

    @user_id.setter
    def user_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_id", value)

    @property
    @pulumi.getter(name="userPrincipalId")
    def user_principal_id(self) -> Optional[pulumi.Input[str]]:
        """
        The user_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_principal_id")

    @user_principal_id.setter
    def user_principal_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_principal_id", value)


class ProjectRoleTemplateBinding(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_principal_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 role_template_id: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 user_principal_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a Rancher v2 Project Role Template Binding resource. This can be used to create Project Role Template Bindings for Rancher v2 environments and retrieve their information.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_rancher2 as rancher2

        # Create a new rancher2 Project Role Template Binding
        foo = rancher2.ProjectRoleTemplateBinding("foo",
            project_id="<project_id>",
            role_template_id="<role_template_id>",
            user_id="<user_id>")
        ```

        ## Import

        Project Role Template Bindings can be imported using the Rancher Project Role Template Binding ID

        ```sh
         $ pulumi import rancher2:index/projectRoleTemplateBinding:ProjectRoleTemplateBinding foo &lt;project_role_template_binding_id&gt;
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, Any]] annotations: Annotations of the resource (map)
        :param pulumi.Input[str] group_id: The group ID to assign project role template binding (string)
        :param pulumi.Input[str] group_principal_id: The group_principal ID to assign project role template binding (string)
        :param pulumi.Input[Mapping[str, Any]] labels: Labels of the resource (map)
        :param pulumi.Input[str] name: The name of the project role template binding (string)
        :param pulumi.Input[str] project_id: The project id where bind project role template (string)
        :param pulumi.Input[str] role_template_id: The role template id from create project role template binding (string)
        :param pulumi.Input[str] user_id: The user ID to assign project role template binding (string)
        :param pulumi.Input[str] user_principal_id: The user_principal ID to assign project role template binding (string)
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProjectRoleTemplateBindingArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Rancher v2 Project Role Template Binding resource. This can be used to create Project Role Template Bindings for Rancher v2 environments and retrieve their information.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_rancher2 as rancher2

        # Create a new rancher2 Project Role Template Binding
        foo = rancher2.ProjectRoleTemplateBinding("foo",
            project_id="<project_id>",
            role_template_id="<role_template_id>",
            user_id="<user_id>")
        ```

        ## Import

        Project Role Template Bindings can be imported using the Rancher Project Role Template Binding ID

        ```sh
         $ pulumi import rancher2:index/projectRoleTemplateBinding:ProjectRoleTemplateBinding foo &lt;project_role_template_binding_id&gt;
        ```

        :param str resource_name: The name of the resource.
        :param ProjectRoleTemplateBindingArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProjectRoleTemplateBindingArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_principal_id: Optional[pulumi.Input[str]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 role_template_id: Optional[pulumi.Input[str]] = None,
                 user_id: Optional[pulumi.Input[str]] = None,
                 user_principal_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ProjectRoleTemplateBindingArgs.__new__(ProjectRoleTemplateBindingArgs)

            __props__.__dict__["annotations"] = annotations
            __props__.__dict__["group_id"] = group_id
            __props__.__dict__["group_principal_id"] = group_principal_id
            __props__.__dict__["labels"] = labels
            __props__.__dict__["name"] = name
            if project_id is None and not opts.urn:
                raise TypeError("Missing required property 'project_id'")
            __props__.__dict__["project_id"] = project_id
            if role_template_id is None and not opts.urn:
                raise TypeError("Missing required property 'role_template_id'")
            __props__.__dict__["role_template_id"] = role_template_id
            __props__.__dict__["user_id"] = user_id
            __props__.__dict__["user_principal_id"] = user_principal_id
        super(ProjectRoleTemplateBinding, __self__).__init__(
            'rancher2:index/projectRoleTemplateBinding:ProjectRoleTemplateBinding',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            group_id: Optional[pulumi.Input[str]] = None,
            group_principal_id: Optional[pulumi.Input[str]] = None,
            labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            name: Optional[pulumi.Input[str]] = None,
            project_id: Optional[pulumi.Input[str]] = None,
            role_template_id: Optional[pulumi.Input[str]] = None,
            user_id: Optional[pulumi.Input[str]] = None,
            user_principal_id: Optional[pulumi.Input[str]] = None) -> 'ProjectRoleTemplateBinding':
        """
        Get an existing ProjectRoleTemplateBinding resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, Any]] annotations: Annotations of the resource (map)
        :param pulumi.Input[str] group_id: The group ID to assign project role template binding (string)
        :param pulumi.Input[str] group_principal_id: The group_principal ID to assign project role template binding (string)
        :param pulumi.Input[Mapping[str, Any]] labels: Labels of the resource (map)
        :param pulumi.Input[str] name: The name of the project role template binding (string)
        :param pulumi.Input[str] project_id: The project id where bind project role template (string)
        :param pulumi.Input[str] role_template_id: The role template id from create project role template binding (string)
        :param pulumi.Input[str] user_id: The user ID to assign project role template binding (string)
        :param pulumi.Input[str] user_principal_id: The user_principal ID to assign project role template binding (string)
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ProjectRoleTemplateBindingState.__new__(_ProjectRoleTemplateBindingState)

        __props__.__dict__["annotations"] = annotations
        __props__.__dict__["group_id"] = group_id
        __props__.__dict__["group_principal_id"] = group_principal_id
        __props__.__dict__["labels"] = labels
        __props__.__dict__["name"] = name
        __props__.__dict__["project_id"] = project_id
        __props__.__dict__["role_template_id"] = role_template_id
        __props__.__dict__["user_id"] = user_id
        __props__.__dict__["user_principal_id"] = user_principal_id
        return ProjectRoleTemplateBinding(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def annotations(self) -> pulumi.Output[Mapping[str, Any]]:
        """
        Annotations of the resource (map)
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Output[str]:
        """
        The group ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_id")

    @property
    @pulumi.getter(name="groupPrincipalId")
    def group_principal_id(self) -> pulumi.Output[str]:
        """
        The group_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "group_principal_id")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, Any]]:
        """
        Labels of the resource (map)
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the project role template binding (string)
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Output[str]:
        """
        The project id where bind project role template (string)
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter(name="roleTemplateId")
    def role_template_id(self) -> pulumi.Output[str]:
        """
        The role template id from create project role template binding (string)
        """
        return pulumi.get(self, "role_template_id")

    @property
    @pulumi.getter(name="userId")
    def user_id(self) -> pulumi.Output[str]:
        """
        The user ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_id")

    @property
    @pulumi.getter(name="userPrincipalId")
    def user_principal_id(self) -> pulumi.Output[str]:
        """
        The user_principal ID to assign project role template binding (string)
        """
        return pulumi.get(self, "user_principal_id")

