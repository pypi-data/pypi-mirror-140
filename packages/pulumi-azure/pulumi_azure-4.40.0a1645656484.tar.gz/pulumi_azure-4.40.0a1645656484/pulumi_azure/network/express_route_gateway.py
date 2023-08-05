# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ExpressRouteGatewayArgs', 'ExpressRouteGateway']

@pulumi.input_type
class ExpressRouteGatewayArgs:
    def __init__(__self__, *,
                 resource_group_name: pulumi.Input[str],
                 scale_units: pulumi.Input[int],
                 virtual_hub_id: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ExpressRouteGateway resource.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[int] scale_units: The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        :param pulumi.Input[str] virtual_hub_id: The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        """
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "scale_units", scale_units)
        pulumi.set(__self__, "virtual_hub_id", virtual_hub_id)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="scaleUnits")
    def scale_units(self) -> pulumi.Input[int]:
        """
        The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        """
        return pulumi.get(self, "scale_units")

    @scale_units.setter
    def scale_units(self, value: pulumi.Input[int]):
        pulumi.set(self, "scale_units", value)

    @property
    @pulumi.getter(name="virtualHubId")
    def virtual_hub_id(self) -> pulumi.Input[str]:
        """
        The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        return pulumi.get(self, "virtual_hub_id")

    @virtual_hub_id.setter
    def virtual_hub_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "virtual_hub_id", value)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _ExpressRouteGatewayState:
    def __init__(__self__, *,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 scale_units: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 virtual_hub_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ExpressRouteGateway resources.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[int] scale_units: The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] virtual_hub_id: The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if scale_units is not None:
            pulumi.set(__self__, "scale_units", scale_units)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if virtual_hub_id is not None:
            pulumi.set(__self__, "virtual_hub_id", virtual_hub_id)

    @property
    @pulumi.getter
    def location(self) -> Optional[pulumi.Input[str]]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @location.setter
    def location(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="scaleUnits")
    def scale_units(self) -> Optional[pulumi.Input[int]]:
        """
        The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        """
        return pulumi.get(self, "scale_units")

    @scale_units.setter
    def scale_units(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "scale_units", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="virtualHubId")
    def virtual_hub_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        return pulumi.get(self, "virtual_hub_id")

    @virtual_hub_id.setter
    def virtual_hub_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "virtual_hub_id", value)


class ExpressRouteGateway(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 scale_units: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 virtual_hub_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages an ExpressRoute gateway.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_virtual_wan = azure.network.VirtualWan("exampleVirtualWan",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location)
        example_virtual_hub = azure.network.VirtualHub("exampleVirtualHub",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            virtual_wan_id=example_virtual_wan.id,
            address_prefix="10.0.1.0/24")
        example_express_route_gateway = azure.network.ExpressRouteGateway("exampleExpressRouteGateway",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            virtual_hub_id=example_virtual_hub.id,
            scale_units=1,
            tags={
                "environment": "Production",
            })
        ```

        ## Import

        ExpressRoute Gateways can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:network/expressRouteGateway:ExpressRouteGateway example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Network/expressRouteGateways/myExpressRouteGateway
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[int] scale_units: The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] virtual_hub_id: The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ExpressRouteGatewayArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an ExpressRoute gateway.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_virtual_wan = azure.network.VirtualWan("exampleVirtualWan",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location)
        example_virtual_hub = azure.network.VirtualHub("exampleVirtualHub",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            virtual_wan_id=example_virtual_wan.id,
            address_prefix="10.0.1.0/24")
        example_express_route_gateway = azure.network.ExpressRouteGateway("exampleExpressRouteGateway",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            virtual_hub_id=example_virtual_hub.id,
            scale_units=1,
            tags={
                "environment": "Production",
            })
        ```

        ## Import

        ExpressRoute Gateways can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:network/expressRouteGateway:ExpressRouteGateway example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.Network/expressRouteGateways/myExpressRouteGateway
        ```

        :param str resource_name: The name of the resource.
        :param ExpressRouteGatewayArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ExpressRouteGatewayArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 scale_units: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 virtual_hub_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ExpressRouteGatewayArgs.__new__(ExpressRouteGatewayArgs)

            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if scale_units is None and not opts.urn:
                raise TypeError("Missing required property 'scale_units'")
            __props__.__dict__["scale_units"] = scale_units
            __props__.__dict__["tags"] = tags
            if virtual_hub_id is None and not opts.urn:
                raise TypeError("Missing required property 'virtual_hub_id'")
            __props__.__dict__["virtual_hub_id"] = virtual_hub_id
        super(ExpressRouteGateway, __self__).__init__(
            'azure:network/expressRouteGateway:ExpressRouteGateway',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            location: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            scale_units: Optional[pulumi.Input[int]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            virtual_hub_id: Optional[pulumi.Input[str]] = None) -> 'ExpressRouteGateway':
        """
        Get an existing ExpressRouteGateway resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        :param pulumi.Input[int] scale_units: The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource.
        :param pulumi.Input[str] virtual_hub_id: The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ExpressRouteGatewayState.__new__(_ExpressRouteGatewayState)

        __props__.__dict__["location"] = location
        __props__.__dict__["name"] = name
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["scale_units"] = scale_units
        __props__.__dict__["tags"] = tags
        __props__.__dict__["virtual_hub_id"] = virtual_hub_id
        return ExpressRouteGateway(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def location(self) -> pulumi.Output[str]:
        """
        Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to create the ExpressRoute gateway. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="scaleUnits")
    def scale_units(self) -> pulumi.Output[int]:
        """
        The number of scale units with which to provision the ExpressRoute gateway. Each scale unit is equal to 2Gbps, with support for up to 10 scale units (20Gbps).
        """
        return pulumi.get(self, "scale_units")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="virtualHubId")
    def virtual_hub_id(self) -> pulumi.Output[str]:
        """
        The ID of a Virtual HUB within which the ExpressRoute gateway should be created.
        """
        return pulumi.get(self, "virtual_hub_id")

