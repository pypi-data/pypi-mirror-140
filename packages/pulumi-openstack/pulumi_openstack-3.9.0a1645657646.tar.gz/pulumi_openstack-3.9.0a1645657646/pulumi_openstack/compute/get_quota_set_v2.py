# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetQuotaSetV2Result',
    'AwaitableGetQuotaSetV2Result',
    'get_quota_set_v2',
    'get_quota_set_v2_output',
]

@pulumi.output_type
class GetQuotaSetV2Result:
    """
    A collection of values returned by getQuotaSetV2.
    """
    def __init__(__self__, cores=None, fixed_ips=None, floating_ips=None, id=None, injected_file_content_bytes=None, injected_file_path_bytes=None, injected_files=None, instances=None, key_pairs=None, metadata_items=None, project_id=None, ram=None, region=None, security_group_rules=None, security_groups=None, server_group_members=None, server_groups=None):
        if cores and not isinstance(cores, int):
            raise TypeError("Expected argument 'cores' to be a int")
        pulumi.set(__self__, "cores", cores)
        if fixed_ips and not isinstance(fixed_ips, int):
            raise TypeError("Expected argument 'fixed_ips' to be a int")
        pulumi.set(__self__, "fixed_ips", fixed_ips)
        if floating_ips and not isinstance(floating_ips, int):
            raise TypeError("Expected argument 'floating_ips' to be a int")
        pulumi.set(__self__, "floating_ips", floating_ips)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if injected_file_content_bytes and not isinstance(injected_file_content_bytes, int):
            raise TypeError("Expected argument 'injected_file_content_bytes' to be a int")
        pulumi.set(__self__, "injected_file_content_bytes", injected_file_content_bytes)
        if injected_file_path_bytes and not isinstance(injected_file_path_bytes, int):
            raise TypeError("Expected argument 'injected_file_path_bytes' to be a int")
        pulumi.set(__self__, "injected_file_path_bytes", injected_file_path_bytes)
        if injected_files and not isinstance(injected_files, int):
            raise TypeError("Expected argument 'injected_files' to be a int")
        pulumi.set(__self__, "injected_files", injected_files)
        if instances and not isinstance(instances, int):
            raise TypeError("Expected argument 'instances' to be a int")
        pulumi.set(__self__, "instances", instances)
        if key_pairs and not isinstance(key_pairs, int):
            raise TypeError("Expected argument 'key_pairs' to be a int")
        pulumi.set(__self__, "key_pairs", key_pairs)
        if metadata_items and not isinstance(metadata_items, int):
            raise TypeError("Expected argument 'metadata_items' to be a int")
        pulumi.set(__self__, "metadata_items", metadata_items)
        if project_id and not isinstance(project_id, str):
            raise TypeError("Expected argument 'project_id' to be a str")
        pulumi.set(__self__, "project_id", project_id)
        if ram and not isinstance(ram, int):
            raise TypeError("Expected argument 'ram' to be a int")
        pulumi.set(__self__, "ram", ram)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if security_group_rules and not isinstance(security_group_rules, int):
            raise TypeError("Expected argument 'security_group_rules' to be a int")
        pulumi.set(__self__, "security_group_rules", security_group_rules)
        if security_groups and not isinstance(security_groups, int):
            raise TypeError("Expected argument 'security_groups' to be a int")
        pulumi.set(__self__, "security_groups", security_groups)
        if server_group_members and not isinstance(server_group_members, int):
            raise TypeError("Expected argument 'server_group_members' to be a int")
        pulumi.set(__self__, "server_group_members", server_group_members)
        if server_groups and not isinstance(server_groups, int):
            raise TypeError("Expected argument 'server_groups' to be a int")
        pulumi.set(__self__, "server_groups", server_groups)

    @property
    @pulumi.getter
    def cores(self) -> int:
        """
        The number of allowed server cores.
        """
        return pulumi.get(self, "cores")

    @property
    @pulumi.getter(name="fixedIps")
    def fixed_ips(self) -> int:
        """
        The number of allowed fixed IP addresses. Available until version 2.35.
        """
        return pulumi.get(self, "fixed_ips")

    @property
    @pulumi.getter(name="floatingIps")
    def floating_ips(self) -> int:
        """
        The number of allowed floating IP addresses. Available until version 2.35.
        """
        return pulumi.get(self, "floating_ips")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="injectedFileContentBytes")
    def injected_file_content_bytes(self) -> int:
        """
        The number of allowed bytes of content for each injected file. Available until version 2.56.
        """
        return pulumi.get(self, "injected_file_content_bytes")

    @property
    @pulumi.getter(name="injectedFilePathBytes")
    def injected_file_path_bytes(self) -> int:
        """
        The number of allowed bytes for each injected file path. Available until version 2.56.
        """
        return pulumi.get(self, "injected_file_path_bytes")

    @property
    @pulumi.getter(name="injectedFiles")
    def injected_files(self) -> int:
        """
        The number of allowed injected files. Available until version 2.56.
        """
        return pulumi.get(self, "injected_files")

    @property
    @pulumi.getter
    def instances(self) -> int:
        """
        The number of allowed servers.
        """
        return pulumi.get(self, "instances")

    @property
    @pulumi.getter(name="keyPairs")
    def key_pairs(self) -> int:
        """
        The number of allowed key pairs for each user.
        """
        return pulumi.get(self, "key_pairs")

    @property
    @pulumi.getter(name="metadataItems")
    def metadata_items(self) -> int:
        """
        The number of allowed metadata items for each server.
        """
        return pulumi.get(self, "metadata_items")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter
    def ram(self) -> int:
        """
        The amount of allowed server RAM, in MiB.
        """
        return pulumi.get(self, "ram")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="securityGroupRules")
    def security_group_rules(self) -> int:
        """
        The number of allowed rules for each security group. Available until version 2.35.
        """
        return pulumi.get(self, "security_group_rules")

    @property
    @pulumi.getter(name="securityGroups")
    def security_groups(self) -> int:
        """
        The number of allowed security groups. Available until version 2.35.
        """
        return pulumi.get(self, "security_groups")

    @property
    @pulumi.getter(name="serverGroupMembers")
    def server_group_members(self) -> int:
        """
        The number of allowed members for each server group.
        """
        return pulumi.get(self, "server_group_members")

    @property
    @pulumi.getter(name="serverGroups")
    def server_groups(self) -> int:
        """
        The number of allowed server groups.
        """
        return pulumi.get(self, "server_groups")


