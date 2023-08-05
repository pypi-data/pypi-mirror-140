# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['DeploymentStrategyArgs', 'DeploymentStrategy']

@pulumi.input_type
class DeploymentStrategyArgs:
    def __init__(__self__, *,
                 deployment_duration_in_minutes: pulumi.Input[int],
                 growth_factor: pulumi.Input[float],
                 replicate_to: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 final_bake_time_in_minutes: Optional[pulumi.Input[int]] = None,
                 growth_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a DeploymentStrategy resource.
        :param pulumi.Input[int] deployment_duration_in_minutes: Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[float] growth_factor: The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        :param pulumi.Input[str] replicate_to: Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        :param pulumi.Input[str] description: A description of the deployment strategy. Can be at most 1024 characters.
        :param pulumi.Input[int] final_bake_time_in_minutes: The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[str] growth_type: The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        :param pulumi.Input[str] name: A name for the deployment strategy. Must be between 1 and 64 characters in length.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "deployment_duration_in_minutes", deployment_duration_in_minutes)
        pulumi.set(__self__, "growth_factor", growth_factor)
        pulumi.set(__self__, "replicate_to", replicate_to)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if final_bake_time_in_minutes is not None:
            pulumi.set(__self__, "final_bake_time_in_minutes", final_bake_time_in_minutes)
        if growth_type is not None:
            pulumi.set(__self__, "growth_type", growth_type)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> pulumi.Input[int]:
        """
        Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "deployment_duration_in_minutes")

    @deployment_duration_in_minutes.setter
    def deployment_duration_in_minutes(self, value: pulumi.Input[int]):
        pulumi.set(self, "deployment_duration_in_minutes", value)

    @property
    @pulumi.getter(name="growthFactor")
    def growth_factor(self) -> pulumi.Input[float]:
        """
        The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        """
        return pulumi.get(self, "growth_factor")

    @growth_factor.setter
    def growth_factor(self, value: pulumi.Input[float]):
        pulumi.set(self, "growth_factor", value)

    @property
    @pulumi.getter(name="replicateTo")
    def replicate_to(self) -> pulumi.Input[str]:
        """
        Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        """
        return pulumi.get(self, "replicate_to")

    @replicate_to.setter
    def replicate_to(self, value: pulumi.Input[str]):
        pulumi.set(self, "replicate_to", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description of the deployment strategy. Can be at most 1024 characters.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> Optional[pulumi.Input[int]]:
        """
        The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "final_bake_time_in_minutes")

    @final_bake_time_in_minutes.setter
    def final_bake_time_in_minutes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "final_bake_time_in_minutes", value)

    @property
    @pulumi.getter(name="growthType")
    def growth_type(self) -> Optional[pulumi.Input[str]]:
        """
        The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        """
        return pulumi.get(self, "growth_type")

    @growth_type.setter
    def growth_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "growth_type", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A name for the deployment strategy. Must be between 1 and 64 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _DeploymentStrategyState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 deployment_duration_in_minutes: Optional[pulumi.Input[int]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 final_bake_time_in_minutes: Optional[pulumi.Input[int]] = None,
                 growth_factor: Optional[pulumi.Input[float]] = None,
                 growth_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 replicate_to: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering DeploymentStrategy resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the AppConfig Deployment Strategy.
        :param pulumi.Input[int] deployment_duration_in_minutes: Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[str] description: A description of the deployment strategy. Can be at most 1024 characters.
        :param pulumi.Input[int] final_bake_time_in_minutes: The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[float] growth_factor: The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        :param pulumi.Input[str] growth_type: The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        :param pulumi.Input[str] name: A name for the deployment strategy. Must be between 1 and 64 characters in length.
        :param pulumi.Input[str] replicate_to: Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if deployment_duration_in_minutes is not None:
            pulumi.set(__self__, "deployment_duration_in_minutes", deployment_duration_in_minutes)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if final_bake_time_in_minutes is not None:
            pulumi.set(__self__, "final_bake_time_in_minutes", final_bake_time_in_minutes)
        if growth_factor is not None:
            pulumi.set(__self__, "growth_factor", growth_factor)
        if growth_type is not None:
            pulumi.set(__self__, "growth_type", growth_type)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if replicate_to is not None:
            pulumi.set(__self__, "replicate_to", replicate_to)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of the AppConfig Deployment Strategy.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> Optional[pulumi.Input[int]]:
        """
        Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "deployment_duration_in_minutes")

    @deployment_duration_in_minutes.setter
    def deployment_duration_in_minutes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "deployment_duration_in_minutes", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description of the deployment strategy. Can be at most 1024 characters.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> Optional[pulumi.Input[int]]:
        """
        The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "final_bake_time_in_minutes")

    @final_bake_time_in_minutes.setter
    def final_bake_time_in_minutes(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "final_bake_time_in_minutes", value)

    @property
    @pulumi.getter(name="growthFactor")
    def growth_factor(self) -> Optional[pulumi.Input[float]]:
        """
        The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        """
        return pulumi.get(self, "growth_factor")

    @growth_factor.setter
    def growth_factor(self, value: Optional[pulumi.Input[float]]):
        pulumi.set(self, "growth_factor", value)

    @property
    @pulumi.getter(name="growthType")
    def growth_type(self) -> Optional[pulumi.Input[str]]:
        """
        The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        """
        return pulumi.get(self, "growth_type")

    @growth_type.setter
    def growth_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "growth_type", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A name for the deployment strategy. Must be between 1 and 64 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="replicateTo")
    def replicate_to(self) -> Optional[pulumi.Input[str]]:
        """
        Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        """
        return pulumi.get(self, "replicate_to")

    @replicate_to.setter
    def replicate_to(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "replicate_to", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        return pulumi.get(self, "tags_all")

    @tags_all.setter
    def tags_all(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags_all", value)


class DeploymentStrategy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_duration_in_minutes: Optional[pulumi.Input[int]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 final_bake_time_in_minutes: Optional[pulumi.Input[int]] = None,
                 growth_factor: Optional[pulumi.Input[float]] = None,
                 growth_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 replicate_to: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides an AppConfig Deployment Strategy resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.appconfig.DeploymentStrategy("example",
            deployment_duration_in_minutes=3,
            description="Example Deployment Strategy",
            final_bake_time_in_minutes=4,
            growth_factor=10,
            growth_type="LINEAR",
            replicate_to="NONE",
            tags={
                "Type": "AppConfig Deployment Strategy",
            })
        ```

        ## Import

        AppConfig Deployment Strategies can be imported by using their deployment strategy ID, e.g.,

        ```sh
         $ pulumi import aws:appconfig/deploymentStrategy:DeploymentStrategy example 11xxxxx
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] deployment_duration_in_minutes: Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[str] description: A description of the deployment strategy. Can be at most 1024 characters.
        :param pulumi.Input[int] final_bake_time_in_minutes: The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[float] growth_factor: The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        :param pulumi.Input[str] growth_type: The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        :param pulumi.Input[str] name: A name for the deployment strategy. Must be between 1 and 64 characters in length.
        :param pulumi.Input[str] replicate_to: Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: DeploymentStrategyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an AppConfig Deployment Strategy resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.appconfig.DeploymentStrategy("example",
            deployment_duration_in_minutes=3,
            description="Example Deployment Strategy",
            final_bake_time_in_minutes=4,
            growth_factor=10,
            growth_type="LINEAR",
            replicate_to="NONE",
            tags={
                "Type": "AppConfig Deployment Strategy",
            })
        ```

        ## Import

        AppConfig Deployment Strategies can be imported by using their deployment strategy ID, e.g.,

        ```sh
         $ pulumi import aws:appconfig/deploymentStrategy:DeploymentStrategy example 11xxxxx
        ```

        :param str resource_name: The name of the resource.
        :param DeploymentStrategyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DeploymentStrategyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_duration_in_minutes: Optional[pulumi.Input[int]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 final_bake_time_in_minutes: Optional[pulumi.Input[int]] = None,
                 growth_factor: Optional[pulumi.Input[float]] = None,
                 growth_type: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 replicate_to: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
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
            __props__ = DeploymentStrategyArgs.__new__(DeploymentStrategyArgs)

            if deployment_duration_in_minutes is None and not opts.urn:
                raise TypeError("Missing required property 'deployment_duration_in_minutes'")
            __props__.__dict__["deployment_duration_in_minutes"] = deployment_duration_in_minutes
            __props__.__dict__["description"] = description
            __props__.__dict__["final_bake_time_in_minutes"] = final_bake_time_in_minutes
            if growth_factor is None and not opts.urn:
                raise TypeError("Missing required property 'growth_factor'")
            __props__.__dict__["growth_factor"] = growth_factor
            __props__.__dict__["growth_type"] = growth_type
            __props__.__dict__["name"] = name
            if replicate_to is None and not opts.urn:
                raise TypeError("Missing required property 'replicate_to'")
            __props__.__dict__["replicate_to"] = replicate_to
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["tags_all"] = None
        super(DeploymentStrategy, __self__).__init__(
            'aws:appconfig/deploymentStrategy:DeploymentStrategy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            deployment_duration_in_minutes: Optional[pulumi.Input[int]] = None,
            description: Optional[pulumi.Input[str]] = None,
            final_bake_time_in_minutes: Optional[pulumi.Input[int]] = None,
            growth_factor: Optional[pulumi.Input[float]] = None,
            growth_type: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            replicate_to: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'DeploymentStrategy':
        """
        Get an existing DeploymentStrategy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the AppConfig Deployment Strategy.
        :param pulumi.Input[int] deployment_duration_in_minutes: Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[str] description: A description of the deployment strategy. Can be at most 1024 characters.
        :param pulumi.Input[int] final_bake_time_in_minutes: The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        :param pulumi.Input[float] growth_factor: The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        :param pulumi.Input[str] growth_type: The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        :param pulumi.Input[str] name: A name for the deployment strategy. Must be between 1 and 64 characters in length.
        :param pulumi.Input[str] replicate_to: Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DeploymentStrategyState.__new__(_DeploymentStrategyState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["deployment_duration_in_minutes"] = deployment_duration_in_minutes
        __props__.__dict__["description"] = description
        __props__.__dict__["final_bake_time_in_minutes"] = final_bake_time_in_minutes
        __props__.__dict__["growth_factor"] = growth_factor
        __props__.__dict__["growth_type"] = growth_type
        __props__.__dict__["name"] = name
        __props__.__dict__["replicate_to"] = replicate_to
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return DeploymentStrategy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of the AppConfig Deployment Strategy.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="deploymentDurationInMinutes")
    def deployment_duration_in_minutes(self) -> pulumi.Output[int]:
        """
        Total amount of time for a deployment to last. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "deployment_duration_in_minutes")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A description of the deployment strategy. Can be at most 1024 characters.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="finalBakeTimeInMinutes")
    def final_bake_time_in_minutes(self) -> pulumi.Output[Optional[int]]:
        """
        The amount of time AWS AppConfig monitors for alarms before considering the deployment to be complete and no longer eligible for automatic roll back. Minimum value of 0, maximum value of 1440.
        """
        return pulumi.get(self, "final_bake_time_in_minutes")

    @property
    @pulumi.getter(name="growthFactor")
    def growth_factor(self) -> pulumi.Output[float]:
        """
        The percentage of targets to receive a deployed configuration during each interval. Minimum value of 1.0, maximum value of 100.0.
        """
        return pulumi.get(self, "growth_factor")

    @property
    @pulumi.getter(name="growthType")
    def growth_type(self) -> pulumi.Output[Optional[str]]:
        """
        The algorithm used to define how percentage grows over time. Valid value: `LINEAR` and `EXPONENTIAL`. Defaults to `LINEAR`.
        """
        return pulumi.get(self, "growth_type")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A name for the deployment strategy. Must be between 1 and 64 characters in length.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="replicateTo")
    def replicate_to(self) -> pulumi.Output[str]:
        """
        Where to save the deployment strategy. Valid values: `NONE` and `SSM_DOCUMENT`.
        """
        return pulumi.get(self, "replicate_to")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        return pulumi.get(self, "tags_all")

