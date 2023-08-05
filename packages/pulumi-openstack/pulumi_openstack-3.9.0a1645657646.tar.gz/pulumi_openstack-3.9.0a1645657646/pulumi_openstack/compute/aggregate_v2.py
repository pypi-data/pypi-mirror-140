# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['AggregateV2Args', 'AggregateV2']

@pulumi.input_type
class AggregateV2Args:
    def __init__(__self__, *,
                 hosts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 metadata: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 zone: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a AggregateV2 resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] hosts: The list of hosts contained in the Host Aggregate. The hosts must be added
               to Openstack and visible in the web interface, or the provider will fail to add them to the host
               aggregate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] metadata: The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        :param pulumi.Input[str] name: The name of the Host Aggregate
        :param pulumi.Input[str] region: The region in which to create the Host Aggregate. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new Host Aggregate.
        :param pulumi.Input[str] zone: The name of the Availability Zone to use. If ommited, it will take the default
               availability zone.
        """
        if hosts is not None:
            pulumi.set(__self__, "hosts", hosts)
        if metadata is not None:
            pulumi.set(__self__, "metadata", metadata)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if zone is not None:
            pulumi.set(__self__, "zone", zone)

    @property
    @pulumi.getter
    def hosts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The list of hosts contained in the Host Aggregate. The hosts must be added
        to Openstack and visible in the web interface, or the provider will fail to add them to the host
        aggregate.
        """
        return pulumi.get(self, "hosts")

    @hosts.setter
    def hosts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "hosts", value)

    @property
    @pulumi.getter
    def metadata(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        """
        return pulumi.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "metadata", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Host Aggregate
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the Host Aggregate. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new Host Aggregate.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def zone(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Availability Zone to use. If ommited, it will take the default
        availability zone.
        """
        return pulumi.get(self, "zone")

    @zone.setter
    def zone(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zone", value)


@pulumi.input_type
class _AggregateV2State:
    def __init__(__self__, *,
                 hosts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 metadata: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 zone: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering AggregateV2 resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] hosts: The list of hosts contained in the Host Aggregate. The hosts must be added
               to Openstack and visible in the web interface, or the provider will fail to add them to the host
               aggregate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] metadata: The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        :param pulumi.Input[str] name: The name of the Host Aggregate
        :param pulumi.Input[str] region: The region in which to create the Host Aggregate. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new Host Aggregate.
        :param pulumi.Input[str] zone: The name of the Availability Zone to use. If ommited, it will take the default
               availability zone.
        """
        if hosts is not None:
            pulumi.set(__self__, "hosts", hosts)
        if metadata is not None:
            pulumi.set(__self__, "metadata", metadata)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if zone is not None:
            pulumi.set(__self__, "zone", zone)

    @property
    @pulumi.getter
    def hosts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The list of hosts contained in the Host Aggregate. The hosts must be added
        to Openstack and visible in the web interface, or the provider will fail to add them to the host
        aggregate.
        """
        return pulumi.get(self, "hosts")

    @hosts.setter
    def hosts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "hosts", value)

    @property
    @pulumi.getter
    def metadata(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        """
        return pulumi.get(self, "metadata")

    @metadata.setter
    def metadata(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "metadata", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Host Aggregate
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the Host Aggregate. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new Host Aggregate.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def zone(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Availability Zone to use. If ommited, it will take the default
        availability zone.
        """
        return pulumi.get(self, "zone")

    @zone.setter
    def zone(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zone", value)


class AggregateV2(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 hosts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 metadata: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 zone: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Host Aggregate within Openstack Nova.

        ## Example Usage
        ### Full example

        ```python
        import pulumi
        import pulumi_openstack as openstack

        dell_servers = openstack.compute.AggregateV2("dellServers",
            hosts=[
                "myhost01.example.com",
                "myhost02.example.com",
            ],
            metadata={
                "cpus": "56",
            },
            region="RegionOne",
            zone="nova")
        ```
        ### Minimum required example

        ```python
        import pulumi
        import pulumi_openstack as openstack

        test = openstack.compute.AggregateV2("test")
        ```

        ## Import

        You can import an existing Host Aggregate by their ID.

        ```sh
         $ pulumi import openstack:compute/aggregateV2:AggregateV2 myaggregate 24
        ```

         The ID can be obtained with an openstack command$ openstack aggregate list +----+------+-------------------+ | ID | Name | Availability Zone | +----+------+-------------------+ | 59 | test | None

        | +----+------+-------------------+

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] hosts: The list of hosts contained in the Host Aggregate. The hosts must be added
               to Openstack and visible in the web interface, or the provider will fail to add them to the host
               aggregate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] metadata: The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        :param pulumi.Input[str] name: The name of the Host Aggregate
        :param pulumi.Input[str] region: The region in which to create the Host Aggregate. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new Host Aggregate.
        :param pulumi.Input[str] zone: The name of the Availability Zone to use. If ommited, it will take the default
               availability zone.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[AggregateV2Args] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Host Aggregate within Openstack Nova.

        ## Example Usage
        ### Full example

        ```python
        import pulumi
        import pulumi_openstack as openstack

        dell_servers = openstack.compute.AggregateV2("dellServers",
            hosts=[
                "myhost01.example.com",
                "myhost02.example.com",
            ],
            metadata={
                "cpus": "56",
            },
            region="RegionOne",
            zone="nova")
        ```
        ### Minimum required example

        ```python
        import pulumi
        import pulumi_openstack as openstack

        test = openstack.compute.AggregateV2("test")
        ```

        ## Import

        You can import an existing Host Aggregate by their ID.

        ```sh
         $ pulumi import openstack:compute/aggregateV2:AggregateV2 myaggregate 24
        ```

         The ID can be obtained with an openstack command$ openstack aggregate list +----+------+-------------------+ | ID | Name | Availability Zone | +----+------+-------------------+ | 59 | test | None

        | +----+------+-------------------+

        :param str resource_name: The name of the resource.
        :param AggregateV2Args args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AggregateV2Args, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 hosts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 metadata: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 zone: Optional[pulumi.Input[str]] = None,
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
            __props__ = AggregateV2Args.__new__(AggregateV2Args)

            __props__.__dict__["hosts"] = hosts
            __props__.__dict__["metadata"] = metadata
            __props__.__dict__["name"] = name
            __props__.__dict__["region"] = region
            __props__.__dict__["zone"] = zone
        super(AggregateV2, __self__).__init__(
            'openstack:compute/aggregateV2:AggregateV2',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            hosts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            metadata: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            name: Optional[pulumi.Input[str]] = None,
            region: Optional[pulumi.Input[str]] = None,
            zone: Optional[pulumi.Input[str]] = None) -> 'AggregateV2':
        """
        Get an existing AggregateV2 resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] hosts: The list of hosts contained in the Host Aggregate. The hosts must be added
               to Openstack and visible in the web interface, or the provider will fail to add them to the host
               aggregate.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] metadata: The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        :param pulumi.Input[str] name: The name of the Host Aggregate
        :param pulumi.Input[str] region: The region in which to create the Host Aggregate. If
               omitted, the `region` argument of the provider is used. Changing this
               creates a new Host Aggregate.
        :param pulumi.Input[str] zone: The name of the Availability Zone to use. If ommited, it will take the default
               availability zone.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AggregateV2State.__new__(_AggregateV2State)

        __props__.__dict__["hosts"] = hosts
        __props__.__dict__["metadata"] = metadata
        __props__.__dict__["name"] = name
        __props__.__dict__["region"] = region
        __props__.__dict__["zone"] = zone
        return AggregateV2(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def hosts(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        The list of hosts contained in the Host Aggregate. The hosts must be added
        to Openstack and visible in the web interface, or the provider will fail to add them to the host
        aggregate.
        """
        return pulumi.get(self, "hosts")

    @property
    @pulumi.getter
    def metadata(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        The metadata of the Host Aggregate. Can be useful to indicate scheduler hints.
        """
        return pulumi.get(self, "metadata")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the Host Aggregate
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to create the Host Aggregate. If
        omitted, the `region` argument of the provider is used. Changing this
        creates a new Host Aggregate.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def zone(self) -> pulumi.Output[Optional[str]]:
        """
        The name of the Availability Zone to use. If ommited, it will take the default
        availability zone.
        """
        return pulumi.get(self, "zone")

