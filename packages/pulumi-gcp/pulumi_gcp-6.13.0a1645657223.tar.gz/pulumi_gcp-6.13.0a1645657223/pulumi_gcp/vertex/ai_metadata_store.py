# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs
from ._inputs import *

__all__ = ['AiMetadataStoreArgs', 'AiMetadataStore']

@pulumi.input_type
class AiMetadataStoreArgs:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 encryption_spec: Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a AiMetadataStore resource.
        :param pulumi.Input[str] description: Description of the MetadataStore.
        :param pulumi.Input['AiMetadataStoreEncryptionSpecArgs'] encryption_spec: Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
               Structure is documented below.
        :param pulumi.Input[str] name: The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the provider project is used.
        :param pulumi.Input[str] region: The region of the Metadata Store. eg us-central1
        """
        if description is not None:
            pulumi.set(__self__, "description", description)
        if encryption_spec is not None:
            pulumi.set(__self__, "encryption_spec", encryption_spec)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if region is not None:
            pulumi.set(__self__, "region", region)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of the MetadataStore.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="encryptionSpec")
    def encryption_spec(self) -> Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']]:
        """
        Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
        Structure is documented below.
        """
        return pulumi.get(self, "encryption_spec")

    @encryption_spec.setter
    def encryption_spec(self, value: Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']]):
        pulumi.set(self, "encryption_spec", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the provider project is used.
        """
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region of the Metadata Store. eg us-central1
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)


@pulumi.input_type
class _AiMetadataStoreState:
    def __init__(__self__, *,
                 create_time: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encryption_spec: Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 states: Optional[pulumi.Input[Sequence[pulumi.Input['AiMetadataStoreStateArgs']]]] = None,
                 update_time: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering AiMetadataStore resources.
        :param pulumi.Input[str] create_time: The timestamp of when the MetadataStore was created in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to
               nine fractional digits.
        :param pulumi.Input[str] description: Description of the MetadataStore.
        :param pulumi.Input['AiMetadataStoreEncryptionSpecArgs'] encryption_spec: Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
               Structure is documented below.
        :param pulumi.Input[str] name: The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the provider project is used.
        :param pulumi.Input[str] region: The region of the Metadata Store. eg us-central1
        :param pulumi.Input[Sequence[pulumi.Input['AiMetadataStoreStateArgs']]] states: State information of the MetadataStore.
        :param pulumi.Input[str] update_time: The timestamp of when the MetadataStore was last updated in RFC3339 UTC "Zulu" format, with nanosecond resolution and up
               to nine fractional digits.
        """
        if create_time is not None:
            pulumi.set(__self__, "create_time", create_time)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if encryption_spec is not None:
            pulumi.set(__self__, "encryption_spec", encryption_spec)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if project is not None:
            pulumi.set(__self__, "project", project)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if states is not None:
            pulumi.set(__self__, "states", states)
        if update_time is not None:
            pulumi.set(__self__, "update_time", update_time)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> Optional[pulumi.Input[str]]:
        """
        The timestamp of when the MetadataStore was created in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to
        nine fractional digits.
        """
        return pulumi.get(self, "create_time")

    @create_time.setter
    def create_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "create_time", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of the MetadataStore.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="encryptionSpec")
    def encryption_spec(self) -> Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']]:
        """
        Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
        Structure is documented below.
        """
        return pulumi.get(self, "encryption_spec")

    @encryption_spec.setter
    def encryption_spec(self, value: Optional[pulumi.Input['AiMetadataStoreEncryptionSpecArgs']]):
        pulumi.set(self, "encryption_spec", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def project(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the provider project is used.
        """
        return pulumi.get(self, "project")

    @project.setter
    def project(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region of the Metadata Store. eg us-central1
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def states(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['AiMetadataStoreStateArgs']]]]:
        """
        State information of the MetadataStore.
        """
        return pulumi.get(self, "states")

    @states.setter
    def states(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['AiMetadataStoreStateArgs']]]]):
        pulumi.set(self, "states", value)

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> Optional[pulumi.Input[str]]:
        """
        The timestamp of when the MetadataStore was last updated in RFC3339 UTC "Zulu" format, with nanosecond resolution and up
        to nine fractional digits.
        """
        return pulumi.get(self, "update_time")

    @update_time.setter
    def update_time(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "update_time", value)


