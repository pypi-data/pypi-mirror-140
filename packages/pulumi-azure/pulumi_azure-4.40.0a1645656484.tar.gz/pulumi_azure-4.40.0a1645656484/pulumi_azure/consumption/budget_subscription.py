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

__all__ = ['BudgetSubscriptionArgs', 'BudgetSubscription']

@pulumi.input_type
class BudgetSubscriptionArgs:
    def __init__(__self__, *,
                 amount: pulumi.Input[float],
                 notifications: pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]],
                 subscription_id: pulumi.Input[str],
                 time_period: pulumi.Input['BudgetSubscriptionTimePeriodArgs'],
                 etag: Optional[pulumi.Input[str]] = None,
                 filter: Optional[pulumi.Input['BudgetSubscriptionFilterArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 time_grain: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a BudgetSubscription resource.
        :param pulumi.Input[float] amount: The total amount of cost to track with the budget.
        :param pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]] notifications: One or more `notification` blocks as defined below.
        :param pulumi.Input[str] subscription_id: The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input['BudgetSubscriptionTimePeriodArgs'] time_period: A `time_period` block as defined below.
        :param pulumi.Input[str] etag: The ETag of the Subscription Consumption Budget.
        :param pulumi.Input['BudgetSubscriptionFilterArgs'] filter: A `filter` block as defined below.
        :param pulumi.Input[str] name: The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[str] time_grain: The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        """
        pulumi.set(__self__, "amount", amount)
        pulumi.set(__self__, "notifications", notifications)
        pulumi.set(__self__, "subscription_id", subscription_id)
        pulumi.set(__self__, "time_period", time_period)
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if filter is not None:
            pulumi.set(__self__, "filter", filter)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if time_grain is not None:
            pulumi.set(__self__, "time_grain", time_grain)

    @property
    @pulumi.getter
    def amount(self) -> pulumi.Input[float]:
        """
        The total amount of cost to track with the budget.
        """
        return pulumi.get(self, "amount")

    @amount.setter
    def amount(self, value: pulumi.Input[float]):
        pulumi.set(self, "amount", value)

    @property
    @pulumi.getter
    def notifications(self) -> pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]]:
        """
        One or more `notification` blocks as defined below.
        """
        return pulumi.get(self, "notifications")

    @notifications.setter
    def notifications(self, value: pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]]):
        pulumi.set(self, "notifications", value)

    @property
    @pulumi.getter(name="subscriptionId")
    def subscription_id(self) -> pulumi.Input[str]:
        """
        The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subscription_id")

    @subscription_id.setter
    def subscription_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "subscription_id", value)

    @property
    @pulumi.getter(name="timePeriod")
    def time_period(self) -> pulumi.Input['BudgetSubscriptionTimePeriodArgs']:
        """
        A `time_period` block as defined below.
        """
        return pulumi.get(self, "time_period")

    @time_period.setter
    def time_period(self, value: pulumi.Input['BudgetSubscriptionTimePeriodArgs']):
        pulumi.set(self, "time_period", value)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        """
        The ETag of the Subscription Consumption Budget.
        """
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter
    def filter(self) -> Optional[pulumi.Input['BudgetSubscriptionFilterArgs']]:
        """
        A `filter` block as defined below.
        """
        return pulumi.get(self, "filter")

    @filter.setter
    def filter(self, value: Optional[pulumi.Input['BudgetSubscriptionFilterArgs']]):
        pulumi.set(self, "filter", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="timeGrain")
    def time_grain(self) -> Optional[pulumi.Input[str]]:
        """
        The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        """
        return pulumi.get(self, "time_grain")

    @time_grain.setter
    def time_grain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "time_grain", value)


