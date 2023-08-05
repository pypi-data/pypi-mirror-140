# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetQosPolicyResult',
    'AwaitableGetQosPolicyResult',
    'get_qos_policy',
    'get_qos_policy_output',
]

@pulumi.output_type
class GetQosPolicyResult:
    """
    A collection of values returned by getQosPolicy.
    """
    def __init__(__self__, all_tags=None, created_at=None, description=None, id=None, is_default=None, name=None, project_id=None, region=None, revision_number=None, shared=None, tags=None, updated_at=None):
        if all_tags and not isinstance(all_tags, list):
            raise TypeError("Expected argument 'all_tags' to be a list")
        pulumi.set(__self__, "all_tags", all_tags)
        if created_at and not isinstance(created_at, str):
            raise TypeError("Expected argument 'created_at' to be a str")
        pulumi.set(__self__, "created_at", created_at)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if is_default and not isinstance(is_default, bool):
            raise TypeError("Expected argument 'is_default' to be a bool")
        pulumi.set(__self__, "is_default", is_default)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if project_id and not isinstance(project_id, str):
            raise TypeError("Expected argument 'project_id' to be a str")
        pulumi.set(__self__, "project_id", project_id)
        if region and not isinstance(region, str):
            raise TypeError("Expected argument 'region' to be a str")
        pulumi.set(__self__, "region", region)
        if revision_number and not isinstance(revision_number, int):
            raise TypeError("Expected argument 'revision_number' to be a int")
        pulumi.set(__self__, "revision_number", revision_number)
        if shared and not isinstance(shared, bool):
            raise TypeError("Expected argument 'shared' to be a bool")
        pulumi.set(__self__, "shared", shared)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)
        if updated_at and not isinstance(updated_at, str):
            raise TypeError("Expected argument 'updated_at' to be a str")
        pulumi.set(__self__, "updated_at", updated_at)

    @property
    @pulumi.getter(name="allTags")
    def all_tags(self) -> Sequence[str]:
        """
        The set of string tags applied on the QoS policy.
        """
        return pulumi.get(self, "all_tags")

    @property
    @pulumi.getter(name="createdAt")
    def created_at(self) -> str:
        """
        The time at which QoS policy was created.
        """
        return pulumi.get(self, "created_at")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="isDefault")
    def is_default(self) -> bool:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "is_default")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> str:
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter
    def region(self) -> str:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter(name="revisionNumber")
    def revision_number(self) -> int:
        """
        The revision number of the QoS policy.
        """
        return pulumi.get(self, "revision_number")

    @property
    @pulumi.getter
    def shared(self) -> bool:
        """
        See Argument Reference above.
        """
        return pulumi.get(self, "shared")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="updatedAt")
    def updated_at(self) -> str:
        """
        The time at which QoS policy was created.
        """
        return pulumi.get(self, "updated_at")


class AwaitableGetQosPolicyResult(GetQosPolicyResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetQosPolicyResult(
            all_tags=self.all_tags,
            created_at=self.created_at,
            description=self.description,
            id=self.id,
            is_default=self.is_default,
            name=self.name,
            project_id=self.project_id,
            region=self.region,
            revision_number=self.revision_number,
            shared=self.shared,
            tags=self.tags,
            updated_at=self.updated_at)


def get_qos_policy(description: Optional[str] = None,
                   is_default: Optional[bool] = None,
                   name: Optional[str] = None,
                   project_id: Optional[str] = None,
                   region: Optional[str] = None,
                   shared: Optional[bool] = None,
                   tags: Optional[Sequence[str]] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetQosPolicyResult:
    """
    Use this data source to get the ID of an available OpenStack QoS policy.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    qos_policy1 = openstack.networking.get_qos_policy(name="qos_policy_1")
    ```


    :param str description: The human-readable description for the QoS policy.
    :param bool is_default: Whether the QoS policy is default policy or not.
    :param str name: The name of the QoS policy.
    :param str project_id: The owner of the QoS policy.
    :param str region: The region in which to obtain the V2 Networking client.
           A Networking client is needed to retrieve a QoS policy ID. If omitted, the
           `region` argument of the provider is used.
    :param bool shared: Whether this QoS policy is shared across all projects.
    :param Sequence[str] tags: The list of QoS policy tags to filter.
    """
    __args__ = dict()
    __args__['description'] = description
    __args__['isDefault'] = is_default
    __args__['name'] = name
    __args__['projectId'] = project_id
    __args__['region'] = region
    __args__['shared'] = shared
    __args__['tags'] = tags
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('openstack:networking/getQosPolicy:getQosPolicy', __args__, opts=opts, typ=GetQosPolicyResult).value

    return AwaitableGetQosPolicyResult(
        all_tags=__ret__.all_tags,
        created_at=__ret__.created_at,
        description=__ret__.description,
        id=__ret__.id,
        is_default=__ret__.is_default,
        name=__ret__.name,
        project_id=__ret__.project_id,
        region=__ret__.region,
        revision_number=__ret__.revision_number,
        shared=__ret__.shared,
        tags=__ret__.tags,
        updated_at=__ret__.updated_at)


@_utilities.lift_output_func(get_qos_policy)
def get_qos_policy_output(description: Optional[pulumi.Input[Optional[str]]] = None,
                          is_default: Optional[pulumi.Input[Optional[bool]]] = None,
                          name: Optional[pulumi.Input[Optional[str]]] = None,
                          project_id: Optional[pulumi.Input[Optional[str]]] = None,
                          region: Optional[pulumi.Input[Optional[str]]] = None,
                          shared: Optional[pulumi.Input[Optional[bool]]] = None,
                          tags: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetQosPolicyResult]:
    """
    Use this data source to get the ID of an available OpenStack QoS policy.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_openstack as openstack

    qos_policy1 = openstack.networking.get_qos_policy(name="qos_policy_1")
    ```


    :param str description: The human-readable description for the QoS policy.
    :param bool is_default: Whether the QoS policy is default policy or not.
    :param str name: The name of the QoS policy.
    :param str project_id: The owner of the QoS policy.
    :param str region: The region in which to obtain the V2 Networking client.
           A Networking client is needed to retrieve a QoS policy ID. If omitted, the
           `region` argument of the provider is used.
    :param bool shared: Whether this QoS policy is shared across all projects.
    :param Sequence[str] tags: The list of QoS policy tags to filter.
    """
    ...
