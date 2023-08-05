# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ApiIamPolicyArgs', 'ApiIamPolicy']

@pulumi.input_type
class ApiIamPolicyArgs:
    def __init__(__self__, *,
                 api: pulumi.Input[str],
                 policy_data: pulumi.Input[str],
                 project: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ApiIamPolicy resource.
        :param pulumi.Input[str] policy_data: The policy data generated by
               a `organizations.get_iam_policy` data source.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        pulumi.set(__self__, "api", api)
        pulumi.set(__self__, "policy_data", policy_data)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter
    def api(self) -> pulumi.Input[str]:
        return pulumi.get(self, "api")

    @api.setter
    def api(self, value: pulumi.Input[str]):
        pulumi.set(self, "api", value)

    @property
    @pulumi.getter(name="policyData")
    def policy_data(self) -> pulumi.Input[str]:
        """
        The policy data generated by
        a `organizations.get_iam_policy` data source.
        """
        return pulumi.get(self, "policy_data")

    @policy_data.setter
    def policy_data(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy_data", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)


@pulumi.input_type
class _ApiIamPolicyState:
    def __init__(__self__, *,
                 api: Optional[pulumi.Input[str]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 policy_data: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ApiIamPolicy resources.
        :param pulumi.Input[str] etag: (Computed) The etag of the IAM policy.
        :param pulumi.Input[str] policy_data: The policy data generated by
               a `organizations.get_iam_policy` data source.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        if api is not None:
            pulumi.set(__self__, "api", api)
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if policy_data is not None:
            pulumi.set(__self__, "policy_data", policy_data)
        if project is not None:
            pulumi.set(__self__, "project", project)

    @property
    @pulumi.getter
    def api(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "api")

    @api.setter
    def api(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "api", value)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        """
        (Computed) The etag of the IAM policy.
        """
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter(name="policyData")
    def policy_data(self) -> Optional[pulumi.Input[str]]:
        """
        The policy data generated by
        a `organizations.get_iam_policy` data source.
        """
        return pulumi.get(self, "policy_data")

    @policy_data.setter
    def policy_data(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_data", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)


class ApiIamPolicy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api: Optional[pulumi.Input[str]] = None,
                 policy_data: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Three different resources help you manage your IAM policy for API Gateway Api. Each of these resources serves a different use case:

        * `apigateway.ApiIamPolicy`: Authoritative. Sets the IAM policy for the api and replaces any existing policy already attached.
        * `apigateway.ApiIamBinding`: Authoritative for a given role. Updates the IAM policy to grant a role to a list of members. Other roles within the IAM policy for the api are preserved.
        * `apigateway.ApiIamMember`: Non-authoritative. Updates the IAM policy to grant a role to a new member. Other members for the role for the api are preserved.

        > **Note:** `apigateway.ApiIamPolicy` **cannot** be used in conjunction with `apigateway.ApiIamBinding` and `apigateway.ApiIamMember` or they will fight over what your policy should be.

        > **Note:** `apigateway.ApiIamBinding` resources **can be** used in conjunction with `apigateway.ApiIamMember` resources **only if** they do not grant privilege to the same role.

        ## google\_api\_gateway\_api\_iam\_policy

        ```python
        import pulumi
        import pulumi_gcp as gcp

        admin = gcp.organizations.get_iam_policy(bindings=[gcp.organizations.GetIAMPolicyBindingArgs(
            role="roles/apigateway.viewer",
            members=["user:jane@example.com"],
        )])
        policy = gcp.apigateway.ApiIamPolicy("policy",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            policy_data=admin.policy_data,
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## google\_api\_gateway\_api\_iam\_binding

        ```python
        import pulumi
        import pulumi_gcp as gcp

        binding = gcp.apigateway.ApiIamBinding("binding",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            role="roles/apigateway.viewer",
            members=["user:jane@example.com"],
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## google\_api\_gateway\_api\_iam\_member

        ```python
        import pulumi
        import pulumi_gcp as gcp

        member = gcp.apigateway.ApiIamMember("member",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            role="roles/apigateway.viewer",
            member="user:jane@example.com",
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## Import

        For all import syntaxes, the "resource in question" can take any of the following forms* projects/{{project}}/locations/global/apis/{{api}} * {{project}}/{{api}} * {{api}} Any variables not passed in the import command will be taken from the provider configuration. API Gateway api IAM resources can be imported using the resource identifiers, role, and member. IAM member imports use space-delimited identifiersthe resource in question, the role, and the member identity, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor "projects/{{project}}/locations/global/apis/{{api}} roles/apigateway.viewer user:jane@example.com"
        ```

         IAM binding imports use space-delimited identifiersthe resource in question and the role, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor "projects/{{project}}/locations/global/apis/{{api}} roles/apigateway.viewer"
        ```

         IAM policy imports use the identifier of the resource in question, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor projects/{{project}}/locations/global/apis/{{api}}
        ```

         -> **Custom Roles**If you're importing a IAM resource with a custom role, make sure to use the

        full name of the custom role, e.g. `[projects/my-project|organizations/my-org]/roles/my-custom-role`.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] policy_data: The policy data generated by
               a `organizations.get_iam_policy` data source.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ApiIamPolicyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Three different resources help you manage your IAM policy for API Gateway Api. Each of these resources serves a different use case:

        * `apigateway.ApiIamPolicy`: Authoritative. Sets the IAM policy for the api and replaces any existing policy already attached.
        * `apigateway.ApiIamBinding`: Authoritative for a given role. Updates the IAM policy to grant a role to a list of members. Other roles within the IAM policy for the api are preserved.
        * `apigateway.ApiIamMember`: Non-authoritative. Updates the IAM policy to grant a role to a new member. Other members for the role for the api are preserved.

        > **Note:** `apigateway.ApiIamPolicy` **cannot** be used in conjunction with `apigateway.ApiIamBinding` and `apigateway.ApiIamMember` or they will fight over what your policy should be.

        > **Note:** `apigateway.ApiIamBinding` resources **can be** used in conjunction with `apigateway.ApiIamMember` resources **only if** they do not grant privilege to the same role.

        ## google\_api\_gateway\_api\_iam\_policy

        ```python
        import pulumi
        import pulumi_gcp as gcp

        admin = gcp.organizations.get_iam_policy(bindings=[gcp.organizations.GetIAMPolicyBindingArgs(
            role="roles/apigateway.viewer",
            members=["user:jane@example.com"],
        )])
        policy = gcp.apigateway.ApiIamPolicy("policy",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            policy_data=admin.policy_data,
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## google\_api\_gateway\_api\_iam\_binding

        ```python
        import pulumi
        import pulumi_gcp as gcp

        binding = gcp.apigateway.ApiIamBinding("binding",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            role="roles/apigateway.viewer",
            members=["user:jane@example.com"],
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## google\_api\_gateway\_api\_iam\_member

        ```python
        import pulumi
        import pulumi_gcp as gcp

        member = gcp.apigateway.ApiIamMember("member",
            project=google_api_gateway_api["api"]["project"],
            api=google_api_gateway_api["api"]["api_id"],
            role="roles/apigateway.viewer",
            member="user:jane@example.com",
            opts=pulumi.ResourceOptions(provider=google_beta))
        ```

        ## Import

        For all import syntaxes, the "resource in question" can take any of the following forms* projects/{{project}}/locations/global/apis/{{api}} * {{project}}/{{api}} * {{api}} Any variables not passed in the import command will be taken from the provider configuration. API Gateway api IAM resources can be imported using the resource identifiers, role, and member. IAM member imports use space-delimited identifiersthe resource in question, the role, and the member identity, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor "projects/{{project}}/locations/global/apis/{{api}} roles/apigateway.viewer user:jane@example.com"
        ```

         IAM binding imports use space-delimited identifiersthe resource in question and the role, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor "projects/{{project}}/locations/global/apis/{{api}} roles/apigateway.viewer"
        ```

         IAM policy imports use the identifier of the resource in question, e.g.

        ```sh
         $ pulumi import gcp:apigateway/apiIamPolicy:ApiIamPolicy editor projects/{{project}}/locations/global/apis/{{api}}
        ```

         -> **Custom Roles**If you're importing a IAM resource with a custom role, make sure to use the

        full name of the custom role, e.g. `[projects/my-project|organizations/my-org]/roles/my-custom-role`.

        :param str resource_name: The name of the resource.
        :param ApiIamPolicyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ApiIamPolicyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 api: Optional[pulumi.Input[str]] = None,
                 policy_data: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
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
            __props__ = ApiIamPolicyArgs.__new__(ApiIamPolicyArgs)

            if api is None and not opts.urn:
                raise TypeError("Missing required property 'api'")
            __props__.__dict__["api"] = api
            if policy_data is None and not opts.urn:
                raise TypeError("Missing required property 'policy_data'")
            __props__.__dict__["policy_data"] = policy_data
            __props__.__dict__["project"] = project
            __props__.__dict__["etag"] = None
        super(ApiIamPolicy, __self__).__init__(
            'gcp:apigateway/apiIamPolicy:ApiIamPolicy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            api: Optional[pulumi.Input[str]] = None,
            etag: Optional[pulumi.Input[str]] = None,
            policy_data: Optional[pulumi.Input[str]] = None,
            project: Optional[pulumi.Input[str]] = None) -> 'ApiIamPolicy':
        """
        Get an existing ApiIamPolicy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] etag: (Computed) The etag of the IAM policy.
        :param pulumi.Input[str] policy_data: The policy data generated by
               a `organizations.get_iam_policy` data source.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ApiIamPolicyState.__new__(_ApiIamPolicyState)

        __props__.__dict__["api"] = api
        __props__.__dict__["etag"] = etag
        __props__.__dict__["policy_data"] = policy_data
        __props__.__dict__["project"] = project
        return ApiIamPolicy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def api(self) -> pulumi.Output[str]:
        return pulumi.get(self, "api")

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        """
        (Computed) The etag of the IAM policy.
        """
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter(name="policyData")
    def policy_data(self) -> pulumi.Output[str]:
        """
        The policy data generated by
        a `organizations.get_iam_policy` data source.
        """
        return pulumi.get(self, "policy_data")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the project will be parsed from the identifier of the parent resource. If no project is provided in the parent identifier and no project is specified, the provider project is used.
        """
        return pulumi.get(self, "project")