@pulumi.input_type
class _BudgetSubscriptionState:
    def __init__(__self__, *,
                 amount: Optional[pulumi.Input[float]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 filter: Optional[pulumi.Input['BudgetSubscriptionFilterArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 notifications: Optional[pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]]] = None,
                 subscription_id: Optional[pulumi.Input[str]] = None,
                 time_grain: Optional[pulumi.Input[str]] = None,
                 time_period: Optional[pulumi.Input['BudgetSubscriptionTimePeriodArgs']] = None):
        """
        Input properties used for looking up and filtering BudgetSubscription resources.
        :param pulumi.Input[float] amount: The total amount of cost to track with the budget.
        :param pulumi.Input[str] etag: The ETag of the Subscription Consumption Budget.
        :param pulumi.Input['BudgetSubscriptionFilterArgs'] filter: A `filter` block as defined below.
        :param pulumi.Input[str] name: The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]] notifications: One or more `notification` blocks as defined below.
        :param pulumi.Input[str] subscription_id: The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[str] time_grain: The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        :param pulumi.Input['BudgetSubscriptionTimePeriodArgs'] time_period: A `time_period` block as defined below.
        """
        if amount is not None:
            pulumi.set(__self__, "amount", amount)
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if filter is not None:
            pulumi.set(__self__, "filter", filter)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if notifications is not None:
            pulumi.set(__self__, "notifications", notifications)
        if subscription_id is not None:
            pulumi.set(__self__, "subscription_id", subscription_id)
        if time_grain is not None:
            pulumi.set(__self__, "time_grain", time_grain)
        if time_period is not None:
            pulumi.set(__self__, "time_period", time_period)

    @property
    @pulumi.getter
    def amount(self) -> Optional[pulumi.Input[float]]:
        """
        The total amount of cost to track with the budget.
        """
        return pulumi.get(self, "amount")

    @amount.setter
    def amount(self, value: Optional[pulumi.Input[float]]):
        pulumi.set(self, "amount", value)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        """
        The ETag of the Subscription Consumption Budget.
        """
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter
    def filter(self) -> Optional[pulumi.Input['BudgetSubscriptionFilterArgs']]:
        """
        A `filter` block as defined below.
        """
        return pulumi.get(self, "filter")

    @filter.setter
    def filter(self, value: Optional[pulumi.Input['BudgetSubscriptionFilterArgs']]):
        pulumi.set(self, "filter", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def notifications(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]]]:
        """
        One or more `notification` blocks as defined below.
        """
        return pulumi.get(self, "notifications")

    @notifications.setter
    def notifications(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['BudgetSubscriptionNotificationArgs']]]]):
        pulumi.set(self, "notifications", value)

    @property
    @pulumi.getter(name="subscriptionId")
    def subscription_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subscription_id")

    @subscription_id.setter
    def subscription_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "subscription_id", value)

    @property
    @pulumi.getter(name="timeGrain")
    def time_grain(self) -> Optional[pulumi.Input[str]]:
        """
        The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        """
        return pulumi.get(self, "time_grain")

    @time_grain.setter
    def time_grain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "time_grain", value)

    @property
    @pulumi.getter(name="timePeriod")
    def time_period(self) -> Optional[pulumi.Input['BudgetSubscriptionTimePeriodArgs']]:
        """
        A `time_period` block as defined below.
        """
        return pulumi.get(self, "time_period")

    @time_period.setter
    def time_period(self, value: Optional[pulumi.Input['BudgetSubscriptionTimePeriodArgs']]):
        pulumi.set(self, "time_period", value)


