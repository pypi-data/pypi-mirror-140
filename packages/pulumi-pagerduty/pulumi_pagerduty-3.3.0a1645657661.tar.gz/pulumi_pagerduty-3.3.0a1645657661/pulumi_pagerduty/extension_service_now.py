# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['ExtensionServiceNowArgs', 'ExtensionServiceNow']

@pulumi.input_type
class ExtensionServiceNowArgs:
    def __init__(__self__, *,
                 extension_objects: pulumi.Input[Sequence[pulumi.Input[str]]],
                 extension_schema: pulumi.Input[str],
                 referer: pulumi.Input[str],
                 snow_password: pulumi.Input[str],
                 snow_user: pulumi.Input[str],
                 sync_options: pulumi.Input[str],
                 target: pulumi.Input[str],
                 task_type: pulumi.Input[str],
                 endpoint_url: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 summary: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ExtensionServiceNow resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] extension_objects: This is the objects for which the extension applies (An array of service ids).
        :param pulumi.Input[str] extension_schema: This is the schema for this extension.
        :param pulumi.Input[str] referer: The ServiceNow referer.
        :param pulumi.Input[str] snow_password: The ServiceNow password.
        :param pulumi.Input[str] snow_user: The ServiceNow username.
        :param pulumi.Input[str] sync_options: The ServiceNow sync option.
        :param pulumi.Input[str] target: Target Webhook URL.
        :param pulumi.Input[str] task_type: The ServiceNow task type, typically `incident`.
        :param pulumi.Input[str] name: The name of the service extension.
        :param pulumi.Input[str] summary: A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        """
        pulumi.set(__self__, "extension_objects", extension_objects)
        pulumi.set(__self__, "extension_schema", extension_schema)
        pulumi.set(__self__, "referer", referer)
        pulumi.set(__self__, "snow_password", snow_password)
        pulumi.set(__self__, "snow_user", snow_user)
        pulumi.set(__self__, "sync_options", sync_options)
        pulumi.set(__self__, "target", target)
        pulumi.set(__self__, "task_type", task_type)
        if endpoint_url is not None:
            pulumi.set(__self__, "endpoint_url", endpoint_url)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if summary is not None:
            pulumi.set(__self__, "summary", summary)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="extensionObjects")
    def extension_objects(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        This is the objects for which the extension applies (An array of service ids).
        """
        return pulumi.get(self, "extension_objects")

    @extension_objects.setter
    def extension_objects(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "extension_objects", value)

    @property
    @pulumi.getter(name="extensionSchema")
    def extension_schema(self) -> pulumi.Input[str]:
        """
        This is the schema for this extension.
        """
        return pulumi.get(self, "extension_schema")

    @extension_schema.setter
    def extension_schema(self, value: pulumi.Input[str]):
        pulumi.set(self, "extension_schema", value)

    @property
    @pulumi.getter
    def referer(self) -> pulumi.Input[str]:
        """
        The ServiceNow referer.
        """
        return pulumi.get(self, "referer")

    @referer.setter
    def referer(self, value: pulumi.Input[str]):
        pulumi.set(self, "referer", value)

    @property
    @pulumi.getter(name="snowPassword")
    def snow_password(self) -> pulumi.Input[str]:
        """
        The ServiceNow password.
        """
        return pulumi.get(self, "snow_password")

    @snow_password.setter
    def snow_password(self, value: pulumi.Input[str]):
        pulumi.set(self, "snow_password", value)

    @property
    @pulumi.getter(name="snowUser")
    def snow_user(self) -> pulumi.Input[str]:
        """
        The ServiceNow username.
        """
        return pulumi.get(self, "snow_user")

    @snow_user.setter
    def snow_user(self, value: pulumi.Input[str]):
        pulumi.set(self, "snow_user", value)

    @property
    @pulumi.getter(name="syncOptions")
    def sync_options(self) -> pulumi.Input[str]:
        """
        The ServiceNow sync option.
        """
        return pulumi.get(self, "sync_options")

    @sync_options.setter
    def sync_options(self, value: pulumi.Input[str]):
        pulumi.set(self, "sync_options", value)

    @property
    @pulumi.getter
    def target(self) -> pulumi.Input[str]:
        """
        Target Webhook URL.
        """
        return pulumi.get(self, "target")

    @target.setter
    def target(self, value: pulumi.Input[str]):
        pulumi.set(self, "target", value)

    @property
    @pulumi.getter(name="taskType")
    def task_type(self) -> pulumi.Input[str]:
        """
        The ServiceNow task type, typically `incident`.
        """
        return pulumi.get(self, "task_type")

    @task_type.setter
    def task_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "task_type", value)

    @property
    @pulumi.getter(name="endpointUrl")
    def endpoint_url(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "endpoint_url")

    @endpoint_url.setter
    def endpoint_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "endpoint_url", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the service extension.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def summary(self) -> Optional[pulumi.Input[str]]:
        """
        A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        """
        return pulumi.get(self, "summary")

    @summary.setter
    def summary(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "summary", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class _ExtensionServiceNowState:
    def __init__(__self__, *,
                 endpoint_url: Optional[pulumi.Input[str]] = None,
                 extension_objects: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 extension_schema: Optional[pulumi.Input[str]] = None,
                 html_url: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 referer: Optional[pulumi.Input[str]] = None,
                 snow_password: Optional[pulumi.Input[str]] = None,
                 snow_user: Optional[pulumi.Input[str]] = None,
                 summary: Optional[pulumi.Input[str]] = None,
                 sync_options: Optional[pulumi.Input[str]] = None,
                 target: Optional[pulumi.Input[str]] = None,
                 task_type: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ExtensionServiceNow resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] extension_objects: This is the objects for which the extension applies (An array of service ids).
        :param pulumi.Input[str] extension_schema: This is the schema for this extension.
        :param pulumi.Input[str] html_url: URL at which the entity is uniquely displayed in the Web app.
        :param pulumi.Input[str] name: The name of the service extension.
        :param pulumi.Input[str] referer: The ServiceNow referer.
        :param pulumi.Input[str] snow_password: The ServiceNow password.
        :param pulumi.Input[str] snow_user: The ServiceNow username.
        :param pulumi.Input[str] summary: A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        :param pulumi.Input[str] sync_options: The ServiceNow sync option.
        :param pulumi.Input[str] target: Target Webhook URL.
        :param pulumi.Input[str] task_type: The ServiceNow task type, typically `incident`.
        """
        if endpoint_url is not None:
            pulumi.set(__self__, "endpoint_url", endpoint_url)
        if extension_objects is not None:
            pulumi.set(__self__, "extension_objects", extension_objects)
        if extension_schema is not None:
            pulumi.set(__self__, "extension_schema", extension_schema)
        if html_url is not None:
            pulumi.set(__self__, "html_url", html_url)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if referer is not None:
            pulumi.set(__self__, "referer", referer)
        if snow_password is not None:
            pulumi.set(__self__, "snow_password", snow_password)
        if snow_user is not None:
            pulumi.set(__self__, "snow_user", snow_user)
        if summary is not None:
            pulumi.set(__self__, "summary", summary)
        if sync_options is not None:
            pulumi.set(__self__, "sync_options", sync_options)
        if target is not None:
            pulumi.set(__self__, "target", target)
        if task_type is not None:
            pulumi.set(__self__, "task_type", task_type)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="endpointUrl")
    def endpoint_url(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "endpoint_url")

    @endpoint_url.setter
    def endpoint_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "endpoint_url", value)

    @property
    @pulumi.getter(name="extensionObjects")
    def extension_objects(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        This is the objects for which the extension applies (An array of service ids).
        """
        return pulumi.get(self, "extension_objects")

    @extension_objects.setter
    def extension_objects(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "extension_objects", value)

    @property
    @pulumi.getter(name="extensionSchema")
    def extension_schema(self) -> Optional[pulumi.Input[str]]:
        """
        This is the schema for this extension.
        """
        return pulumi.get(self, "extension_schema")

    @extension_schema.setter
    def extension_schema(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "extension_schema", value)

    @property
    @pulumi.getter(name="htmlUrl")
    def html_url(self) -> Optional[pulumi.Input[str]]:
        """
        URL at which the entity is uniquely displayed in the Web app.
        """
        return pulumi.get(self, "html_url")

    @html_url.setter
    def html_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "html_url", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the service extension.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def referer(self) -> Optional[pulumi.Input[str]]:
        """
        The ServiceNow referer.
        """
        return pulumi.get(self, "referer")

    @referer.setter
    def referer(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "referer", value)

    @property
    @pulumi.getter(name="snowPassword")
    def snow_password(self) -> Optional[pulumi.Input[str]]:
        """
        The ServiceNow password.
        """
        return pulumi.get(self, "snow_password")

    @snow_password.setter
    def snow_password(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "snow_password", value)

    @property
    @pulumi.getter(name="snowUser")
    def snow_user(self) -> Optional[pulumi.Input[str]]:
        """
        The ServiceNow username.
        """
        return pulumi.get(self, "snow_user")

    @snow_user.setter
    def snow_user(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "snow_user", value)

    @property
    @pulumi.getter
    def summary(self) -> Optional[pulumi.Input[str]]:
        """
        A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        """
        return pulumi.get(self, "summary")

    @summary.setter
    def summary(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "summary", value)

    @property
    @pulumi.getter(name="syncOptions")
    def sync_options(self) -> Optional[pulumi.Input[str]]:
        """
        The ServiceNow sync option.
        """
        return pulumi.get(self, "sync_options")

    @sync_options.setter
    def sync_options(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "sync_options", value)

    @property
    @pulumi.getter
    def target(self) -> Optional[pulumi.Input[str]]:
        """
        Target Webhook URL.
        """
        return pulumi.get(self, "target")

    @target.setter
    def target(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "target", value)

    @property
    @pulumi.getter(name="taskType")
    def task_type(self) -> Optional[pulumi.Input[str]]:
        """
        The ServiceNow task type, typically `incident`.
        """
        return pulumi.get(self, "task_type")

    @task_type.setter
    def task_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "task_type", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


class ExtensionServiceNow(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_url: Optional[pulumi.Input[str]] = None,
                 extension_objects: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 extension_schema: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 referer: Optional[pulumi.Input[str]] = None,
                 snow_password: Optional[pulumi.Input[str]] = None,
                 snow_user: Optional[pulumi.Input[str]] = None,
                 summary: Optional[pulumi.Input[str]] = None,
                 sync_options: Optional[pulumi.Input[str]] = None,
                 target: Optional[pulumi.Input[str]] = None,
                 task_type: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        A special case for [extension](https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1extensions/post) for ServiceNow.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_pagerduty as pagerduty

        webhook = pagerduty.get_extension_schema(name="Generic V2 Webhook")
        example_user = pagerduty.User("exampleUser", email="howard.james@example.domain")
        example_escalation_policy = pagerduty.EscalationPolicy("exampleEscalationPolicy",
            num_loops=2,
            rules=[pagerduty.EscalationPolicyRuleArgs(
                escalation_delay_in_minutes=10,
                targets=[pagerduty.EscalationPolicyRuleTargetArgs(
                    type="user",
                    id=example_user.id,
                )],
            )])
        example_service = pagerduty.Service("exampleService",
            auto_resolve_timeout="14400",
            acknowledgement_timeout="600",
            escalation_policy=example_escalation_policy.id)
        snow = pagerduty.ExtensionServiceNow("snow",
            extension_schema=webhook.id,
            extension_objects=[example_service.id],
            snow_user="meeps",
            snow_password="zorz",
            sync_options="manual_sync",
            target="https://foo.servicenow.com/webhook_foo",
            task_type="incident",
            referer="None")
        ```

        ## Import

        Extensions can be imported using the id.e.g.

        ```sh
         $ pulumi import pagerduty:index/extensionServiceNow:ExtensionServiceNow main PLBP09X
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] extension_objects: This is the objects for which the extension applies (An array of service ids).
        :param pulumi.Input[str] extension_schema: This is the schema for this extension.
        :param pulumi.Input[str] name: The name of the service extension.
        :param pulumi.Input[str] referer: The ServiceNow referer.
        :param pulumi.Input[str] snow_password: The ServiceNow password.
        :param pulumi.Input[str] snow_user: The ServiceNow username.
        :param pulumi.Input[str] summary: A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        :param pulumi.Input[str] sync_options: The ServiceNow sync option.
        :param pulumi.Input[str] target: Target Webhook URL.
        :param pulumi.Input[str] task_type: The ServiceNow task type, typically `incident`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ExtensionServiceNowArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        A special case for [extension](https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1extensions/post) for ServiceNow.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_pagerduty as pagerduty

        webhook = pagerduty.get_extension_schema(name="Generic V2 Webhook")
        example_user = pagerduty.User("exampleUser", email="howard.james@example.domain")
        example_escalation_policy = pagerduty.EscalationPolicy("exampleEscalationPolicy",
            num_loops=2,
            rules=[pagerduty.EscalationPolicyRuleArgs(
                escalation_delay_in_minutes=10,
                targets=[pagerduty.EscalationPolicyRuleTargetArgs(
                    type="user",
                    id=example_user.id,
                )],
            )])
        example_service = pagerduty.Service("exampleService",
            auto_resolve_timeout="14400",
            acknowledgement_timeout="600",
            escalation_policy=example_escalation_policy.id)
        snow = pagerduty.ExtensionServiceNow("snow",
            extension_schema=webhook.id,
            extension_objects=[example_service.id],
            snow_user="meeps",
            snow_password="zorz",
            sync_options="manual_sync",
            target="https://foo.servicenow.com/webhook_foo",
            task_type="incident",
            referer="None")
        ```

        ## Import

        Extensions can be imported using the id.e.g.

        ```sh
         $ pulumi import pagerduty:index/extensionServiceNow:ExtensionServiceNow main PLBP09X
        ```

        :param str resource_name: The name of the resource.
        :param ExtensionServiceNowArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ExtensionServiceNowArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_url: Optional[pulumi.Input[str]] = None,
                 extension_objects: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 extension_schema: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 referer: Optional[pulumi.Input[str]] = None,
                 snow_password: Optional[pulumi.Input[str]] = None,
                 snow_user: Optional[pulumi.Input[str]] = None,
                 summary: Optional[pulumi.Input[str]] = None,
                 sync_options: Optional[pulumi.Input[str]] = None,
                 target: Optional[pulumi.Input[str]] = None,
                 task_type: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
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
            __props__ = ExtensionServiceNowArgs.__new__(ExtensionServiceNowArgs)

            __props__.__dict__["endpoint_url"] = endpoint_url
            if extension_objects is None and not opts.urn:
                raise TypeError("Missing required property 'extension_objects'")
            __props__.__dict__["extension_objects"] = extension_objects
            if extension_schema is None and not opts.urn:
                raise TypeError("Missing required property 'extension_schema'")
            __props__.__dict__["extension_schema"] = extension_schema
            __props__.__dict__["name"] = name
            if referer is None and not opts.urn:
                raise TypeError("Missing required property 'referer'")
            __props__.__dict__["referer"] = referer
            if snow_password is None and not opts.urn:
                raise TypeError("Missing required property 'snow_password'")
            __props__.__dict__["snow_password"] = snow_password
            if snow_user is None and not opts.urn:
                raise TypeError("Missing required property 'snow_user'")
            __props__.__dict__["snow_user"] = snow_user
            __props__.__dict__["summary"] = summary
            if sync_options is None and not opts.urn:
                raise TypeError("Missing required property 'sync_options'")
            __props__.__dict__["sync_options"] = sync_options
            if target is None and not opts.urn:
                raise TypeError("Missing required property 'target'")
            __props__.__dict__["target"] = target
            if task_type is None and not opts.urn:
                raise TypeError("Missing required property 'task_type'")
            __props__.__dict__["task_type"] = task_type
            __props__.__dict__["type"] = type
            __props__.__dict__["html_url"] = None
        super(ExtensionServiceNow, __self__).__init__(
            'pagerduty:index/extensionServiceNow:ExtensionServiceNow',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            endpoint_url: Optional[pulumi.Input[str]] = None,
            extension_objects: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            extension_schema: Optional[pulumi.Input[str]] = None,
            html_url: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            referer: Optional[pulumi.Input[str]] = None,
            snow_password: Optional[pulumi.Input[str]] = None,
            snow_user: Optional[pulumi.Input[str]] = None,
            summary: Optional[pulumi.Input[str]] = None,
            sync_options: Optional[pulumi.Input[str]] = None,
            target: Optional[pulumi.Input[str]] = None,
            task_type: Optional[pulumi.Input[str]] = None,
            type: Optional[pulumi.Input[str]] = None) -> 'ExtensionServiceNow':
        """
        Get an existing ExtensionServiceNow resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] extension_objects: This is the objects for which the extension applies (An array of service ids).
        :param pulumi.Input[str] extension_schema: This is the schema for this extension.
        :param pulumi.Input[str] html_url: URL at which the entity is uniquely displayed in the Web app.
        :param pulumi.Input[str] name: The name of the service extension.
        :param pulumi.Input[str] referer: The ServiceNow referer.
        :param pulumi.Input[str] snow_password: The ServiceNow password.
        :param pulumi.Input[str] snow_user: The ServiceNow username.
        :param pulumi.Input[str] summary: A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        :param pulumi.Input[str] sync_options: The ServiceNow sync option.
        :param pulumi.Input[str] target: Target Webhook URL.
        :param pulumi.Input[str] task_type: The ServiceNow task type, typically `incident`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ExtensionServiceNowState.__new__(_ExtensionServiceNowState)

        __props__.__dict__["endpoint_url"] = endpoint_url
        __props__.__dict__["extension_objects"] = extension_objects
        __props__.__dict__["extension_schema"] = extension_schema
        __props__.__dict__["html_url"] = html_url
        __props__.__dict__["name"] = name
        __props__.__dict__["referer"] = referer
        __props__.__dict__["snow_password"] = snow_password
        __props__.__dict__["snow_user"] = snow_user
        __props__.__dict__["summary"] = summary
        __props__.__dict__["sync_options"] = sync_options
        __props__.__dict__["target"] = target
        __props__.__dict__["task_type"] = task_type
        __props__.__dict__["type"] = type
        return ExtensionServiceNow(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="endpointUrl")
    def endpoint_url(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "endpoint_url")

    @property
    @pulumi.getter(name="extensionObjects")
    def extension_objects(self) -> pulumi.Output[Sequence[str]]:
        """
        This is the objects for which the extension applies (An array of service ids).
        """
        return pulumi.get(self, "extension_objects")

    @property
    @pulumi.getter(name="extensionSchema")
    def extension_schema(self) -> pulumi.Output[str]:
        """
        This is the schema for this extension.
        """
        return pulumi.get(self, "extension_schema")

    @property
    @pulumi.getter(name="htmlUrl")
    def html_url(self) -> pulumi.Output[str]:
        """
        URL at which the entity is uniquely displayed in the Web app.
        """
        return pulumi.get(self, "html_url")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the service extension.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def referer(self) -> pulumi.Output[str]:
        """
        The ServiceNow referer.
        """
        return pulumi.get(self, "referer")

    @property
    @pulumi.getter(name="snowPassword")
    def snow_password(self) -> pulumi.Output[str]:
        """
        The ServiceNow password.
        """
        return pulumi.get(self, "snow_password")

    @property
    @pulumi.getter(name="snowUser")
    def snow_user(self) -> pulumi.Output[str]:
        """
        The ServiceNow username.
        """
        return pulumi.get(self, "snow_user")

    @property
    @pulumi.getter
    def summary(self) -> pulumi.Output[str]:
        """
        A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.
        """
        return pulumi.get(self, "summary")

    @property
    @pulumi.getter(name="syncOptions")
    def sync_options(self) -> pulumi.Output[str]:
        """
        The ServiceNow sync option.
        """
        return pulumi.get(self, "sync_options")

    @property
    @pulumi.getter
    def target(self) -> pulumi.Output[str]:
        """
        Target Webhook URL.
        """
        return pulumi.get(self, "target")

    @property
    @pulumi.getter(name="taskType")
    def task_type(self) -> pulumi.Output[str]:
        """
        The ServiceNow task type, typically `incident`.
        """
        return pulumi.get(self, "task_type")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[str]:
        return pulumi.get(self, "type")

