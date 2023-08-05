# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['SecurityGroupArgs', 'SecurityGroup']

@pulumi.input_type
class SecurityGroupArgs:
    def __init__(__self__, *,
                 security_group_names: pulumi.Input[Sequence[pulumi.Input[str]]],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a SecurityGroup resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] security_group_names: List of EC2 security group names to be
               authorized for ingress to the cache security group
        :param pulumi.Input[str] description: description for the cache security group. Defaults to "Managed by Pulumi".
        :param pulumi.Input[str] name: Name for the cache security group. This value is stored as a lowercase string.
        """
        pulumi.set(__self__, "security_group_names", security_group_names)
        if description is None:
            description = 'Managed by Pulumi'
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="securityGroupNames")
    def security_group_names(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        List of EC2 security group names to be
        authorized for ingress to the cache security group
        """
        return pulumi.get(self, "security_group_names")

    @security_group_names.setter
    def security_group_names(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "security_group_names", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        description for the cache security group. Defaults to "Managed by Pulumi".
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name for the cache security group. This value is stored as a lowercase string.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class _SecurityGroupState:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 security_group_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering SecurityGroup resources.
        :param pulumi.Input[str] description: description for the cache security group. Defaults to "Managed by Pulumi".
        :param pulumi.Input[str] name: Name for the cache security group. This value is stored as a lowercase string.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] security_group_names: List of EC2 security group names to be
               authorized for ingress to the cache security group
        """
        if description is None:
            description = 'Managed by Pulumi'
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if security_group_names is not None:
            pulumi.set(__self__, "security_group_names", security_group_names)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        description for the cache security group. Defaults to "Managed by Pulumi".
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name for the cache security group. This value is stored as a lowercase string.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="securityGroupNames")
    def security_group_names(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of EC2 security group names to be
        authorized for ingress to the cache security group
        """
        return pulumi.get(self, "security_group_names")

    @security_group_names.setter
    def security_group_names(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "security_group_names", value)


class SecurityGroup(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 security_group_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides an ElastiCache Security Group to control access to one or more cache
        clusters.

        > **NOTE:** ElastiCache Security Groups are for use only when working with an
        ElastiCache cluster **outside** of a VPC. If you are using a VPC, see the
        ElastiCache Subnet Group resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        bar_security_group = aws.ec2.SecurityGroup("barSecurityGroup")
        bar_elasticache_security_group_security_group = aws.elasticache.SecurityGroup("barElasticache/securityGroupSecurityGroup", security_group_names=[bar_security_group.name])
        ```

        ## Import

        ElastiCache Security Groups can be imported by name, e.g.,

        ```sh
         $ pulumi import aws:elasticache/securityGroup:SecurityGroup my_ec_security_group ec-security-group-1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: description for the cache security group. Defaults to "Managed by Pulumi".
        :param pulumi.Input[str] name: Name for the cache security group. This value is stored as a lowercase string.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] security_group_names: List of EC2 security group names to be
               authorized for ingress to the cache security group
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SecurityGroupArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an ElastiCache Security Group to control access to one or more cache
        clusters.

        > **NOTE:** ElastiCache Security Groups are for use only when working with an
        ElastiCache cluster **outside** of a VPC. If you are using a VPC, see the
        ElastiCache Subnet Group resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        bar_security_group = aws.ec2.SecurityGroup("barSecurityGroup")
        bar_elasticache_security_group_security_group = aws.elasticache.SecurityGroup("barElasticache/securityGroupSecurityGroup", security_group_names=[bar_security_group.name])
        ```

        ## Import

        ElastiCache Security Groups can be imported by name, e.g.,

        ```sh
         $ pulumi import aws:elasticache/securityGroup:SecurityGroup my_ec_security_group ec-security-group-1
        ```

        :param str resource_name: The name of the resource.
        :param SecurityGroupArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SecurityGroupArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 security_group_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
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
            __props__ = SecurityGroupArgs.__new__(SecurityGroupArgs)

            if description is None:
                description = 'Managed by Pulumi'
            __props__.__dict__["description"] = description
            __props__.__dict__["name"] = name
            if security_group_names is None and not opts.urn:
                raise TypeError("Missing required property 'security_group_names'")
            __props__.__dict__["security_group_names"] = security_group_names
        super(SecurityGroup, __self__).__init__(
            'aws:elasticache/securityGroup:SecurityGroup',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            description: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            security_group_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'SecurityGroup':
        """
        Get an existing SecurityGroup resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: description for the cache security group. Defaults to "Managed by Pulumi".
        :param pulumi.Input[str] name: Name for the cache security group. This value is stored as a lowercase string.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] security_group_names: List of EC2 security group names to be
               authorized for ingress to the cache security group
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SecurityGroupState.__new__(_SecurityGroupState)

        __props__.__dict__["description"] = description
        __props__.__dict__["name"] = name
        __props__.__dict__["security_group_names"] = security_group_names
        return SecurityGroup(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[str]:
        """
        description for the cache security group. Defaults to "Managed by Pulumi".
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Name for the cache security group. This value is stored as a lowercase string.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="securityGroupNames")
    def security_group_names(self) -> pulumi.Output[Sequence[str]]:
        """
        List of EC2 security group names to be
        authorized for ingress to the cache security group
        """
        return pulumi.get(self, "security_group_names")

