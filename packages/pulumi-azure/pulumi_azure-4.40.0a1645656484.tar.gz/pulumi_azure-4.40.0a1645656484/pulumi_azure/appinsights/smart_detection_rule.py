# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['SmartDetectionRuleArgs', 'SmartDetectionRule']

@pulumi.input_type
class SmartDetectionRuleArgs:
    def __init__(__self__, *,
                 application_insights_id: pulumi.Input[str],
                 additional_email_recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 send_emails_to_subscription_owners: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a SmartDetectionRule resource.
        :param pulumi.Input[str] application_insights_id: The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] additional_email_recipients: Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        :param pulumi.Input[bool] enabled: Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        :param pulumi.Input[str] name: Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
               `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
               `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        :param pulumi.Input[bool] send_emails_to_subscription_owners: Do emails get sent to subscription owners? Defaults to `true`.
        """
        pulumi.set(__self__, "application_insights_id", application_insights_id)
        if additional_email_recipients is not None:
            pulumi.set(__self__, "additional_email_recipients", additional_email_recipients)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if send_emails_to_subscription_owners is not None:
            pulumi.set(__self__, "send_emails_to_subscription_owners", send_emails_to_subscription_owners)

    @property
    @pulumi.getter(name="applicationInsightsId")
    def application_insights_id(self) -> pulumi.Input[str]:
        """
        The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "application_insights_id")

    @application_insights_id.setter
    def application_insights_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "application_insights_id", value)

    @property
    @pulumi.getter(name="additionalEmailRecipients")
    def additional_email_recipients(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        """
        return pulumi.get(self, "additional_email_recipients")

    @additional_email_recipients.setter
    def additional_email_recipients(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "additional_email_recipients", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
        `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
        `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="sendEmailsToSubscriptionOwners")
    def send_emails_to_subscription_owners(self) -> Optional[pulumi.Input[bool]]:
        """
        Do emails get sent to subscription owners? Defaults to `true`.
        """
        return pulumi.get(self, "send_emails_to_subscription_owners")

    @send_emails_to_subscription_owners.setter
    def send_emails_to_subscription_owners(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "send_emails_to_subscription_owners", value)


@pulumi.input_type
class _SmartDetectionRuleState:
    def __init__(__self__, *,
                 additional_email_recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 application_insights_id: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 send_emails_to_subscription_owners: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering SmartDetectionRule resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] additional_email_recipients: Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        :param pulumi.Input[str] application_insights_id: The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] enabled: Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        :param pulumi.Input[str] name: Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
               `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
               `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        :param pulumi.Input[bool] send_emails_to_subscription_owners: Do emails get sent to subscription owners? Defaults to `true`.
        """
        if additional_email_recipients is not None:
            pulumi.set(__self__, "additional_email_recipients", additional_email_recipients)
        if application_insights_id is not None:
            pulumi.set(__self__, "application_insights_id", application_insights_id)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if send_emails_to_subscription_owners is not None:
            pulumi.set(__self__, "send_emails_to_subscription_owners", send_emails_to_subscription_owners)

    @property
    @pulumi.getter(name="additionalEmailRecipients")
    def additional_email_recipients(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        """
        return pulumi.get(self, "additional_email_recipients")

    @additional_email_recipients.setter
    def additional_email_recipients(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "additional_email_recipients", value)

    @property
    @pulumi.getter(name="applicationInsightsId")
    def application_insights_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "application_insights_id")

    @application_insights_id.setter
    def application_insights_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "application_insights_id", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
        `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
        `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="sendEmailsToSubscriptionOwners")
    def send_emails_to_subscription_owners(self) -> Optional[pulumi.Input[bool]]:
        """
        Do emails get sent to subscription owners? Defaults to `true`.
        """
        return pulumi.get(self, "send_emails_to_subscription_owners")

    @send_emails_to_subscription_owners.setter
    def send_emails_to_subscription_owners(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "send_emails_to_subscription_owners", value)


class SmartDetectionRule(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 additional_email_recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 application_insights_id: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 send_emails_to_subscription_owners: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        Manages an Application Insights Smart Detection Rule.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_insights = azure.appinsights.Insights("exampleInsights",
            location="West Europe",
            resource_group_name=example_resource_group.name,
            application_type="web")
        example_smart_detection_rule = azure.appinsights.SmartDetectionRule("exampleSmartDetectionRule",
            application_insights_id=example_insights.id,
            enabled=False)
        ```

        ## Import

        Application Insights Smart Detection Rules can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appinsights/smartDetectionRule:SmartDetectionRule rule1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Insights/components/mycomponent1/smartDetectionRule/myrule1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] additional_email_recipients: Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        :param pulumi.Input[str] application_insights_id: The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] enabled: Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        :param pulumi.Input[str] name: Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
               `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
               `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        :param pulumi.Input[bool] send_emails_to_subscription_owners: Do emails get sent to subscription owners? Defaults to `true`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SmartDetectionRuleArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an Application Insights Smart Detection Rule.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_insights = azure.appinsights.Insights("exampleInsights",
            location="West Europe",
            resource_group_name=example_resource_group.name,
            application_type="web")
        example_smart_detection_rule = azure.appinsights.SmartDetectionRule("exampleSmartDetectionRule",
            application_insights_id=example_insights.id,
            enabled=False)
        ```

        ## Import

        Application Insights Smart Detection Rules can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:appinsights/smartDetectionRule:SmartDetectionRule rule1 /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Insights/components/mycomponent1/smartDetectionRule/myrule1
        ```

        :param str resource_name: The name of the resource.
        :param SmartDetectionRuleArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SmartDetectionRuleArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 additional_email_recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 application_insights_id: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 send_emails_to_subscription_owners: Optional[pulumi.Input[bool]] = None,
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
            __props__ = SmartDetectionRuleArgs.__new__(SmartDetectionRuleArgs)

            __props__.__dict__["additional_email_recipients"] = additional_email_recipients
            if application_insights_id is None and not opts.urn:
                raise TypeError("Missing required property 'application_insights_id'")
            __props__.__dict__["application_insights_id"] = application_insights_id
            __props__.__dict__["enabled"] = enabled
            __props__.__dict__["name"] = name
            __props__.__dict__["send_emails_to_subscription_owners"] = send_emails_to_subscription_owners
        super(SmartDetectionRule, __self__).__init__(
            'azure:appinsights/smartDetectionRule:SmartDetectionRule',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            additional_email_recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            application_insights_id: Optional[pulumi.Input[str]] = None,
            enabled: Optional[pulumi.Input[bool]] = None,
            name: Optional[pulumi.Input[str]] = None,
            send_emails_to_subscription_owners: Optional[pulumi.Input[bool]] = None) -> 'SmartDetectionRule':
        """
        Get an existing SmartDetectionRule resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] additional_email_recipients: Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        :param pulumi.Input[str] application_insights_id: The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] enabled: Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        :param pulumi.Input[str] name: Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
               `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
               `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        :param pulumi.Input[bool] send_emails_to_subscription_owners: Do emails get sent to subscription owners? Defaults to `true`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SmartDetectionRuleState.__new__(_SmartDetectionRuleState)

        __props__.__dict__["additional_email_recipients"] = additional_email_recipients
        __props__.__dict__["application_insights_id"] = application_insights_id
        __props__.__dict__["enabled"] = enabled
        __props__.__dict__["name"] = name
        __props__.__dict__["send_emails_to_subscription_owners"] = send_emails_to_subscription_owners
        return SmartDetectionRule(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="additionalEmailRecipients")
    def additional_email_recipients(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Specifies a list of additional recipients that will be sent emails on this Application Insights Smart Detection Rule.
        """
        return pulumi.get(self, "additional_email_recipients")

    @property
    @pulumi.getter(name="applicationInsightsId")
    def application_insights_id(self) -> pulumi.Output[str]:
        """
        The ID of the Application Insights component on which the Smart Detection Rule operates. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "application_insights_id")

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is the Application Insights Smart Detection Rule enabled? Defaults to `true`.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specifies the name of the Application Insights Smart Detection Rule. Valid values include `Slow page load time`, `Slow server response time`, 
        `Long dependency duration`, `Degradation in server response time`, `Degradation in dependency duration`, `Degradation in trace severity ratio`, `Abnormal rise in exception volume`,
        `Potential memory leak detected`, `Potential security issue detected`, `Abnormal rise in daily data volume`.  Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="sendEmailsToSubscriptionOwners")
    def send_emails_to_subscription_owners(self) -> pulumi.Output[Optional[bool]]:
        """
        Do emails get sent to subscription owners? Defaults to `true`.
        """
        return pulumi.get(self, "send_emails_to_subscription_owners")

