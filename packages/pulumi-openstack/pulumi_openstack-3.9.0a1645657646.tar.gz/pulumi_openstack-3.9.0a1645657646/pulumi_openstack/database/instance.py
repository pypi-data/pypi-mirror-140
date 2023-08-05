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

__all__ = ['InstanceArgs', 'Instance']

@pulumi.input_type
class InstanceArgs:
    def __init__(__self__, *,
                 datastore: pulumi.Input['InstanceDatastoreArgs'],
                 size: pulumi.Input[int],
                 configuration_id: Optional[pulumi.Input[str]] = None,
                 databases: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]] = None,
                 flavor_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 networks: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]] = None):
        """
        The set of arguments for constructing a Instance resource.
        :param pulumi.Input['InstanceDatastoreArgs'] datastore: An array of database engine type and version. The datastore
               object structure is documented below. Changing this creates a new instance.
        :param pulumi.Input[int] size: Specifies the volume size in GB. Changing this creates new instance.
        :param pulumi.Input[str] configuration_id: Configuration ID to be attached to the instance. Database instance
               will be rebooted when configuration is detached.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]] databases: An array of database name, charset and collate. The database
               object structure is documented below.
        :param pulumi.Input[str] flavor_id: The flavor ID of the desired flavor for the instance.
               Changing this creates new instance.
        :param pulumi.Input[str] name: Database to be created on new instance. Changing this creates a
               new instance.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]] networks: An array of one or more networks to attach to the
               instance. The network object structure is documented below. Changing this
               creates a new instance.
        :param pulumi.Input[str] region: The region in which to create the db instance. Changing this
               creates a new instance.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]] users: An array of username, password, host and databases. The user
               object structure is documented below.
        """
        pulumi.set(__self__, "datastore", datastore)
        pulumi.set(__self__, "size", size)
        if configuration_id is not None:
            pulumi.set(__self__, "configuration_id", configuration_id)
        if databases is not None:
            pulumi.set(__self__, "databases", databases)
        if flavor_id is not None:
            pulumi.set(__self__, "flavor_id", flavor_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if networks is not None:
            pulumi.set(__self__, "networks", networks)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if users is not None:
            pulumi.set(__self__, "users", users)

    @property
    @pulumi.getter
    def datastore(self) -> pulumi.Input['InstanceDatastoreArgs']:
        """
        An array of database engine type and version. The datastore
        object structure is documented below. Changing this creates a new instance.
        """
        return pulumi.get(self, "datastore")

    @datastore.setter
    def datastore(self, value: pulumi.Input['InstanceDatastoreArgs']):
        pulumi.set(self, "datastore", value)

    @property
    @pulumi.getter
    def size(self) -> pulumi.Input[int]:
        """
        Specifies the volume size in GB. Changing this creates new instance.
        """
        return pulumi.get(self, "size")

    @size.setter
    def size(self, value: pulumi.Input[int]):
        pulumi.set(self, "size", value)

    @property
    @pulumi.getter(name="configurationId")
    def configuration_id(self) -> Optional[pulumi.Input[str]]:
        """
        Configuration ID to be attached to the instance. Database instance
        will be rebooted when configuration is detached.
        """
        return pulumi.get(self, "configuration_id")

    @configuration_id.setter
    def configuration_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "configuration_id", value)

    @property
    @pulumi.getter
    def databases(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]]:
        """
        An array of database name, charset and collate. The database
        object structure is documented below.
        """
        return pulumi.get(self, "databases")

    @databases.setter
    def databases(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]]):
        pulumi.set(self, "databases", value)

    @property
    @pulumi.getter(name="flavorId")
    def flavor_id(self) -> Optional[pulumi.Input[str]]:
        """
        The flavor ID of the desired flavor for the instance.
        Changing this creates new instance.
        """
        return pulumi.get(self, "flavor_id")

    @flavor_id.setter
    def flavor_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "flavor_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Database to be created on new instance. Changing this creates a
        new instance.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def networks(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]]:
        """
        An array of one or more networks to attach to the
        instance. The network object structure is documented below. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "networks")

    @networks.setter
    def networks(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]]):
        pulumi.set(self, "networks", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the db instance. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def users(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]]:
        """
        An array of username, password, host and databases. The user
        object structure is documented below.
        """
        return pulumi.get(self, "users")

    @users.setter
    def users(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]]):
        pulumi.set(self, "users", value)


@pulumi.input_type
class _InstanceState:
    def __init__(__self__, *,
                 addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 configuration_id: Optional[pulumi.Input[str]] = None,
                 databases: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]] = None,
                 datastore: Optional[pulumi.Input['InstanceDatastoreArgs']] = None,
                 flavor_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 networks: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 size: Optional[pulumi.Input[int]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]] = None):
        """
        Input properties used for looking up and filtering Instance resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] addresses: A list of IP addresses assigned to the instance.
        :param pulumi.Input[str] configuration_id: Configuration ID to be attached to the instance. Database instance
               will be rebooted when configuration is detached.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]] databases: An array of database name, charset and collate. The database
               object structure is documented below.
        :param pulumi.Input['InstanceDatastoreArgs'] datastore: An array of database engine type and version. The datastore
               object structure is documented below. Changing this creates a new instance.
        :param pulumi.Input[str] flavor_id: The flavor ID of the desired flavor for the instance.
               Changing this creates new instance.
        :param pulumi.Input[str] name: Database to be created on new instance. Changing this creates a
               new instance.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]] networks: An array of one or more networks to attach to the
               instance. The network object structure is documented below. Changing this
               creates a new instance.
        :param pulumi.Input[str] region: The region in which to create the db instance. Changing this
               creates a new instance.
        :param pulumi.Input[int] size: Specifies the volume size in GB. Changing this creates new instance.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]] users: An array of username, password, host and databases. The user
               object structure is documented below.
        """
        if addresses is not None:
            pulumi.set(__self__, "addresses", addresses)
        if configuration_id is not None:
            pulumi.set(__self__, "configuration_id", configuration_id)
        if databases is not None:
            pulumi.set(__self__, "databases", databases)
        if datastore is not None:
            pulumi.set(__self__, "datastore", datastore)
        if flavor_id is not None:
            pulumi.set(__self__, "flavor_id", flavor_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if networks is not None:
            pulumi.set(__self__, "networks", networks)
        if region is not None:
            pulumi.set(__self__, "region", region)
        if size is not None:
            pulumi.set(__self__, "size", size)
        if users is not None:
            pulumi.set(__self__, "users", users)

    @property
    @pulumi.getter
    def addresses(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of IP addresses assigned to the instance.
        """
        return pulumi.get(self, "addresses")

    @addresses.setter
    def addresses(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "addresses", value)

    @property
    @pulumi.getter(name="configurationId")
    def configuration_id(self) -> Optional[pulumi.Input[str]]:
        """
        Configuration ID to be attached to the instance. Database instance
        will be rebooted when configuration is detached.
        """
        return pulumi.get(self, "configuration_id")

    @configuration_id.setter
    def configuration_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "configuration_id", value)

    @property
    @pulumi.getter
    def databases(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]]:
        """
        An array of database name, charset and collate. The database
        object structure is documented below.
        """
        return pulumi.get(self, "databases")

    @databases.setter
    def databases(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceDatabaseArgs']]]]):
        pulumi.set(self, "databases", value)

    @property
    @pulumi.getter
    def datastore(self) -> Optional[pulumi.Input['InstanceDatastoreArgs']]:
        """
        An array of database engine type and version. The datastore
        object structure is documented below. Changing this creates a new instance.
        """
        return pulumi.get(self, "datastore")

    @datastore.setter
    def datastore(self, value: Optional[pulumi.Input['InstanceDatastoreArgs']]):
        pulumi.set(self, "datastore", value)

    @property
    @pulumi.getter(name="flavorId")
    def flavor_id(self) -> Optional[pulumi.Input[str]]:
        """
        The flavor ID of the desired flavor for the instance.
        Changing this creates new instance.
        """
        return pulumi.get(self, "flavor_id")

    @flavor_id.setter
    def flavor_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "flavor_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Database to be created on new instance. Changing this creates a
        new instance.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def networks(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]]:
        """
        An array of one or more networks to attach to the
        instance. The network object structure is documented below. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "networks")

    @networks.setter
    def networks(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceNetworkArgs']]]]):
        pulumi.set(self, "networks", value)

    @property
    @pulumi.getter
    def region(self) -> Optional[pulumi.Input[str]]:
        """
        The region in which to create the db instance. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "region")

    @region.setter
    def region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "region", value)

    @property
    @pulumi.getter
    def size(self) -> Optional[pulumi.Input[int]]:
        """
        Specifies the volume size in GB. Changing this creates new instance.
        """
        return pulumi.get(self, "size")

    @size.setter
    def size(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "size", value)

    @property
    @pulumi.getter
    def users(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]]:
        """
        An array of username, password, host and databases. The user
        object structure is documented below.
        """
        return pulumi.get(self, "users")

    @users.setter
    def users(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceUserArgs']]]]):
        pulumi.set(self, "users", value)


class Instance(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration_id: Optional[pulumi.Input[str]] = None,
                 databases: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceDatabaseArgs']]]]] = None,
                 datastore: Optional[pulumi.Input[pulumi.InputType['InstanceDatastoreArgs']]] = None,
                 flavor_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 networks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceNetworkArgs']]]]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 size: Optional[pulumi.Input[int]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceUserArgs']]]]] = None,
                 __props__=None):
        """
        Create a Instance resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] configuration_id: Configuration ID to be attached to the instance. Database instance
               will be rebooted when configuration is detached.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceDatabaseArgs']]]] databases: An array of database name, charset and collate. The database
               object structure is documented below.
        :param pulumi.Input[pulumi.InputType['InstanceDatastoreArgs']] datastore: An array of database engine type and version. The datastore
               object structure is documented below. Changing this creates a new instance.
        :param pulumi.Input[str] flavor_id: The flavor ID of the desired flavor for the instance.
               Changing this creates new instance.
        :param pulumi.Input[str] name: Database to be created on new instance. Changing this creates a
               new instance.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceNetworkArgs']]]] networks: An array of one or more networks to attach to the
               instance. The network object structure is documented below. Changing this
               creates a new instance.
        :param pulumi.Input[str] region: The region in which to create the db instance. Changing this
               creates a new instance.
        :param pulumi.Input[int] size: Specifies the volume size in GB. Changing this creates new instance.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceUserArgs']]]] users: An array of username, password, host and databases. The user
               object structure is documented below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: InstanceArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Create a Instance resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param InstanceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InstanceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration_id: Optional[pulumi.Input[str]] = None,
                 databases: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceDatabaseArgs']]]]] = None,
                 datastore: Optional[pulumi.Input[pulumi.InputType['InstanceDatastoreArgs']]] = None,
                 flavor_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 networks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceNetworkArgs']]]]] = None,
                 region: Optional[pulumi.Input[str]] = None,
                 size: Optional[pulumi.Input[int]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceUserArgs']]]]] = None,
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
            __props__ = InstanceArgs.__new__(InstanceArgs)

            __props__.__dict__["configuration_id"] = configuration_id
            __props__.__dict__["databases"] = databases
            if datastore is None and not opts.urn:
                raise TypeError("Missing required property 'datastore'")
            __props__.__dict__["datastore"] = datastore
            __props__.__dict__["flavor_id"] = flavor_id
            __props__.__dict__["name"] = name
            __props__.__dict__["networks"] = networks
            __props__.__dict__["region"] = region
            if size is None and not opts.urn:
                raise TypeError("Missing required property 'size'")
            __props__.__dict__["size"] = size
            __props__.__dict__["users"] = users
            __props__.__dict__["addresses"] = None
        super(Instance, __self__).__init__(
            'openstack:database/instance:Instance',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            addresses: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            configuration_id: Optional[pulumi.Input[str]] = None,
            databases: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceDatabaseArgs']]]]] = None,
            datastore: Optional[pulumi.Input[pulumi.InputType['InstanceDatastoreArgs']]] = None,
            flavor_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            networks: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceNetworkArgs']]]]] = None,
            region: Optional[pulumi.Input[str]] = None,
            size: Optional[pulumi.Input[int]] = None,
            users: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceUserArgs']]]]] = None) -> 'Instance':
        """
        Get an existing Instance resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] addresses: A list of IP addresses assigned to the instance.
        :param pulumi.Input[str] configuration_id: Configuration ID to be attached to the instance. Database instance
               will be rebooted when configuration is detached.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceDatabaseArgs']]]] databases: An array of database name, charset and collate. The database
               object structure is documented below.
        :param pulumi.Input[pulumi.InputType['InstanceDatastoreArgs']] datastore: An array of database engine type and version. The datastore
               object structure is documented below. Changing this creates a new instance.
        :param pulumi.Input[str] flavor_id: The flavor ID of the desired flavor for the instance.
               Changing this creates new instance.
        :param pulumi.Input[str] name: Database to be created on new instance. Changing this creates a
               new instance.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceNetworkArgs']]]] networks: An array of one or more networks to attach to the
               instance. The network object structure is documented below. Changing this
               creates a new instance.
        :param pulumi.Input[str] region: The region in which to create the db instance. Changing this
               creates a new instance.
        :param pulumi.Input[int] size: Specifies the volume size in GB. Changing this creates new instance.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceUserArgs']]]] users: An array of username, password, host and databases. The user
               object structure is documented below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _InstanceState.__new__(_InstanceState)

        __props__.__dict__["addresses"] = addresses
        __props__.__dict__["configuration_id"] = configuration_id
        __props__.__dict__["databases"] = databases
        __props__.__dict__["datastore"] = datastore
        __props__.__dict__["flavor_id"] = flavor_id
        __props__.__dict__["name"] = name
        __props__.__dict__["networks"] = networks
        __props__.__dict__["region"] = region
        __props__.__dict__["size"] = size
        __props__.__dict__["users"] = users
        return Instance(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def addresses(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of IP addresses assigned to the instance.
        """
        return pulumi.get(self, "addresses")

    @property
    @pulumi.getter(name="configurationId")
    def configuration_id(self) -> pulumi.Output[Optional[str]]:
        """
        Configuration ID to be attached to the instance. Database instance
        will be rebooted when configuration is detached.
        """
        return pulumi.get(self, "configuration_id")

    @property
    @pulumi.getter
    def databases(self) -> pulumi.Output[Optional[Sequence['outputs.InstanceDatabase']]]:
        """
        An array of database name, charset and collate. The database
        object structure is documented below.
        """
        return pulumi.get(self, "databases")

    @property
    @pulumi.getter
    def datastore(self) -> pulumi.Output['outputs.InstanceDatastore']:
        """
        An array of database engine type and version. The datastore
        object structure is documented below. Changing this creates a new instance.
        """
        return pulumi.get(self, "datastore")

    @property
    @pulumi.getter(name="flavorId")
    def flavor_id(self) -> pulumi.Output[str]:
        """
        The flavor ID of the desired flavor for the instance.
        Changing this creates new instance.
        """
        return pulumi.get(self, "flavor_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Database to be created on new instance. Changing this creates a
        new instance.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def networks(self) -> pulumi.Output[Optional[Sequence['outputs.InstanceNetwork']]]:
        """
        An array of one or more networks to attach to the
        instance. The network object structure is documented below. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "networks")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        """
        The region in which to create the db instance. Changing this
        creates a new instance.
        """
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def size(self) -> pulumi.Output[int]:
        """
        Specifies the volume size in GB. Changing this creates new instance.
        """
        return pulumi.get(self, "size")

    @property
    @pulumi.getter
    def users(self) -> pulumi.Output[Optional[Sequence['outputs.InstanceUser']]]:
        """
        An array of username, password, host and databases. The user
        object structure is documented below.
        """
        return pulumi.get(self, "users")