class AwaitableGetQuotaSetV2Result(GetQuotaSetV2Result):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetQuotaSetV2Result(
            cores=self.cores,
            fixed_ips=self.fixed_ips,
            floating_ips=self.floating_ips,
            id=self.id,
            injected_file_content_bytes=self.injected_file_content_bytes,
            injected_file_path_bytes=self.injected_file_path_bytes,
            injected_files=self.injected_files,
            instances=self.instances,
            key_pairs=self.key_pairs,
            metadata_items=self.metadata_items,
            project_id=self.project_id,
            ram=self.ram,
            region=self.region,
            security_group_rules=self.security_group_rules,
            security_groups=self.security_groups,
            server_group_members=self.server_group_members,
            server_groups=self.server_groups)


def get_quota_set_v2(project_id: Optional[str] = None,
                     region: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetQuotaSetV2Result:
    """
    Use this data source to get the compute quotaset of an OpenStack project.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    quota = openstack.compute.get_quota_set_v2(project_id="2e367a3d29f94fd988e6ec54e305ec9d")
    ```


    :param str project_id: The id of the project to retrieve the quotaset.
    :param str region: The region in which to obtain the V2 Compute client.
           If omitted, the `region` argument of the provider is used.
    """
    __args__ = dict()
    __args__['projectId'] = project_id
    __args__['region'] = region
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('openstack:compute/getQuotaSetV2:getQuotaSetV2', __args__, opts=opts, typ=GetQuotaSetV2Result).value

    return AwaitableGetQuotaSetV2Result(
        cores=__ret__.cores,
        fixed_ips=__ret__.fixed_ips,
        floating_ips=__ret__.floating_ips,
        id=__ret__.id,
        injected_file_content_bytes=__ret__.injected_file_content_bytes,
        injected_file_path_bytes=__ret__.injected_file_path_bytes,
        injected_files=__ret__.injected_files,
        instances=__ret__.instances,
        key_pairs=__ret__.key_pairs,
        metadata_items=__ret__.metadata_items,
        project_id=__ret__.project_id,
        ram=__ret__.ram,
        region=__ret__.region,
        security_group_rules=__ret__.security_group_rules,
        security_groups=__ret__.security_groups,
        server_group_members=__ret__.server_group_members,
        server_groups=__ret__.server_groups)


@_utilities.lift_output_func(get_quota_set_v2)
def get_quota_set_v2_output(project_id: Optional[pulumi.Input[str]] = None,
                            region: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetQuotaSetV2Result]:
    """
    Use this data source to get the compute quotaset of an OpenStack project.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    quota = openstack.compute.get_quota_set_v2(project_id="2e367a3d29f94fd988e6ec54e305ec9d")
    ```


    :param str project_id: The id of the project to retrieve the quotaset.
    :param str region: The region in which to obtain the V2 Compute client.
           If omitted, the `region` argument of the provider is used.
    """
    ...
