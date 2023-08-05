# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'GetKubernetesClusterResult',
    'AwaitableGetKubernetesClusterResult',
    'get_kubernetes_cluster',
    'get_kubernetes_cluster_output',
]

@pulumi.output_type
class GetKubernetesClusterResult:
    """
    A collection of values returned by getKubernetesCluster.
    """
    def __init__(__self__, addon_profiles=None, agent_pool_profiles=None, api_server_authorized_ip_ranges=None, disk_encryption_set_id=None, dns_prefix=None, fqdn=None, id=None, identities=None, kube_admin_config_raw=None, kube_admin_configs=None, kube_config_raw=None, kube_configs=None, kubelet_identities=None, kubernetes_version=None, linux_profiles=None, location=None, name=None, network_profiles=None, node_resource_group=None, private_cluster_enabled=None, private_fqdn=None, private_link_enabled=None, resource_group_name=None, role_based_access_controls=None, service_principals=None, tags=None, windows_profiles=None):
        if addon_profiles and not isinstance(addon_profiles, list):
            raise TypeError("Expected argument 'addon_profiles' to be a list")
        pulumi.set(__self__, "addon_profiles", addon_profiles)
        if agent_pool_profiles and not isinstance(agent_pool_profiles, list):
            raise TypeError("Expected argument 'agent_pool_profiles' to be a list")
        pulumi.set(__self__, "agent_pool_profiles", agent_pool_profiles)
        if api_server_authorized_ip_ranges and not isinstance(api_server_authorized_ip_ranges, list):
            raise TypeError("Expected argument 'api_server_authorized_ip_ranges' to be a list")
        pulumi.set(__self__, "api_server_authorized_ip_ranges", api_server_authorized_ip_ranges)
        if disk_encryption_set_id and not isinstance(disk_encryption_set_id, str):
            raise TypeError("Expected argument 'disk_encryption_set_id' to be a str")
        pulumi.set(__self__, "disk_encryption_set_id", disk_encryption_set_id)
        if dns_prefix and not isinstance(dns_prefix, str):
            raise TypeError("Expected argument 'dns_prefix' to be a str")
        pulumi.set(__self__, "dns_prefix", dns_prefix)
        if fqdn and not isinstance(fqdn, str):
            raise TypeError("Expected argument 'fqdn' to be a str")
        pulumi.set(__self__, "fqdn", fqdn)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if identities and not isinstance(identities, list):
            raise TypeError("Expected argument 'identities' to be a list")
        pulumi.set(__self__, "identities", identities)
        if kube_admin_config_raw and not isinstance(kube_admin_config_raw, str):
            raise TypeError("Expected argument 'kube_admin_config_raw' to be a str")
        pulumi.set(__self__, "kube_admin_config_raw", kube_admin_config_raw)
        if kube_admin_configs and not isinstance(kube_admin_configs, list):
            raise TypeError("Expected argument 'kube_admin_configs' to be a list")
        pulumi.set(__self__, "kube_admin_configs", kube_admin_configs)
        if kube_config_raw and not isinstance(kube_config_raw, str):
            raise TypeError("Expected argument 'kube_config_raw' to be a str")
        pulumi.set(__self__, "kube_config_raw", kube_config_raw)
        if kube_configs and not isinstance(kube_configs, list):
            raise TypeError("Expected argument 'kube_configs' to be a list")
        pulumi.set(__self__, "kube_configs", kube_configs)
        if kubelet_identities and not isinstance(kubelet_identities, list):
            raise TypeError("Expected argument 'kubelet_identities' to be a list")
        pulumi.set(__self__, "kubelet_identities", kubelet_identities)
        if kubernetes_version and not isinstance(kubernetes_version, str):
            raise TypeError("Expected argument 'kubernetes_version' to be a str")
        pulumi.set(__self__, "kubernetes_version", kubernetes_version)
        if linux_profiles and not isinstance(linux_profiles, list):
            raise TypeError("Expected argument 'linux_profiles' to be a list")
        pulumi.set(__self__, "linux_profiles", linux_profiles)
        if location and not isinstance(location, str):
            raise TypeError("Expected argument 'location' to be a str")
        pulumi.set(__self__, "location", location)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if network_profiles and not isinstance(network_profiles, list):
            raise TypeError("Expected argument 'network_profiles' to be a list")
        pulumi.set(__self__, "network_profiles", network_profiles)
        if node_resource_group and not isinstance(node_resource_group, str):
            raise TypeError("Expected argument 'node_resource_group' to be a str")
        pulumi.set(__self__, "node_resource_group", node_resource_group)
        if private_cluster_enabled and not isinstance(private_cluster_enabled, bool):
            raise TypeError("Expected argument 'private_cluster_enabled' to be a bool")
        pulumi.set(__self__, "private_cluster_enabled", private_cluster_enabled)
        if private_fqdn and not isinstance(private_fqdn, str):
            raise TypeError("Expected argument 'private_fqdn' to be a str")
        pulumi.set(__self__, "private_fqdn", private_fqdn)
        if private_link_enabled and not isinstance(private_link_enabled, bool):
            raise TypeError("Expected argument 'private_link_enabled' to be a bool")
        pulumi.set(__self__, "private_link_enabled", private_link_enabled)
        if resource_group_name and not isinstance(resource_group_name, str):
            raise TypeError("Expected argument 'resource_group_name' to be a str")
        pulumi.set(__self__, "resource_group_name", resource_group_name)
        if role_based_access_controls and not isinstance(role_based_access_controls, list):
            raise TypeError("Expected argument 'role_based_access_controls' to be a list")
        pulumi.set(__self__, "role_based_access_controls", role_based_access_controls)
        if service_principals and not isinstance(service_principals, list):
            raise TypeError("Expected argument 'service_principals' to be a list")
        pulumi.set(__self__, "service_principals", service_principals)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if windows_profiles and not isinstance(windows_profiles, list):
            raise TypeError("Expected argument 'windows_profiles' to be a list")
        pulumi.set(__self__, "windows_profiles", windows_profiles)

    @property
    @pulumi.getter(name="addonProfiles")
    def addon_profiles(self) -> Sequence['outputs.GetKubernetesClusterAddonProfileResult']:
        """
        A `addon_profile` block as documented below.
        """
        return pulumi.get(self, "addon_profiles")

    @property
    @pulumi.getter(name="agentPoolProfiles")
    def agent_pool_profiles(self) -> Sequence['outputs.GetKubernetesClusterAgentPoolProfileResult']:
        """
        An `agent_pool_profile` block as documented below.
        """
        return pulumi.get(self, "agent_pool_profiles")

    @property
    @pulumi.getter(name="apiServerAuthorizedIpRanges")
    def api_server_authorized_ip_ranges(self) -> Sequence[str]:
        """
        The IP ranges to whitelist for incoming traffic to the primaries.
        """
        return pulumi.get(self, "api_server_authorized_ip_ranges")

    @property
    @pulumi.getter(name="diskEncryptionSetId")
    def disk_encryption_set_id(self) -> str:
        """
        The ID of the Disk Encryption Set used for the Nodes and Volumes.
        """
        return pulumi.get(self, "disk_encryption_set_id")

    @property
    @pulumi.getter(name="dnsPrefix")
    def dns_prefix(self) -> str:
        """
        The DNS Prefix of the managed Kubernetes cluster.
        """
        return pulumi.get(self, "dns_prefix")

    @property
    @pulumi.getter
    def fqdn(self) -> str:
        """
        The FQDN of the Azure Kubernetes Managed Cluster.
        """
        return pulumi.get(self, "fqdn")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def identities(self) -> Sequence['outputs.GetKubernetesClusterIdentityResult']:
        """
        A `identity` block as documented below.
        """
        return pulumi.get(self, "identities")

    @property
    @pulumi.getter(name="kubeAdminConfigRaw")
    def kube_admin_config_raw(self) -> str:
        """
        Raw Kubernetes config for the admin account to be used by [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) and other compatible tools. This is only available when Role Based Access Control with Azure Active Directory is enabled and local accounts are not disabled.
        """
        return pulumi.get(self, "kube_admin_config_raw")

    @property
    @pulumi.getter(name="kubeAdminConfigs")
    def kube_admin_configs(self) -> Sequence['outputs.GetKubernetesClusterKubeAdminConfigResult']:
        """
        A `kube_admin_config` block as defined below. This is only available when Role Based Access Control with Azure Active Directory is enabled and local accounts are not disabled.
        """
        return pulumi.get(self, "kube_admin_configs")

    @property
    @pulumi.getter(name="kubeConfigRaw")
    def kube_config_raw(self) -> str:
        """
        Base64 encoded Kubernetes configuration.
        """
        return pulumi.get(self, "kube_config_raw")

    @property
    @pulumi.getter(name="kubeConfigs")
    def kube_configs(self) -> Sequence['outputs.GetKubernetesClusterKubeConfigResult']:
        """
        A `kube_config` block as defined below.
        """
        return pulumi.get(self, "kube_configs")

    @property
    @pulumi.getter(name="kubeletIdentities")
    def kubelet_identities(self) -> Sequence['outputs.GetKubernetesClusterKubeletIdentityResult']:
        """
        A `kubelet_identity` block as documented below.
        """
        return pulumi.get(self, "kubelet_identities")

    @property
    @pulumi.getter(name="kubernetesVersion")
    def kubernetes_version(self) -> str:
        """
        The version of Kubernetes used on the managed Kubernetes Cluster.
        """
        return pulumi.get(self, "kubernetes_version")

    @property
    @pulumi.getter(name="linuxProfiles")
    def linux_profiles(self) -> Sequence['outputs.GetKubernetesClusterLinuxProfileResult']:
        """
        A `linux_profile` block as documented below.
        """
        return pulumi.get(self, "linux_profiles")

    @property
    @pulumi.getter
    def location(self) -> str:
        """
        The Azure Region in which the managed Kubernetes Cluster exists.
        """
        return pulumi.get(self, "location")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name assigned to this pool of agents.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="networkProfiles")
    def network_profiles(self) -> Sequence['outputs.GetKubernetesClusterNetworkProfileResult']:
        """
        A `network_profile` block as documented below.
        """
        return pulumi.get(self, "network_profiles")

    @property
    @pulumi.getter(name="nodeResourceGroup")
    def node_resource_group(self) -> str:
        """
        Auto-generated Resource Group containing AKS Cluster resources.
        """
        return pulumi.get(self, "node_resource_group")

    @property
    @pulumi.getter(name="privateClusterEnabled")
    def private_cluster_enabled(self) -> bool:
        """
        If the cluster has the Kubernetes API only exposed on internal IP addresses.
        """
        return pulumi.get(self, "private_cluster_enabled")

    @property
    @pulumi.getter(name="privateFqdn")
    def private_fqdn(self) -> str:
        """
        The FQDN of this Kubernetes Cluster when private link has been enabled. This name is only resolvable inside the Virtual Network where the Azure Kubernetes Service is located
        """
        return pulumi.get(self, "private_fqdn")

    @property
    @pulumi.getter(name="privateLinkEnabled")
    def private_link_enabled(self) -> bool:
        return pulumi.get(self, "private_link_enabled")

    @property
    @pulumi.getter(name="resourceGroupName")
    def resource_group_name(self) -> str:
        return pulumi.get(self, "resource_group_name")

    @property
    @pulumi.getter(name="roleBasedAccessControls")
    def role_based_access_controls(self) -> Sequence['outputs.GetKubernetesClusterRoleBasedAccessControlResult']:
        """
        A `role_based_access_control` block as documented below.
        """
        return pulumi.get(self, "role_based_access_controls")

    @property
    @pulumi.getter(name="servicePrincipals")
    def service_principals(self) -> Sequence['outputs.GetKubernetesClusterServicePrincipalResult']:
        """
        A `service_principal` block as documented below.
        """
        return pulumi.get(self, "service_principals")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        A mapping of tags to assign to the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="windowsProfiles")
    def windows_profiles(self) -> Sequence['outputs.GetKubernetesClusterWindowsProfileResult']:
        """
        A `windows_profile` block as documented below.
        """
        return pulumi.get(self, "windows_profiles")


