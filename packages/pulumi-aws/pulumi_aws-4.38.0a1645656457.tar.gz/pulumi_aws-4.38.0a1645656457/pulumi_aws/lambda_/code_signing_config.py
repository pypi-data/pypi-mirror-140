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

__all__ = ['CodeSigningConfigArgs', 'CodeSigningConfig']

@pulumi.input_type
class CodeSigningConfigArgs:
    def __init__(__self__, *,
                 allowed_publishers: pulumi.Input['CodeSigningConfigAllowedPublishersArgs'],
                 description: Optional[pulumi.Input[str]] = None,
                 policies: Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']] = None):
        """
        The set of arguments for constructing a CodeSigningConfig resource.
        :param pulumi.Input['CodeSigningConfigAllowedPublishersArgs'] allowed_publishers: A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        :param pulumi.Input[str] description: Descriptive name for this code signing configuration.
        :param pulumi.Input['CodeSigningConfigPoliciesArgs'] policies: A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        pulumi.set(__self__, "allowed_publishers", allowed_publishers)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if policies is not None:
            pulumi.set(__self__, "policies", policies)

    @property
    @pulumi.getter(name="allowedPublishers")
    def allowed_publishers(self) -> pulumi.Input['CodeSigningConfigAllowedPublishersArgs']:
        """
        A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        """
        return pulumi.get(self, "allowed_publishers")

    @allowed_publishers.setter
    def allowed_publishers(self, value: pulumi.Input['CodeSigningConfigAllowedPublishersArgs']):
        pulumi.set(self, "allowed_publishers", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Descriptive name for this code signing configuration.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def policies(self) -> Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']]:
        """
        A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        return pulumi.get(self, "policies")

    @policies.setter
    def policies(self, value: Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']]):
        pulumi.set(self, "policies", value)


@pulumi.input_type
class _CodeSigningConfigState:
    def __init__(__self__, *,
                 allowed_publishers: Optional[pulumi.Input['CodeSigningConfigAllowedPublishersArgs']] = None,
                 arn: Optional[pulumi.Input[str]] = None,
                 config_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 last_modified: Optional[pulumi.Input[str]] = None,
                 policies: Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']] = None):
        """
        Input properties used for looking up and filtering CodeSigningConfig resources.
        :param pulumi.Input['CodeSigningConfigAllowedPublishersArgs'] allowed_publishers: A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the code signing configuration.
        :param pulumi.Input[str] config_id: Unique identifier for the code signing configuration.
        :param pulumi.Input[str] description: Descriptive name for this code signing configuration.
        :param pulumi.Input[str] last_modified: The date and time that the code signing configuration was last modified.
        :param pulumi.Input['CodeSigningConfigPoliciesArgs'] policies: A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        if allowed_publishers is not None:
            pulumi.set(__self__, "allowed_publishers", allowed_publishers)
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if config_id is not None:
            pulumi.set(__self__, "config_id", config_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if last_modified is not None:
            pulumi.set(__self__, "last_modified", last_modified)
        if policies is not None:
            pulumi.set(__self__, "policies", policies)

    @property
    @pulumi.getter(name="allowedPublishers")
    def allowed_publishers(self) -> Optional[pulumi.Input['CodeSigningConfigAllowedPublishersArgs']]:
        """
        A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        """
        return pulumi.get(self, "allowed_publishers")

    @allowed_publishers.setter
    def allowed_publishers(self, value: Optional[pulumi.Input['CodeSigningConfigAllowedPublishersArgs']]):
        pulumi.set(self, "allowed_publishers", value)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of the code signing configuration.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="configId")
    def config_id(self) -> Optional[pulumi.Input[str]]:
        """
        Unique identifier for the code signing configuration.
        """
        return pulumi.get(self, "config_id")

    @config_id.setter
    def config_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "config_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Descriptive name for this code signing configuration.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="lastModified")
    def last_modified(self) -> Optional[pulumi.Input[str]]:
        """
        The date and time that the code signing configuration was last modified.
        """
        return pulumi.get(self, "last_modified")

    @last_modified.setter
    def last_modified(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_modified", value)

    @property
    @pulumi.getter
    def policies(self) -> Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']]:
        """
        A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        return pulumi.get(self, "policies")

    @policies.setter
    def policies(self, value: Optional[pulumi.Input['CodeSigningConfigPoliciesArgs']]):
        pulumi.set(self, "policies", value)


class CodeSigningConfig(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 allowed_publishers: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigAllowedPublishersArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 policies: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigPoliciesArgs']]] = None,
                 __props__=None):
        """
        Provides a Lambda Code Signing Config resource. A code signing configuration defines a list of allowed signing profiles and defines the code-signing validation policy (action to be taken if deployment validation checks fail).

        For information about Lambda code signing configurations and how to use them, see [configuring code signing for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-codesigning.html)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        new_csc = aws.lambda_.CodeSigningConfig("newCsc",
            allowed_publishers=aws.lambda..CodeSigningConfigAllowedPublishersArgs(
                signing_profile_version_arns=[
                    aws_signer_signing_profile["example1"]["arn"],
                    aws_signer_signing_profile["example2"]["arn"],
                ],
            ),
            policies=aws.lambda..CodeSigningConfigPoliciesArgs(
                untrusted_artifact_on_deployment="Warn",
            ),
            description="My awesome code signing config.")
        ```

        ## Import

        Code Signing Configs can be imported using their ARN, e.g.,

        ```sh
         $ pulumi import aws:lambda/codeSigningConfig:CodeSigningConfig imported_csc arn:aws:lambda:us-west-2:123456789012:code-signing-config:csc-0f6c334abcdea4d8b
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['CodeSigningConfigAllowedPublishersArgs']] allowed_publishers: A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        :param pulumi.Input[str] description: Descriptive name for this code signing configuration.
        :param pulumi.Input[pulumi.InputType['CodeSigningConfigPoliciesArgs']] policies: A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: CodeSigningConfigArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Lambda Code Signing Config resource. A code signing configuration defines a list of allowed signing profiles and defines the code-signing validation policy (action to be taken if deployment validation checks fail).

        For information about Lambda code signing configurations and how to use them, see [configuring code signing for Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/configuration-codesigning.html)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        new_csc = aws.lambda_.CodeSigningConfig("newCsc",
            allowed_publishers=aws.lambda..CodeSigningConfigAllowedPublishersArgs(
                signing_profile_version_arns=[
                    aws_signer_signing_profile["example1"]["arn"],
                    aws_signer_signing_profile["example2"]["arn"],
                ],
            ),
            policies=aws.lambda..CodeSigningConfigPoliciesArgs(
                untrusted_artifact_on_deployment="Warn",
            ),
            description="My awesome code signing config.")
        ```

        ## Import

        Code Signing Configs can be imported using their ARN, e.g.,

        ```sh
         $ pulumi import aws:lambda/codeSigningConfig:CodeSigningConfig imported_csc arn:aws:lambda:us-west-2:123456789012:code-signing-config:csc-0f6c334abcdea4d8b
        ```

        :param str resource_name: The name of the resource.
        :param CodeSigningConfigArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(CodeSigningConfigArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 allowed_publishers: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigAllowedPublishersArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 policies: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigPoliciesArgs']]] = None,
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
            __props__ = CodeSigningConfigArgs.__new__(CodeSigningConfigArgs)

            if allowed_publishers is None and not opts.urn:
                raise TypeError("Missing required property 'allowed_publishers'")
            __props__.__dict__["allowed_publishers"] = allowed_publishers
            __props__.__dict__["description"] = description
            __props__.__dict__["policies"] = policies
            __props__.__dict__["arn"] = None
            __props__.__dict__["config_id"] = None
            __props__.__dict__["last_modified"] = None
        super(CodeSigningConfig, __self__).__init__(
            'aws:lambda/codeSigningConfig:CodeSigningConfig',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            allowed_publishers: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigAllowedPublishersArgs']]] = None,
            arn: Optional[pulumi.Input[str]] = None,
            config_id: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            last_modified: Optional[pulumi.Input[str]] = None,
            policies: Optional[pulumi.Input[pulumi.InputType['CodeSigningConfigPoliciesArgs']]] = None) -> 'CodeSigningConfig':
        """
        Get an existing CodeSigningConfig resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['CodeSigningConfigAllowedPublishersArgs']] allowed_publishers: A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the code signing configuration.
        :param pulumi.Input[str] config_id: Unique identifier for the code signing configuration.
        :param pulumi.Input[str] description: Descriptive name for this code signing configuration.
        :param pulumi.Input[str] last_modified: The date and time that the code signing configuration was last modified.
        :param pulumi.Input[pulumi.InputType['CodeSigningConfigPoliciesArgs']] policies: A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _CodeSigningConfigState.__new__(_CodeSigningConfigState)

        __props__.__dict__["allowed_publishers"] = allowed_publishers
        __props__.__dict__["arn"] = arn
        __props__.__dict__["config_id"] = config_id
        __props__.__dict__["description"] = description
        __props__.__dict__["last_modified"] = last_modified
        __props__.__dict__["policies"] = policies
        return CodeSigningConfig(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="allowedPublishers")
    def allowed_publishers(self) -> pulumi.Output['outputs.CodeSigningConfigAllowedPublishers']:
        """
        A configuration block of allowed publishers as signing profiles for this code signing configuration. Detailed below.
        """
        return pulumi.get(self, "allowed_publishers")

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of the code signing configuration.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="configId")
    def config_id(self) -> pulumi.Output[str]:
        """
        Unique identifier for the code signing configuration.
        """
        return pulumi.get(self, "config_id")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        Descriptive name for this code signing configuration.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="lastModified")
    def last_modified(self) -> pulumi.Output[str]:
        """
        The date and time that the code signing configuration was last modified.
        """
        return pulumi.get(self, "last_modified")

    @property
    @pulumi.getter
    def policies(self) -> pulumi.Output['outputs.CodeSigningConfigPolicies']:
        """
        A configuration block of code signing policies that define the actions to take if the validation checks fail. Detailed below.
        """
        return pulumi.get(self, "policies")