class AiMetadataStore(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encryption_spec: Optional[pulumi.Input[pulumi.InputType['AiMetadataStoreEncryptionSpecArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        ## Import

        MetadataStore can be imported using any of these accepted formats

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default projects/{{project}}/locations/{{region}}/metadataStores/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{project}}/{{region}}/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{region}}/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{name}}
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: Description of the MetadataStore.
        :param pulumi.Input[pulumi.InputType['AiMetadataStoreEncryptionSpecArgs']] encryption_spec: Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
               Structure is documented below.
        :param pulumi.Input[str] name: The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the provider project is used.
        :param pulumi.Input[str] region: The region of the Metadata Store. eg us-central1
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[AiMetadataStoreArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Import

        MetadataStore can be imported using any of these accepted formats

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default projects/{{project}}/locations/{{region}}/metadataStores/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{project}}/{{region}}/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{region}}/{{name}}
        ```

        ```sh
         $ pulumi import gcp:vertex/aiMetadataStore:AiMetadataStore default {{name}}
        ```

        :param str resource_name: The name of the resource.
        :param AiMetadataStoreArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AiMetadataStoreArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 encryption_spec: Optional[pulumi.Input[pulumi.InputType['AiMetadataStoreEncryptionSpecArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 project: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
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
            __props__ = AiMetadataStoreArgs.__new__(AiMetadataStoreArgs)

            __props__.__dict__["description"] = description
            __props__.__dict__["encryption_spec"] = encryption_spec
            __props__.__dict__["name"] = name
            __props__.__dict__["project"] = project
            __props__.__dict__["region"] = region
            __props__.__dict__["create_time"] = None
            __props__.__dict__["states"] = None
            __props__.__dict__["update_time"] = None
        super(AiMetadataStore, __self__).__init__(
            'gcp:vertex/aiMetadataStore:AiMetadataStore',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            create_time: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            encryption_spec: Optional[pulumi.Input[pulumi.InputType['AiMetadataStoreEncryptionSpecArgs']]] = None,
            name: Optional[pulumi.Input[str]] = None,
            project: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            states: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['AiMetadataStoreStateArgs']]]]] = None,
            update_time: Optional[pulumi.Input[str]] = None) -> 'AiMetadataStore':
        """
        Get an existing AiMetadataStore resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] create_time: The timestamp of when the MetadataStore was created in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to
               nine fractional digits.
        :param pulumi.Input[str] description: Description of the MetadataStore.
        :param pulumi.Input[pulumi.InputType['AiMetadataStoreEncryptionSpecArgs']] encryption_spec: Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
               Structure is documented below.
        :param pulumi.Input[str] name: The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        :param pulumi.Input[str] project: The ID of the project in which the resource belongs.
               If it is not provided, the provider project is used.
        :param pulumi.Input[str] region: The region of the Metadata Store. eg us-central1
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['AiMetadataStoreStateArgs']]]] states: State information of the MetadataStore.
        :param pulumi.Input[str] update_time: The timestamp of when the MetadataStore was last updated in RFC3339 UTC "Zulu" format, with nanosecond resolution and up
               to nine fractional digits.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AiMetadataStoreState.__new__(_AiMetadataStoreState)

        __props__.__dict__["create_time"] = create_time
        __props__.__dict__["description"] = description
        __props__.__dict__["encryption_spec"] = encryption_spec
        __props__.__dict__["name"] = name
        __props__.__dict__["project"] = project
        __props__.__dict__["region"] = region
        __props__.__dict__["states"] = states
        __props__.__dict__["update_time"] = update_time
        return AiMetadataStore(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="createTime")
    def create_time(self) -> pulumi.Output[str]:
        """
        The timestamp of when the MetadataStore was created in RFC3339 UTC "Zulu" format, with nanosecond resolution and up to
        nine fractional digits.
        """
        return pulumi.get(self, "create_time")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        Description of the MetadataStore.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="encryptionSpec")
    def encryption_spec(self) -> pulumi.Output[Optional['outputs.AiMetadataStoreEncryptionSpec']]:
        """
        Customer-managed encryption key spec for a MetadataStore. If set, this MetadataStore and all sub-resources of this MetadataStore will be secured by this key.
        Structure is documented below.
        """
        return pulumi.get(self, "encryption_spec")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the MetadataStore. This value may be up to 60 characters, and valid characters are [a-z0-9_]. The first character cannot be a number.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def project(self) -> pulumi.Output[str]:
        """
        The ID of the project in which the resource belongs.
        If it is not provided, the provider project is used.
        """
        return pulumi.get(self, "project")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region of the Metadata Store. eg us-central1
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def states(self) -> pulumi.Output[Sequence['outputs.AiMetadataStoreState']]:
        """
        State information of the MetadataStore.
        """
        return pulumi.get(self, "states")

    @property
    @pulumi.getter(name="updateTime")
    def update_time(self) -> pulumi.Output[str]:
        """
        The timestamp of when the MetadataStore was last updated in RFC3339 UTC "Zulu" format, with nanosecond resolution and up
        to nine fractional digits.
        """
        return pulumi.get(self, "update_time")