class AwaitableGetKubernetesClusterResult(GetKubernetesClusterResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetKubernetesClusterResult(
            addon_profiles=self.addon_profiles,
            agent_pool_profiles=self.agent_pool_profiles,
            api_server_authorized_ip_ranges=self.api_server_authorized_ip_ranges,
            disk_encryption_set_id=self.disk_encryption_set_id,
            dns_prefix=self.dns_prefix,
            fqdn=self.fqdn,
            id=self.id,
            identities=self.identities,
            kube_admin_config_raw=self.kube_admin_config_raw,
            kube_admin_configs=self.kube_admin_configs,
            kube_config_raw=self.kube_config_raw,
            kube_configs=self.kube_configs,
            kubelet_identities=self.kubelet_identities,
            kubernetes_version=self.kubernetes_version,
            linux_profiles=self.linux_profiles,
            location=self.location,
            name=self.name,
            network_profiles=self.network_profiles,
            node_resource_group=self.node_resource_group,
            private_cluster_enabled=self.private_cluster_enabled,
            private_fqdn=self.private_fqdn,
            private_link_enabled=self.private_link_enabled,
            resource_group_name=self.resource_group_name,
            role_based_access_controls=self.role_based_access_controls,
            service_principals=self.service_principals,
            tags=self.tags,
            windows_profiles=self.windows_profiles)


def get_kubernetes_cluster(name: Optional[str] = None,
                           resource_group_name: Optional[str] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetKubernetesClusterResult:
    """
    Use this data source to access information about an existing Managed Kubernetes Cluster (AKS).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.containerservice.get_kubernetes_cluster(name="myakscluster",
        resource_group_name="my-example-resource-group")
    ```


    :param str name: The name of the managed Kubernetes Cluster.
    :param str resource_group_name: The name of the Resource Group in which the managed Kubernetes Cluster exists.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['resourceGroupName'] = resource_group_name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('azure:containerservice/getKubernetesCluster:getKubernetesCluster', __args__, opts=opts, typ=GetKubernetesClusterResult).value

    return AwaitableGetKubernetesClusterResult(
        addon_profiles=__ret__.addon_profiles,
        agent_pool_profiles=__ret__.agent_pool_profiles,
        api_server_authorized_ip_ranges=__ret__.api_server_authorized_ip_ranges,
        disk_encryption_set_id=__ret__.disk_encryption_set_id,
        dns_prefix=__ret__.dns_prefix,
        fqdn=__ret__.fqdn,
        id=__ret__.id,
        identities=__ret__.identities,
        kube_admin_config_raw=__ret__.kube_admin_config_raw,
        kube_admin_configs=__ret__.kube_admin_configs,
        kube_config_raw=__ret__.kube_config_raw,
        kube_configs=__ret__.kube_configs,
        kubelet_identities=__ret__.kubelet_identities,
        kubernetes_version=__ret__.kubernetes_version,
        linux_profiles=__ret__.linux_profiles,
        location=__ret__.location,
        name=__ret__.name,
        network_profiles=__ret__.network_profiles,
        node_resource_group=__ret__.node_resource_group,
        private_cluster_enabled=__ret__.private_cluster_enabled,
        private_fqdn=__ret__.private_fqdn,
        private_link_enabled=__ret__.private_link_enabled,
        resource_group_name=__ret__.resource_group_name,
        role_based_access_controls=__ret__.role_based_access_controls,
        service_principals=__ret__.service_principals,
        tags=__ret__.tags,
        windows_profiles=__ret__.windows_profiles)


@_utilities.lift_output_func(get_kubernetes_cluster)
def get_kubernetes_cluster_output(name: Optional[pulumi.Input[str]] = None,
                                  resource_group_name: Optional[pulumi.Input[str]] = None,
                                  opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetKubernetesClusterResult]:
    """
    Use this data source to access information about an existing Managed Kubernetes Cluster (AKS).

    ## Example Usage

    ```python
    import pulumi
    import pulumi_azure as azure

    example = azure.containerservice.get_kubernetes_cluster(name="myakscluster",
        resource_group_name="my-example-resource-group")
    ```


    :param str name: The name of the managed Kubernetes Cluster.
    :param str resource_group_name: The name of the Resource Group in which the managed Kubernetes Cluster exists.
    """
    ...