class BudgetSubscription(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 amount: Optional[pulumi.Input[float]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 filter: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionFilterArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 notifications: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['BudgetSubscriptionNotificationArgs']]]]] = None,
                 subscription_id: Optional[pulumi.Input[str]] = None,
                 time_grain: Optional[pulumi.Input[str]] = None,
                 time_period: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionTimePeriodArgs']]] = None,
                 __props__=None):
        """
        Manages a Subscription Consumption Budget.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_subscription()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="eastus")
        example_action_group = azure.monitoring.ActionGroup("exampleActionGroup",
            resource_group_name=example_resource_group.name,
            short_name="example")
        example_budget_subscription = azure.consumption.BudgetSubscription("exampleBudgetSubscription",
            subscription_id=current.id,
            amount=1000,
            time_grain="Monthly",
            time_period=azure.consumption.BudgetSubscriptionTimePeriodArgs(
                start_date="2022-06-01T00:00:00Z",
                end_date="2022-07-01T00:00:00Z",
            ),
            filter=azure.consumption.BudgetSubscriptionFilterArgs(
                dimensions=[azure.consumption.BudgetSubscriptionFilterDimensionArgs(
                    name="ResourceGroupName",
                    values=[example_resource_group.name],
                )],
                tags=[azure.consumption.BudgetSubscriptionFilterTagArgs(
                    name="foo",
                    values=[
                        "bar",
                        "baz",
                    ],
                )],
            ),
            notifications=[
                azure.consumption.BudgetSubscriptionNotificationArgs(
                    enabled=True,
                    threshold=90,
                    operator="EqualTo",
                    contact_emails=[
                        "foo@example.com",
                        "bar@example.com",
                    ],
                    contact_groups=[example_action_group.id],
                    contact_roles=["Owner"],
                ),
                azure.consumption.BudgetSubscriptionNotificationArgs(
                    enabled=False,
                    threshold=100,
                    operator="GreaterThan",
                    threshold_type="Forecasted",
                    contact_emails=[
                        "foo@example.com",
                        "bar@example.com",
                    ],
                ),
            ])
        ```

        ## Import

        Subscription Consumption Budgets can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:consumption/budgetSubscription:BudgetSubscription example /subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Consumption/budgets/subscription1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[float] amount: The total amount of cost to track with the budget.
        :param pulumi.Input[str] etag: The ETag of the Subscription Consumption Budget.
        :param pulumi.Input[pulumi.InputType['BudgetSubscriptionFilterArgs']] filter: A `filter` block as defined below.
        :param pulumi.Input[str] name: The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['BudgetSubscriptionNotificationArgs']]]] notifications: One or more `notification` blocks as defined below.
        :param pulumi.Input[str] subscription_id: The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[str] time_grain: The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        :param pulumi.Input[pulumi.InputType['BudgetSubscriptionTimePeriodArgs']] time_period: A `time_period` block as defined below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: BudgetSubscriptionArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Subscription Consumption Budget.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_subscription()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="eastus")
        example_action_group = azure.monitoring.ActionGroup("exampleActionGroup",
            resource_group_name=example_resource_group.name,
            short_name="example")
        example_budget_subscription = azure.consumption.BudgetSubscription("exampleBudgetSubscription",
            subscription_id=current.id,
            amount=1000,
            time_grain="Monthly",
            time_period=azure.consumption.BudgetSubscriptionTimePeriodArgs(
                start_date="2022-06-01T00:00:00Z",
                end_date="2022-07-01T00:00:00Z",
            ),
            filter=azure.consumption.BudgetSubscriptionFilterArgs(
                dimensions=[azure.consumption.BudgetSubscriptionFilterDimensionArgs(
                    name="ResourceGroupName",
                    values=[example_resource_group.name],
                )],
                tags=[azure.consumption.BudgetSubscriptionFilterTagArgs(
                    name="foo",
                    values=[
                        "bar",
                        "baz",
                    ],
                )],
            ),
            notifications=[
                azure.consumption.BudgetSubscriptionNotificationArgs(
                    enabled=True,
                    threshold=90,
                    operator="EqualTo",
                    contact_emails=[
                        "foo@example.com",
                        "bar@example.com",
                    ],
                    contact_groups=[example_action_group.id],
                    contact_roles=["Owner"],
                ),
                azure.consumption.BudgetSubscriptionNotificationArgs(
                    enabled=False,
                    threshold=100,
                    operator="GreaterThan",
                    threshold_type="Forecasted",
                    contact_emails=[
                        "foo@example.com",
                        "bar@example.com",
                    ],
                ),
            ])
        ```

        ## Import

        Subscription Consumption Budgets can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:consumption/budgetSubscription:BudgetSubscription example /subscriptions/00000000-0000-0000-0000-000000000000/providers/Microsoft.Consumption/budgets/subscription1
        ```

        :param str resource_name: The name of the resource.
        :param BudgetSubscriptionArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(BudgetSubscriptionArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 amount: Optional[pulumi.Input[float]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 filter: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionFilterArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 notifications: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['BudgetSubscriptionNotificationArgs']]]]] = None,
                 subscription_id: Optional[pulumi.Input[str]] = None,
                 time_grain: Optional[pulumi.Input[str]] = None,
                 time_period: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionTimePeriodArgs']]] = None,
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
            __props__ = BudgetSubscriptionArgs.__new__(BudgetSubscriptionArgs)

            if amount is None and not opts.urn:
                raise TypeError("Missing required property 'amount'")
            __props__.__dict__["amount"] = amount
            __props__.__dict__["etag"] = etag
            __props__.__dict__["filter"] = filter
            __props__.__dict__["name"] = name
            if notifications is None and not opts.urn:
                raise TypeError("Missing required property 'notifications'")
            __props__.__dict__["notifications"] = notifications
            if subscription_id is None and not opts.urn:
                raise TypeError("Missing required property 'subscription_id'")
            __props__.__dict__["subscription_id"] = subscription_id
            __props__.__dict__["time_grain"] = time_grain
            if time_period is None and not opts.urn:
                raise TypeError("Missing required property 'time_period'")
            __props__.__dict__["time_period"] = time_period
        super(BudgetSubscription, __self__).__init__(
            'azure:consumption/budgetSubscription:BudgetSubscription',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            amount: Optional[pulumi.Input[float]] = None,
            etag: Optional[pulumi.Input[str]] = None,
            filter: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionFilterArgs']]] = None,
            name: Optional[pulumi.Input[str]] = None,
            notifications: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['BudgetSubscriptionNotificationArgs']]]]] = None,
            subscription_id: Optional[pulumi.Input[str]] = None,
            time_grain: Optional[pulumi.Input[str]] = None,
            time_period: Optional[pulumi.Input[pulumi.InputType['BudgetSubscriptionTimePeriodArgs']]] = None) -> 'BudgetSubscription':
        """
        Get an existing BudgetSubscription resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[float] amount: The total amount of cost to track with the budget.
        :param pulumi.Input[str] etag: The ETag of the Subscription Consumption Budget.
        :param pulumi.Input[pulumi.InputType['BudgetSubscriptionFilterArgs']] filter: A `filter` block as defined below.
        :param pulumi.Input[str] name: The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['BudgetSubscriptionNotificationArgs']]]] notifications: One or more `notification` blocks as defined below.
        :param pulumi.Input[str] subscription_id: The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        :param pulumi.Input[str] time_grain: The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        :param pulumi.Input[pulumi.InputType['BudgetSubscriptionTimePeriodArgs']] time_period: A `time_period` block as defined below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _BudgetSubscriptionState.__new__(_BudgetSubscriptionState)

        __props__.__dict__["amount"] = amount
        __props__.__dict__["etag"] = etag
        __props__.__dict__["filter"] = filter
        __props__.__dict__["name"] = name
        __props__.__dict__["notifications"] = notifications
        __props__.__dict__["subscription_id"] = subscription_id
        __props__.__dict__["time_grain"] = time_grain
        __props__.__dict__["time_period"] = time_period
        return BudgetSubscription(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def amount(self) -> pulumi.Output[float]:
        """
        The total amount of cost to track with the budget.
        """
        return pulumi.get(self, "amount")

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        """
        The ETag of the Subscription Consumption Budget.
        """
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter
    def filter(self) -> pulumi.Output[Optional['outputs.BudgetSubscriptionFilter']]:
        """
        A `filter` block as defined below.
        """
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name which should be used for this Subscription Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def notifications(self) -> pulumi.Output[Sequence['outputs.BudgetSubscriptionNotification']]:
        """
        One or more `notification` blocks as defined below.
        """
        return pulumi.get(self, "notifications")

    @property
    @pulumi.getter(name="subscriptionId")
    def subscription_id(self) -> pulumi.Output[str]:
        """
        The ID of the Subscription for which to create a Consumption Budget. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "subscription_id")

    @property
    @pulumi.getter(name="timeGrain")
    def time_grain(self) -> pulumi.Output[Optional[str]]:
        """
        The time covered by a budget. Tracking of the amount will be reset based on the time grain. Must be one of `Monthly`, `Quarterly`, `Annually`, `BillingMonth`, `BillingQuarter`, or `BillingYear`. Defaults to `Monthly`.
        """
        return pulumi.get(self, "time_grain")

    @property
    @pulumi.getter(name="timePeriod")
    def time_period(self) -> pulumi.Output['outputs.BudgetSubscriptionTimePeriod']:
        """
        A `time_period` block as defined below.
        """
        return pulumi.get(self, "time_period")

