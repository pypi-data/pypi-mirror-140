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

__all__ = ['InventoryArgs', 'Inventory']

@pulumi.input_type
class InventoryArgs:
    def __init__(__self__, *,
                 bucket: pulumi.Input[str],
                 destination: pulumi.Input['InventoryDestinationArgs'],
                 included_object_versions: pulumi.Input[str],
                 schedule: pulumi.Input['InventoryScheduleArgs'],
                 enabled: Optional[pulumi.Input[bool]] = None,
                 filter: Optional[pulumi.Input['InventoryFilterArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 optional_fields: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Inventory resource.
        :param pulumi.Input[str] bucket: The name of the source bucket that inventory lists the objects for.
        :param pulumi.Input['InventoryDestinationArgs'] destination: Contains information about where to publish the inventory results (documented below).
        :param pulumi.Input[str] included_object_versions: Object versions to include in the inventory list. Valid values: `All`, `Current`.
        :param pulumi.Input['InventoryScheduleArgs'] schedule: Specifies the schedule for generating inventory results (documented below).
        :param pulumi.Input[bool] enabled: Specifies whether the inventory is enabled or disabled.
        :param pulumi.Input['InventoryFilterArgs'] filter: Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        :param pulumi.Input[str] name: Unique identifier of the inventory configuration for the bucket.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] optional_fields: List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        """
        pulumi.set(__self__, "bucket", bucket)
        pulumi.set(__self__, "destination", destination)
        pulumi.set(__self__, "included_object_versions", included_object_versions)
        pulumi.set(__self__, "schedule", schedule)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if filter is not None:
            pulumi.set(__self__, "filter", filter)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if optional_fields is not None:
            pulumi.set(__self__, "optional_fields", optional_fields)

    @property
    @pulumi.getter
    def bucket(self) -> pulumi.Input[str]:
        """
        The name of the source bucket that inventory lists the objects for.
        """
        return pulumi.get(self, "bucket")

    @bucket.setter
    def bucket(self, value: pulumi.Input[str]):
        pulumi.set(self, "bucket", value)

    @property
    @pulumi.getter
    def destination(self) -> pulumi.Input['InventoryDestinationArgs']:
        """
        Contains information about where to publish the inventory results (documented below).
        """
        return pulumi.get(self, "destination")

    @destination.setter
    def destination(self, value: pulumi.Input['InventoryDestinationArgs']):
        pulumi.set(self, "destination", value)

    @property
    @pulumi.getter(name="includedObjectVersions")
    def included_object_versions(self) -> pulumi.Input[str]:
        """
        Object versions to include in the inventory list. Valid values: `All`, `Current`.
        """
        return pulumi.get(self, "included_object_versions")

    @included_object_versions.setter
    def included_object_versions(self, value: pulumi.Input[str]):
        pulumi.set(self, "included_object_versions", value)

    @property
    @pulumi.getter
    def schedule(self) -> pulumi.Input['InventoryScheduleArgs']:
        """
        Specifies the schedule for generating inventory results (documented below).
        """
        return pulumi.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: pulumi.Input['InventoryScheduleArgs']):
        pulumi.set(self, "schedule", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Specifies whether the inventory is enabled or disabled.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def filter(self) -> Optional[pulumi.Input['InventoryFilterArgs']]:
        """
        Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        """
        return pulumi.get(self, "filter")

    @filter.setter
    def filter(self, value: Optional[pulumi.Input['InventoryFilterArgs']]):
        pulumi.set(self, "filter", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Unique identifier of the inventory configuration for the bucket.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="optionalFields")
    def optional_fields(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        """
        return pulumi.get(self, "optional_fields")

    @optional_fields.setter
    def optional_fields(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "optional_fields", value)


@pulumi.input_type
class _InventoryState:
    def __init__(__self__, *,
                 bucket: Optional[pulumi.Input[str]] = None,
                 destination: Optional[pulumi.Input['InventoryDestinationArgs']] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 filter: Optional[pulumi.Input['InventoryFilterArgs']] = None,
                 included_object_versions: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 optional_fields: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schedule: Optional[pulumi.Input['InventoryScheduleArgs']] = None):
        """
        Input properties used for looking up and filtering Inventory resources.
        :param pulumi.Input[str] bucket: The name of the source bucket that inventory lists the objects for.
        :param pulumi.Input['InventoryDestinationArgs'] destination: Contains information about where to publish the inventory results (documented below).
        :param pulumi.Input[bool] enabled: Specifies whether the inventory is enabled or disabled.
        :param pulumi.Input['InventoryFilterArgs'] filter: Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        :param pulumi.Input[str] included_object_versions: Object versions to include in the inventory list. Valid values: `All`, `Current`.
        :param pulumi.Input[str] name: Unique identifier of the inventory configuration for the bucket.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] optional_fields: List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        :param pulumi.Input['InventoryScheduleArgs'] schedule: Specifies the schedule for generating inventory results (documented below).
        """
        if bucket is not None:
            pulumi.set(__self__, "bucket", bucket)
        if destination is not None:
            pulumi.set(__self__, "destination", destination)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if filter is not None:
            pulumi.set(__self__, "filter", filter)
        if included_object_versions is not None:
            pulumi.set(__self__, "included_object_versions", included_object_versions)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if optional_fields is not None:
            pulumi.set(__self__, "optional_fields", optional_fields)
        if schedule is not None:
            pulumi.set(__self__, "schedule", schedule)

    @property
    @pulumi.getter
    def bucket(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the source bucket that inventory lists the objects for.
        """
        return pulumi.get(self, "bucket")

    @bucket.setter
    def bucket(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bucket", value)

    @property
    @pulumi.getter
    def destination(self) -> Optional[pulumi.Input['InventoryDestinationArgs']]:
        """
        Contains information about where to publish the inventory results (documented below).
        """
        return pulumi.get(self, "destination")

    @destination.setter
    def destination(self, value: Optional[pulumi.Input['InventoryDestinationArgs']]):
        pulumi.set(self, "destination", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        Specifies whether the inventory is enabled or disabled.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def filter(self) -> Optional[pulumi.Input['InventoryFilterArgs']]:
        """
        Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        """
        return pulumi.get(self, "filter")

    @filter.setter
    def filter(self, value: Optional[pulumi.Input['InventoryFilterArgs']]):
        pulumi.set(self, "filter", value)

    @property
    @pulumi.getter(name="includedObjectVersions")
    def included_object_versions(self) -> Optional[pulumi.Input[str]]:
        """
        Object versions to include in the inventory list. Valid values: `All`, `Current`.
        """
        return pulumi.get(self, "included_object_versions")

    @included_object_versions.setter
    def included_object_versions(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "included_object_versions", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Unique identifier of the inventory configuration for the bucket.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="optionalFields")
    def optional_fields(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        """
        return pulumi.get(self, "optional_fields")

    @optional_fields.setter
    def optional_fields(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "optional_fields", value)

    @property
    @pulumi.getter
    def schedule(self) -> Optional[pulumi.Input['InventoryScheduleArgs']]:
        """
        Specifies the schedule for generating inventory results (documented below).
        """
        return pulumi.get(self, "schedule")

    @schedule.setter
    def schedule(self, value: Optional[pulumi.Input['InventoryScheduleArgs']]):
        pulumi.set(self, "schedule", value)


class Inventory(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket: Optional[pulumi.Input[str]] = None,
                 destination: Optional[pulumi.Input[pulumi.InputType['InventoryDestinationArgs']]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 filter: Optional[pulumi.Input[pulumi.InputType['InventoryFilterArgs']]] = None,
                 included_object_versions: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 optional_fields: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schedule: Optional[pulumi.Input[pulumi.InputType['InventoryScheduleArgs']]] = None,
                 __props__=None):
        """
        Provides a S3 bucket [inventory configuration](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-inventory.html) resource.

        ## Example Usage
        ### Add inventory configuration

        ```python
        import pulumi
        import pulumi_aws as aws

        test_bucket = aws.s3.Bucket("testBucket")
        inventory = aws.s3.Bucket("inventory")
        test_inventory = aws.s3.Inventory("testInventory",
            bucket=test_bucket.id,
            included_object_versions="All",
            schedule=aws.s3.InventoryScheduleArgs(
                frequency="Daily",
            ),
            destination=aws.s3.InventoryDestinationArgs(
                bucket=aws.s3.InventoryDestinationBucketArgs(
                    format="ORC",
                    bucket_arn=inventory.arn,
                ),
            ))
        ```
        ### Add inventory configuration with S3 bucket object prefix

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.s3.Bucket("test")
        inventory = aws.s3.Bucket("inventory")
        test_prefix = aws.s3.Inventory("test-prefix",
            bucket=test.id,
            included_object_versions="All",
            schedule=aws.s3.InventoryScheduleArgs(
                frequency="Daily",
            ),
            filter=aws.s3.InventoryFilterArgs(
                prefix="documents/",
            ),
            destination=aws.s3.InventoryDestinationArgs(
                bucket=aws.s3.InventoryDestinationBucketArgs(
                    format="ORC",
                    bucket_arn=inventory.arn,
                    prefix="inventory",
                ),
            ))
        ```

        ## Import

        S3 bucket inventory configurations can be imported using `bucket:inventory`, e.g.,

        ```sh
         $ pulumi import aws:s3/inventory:Inventory my-bucket-entire-bucket my-bucket:EntireBucket
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bucket: The name of the source bucket that inventory lists the objects for.
        :param pulumi.Input[pulumi.InputType['InventoryDestinationArgs']] destination: Contains information about where to publish the inventory results (documented below).
        :param pulumi.Input[bool] enabled: Specifies whether the inventory is enabled or disabled.
        :param pulumi.Input[pulumi.InputType['InventoryFilterArgs']] filter: Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        :param pulumi.Input[str] included_object_versions: Object versions to include in the inventory list. Valid values: `All`, `Current`.
        :param pulumi.Input[str] name: Unique identifier of the inventory configuration for the bucket.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] optional_fields: List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        :param pulumi.Input[pulumi.InputType['InventoryScheduleArgs']] schedule: Specifies the schedule for generating inventory results (documented below).
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: InventoryArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a S3 bucket [inventory configuration](https://docs.aws.amazon.com/AmazonS3/latest/dev/storage-inventory.html) resource.

        ## Example Usage
        ### Add inventory configuration

        ```python
        import pulumi
        import pulumi_aws as aws

        test_bucket = aws.s3.Bucket("testBucket")
        inventory = aws.s3.Bucket("inventory")
        test_inventory = aws.s3.Inventory("testInventory",
            bucket=test_bucket.id,
            included_object_versions="All",
            schedule=aws.s3.InventoryScheduleArgs(
                frequency="Daily",
            ),
            destination=aws.s3.InventoryDestinationArgs(
                bucket=aws.s3.InventoryDestinationBucketArgs(
                    format="ORC",
                    bucket_arn=inventory.arn,
                ),
            ))
        ```
        ### Add inventory configuration with S3 bucket object prefix

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.s3.Bucket("test")
        inventory = aws.s3.Bucket("inventory")
        test_prefix = aws.s3.Inventory("test-prefix",
            bucket=test.id,
            included_object_versions="All",
            schedule=aws.s3.InventoryScheduleArgs(
                frequency="Daily",
            ),
            filter=aws.s3.InventoryFilterArgs(
                prefix="documents/",
            ),
            destination=aws.s3.InventoryDestinationArgs(
                bucket=aws.s3.InventoryDestinationBucketArgs(
                    format="ORC",
                    bucket_arn=inventory.arn,
                    prefix="inventory",
                ),
            ))
        ```

        ## Import

        S3 bucket inventory configurations can be imported using `bucket:inventory`, e.g.,

        ```sh
         $ pulumi import aws:s3/inventory:Inventory my-bucket-entire-bucket my-bucket:EntireBucket
        ```

        :param str resource_name: The name of the resource.
        :param InventoryArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InventoryArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bucket: Optional[pulumi.Input[str]] = None,
                 destination: Optional[pulumi.Input[pulumi.InputType['InventoryDestinationArgs']]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 filter: Optional[pulumi.Input[pulumi.InputType['InventoryFilterArgs']]] = None,
                 included_object_versions: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 optional_fields: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schedule: Optional[pulumi.Input[pulumi.InputType['InventoryScheduleArgs']]] = None,
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
            __props__ = InventoryArgs.__new__(InventoryArgs)

            if bucket is None and not opts.urn:
                raise TypeError("Missing required property 'bucket'")
            __props__.__dict__["bucket"] = bucket
            if destination is None and not opts.urn:
                raise TypeError("Missing required property 'destination'")
            __props__.__dict__["destination"] = destination
            __props__.__dict__["enabled"] = enabled
            __props__.__dict__["filter"] = filter
            if included_object_versions is None and not opts.urn:
                raise TypeError("Missing required property 'included_object_versions'")
            __props__.__dict__["included_object_versions"] = included_object_versions
            __props__.__dict__["name"] = name
            __props__.__dict__["optional_fields"] = optional_fields
            if schedule is None and not opts.urn:
                raise TypeError("Missing required property 'schedule'")
            __props__.__dict__["schedule"] = schedule
        super(Inventory, __self__).__init__(
            'aws:s3/inventory:Inventory',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            bucket: Optional[pulumi.Input[str]] = None,
            destination: Optional[pulumi.Input[pulumi.InputType['InventoryDestinationArgs']]] = None,
            enabled: Optional[pulumi.Input[bool]] = None,
            filter: Optional[pulumi.Input[pulumi.InputType['InventoryFilterArgs']]] = None,
            included_object_versions: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            optional_fields: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            schedule: Optional[pulumi.Input[pulumi.InputType['InventoryScheduleArgs']]] = None) -> 'Inventory':
        """
        Get an existing Inventory resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bucket: The name of the source bucket that inventory lists the objects for.
        :param pulumi.Input[pulumi.InputType['InventoryDestinationArgs']] destination: Contains information about where to publish the inventory results (documented below).
        :param pulumi.Input[bool] enabled: Specifies whether the inventory is enabled or disabled.
        :param pulumi.Input[pulumi.InputType['InventoryFilterArgs']] filter: Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        :param pulumi.Input[str] included_object_versions: Object versions to include in the inventory list. Valid values: `All`, `Current`.
        :param pulumi.Input[str] name: Unique identifier of the inventory configuration for the bucket.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] optional_fields: List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        :param pulumi.Input[pulumi.InputType['InventoryScheduleArgs']] schedule: Specifies the schedule for generating inventory results (documented below).
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _InventoryState.__new__(_InventoryState)

        __props__.__dict__["bucket"] = bucket
        __props__.__dict__["destination"] = destination
        __props__.__dict__["enabled"] = enabled
        __props__.__dict__["filter"] = filter
        __props__.__dict__["included_object_versions"] = included_object_versions
        __props__.__dict__["name"] = name
        __props__.__dict__["optional_fields"] = optional_fields
        __props__.__dict__["schedule"] = schedule
        return Inventory(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def bucket(self) -> pulumi.Output[str]:
        """
        The name of the source bucket that inventory lists the objects for.
        """
        return pulumi.get(self, "bucket")

    @property
    @pulumi.getter
    def destination(self) -> pulumi.Output['outputs.InventoryDestination']:
        """
        Contains information about where to publish the inventory results (documented below).
        """
        return pulumi.get(self, "destination")

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        Specifies whether the inventory is enabled or disabled.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter
    def filter(self) -> pulumi.Output[Optional['outputs.InventoryFilter']]:
        """
        Specifies an inventory filter. The inventory only includes objects that meet the filter's criteria (documented below).
        """
        return pulumi.get(self, "filter")

    @property
    @pulumi.getter(name="includedObjectVersions")
    def included_object_versions(self) -> pulumi.Output[str]:
        """
        Object versions to include in the inventory list. Valid values: `All`, `Current`.
        """
        return pulumi.get(self, "included_object_versions")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Unique identifier of the inventory configuration for the bucket.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="optionalFields")
    def optional_fields(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        List of optional fields that are included in the inventory results. Please refer to the S3 [documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_InventoryConfiguration.html#AmazonS3-Type-InventoryConfiguration-OptionalFields) for more details.
        """
        return pulumi.get(self, "optional_fields")

    @property
    @pulumi.getter
    def schedule(self) -> pulumi.Output['outputs.InventorySchedule']:
        """
        Specifies the schedule for generating inventory results (documented below).
        """
        return pulumi.get(self, "schedule")

