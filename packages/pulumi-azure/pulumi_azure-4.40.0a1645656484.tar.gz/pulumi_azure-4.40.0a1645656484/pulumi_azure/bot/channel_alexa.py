# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ChannelAlexaArgs', 'ChannelAlexa']

@pulumi.input_type
class ChannelAlexaArgs:
    def __init__(__self__, *,
                 bot_name: pulumi.Input[str],
                 resource_group_name: pulumi.Input[str],
                 skill_id: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ChannelAlexa resource.
        :param pulumi.Input[str] bot_name: The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] skill_id: The Alexa skill ID for the Alexa Channel.
        :param pulumi.Input[str] location: The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        pulumi.set(__self__, "bot_name", bot_name)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "skill_id", skill_id)
        if location is not None:
            pulumi.set(__self__, "location", location)

    @property
    @pulumi.getter(name="botName")
    def bot_name(self) -> pulumi.Input[str]:
        """
        The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "bot_name")

    @bot_name.setter
    def bot_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "bot_name", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skillId")
    def skill_id(self) -> pulumi.Input[str]:
        """
        The Alexa skill ID for the Alexa Channel.
        """
        return pulumi.get(self, "skill_id")

    @skill_id.setter
    def skill_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "skill_id", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)


@pulumi.input_type
class _ChannelAlexaState:
    def __init__(__self__, *,
                 bot_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 skill_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ChannelAlexa resources.
        :param pulumi.Input[str] bot_name: The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] skill_id: The Alexa skill ID for the Alexa Channel.
        """
        if bot_name is not None:
            pulumi.set(__self__, "bot_name", bot_name)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if skill_id is not None:
            pulumi.set(__self__, "skill_id", skill_id)

    @property
    @pulumi.getter(name="botName")
    def bot_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "bot_name")

    @bot_name.setter
    def bot_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bot_name", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skillId")
    def skill_id(self) -> Optional[pulumi.Input[str]]:
        """
        The Alexa skill ID for the Alexa Channel.
        """
        return pulumi.get(self, "skill_id")

    @skill_id.setter
    def skill_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "skill_id", value)


class ChannelAlexa(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bot_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 skill_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages an Alexa integration for a Bot Channel

        > **Note** A bot can only have a single Alexa Channel associated with it.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_channels_registration = azure.bot.ChannelsRegistration("exampleChannelsRegistration",
            location="global",
            resource_group_name=example_resource_group.name,
            sku="F0",
            microsoft_app_id=current.client_id)
        example_channel_alexa = azure.bot.ChannelAlexa("exampleChannelAlexa",
            bot_name=example_channels_registration.name,
            location=example_channels_registration.location,
            resource_group_name=example_resource_group.name,
            skill_id="amzn1.ask.skill.00000000-0000-0000-0000-000000000000")
        ```

        ## Import

        The Alexa Integration for a Bot Channel can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:bot/channelAlexa:ChannelAlexa example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.BotService/botServices/botService1/channels/AlexaChannel
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bot_name: The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] skill_id: The Alexa skill ID for the Alexa Channel.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ChannelAlexaArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an Alexa integration for a Bot Channel

        > **Note** A bot can only have a single Alexa Channel associated with it.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_channels_registration = azure.bot.ChannelsRegistration("exampleChannelsRegistration",
            location="global",
            resource_group_name=example_resource_group.name,
            sku="F0",
            microsoft_app_id=current.client_id)
        example_channel_alexa = azure.bot.ChannelAlexa("exampleChannelAlexa",
            bot_name=example_channels_registration.name,
            location=example_channels_registration.location,
            resource_group_name=example_resource_group.name,
            skill_id="amzn1.ask.skill.00000000-0000-0000-0000-000000000000")
        ```

        ## Import

        The Alexa Integration for a Bot Channel can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:bot/channelAlexa:ChannelAlexa example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/group1/providers/Microsoft.BotService/botServices/botService1/channels/AlexaChannel
        ```

        :param str resource_name: The name of the resource.
        :param ChannelAlexaArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ChannelAlexaArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bot_name: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 skill_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ChannelAlexaArgs.__new__(ChannelAlexaArgs)

            if bot_name is None and not opts.urn:
                raise TypeError("Missing required property 'bot_name'")
            __props__.__dict__["bot_name"] = bot_name
            __props__.__dict__["location"] = location
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if skill_id is None and not opts.urn:
                raise TypeError("Missing required property 'skill_id'")
            __props__.__dict__["skill_id"] = skill_id
        super(ChannelAlexa, __self__).__init__(
            'azure:bot/channelAlexa:ChannelAlexa',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            bot_name: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            skill_id: Optional[pulumi.Input[str]] = None) -> 'ChannelAlexa':
        """
        Get an existing ChannelAlexa resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bot_name: The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        :param pulumi.Input[str] skill_id: The Alexa skill ID for the Alexa Channel.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ChannelAlexaState.__new__(_ChannelAlexaState)

        __props__.__dict__["bot_name"] = bot_name
        __props__.__dict__["location"] = location
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["skill_id"] = skill_id
        return ChannelAlexa(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="botName")
    def bot_name(self) -> pulumi.Output[str]:
        """
        The name of the Bot Resource this channel will be associated with. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "bot_name")

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        The supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group where the Alexa Channel should be created. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="skillId")
    def skill_id(self) -> pulumi.Output[str]:
        """
        The Alexa skill ID for the Alexa Channel.
        """
        return pulumi.get(self, "skill_id")

