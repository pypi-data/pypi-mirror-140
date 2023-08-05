# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ManagedHardwareSecurityModuleArgs', 'ManagedHardwareSecurityModule']

@pulumi.input_type
class ManagedHardwareSecurityModuleArgs:
    def __init__(__self__, *,
                 admin_object_ids: pulumi.Input[Sequence[pulumi.Input[str]]],
                 resource_group_name: pulumi.Input[str],
                 sku_name: pulumi.Input[str],
                 tenant_id: pulumi.Input[str],
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 purge_protection_enabled: Optional[pulumi.Input[bool]] = None,
                 soft_delete_retention_days: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ManagedHardwareSecurityModule resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] admin_object_ids: Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] tenant_id: The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] purge_protection_enabled: Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[int] soft_delete_retention_days: The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        """
        pulumi.set(__self__, "admin_object_ids", admin_object_ids)
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        pulumi.set(__self__, "sku_name", sku_name)
        pulumi.set(__self__, "tenant_id", tenant_id)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if purge_protection_enabled is not None:
            pulumi.set(__self__, "purge_protection_enabled", purge_protection_enabled)
        if soft_delete_retention_days is not None:
            pulumi.set(__self__, "soft_delete_retention_days", soft_delete_retention_days)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="adminObjectIds")
    def admin_object_ids(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "admin_object_ids")

    @admin_object_ids.setter
    def admin_object_ids(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "admin_object_ids", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Input[str]:
        """
        The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> pulumi.Input[str]:
        """
        The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "sku_name")

    @sku_name.setter
    def sku_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "sku_name", value)

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> pulumi.Input[str]:
        """
        The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tenant_id")

    @tenant_id.setter
    def tenant_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "tenant_id", value)

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
        Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="purgeProtectionEnabled")
    def purge_protection_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "purge_protection_enabled")

    @purge_protection_enabled.setter
    def purge_protection_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "purge_protection_enabled", value)

    @property
    @pulumi.getter(name="softDeleteRetentionDays")
    def soft_delete_retention_days(self) -> Optional[pulumi.Input[int]]:
        """
        The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "soft_delete_retention_days")

    @soft_delete_retention_days.setter
    def soft_delete_retention_days(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "soft_delete_retention_days", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _ManagedHardwareSecurityModuleState:
    def __init__(__self__, *,
                 admin_object_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 hsm_uri: Optional[pulumi.Input[str]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 purge_protection_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
                 soft_delete_retention_days: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ManagedHardwareSecurityModule resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] admin_object_ids: Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] hsm_uri: The URI of the Key Vault Managed Hardware Security Module, used for performing operations on keys.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] purge_protection_enabled: Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        :param pulumi.Input[int] soft_delete_retention_days: The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] tenant_id: The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        if admin_object_ids is not None:
            pulumi.set(__self__, "admin_object_ids", admin_object_ids)
        if hsm_uri is not None:
            pulumi.set(__self__, "hsm_uri", hsm_uri)
        if location is not None:
            pulumi.set(__self__, "location", location)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if purge_protection_enabled is not None:
            pulumi.set(__self__, "purge_protection_enabled", purge_protection_enabled)
        if resource_group_name is not None:
            pulumi.set(__self__, "resource_group_name", resource_group_name)
        if sku_name is not None:
            pulumi.set(__self__, "sku_name", sku_name)
        if soft_delete_retention_days is not None:
            pulumi.set(__self__, "soft_delete_retention_days", soft_delete_retention_days)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tenant_id is not None:
            pulumi.set(__self__, "tenant_id", tenant_id)

    @property
    @pulumi.getter(name="adminObjectIds")
    def admin_object_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "admin_object_ids")

    @admin_object_ids.setter
    def admin_object_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "admin_object_ids", value)

    @property
    @pulumi.getter(name="hsmUri")
    def hsm_uri(self) -> Optional[pulumi.Input[str]]:
        """
        The URI of the Key Vault Managed Hardware Security Module, used for performing operations on keys.
        """
        return pulumi.get(self, "hsm_uri")

    @hsm_uri.setter
    def hsm_uri(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "hsm_uri", value)

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
        Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="purgeProtectionEnabled")
    def purge_protection_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "purge_protection_enabled")

    @purge_protection_enabled.setter
    def purge_protection_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "purge_protection_enabled", value)

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @resource_group_name.setter
    def resource_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_group_name", value)

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "sku_name")

    @sku_name.setter
    def sku_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "sku_name", value)

    @property
    @pulumi.getter(name="softDeleteRetentionDays")
    def soft_delete_retention_days(self) -> Optional[pulumi.Input[int]]:
        """
        The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "soft_delete_retention_days")

    @soft_delete_retention_days.setter
    def soft_delete_retention_days(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "soft_delete_retention_days", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> Optional[pulumi.Input[str]]:
        """
        The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tenant_id")

    @tenant_id.setter
    def tenant_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tenant_id", value)


class ManagedHardwareSecurityModule(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 admin_object_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 purge_protection_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
                 soft_delete_retention_days: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Key Vault Managed Hardware Security Module.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_managed_hardware_security_module = azure.keyvault.ManagedHardwareSecurityModule("exampleManagedHardwareSecurityModule",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            sku_name="Standard_B1",
            purge_protection_enabled=False,
            soft_delete_retention_days=90,
            tenant_id=current.tenant_id,
            admin_object_ids=[current.object_id],
            tags={
                "Env": "Test",
            })
        ```

        ## Import

        Key Vault Managed Hardware Security Module can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:keyvault/managedHardwareSecurityModule:ManagedHardwareSecurityModule example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.KeyVault/managedHSMs/hsm1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] admin_object_ids: Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] purge_protection_enabled: Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        :param pulumi.Input[int] soft_delete_retention_days: The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] tenant_id: The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ManagedHardwareSecurityModuleArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Key Vault Managed Hardware Security Module.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azure as azure

        current = azure.core.get_client_config()
        example_resource_group = azure.core.ResourceGroup("exampleResourceGroup", location="West Europe")
        example_managed_hardware_security_module = azure.keyvault.ManagedHardwareSecurityModule("exampleManagedHardwareSecurityModule",
            resource_group_name=example_resource_group.name,
            location=example_resource_group.location,
            sku_name="Standard_B1",
            purge_protection_enabled=False,
            soft_delete_retention_days=90,
            tenant_id=current.tenant_id,
            admin_object_ids=[current.object_id],
            tags={
                "Env": "Test",
            })
        ```

        ## Import

        Key Vault Managed Hardware Security Module can be imported using the `resource id`, e.g.

        ```sh
         $ pulumi import azure:keyvault/managedHardwareSecurityModule:ManagedHardwareSecurityModule example /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/mygroup1/providers/Microsoft.KeyVault/managedHSMs/hsm1
        ```

        :param str resource_name: The name of the resource.
        :param ManagedHardwareSecurityModuleArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ManagedHardwareSecurityModuleArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 admin_object_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 location: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 purge_protection_enabled: Optional[pulumi.Input[bool]] = None,
                 resource_group_name: Optional[pulumi.Input[str]] = None,
                 sku_name: Optional[pulumi.Input[str]] = None,
                 soft_delete_retention_days: Optional[pulumi.Input[int]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tenant_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = ManagedHardwareSecurityModuleArgs.__new__(ManagedHardwareSecurityModuleArgs)

            if admin_object_ids is None and not opts.urn:
                raise TypeError("Missing required property 'admin_object_ids'")
            __props__.__dict__["admin_object_ids"] = admin_object_ids
            __props__.__dict__["location"] = location
            __props__.__dict__["name"] = name
            __props__.__dict__["purge_protection_enabled"] = purge_protection_enabled
            if resource_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'resource_group_name'")
            __props__.__dict__["resource_group_name"] = resource_group_name
            if sku_name is None and not opts.urn:
                raise TypeError("Missing required property 'sku_name'")
            __props__.__dict__["sku_name"] = sku_name
            __props__.__dict__["soft_delete_retention_days"] = soft_delete_retention_days
            __props__.__dict__["tags"] = tags
            if tenant_id is None and not opts.urn:
                raise TypeError("Missing required property 'tenant_id'")
            __props__.__dict__["tenant_id"] = tenant_id
            __props__.__dict__["hsm_uri"] = None
        super(ManagedHardwareSecurityModule, __self__).__init__(
            'azure:keyvault/managedHardwareSecurityModule:ManagedHardwareSecurityModule',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            admin_object_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            hsm_uri: Optional[pulumi.Input[str]] = None,
            location: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            purge_protection_enabled: Optional[pulumi.Input[bool]] = None,
            resource_group_name: Optional[pulumi.Input[str]] = None,
            sku_name: Optional[pulumi.Input[str]] = None,
            soft_delete_retention_days: Optional[pulumi.Input[int]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tenant_id: Optional[pulumi.Input[str]] = None) -> 'ManagedHardwareSecurityModule':
        """
        Get an existing ManagedHardwareSecurityModule resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] admin_object_ids: Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] hsm_uri: The URI of the Key Vault Managed Hardware Security Module, used for performing operations on keys.
        :param pulumi.Input[str] location: Specifies the supported Azure location where the resource exists. Changing this forces a new resource to be created.
        :param pulumi.Input[str] name: Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[bool] purge_protection_enabled: Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        :param pulumi.Input[str] resource_group_name: The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        :param pulumi.Input[str] sku_name: The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        :param pulumi.Input[int] soft_delete_retention_days: The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        :param pulumi.Input[str] tenant_id: The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ManagedHardwareSecurityModuleState.__new__(_ManagedHardwareSecurityModuleState)

        __props__.__dict__["admin_object_ids"] = admin_object_ids
        __props__.__dict__["hsm_uri"] = hsm_uri
        __props__.__dict__["location"] = location
        __props__.__dict__["name"] = name
        __props__.__dict__["purge_protection_enabled"] = purge_protection_enabled
        __props__.__dict__["resource_group_name"] = resource_group_name
        __props__.__dict__["sku_name"] = sku_name
        __props__.__dict__["soft_delete_retention_days"] = soft_delete_retention_days
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tenant_id"] = tenant_id
        return ManagedHardwareSecurityModule(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="adminObjectIds")
    def admin_object_ids(self) -> pulumi.Output[Sequence[str]]:
        """
        Specifies a list of administrators object IDs for the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "admin_object_ids")

    @property
    @pulumi.getter(name="hsmUri")
    def hsm_uri(self) -> pulumi.Output[str]:
        """
        The URI of the Key Vault Managed Hardware Security Module, used for performing operations on keys.
        """
        return pulumi.get(self, "hsm_uri")

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
        Specifies the name of the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="purgeProtectionEnabled")
    def purge_protection_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Is Purge Protection enabled for this Key Vault Managed Hardware Security Module? Defaults to `false`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "purge_protection_enabled")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> pulumi.Output[str]:
        """
        The name of the resource group in which to create the Key Vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="skuName")
    def sku_name(self) -> pulumi.Output[str]:
        """
        The Name of the SKU used for this Key Vault Managed Hardware Security Module. Possible value is `Standard_B1`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "sku_name")

    @property
    @pulumi.getter(name="softDeleteRetentionDays")
    def soft_delete_retention_days(self) -> pulumi.Output[Optional[int]]:
        """
        The number of days that items should be retained for once soft-deleted. This value can be between `7` and `90` days. Defaults to `90`. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "soft_delete_retention_days")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A mapping of tags to assign to the resource. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tenantId")
    def tenant_id(self) -> pulumi.Output[str]:
        """
        The Azure Active Directory Tenant ID that should be used for authenticating requests to the key vault Managed Hardware Security Module. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "tenant_id")

