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

__all__ = ['ResponsePlayArgs', 'ResponsePlay']

@pulumi.input_type
class ResponsePlayArgs:
    def __init__(__self__, *,
                 from_: pulumi.Input[str],
                 conference_number: Optional[pulumi.Input[str]] = None,
                 conference_url: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 responders: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]] = None,
                 responders_message: Optional[pulumi.Input[str]] = None,
                 runnability: Optional[pulumi.Input[str]] = None,
                 subscribers: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]] = None,
                 subscribers_message: Optional[pulumi.Input[str]] = None,
                 team: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ResponsePlay resource.
        :param pulumi.Input[str] from_: The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        :param pulumi.Input[str] conference_number: The telephone number that will be set as the conference number for any incident on which this response play is run.
        :param pulumi.Input[str] conference_url: The URL that will be set as the conference URL for any incident on which this response play is run.
        :param pulumi.Input[str] name: The name of the response play.
        :param pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]] responders: A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        :param pulumi.Input[str] responders_message: The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        :param pulumi.Input[str] runnability: String representing how this response play is allowed to be run. Valid options are:
        :param pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]] subscribers: A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        :param pulumi.Input[str] subscribers_message: The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        :param pulumi.Input[str] team: The ID of the team associated with the response play.
        :param pulumi.Input[str] type: A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        pulumi.set(__self__, "from_", from_)
        if conference_number is not None:
            pulumi.set(__self__, "conference_number", conference_number)
        if conference_url is not None:
            pulumi.set(__self__, "conference_url", conference_url)
        if description is None:
            description = 'Managed by Pulumi'
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if responders is not None:
            pulumi.set(__self__, "responders", responders)
        if responders_message is not None:
            pulumi.set(__self__, "responders_message", responders_message)
        if runnability is not None:
            pulumi.set(__self__, "runnability", runnability)
        if subscribers is not None:
            pulumi.set(__self__, "subscribers", subscribers)
        if subscribers_message is not None:
            pulumi.set(__self__, "subscribers_message", subscribers_message)
        if team is not None:
            pulumi.set(__self__, "team", team)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="from")
    def from_(self) -> pulumi.Input[str]:
        """
        The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        """
        return pulumi.get(self, "from_")

    @from_.setter
    def from_(self, value: pulumi.Input[str]):
        pulumi.set(self, "from_", value)

    @property
    @pulumi.getter(name="conferenceNumber")
    def conference_number(self) -> Optional[pulumi.Input[str]]:
        """
        The telephone number that will be set as the conference number for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_number")

    @conference_number.setter
    def conference_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "conference_number", value)

    @property
    @pulumi.getter(name="conferenceUrl")
    def conference_url(self) -> Optional[pulumi.Input[str]]:
        """
        The URL that will be set as the conference URL for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_url")

    @conference_url.setter
    def conference_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "conference_url", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the response play.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def responders(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]]:
        """
        A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        """
        return pulumi.get(self, "responders")

    @responders.setter
    def responders(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]]):
        pulumi.set(self, "responders", value)

    @property
    @pulumi.getter(name="respondersMessage")
    def responders_message(self) -> Optional[pulumi.Input[str]]:
        """
        The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        """
        return pulumi.get(self, "responders_message")

    @responders_message.setter
    def responders_message(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "responders_message", value)

    @property
    @pulumi.getter
    def runnability(self) -> Optional[pulumi.Input[str]]:
        """
        String representing how this response play is allowed to be run. Valid options are:
        """
        return pulumi.get(self, "runnability")

    @runnability.setter
    def runnability(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "runnability", value)

    @property
    @pulumi.getter
    def subscribers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]]:
        """
        A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        """
        return pulumi.get(self, "subscribers")

    @subscribers.setter
    def subscribers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]]):
        pulumi.set(self, "subscribers", value)

    @property
    @pulumi.getter(name="subscribersMessage")
    def subscribers_message(self) -> Optional[pulumi.Input[str]]:
        """
        The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        """
        return pulumi.get(self, "subscribers_message")

    @subscribers_message.setter
    def subscribers_message(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subscribers_message", value)

    @property
    @pulumi.getter
    def team(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the team associated with the response play.
        """
        return pulumi.get(self, "team")

    @team.setter
    def team(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "team", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class _ResponsePlayState:
    def __init__(__self__, *,
                 conference_number: Optional[pulumi.Input[str]] = None,
                 conference_url: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 from_: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 responders: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]] = None,
                 responders_message: Optional[pulumi.Input[str]] = None,
                 runnability: Optional[pulumi.Input[str]] = None,
                 subscribers: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]] = None,
                 subscribers_message: Optional[pulumi.Input[str]] = None,
                 team: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ResponsePlay resources.
        :param pulumi.Input[str] conference_number: The telephone number that will be set as the conference number for any incident on which this response play is run.
        :param pulumi.Input[str] conference_url: The URL that will be set as the conference URL for any incident on which this response play is run.
        :param pulumi.Input[str] from_: The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        :param pulumi.Input[str] name: The name of the response play.
        :param pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]] responders: A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        :param pulumi.Input[str] responders_message: The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        :param pulumi.Input[str] runnability: String representing how this response play is allowed to be run. Valid options are:
        :param pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]] subscribers: A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        :param pulumi.Input[str] subscribers_message: The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        :param pulumi.Input[str] team: The ID of the team associated with the response play.
        :param pulumi.Input[str] type: A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        if conference_number is not None:
            pulumi.set(__self__, "conference_number", conference_number)
        if conference_url is not None:
            pulumi.set(__self__, "conference_url", conference_url)
        if description is None:
            description = 'Managed by Pulumi'
        if description is not None:
            pulumi.set(__self__, "description", description)
        if from_ is not None:
            pulumi.set(__self__, "from_", from_)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if responders is not None:
            pulumi.set(__self__, "responders", responders)
        if responders_message is not None:
            pulumi.set(__self__, "responders_message", responders_message)
        if runnability is not None:
            pulumi.set(__self__, "runnability", runnability)
        if subscribers is not None:
            pulumi.set(__self__, "subscribers", subscribers)
        if subscribers_message is not None:
            pulumi.set(__self__, "subscribers_message", subscribers_message)
        if team is not None:
            pulumi.set(__self__, "team", team)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="conferenceNumber")
    def conference_number(self) -> Optional[pulumi.Input[str]]:
        """
        The telephone number that will be set as the conference number for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_number")

    @conference_number.setter
    def conference_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "conference_number", value)

    @property
    @pulumi.getter(name="conferenceUrl")
    def conference_url(self) -> Optional[pulumi.Input[str]]:
        """
        The URL that will be set as the conference URL for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_url")

    @conference_url.setter
    def conference_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "conference_url", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="from")
    def from_(self) -> Optional[pulumi.Input[str]]:
        """
        The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        """
        return pulumi.get(self, "from_")

    @from_.setter
    def from_(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "from_", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the response play.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def responders(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]]:
        """
        A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        """
        return pulumi.get(self, "responders")

    @responders.setter
    def responders(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlayResponderArgs']]]]):
        pulumi.set(self, "responders", value)

    @property
    @pulumi.getter(name="respondersMessage")
    def responders_message(self) -> Optional[pulumi.Input[str]]:
        """
        The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        """
        return pulumi.get(self, "responders_message")

    @responders_message.setter
    def responders_message(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "responders_message", value)

    @property
    @pulumi.getter
    def runnability(self) -> Optional[pulumi.Input[str]]:
        """
        String representing how this response play is allowed to be run. Valid options are:
        """
        return pulumi.get(self, "runnability")

    @runnability.setter
    def runnability(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "runnability", value)

    @property
    @pulumi.getter
    def subscribers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]]:
        """
        A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        """
        return pulumi.get(self, "subscribers")

    @subscribers.setter
    def subscribers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ResponsePlaySubscriberArgs']]]]):
        pulumi.set(self, "subscribers", value)

    @property
    @pulumi.getter(name="subscribersMessage")
    def subscribers_message(self) -> Optional[pulumi.Input[str]]:
        """
        The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        """
        return pulumi.get(self, "subscribers_message")

    @subscribers_message.setter
    def subscribers_message(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subscribers_message", value)

    @property
    @pulumi.getter
    def team(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the team associated with the response play.
        """
        return pulumi.get(self, "team")

    @team.setter
    def team(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "team", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


class ResponsePlay(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 conference_number: Optional[pulumi.Input[str]] = None,
                 conference_url: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 from_: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 responders: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlayResponderArgs']]]]] = None,
                 responders_message: Optional[pulumi.Input[str]] = None,
                 runnability: Optional[pulumi.Input[str]] = None,
                 subscribers: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlaySubscriberArgs']]]]] = None,
                 subscribers_message: Optional[pulumi.Input[str]] = None,
                 team: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        A [response play](https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1response_plays/get) allows you to create packages of Incident Actions that can be applied during an Incident's life cycle.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_pagerduty as pagerduty

        example_user = pagerduty.User("exampleUser",
            email="125.greenholt.earline@graham.name",
            teams=[pagerduty_team["example"]["id"]])
        example_escalation_policy = pagerduty.EscalationPolicy("exampleEscalationPolicy",
            num_loops=2,
            rules=[pagerduty.EscalationPolicyRuleArgs(
                escalation_delay_in_minutes=10,
                targets=[pagerduty.EscalationPolicyRuleTargetArgs(
                    type="user",
                    id=example_user.id,
                )],
            )])
        example_response_play = pagerduty.ResponsePlay("exampleResponsePlay",
            from_=example_user.email,
            responders=[pagerduty.ResponsePlayResponderArgs(
                type="escalation_policy_reference",
                id=example_escalation_policy.id,
            )],
            subscribers=[pagerduty.ResponsePlaySubscriberArgs(
                type="user_reference",
                id=example_user.id,
            )],
            runnability="services")
        ```

        ## Import

        Response Plays can be imported using the `id.from(email)`, e.g.

        ```sh
         $ pulumi import pagerduty:index/responsePlay:ResponsePlay main 16208303-022b-f745-f2f5-560e537a2a74.user@email.com
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] conference_number: The telephone number that will be set as the conference number for any incident on which this response play is run.
        :param pulumi.Input[str] conference_url: The URL that will be set as the conference URL for any incident on which this response play is run.
        :param pulumi.Input[str] from_: The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        :param pulumi.Input[str] name: The name of the response play.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlayResponderArgs']]]] responders: A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        :param pulumi.Input[str] responders_message: The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        :param pulumi.Input[str] runnability: String representing how this response play is allowed to be run. Valid options are:
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlaySubscriberArgs']]]] subscribers: A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        :param pulumi.Input[str] subscribers_message: The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        :param pulumi.Input[str] team: The ID of the team associated with the response play.
        :param pulumi.Input[str] type: A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ResponsePlayArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        A [response play](https://developer.pagerduty.com/api-reference/reference/REST/openapiv3.json/paths/~1response_plays/get) allows you to create packages of Incident Actions that can be applied during an Incident's life cycle.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_pagerduty as pagerduty

        example_user = pagerduty.User("exampleUser",
            email="125.greenholt.earline@graham.name",
            teams=[pagerduty_team["example"]["id"]])
        example_escalation_policy = pagerduty.EscalationPolicy("exampleEscalationPolicy",
            num_loops=2,
            rules=[pagerduty.EscalationPolicyRuleArgs(
                escalation_delay_in_minutes=10,
                targets=[pagerduty.EscalationPolicyRuleTargetArgs(
                    type="user",
                    id=example_user.id,
                )],
            )])
        example_response_play = pagerduty.ResponsePlay("exampleResponsePlay",
            from_=example_user.email,
            responders=[pagerduty.ResponsePlayResponderArgs(
                type="escalation_policy_reference",
                id=example_escalation_policy.id,
            )],
            subscribers=[pagerduty.ResponsePlaySubscriberArgs(
                type="user_reference",
                id=example_user.id,
            )],
            runnability="services")
        ```

        ## Import

        Response Plays can be imported using the `id.from(email)`, e.g.

        ```sh
         $ pulumi import pagerduty:index/responsePlay:ResponsePlay main 16208303-022b-f745-f2f5-560e537a2a74.user@email.com
        ```

        :param str resource_name: The name of the resource.
        :param ResponsePlayArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ResponsePlayArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 conference_number: Optional[pulumi.Input[str]] = None,
                 conference_url: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 from_: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 responders: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlayResponderArgs']]]]] = None,
                 responders_message: Optional[pulumi.Input[str]] = None,
                 runnability: Optional[pulumi.Input[str]] = None,
                 subscribers: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlaySubscriberArgs']]]]] = None,
                 subscribers_message: Optional[pulumi.Input[str]] = None,
                 team: Optional[pulumi.Input[str]] = None,
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
            __props__ = ResponsePlayArgs.__new__(ResponsePlayArgs)

            __props__.__dict__["conference_number"] = conference_number
            __props__.__dict__["conference_url"] = conference_url
            if description is None:
                description = 'Managed by Pulumi'
            __props__.__dict__["description"] = description
            if from_ is None and not opts.urn:
                raise TypeError("Missing required property 'from_'")
            __props__.__dict__["from_"] = from_
            __props__.__dict__["name"] = name
            __props__.__dict__["responders"] = responders
            __props__.__dict__["responders_message"] = responders_message
            __props__.__dict__["runnability"] = runnability
            __props__.__dict__["subscribers"] = subscribers
            __props__.__dict__["subscribers_message"] = subscribers_message
            __props__.__dict__["team"] = team
            __props__.__dict__["type"] = type
        super(ResponsePlay, __self__).__init__(
            'pagerduty:index/responsePlay:ResponsePlay',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            conference_number: Optional[pulumi.Input[str]] = None,
            conference_url: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            from_: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            responders: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlayResponderArgs']]]]] = None,
            responders_message: Optional[pulumi.Input[str]] = None,
            runnability: Optional[pulumi.Input[str]] = None,
            subscribers: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlaySubscriberArgs']]]]] = None,
            subscribers_message: Optional[pulumi.Input[str]] = None,
            team: Optional[pulumi.Input[str]] = None,
            type: Optional[pulumi.Input[str]] = None) -> 'ResponsePlay':
        """
        Get an existing ResponsePlay resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] conference_number: The telephone number that will be set as the conference number for any incident on which this response play is run.
        :param pulumi.Input[str] conference_url: The URL that will be set as the conference URL for any incident on which this response play is run.
        :param pulumi.Input[str] from_: The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        :param pulumi.Input[str] name: The name of the response play.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlayResponderArgs']]]] responders: A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        :param pulumi.Input[str] responders_message: The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        :param pulumi.Input[str] runnability: String representing how this response play is allowed to be run. Valid options are:
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ResponsePlaySubscriberArgs']]]] subscribers: A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        :param pulumi.Input[str] subscribers_message: The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        :param pulumi.Input[str] team: The ID of the team associated with the response play.
        :param pulumi.Input[str] type: A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ResponsePlayState.__new__(_ResponsePlayState)

        __props__.__dict__["conference_number"] = conference_number
        __props__.__dict__["conference_url"] = conference_url
        __props__.__dict__["description"] = description
        __props__.__dict__["from_"] = from_
        __props__.__dict__["name"] = name
        __props__.__dict__["responders"] = responders
        __props__.__dict__["responders_message"] = responders_message
        __props__.__dict__["runnability"] = runnability
        __props__.__dict__["subscribers"] = subscribers
        __props__.__dict__["subscribers_message"] = subscribers_message
        __props__.__dict__["team"] = team
        __props__.__dict__["type"] = type
        return ResponsePlay(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="conferenceNumber")
    def conference_number(self) -> pulumi.Output[Optional[str]]:
        """
        The telephone number that will be set as the conference number for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_number")

    @property
    @pulumi.getter(name="conferenceUrl")
    def conference_url(self) -> pulumi.Output[Optional[str]]:
        """
        The URL that will be set as the conference URL for any incident on which this response play is run.
        """
        return pulumi.get(self, "conference_url")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="from")
    def from_(self) -> pulumi.Output[str]:
        """
        The email of the user attributed to the request. Needs to be a valid email address of a user in the PagerDuty account.
        """
        return pulumi.get(self, "from_")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the response play.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def responders(self) -> pulumi.Output[Optional[Sequence['outputs.ResponsePlayResponder']]]:
        """
        A user and/or escalation policy to be requested as a responder to any incident on which this response play is run. There can be multiple responders defined on a single response play.
        """
        return pulumi.get(self, "responders")

    @property
    @pulumi.getter(name="respondersMessage")
    def responders_message(self) -> pulumi.Output[Optional[str]]:
        """
        The message body of the notification that will be sent to this response play's set of responders. If empty, a default response request notification will be sent.
        """
        return pulumi.get(self, "responders_message")

    @property
    @pulumi.getter
    def runnability(self) -> pulumi.Output[Optional[str]]:
        """
        String representing how this response play is allowed to be run. Valid options are:
        """
        return pulumi.get(self, "runnability")

    @property
    @pulumi.getter
    def subscribers(self) -> pulumi.Output[Optional[Sequence['outputs.ResponsePlaySubscriber']]]:
        """
        A user and/or team to be added as a subscriber to any incident on which this response play is run. There can be multiple subscribers defined on a single response play.
        """
        return pulumi.get(self, "subscribers")

    @property
    @pulumi.getter(name="subscribersMessage")
    def subscribers_message(self) -> pulumi.Output[Optional[str]]:
        """
        The content of the notification that will be sent to all incident subscribers upon the running of this response play. Note that this includes any users who may have already been subscribed to the incident prior to the running of this response play. If empty, no notifications will be sent.
        """
        return pulumi.get(self, "subscribers_message")

    @property
    @pulumi.getter
    def team(self) -> pulumi.Output[Optional[str]]:
        """
        The ID of the team associated with the response play.
        """
        return pulumi.get(self, "team")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[Optional[str]]:
        """
        A string that determines the schema of the object. If not set, the default value is "response_play".
        """
        return pulumi.get(self, "type")

