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

__all__ = ['CertificateArgs', 'Certificate']

@pulumi.input_type
class CertificateArgs:
    def __init__(__self__, *,
                 certificate_authority_arn: Optional[pulumi.Input[str]] = None,
                 certificate_body: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_name: Optional[pulumi.Input[str]] = None,
                 options: Optional[pulumi.Input['CertificateOptionsArgs']] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 subject_alternative_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 validation_method: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Certificate resource.
        :param pulumi.Input[str] certificate_authority_arn: ARN of an ACM PCA
        :param pulumi.Input[str] certificate_body: The certificate's PEM-formatted public key
        :param pulumi.Input[str] certificate_chain: The certificate's PEM-formatted chain
               * Creating a private CA issued certificate
        :param pulumi.Input[str] domain_name: A domain name for which the certificate should be issued
        :param pulumi.Input['CertificateOptionsArgs'] options: Configuration block used to set certificate options. Detailed below.
               * Importing an existing certificate
        :param pulumi.Input[str] private_key: The certificate's PEM-formatted private key
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subject_alternative_names: Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource..
        :param pulumi.Input[str] validation_method: Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        if certificate_authority_arn is not None:
            pulumi.set(__self__, "certificate_authority_arn", certificate_authority_arn)
        if certificate_body is not None:
            pulumi.set(__self__, "certificate_body", certificate_body)
        if certificate_chain is not None:
            pulumi.set(__self__, "certificate_chain", certificate_chain)
        if domain_name is not None:
            pulumi.set(__self__, "domain_name", domain_name)
        if options is not None:
            pulumi.set(__self__, "options", options)
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)
        if subject_alternative_names is not None:
            pulumi.set(__self__, "subject_alternative_names", subject_alternative_names)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if validation_method is not None:
            pulumi.set(__self__, "validation_method", validation_method)

    @property
    @pulumi.getter(name="certificateAuthorityArn")
    def certificate_authority_arn(self) -> Optional[pulumi.Input[str]]:
        """
        ARN of an ACM PCA
        """
        return pulumi.get(self, "certificate_authority_arn")

    @certificate_authority_arn.setter
    def certificate_authority_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_authority_arn", value)

    @property
    @pulumi.getter(name="certificateBody")
    def certificate_body(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted public key
        """
        return pulumi.get(self, "certificate_body")

    @certificate_body.setter
    def certificate_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_body", value)

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted chain
        * Creating a private CA issued certificate
        """
        return pulumi.get(self, "certificate_chain")

    @certificate_chain.setter
    def certificate_chain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_chain", value)

    @property
    @pulumi.getter(name="domainName")
    def domain_name(self) -> Optional[pulumi.Input[str]]:
        """
        A domain name for which the certificate should be issued
        """
        return pulumi.get(self, "domain_name")

    @domain_name.setter
    def domain_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_name", value)

    @property
    @pulumi.getter
    def options(self) -> Optional[pulumi.Input['CertificateOptionsArgs']]:
        """
        Configuration block used to set certificate options. Detailed below.
        * Importing an existing certificate
        """
        return pulumi.get(self, "options")

    @options.setter
    def options(self, value: Optional[pulumi.Input['CertificateOptionsArgs']]):
        pulumi.set(self, "options", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted private key
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter(name="subjectAlternativeNames")
    def subject_alternative_names(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        """
        return pulumi.get(self, "subject_alternative_names")

    @subject_alternative_names.setter
    def subject_alternative_names(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subject_alternative_names", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource..
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="validationMethod")
    def validation_method(self) -> Optional[pulumi.Input[str]]:
        """
        Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        return pulumi.get(self, "validation_method")

    @validation_method.setter
    def validation_method(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "validation_method", value)


@pulumi.input_type
class _CertificateState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 certificate_authority_arn: Optional[pulumi.Input[str]] = None,
                 certificate_body: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_name: Optional[pulumi.Input[str]] = None,
                 domain_validation_options: Optional[pulumi.Input[Sequence[pulumi.Input['CertificateDomainValidationOptionArgs']]]] = None,
                 options: Optional[pulumi.Input['CertificateOptionsArgs']] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 subject_alternative_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 validation_emails: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 validation_method: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering Certificate resources.
        :param pulumi.Input[str] arn: The ARN of the certificate
        :param pulumi.Input[str] certificate_authority_arn: ARN of an ACM PCA
        :param pulumi.Input[str] certificate_body: The certificate's PEM-formatted public key
        :param pulumi.Input[str] certificate_chain: The certificate's PEM-formatted chain
               * Creating a private CA issued certificate
        :param pulumi.Input[str] domain_name: A domain name for which the certificate should be issued
        :param pulumi.Input[Sequence[pulumi.Input['CertificateDomainValidationOptionArgs']]] domain_validation_options: Set of domain validation objects which can be used to complete certificate validation. Can have more than one element, e.g., if SANs are defined. Only set if `DNS`-validation was used.
        :param pulumi.Input['CertificateOptionsArgs'] options: Configuration block used to set certificate options. Detailed below.
               * Importing an existing certificate
        :param pulumi.Input[str] private_key: The certificate's PEM-formatted private key
        :param pulumi.Input[str] status: Status of the certificate.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subject_alternative_names: Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource..
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider .
        :param pulumi.Input[Sequence[pulumi.Input[str]]] validation_emails: A list of addresses that received a validation E-Mail. Only set if `EMAIL`-validation was used.
        :param pulumi.Input[str] validation_method: Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if certificate_authority_arn is not None:
            pulumi.set(__self__, "certificate_authority_arn", certificate_authority_arn)
        if certificate_body is not None:
            pulumi.set(__self__, "certificate_body", certificate_body)
        if certificate_chain is not None:
            pulumi.set(__self__, "certificate_chain", certificate_chain)
        if domain_name is not None:
            pulumi.set(__self__, "domain_name", domain_name)
        if domain_validation_options is not None:
            pulumi.set(__self__, "domain_validation_options", domain_validation_options)
        if options is not None:
            pulumi.set(__self__, "options", options)
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if subject_alternative_names is not None:
            pulumi.set(__self__, "subject_alternative_names", subject_alternative_names)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)
        if validation_emails is not None:
            pulumi.set(__self__, "validation_emails", validation_emails)
        if validation_method is not None:
            pulumi.set(__self__, "validation_method", validation_method)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the certificate
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="certificateAuthorityArn")
    def certificate_authority_arn(self) -> Optional[pulumi.Input[str]]:
        """
        ARN of an ACM PCA
        """
        return pulumi.get(self, "certificate_authority_arn")

    @certificate_authority_arn.setter
    def certificate_authority_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_authority_arn", value)

    @property
    @pulumi.getter(name="certificateBody")
    def certificate_body(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted public key
        """
        return pulumi.get(self, "certificate_body")

    @certificate_body.setter
    def certificate_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_body", value)

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted chain
        * Creating a private CA issued certificate
        """
        return pulumi.get(self, "certificate_chain")

    @certificate_chain.setter
    def certificate_chain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "certificate_chain", value)

    @property
    @pulumi.getter(name="domainName")
    def domain_name(self) -> Optional[pulumi.Input[str]]:
        """
        A domain name for which the certificate should be issued
        """
        return pulumi.get(self, "domain_name")

    @domain_name.setter
    def domain_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_name", value)

    @property
    @pulumi.getter(name="domainValidationOptions")
    def domain_validation_options(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['CertificateDomainValidationOptionArgs']]]]:
        """
        Set of domain validation objects which can be used to complete certificate validation. Can have more than one element, e.g., if SANs are defined. Only set if `DNS`-validation was used.
        """
        return pulumi.get(self, "domain_validation_options")

    @domain_validation_options.setter
    def domain_validation_options(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['CertificateDomainValidationOptionArgs']]]]):
        pulumi.set(self, "domain_validation_options", value)

    @property
    @pulumi.getter
    def options(self) -> Optional[pulumi.Input['CertificateOptionsArgs']]:
        """
        Configuration block used to set certificate options. Detailed below.
        * Importing an existing certificate
        """
        return pulumi.get(self, "options")

    @options.setter
    def options(self, value: Optional[pulumi.Input['CertificateOptionsArgs']]):
        pulumi.set(self, "options", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        The certificate's PEM-formatted private key
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        Status of the certificate.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter(name="subjectAlternativeNames")
    def subject_alternative_names(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        """
        return pulumi.get(self, "subject_alternative_names")

    @subject_alternative_names.setter
    def subject_alternative_names(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "subject_alternative_names", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource..
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider .
        """
        return pulumi.get(self, "tags_all")

    @tags_all.setter
    def tags_all(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags_all", value)

    @property
    @pulumi.getter(name="validationEmails")
    def validation_emails(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of addresses that received a validation E-Mail. Only set if `EMAIL`-validation was used.
        """
        return pulumi.get(self, "validation_emails")

    @validation_emails.setter
    def validation_emails(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "validation_emails", value)

    @property
    @pulumi.getter(name="validationMethod")
    def validation_method(self) -> Optional[pulumi.Input[str]]:
        """
        Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        return pulumi.get(self, "validation_method")

    @validation_method.setter
    def validation_method(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "validation_method", value)


class Certificate(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 certificate_authority_arn: Optional[pulumi.Input[str]] = None,
                 certificate_body: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_name: Optional[pulumi.Input[str]] = None,
                 options: Optional[pulumi.Input[pulumi.InputType['CertificateOptionsArgs']]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 subject_alternative_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 validation_method: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        The ACM certificate resource allows requesting and management of certificates
        from the Amazon Certificate Manager.

        It deals with requesting certificates and managing their attributes and life-cycle.
        This resource does not deal with validation of a certificate but can provide inputs
        for other resources implementing the validation. It does not wait for a certificate to be issued.
        Use a `acm.CertificateValidation` resource for this.

        Most commonly, this resource is used together with `route53.Record` and
        `acm.CertificateValidation` to request a DNS validated certificate,
        deploy the required validation records and wait for validation to complete.

        Domain validation through E-Mail is also supported but should be avoided as it requires a manual step outside
        of this provider.

        ## Example Usage
        ### Create Certificate

        ```python
        import pulumi
        import pulumi_aws as aws

        cert = aws.acm.Certificate("cert",
            domain_name="example.com",
            tags={
                "Environment": "test",
            },
            validation_method="DNS")
        ```
        ### Existing Certificate Body Import

        ```python
        import pulumi
        import pulumi_aws as aws
        import pulumi_tls as tls

        example_private_key = tls.PrivateKey("examplePrivateKey", algorithm="RSA")
        example_self_signed_cert = tls.SelfSignedCert("exampleSelfSignedCert",
            key_algorithm="RSA",
            private_key_pem=example_private_key.private_key_pem,
            subjects=[tls.SelfSignedCertSubjectArgs(
                common_name="example.com",
                organization="ACME Examples, Inc",
            )],
            validity_period_hours=12,
            allowed_uses=[
                "key_encipherment",
                "digital_signature",
                "server_auth",
            ])
        cert = aws.acm.Certificate("cert",
            private_key=example_private_key.private_key_pem,
            certificate_body=example_self_signed_cert.cert_pem)
        ```
        ### Referencing domain_validation_options With for_each Based Resources

        See the `acm.CertificateValidation` resource for a full example of performing DNS validation.

        ```python
        import pulumi
        import pulumi_aws as aws

        example = []
        for range in [{"key": k, "value": v} for [k, v] in enumerate({dvo.domainName: {
            name: dvo.resourceRecordName,
            record: dvo.resourceRecordValue,
            type: dvo.resourceRecordType,
        } for dvo in aws_acm_certificate.example.domain_validation_options})]:
            example.append(aws.route53.Record(f"example-{range['key']}",
                allow_overwrite=True,
                name=range["value"]["name"],
                records=[range["value"]["record"]],
                ttl=60,
                type=range["value"]["type"],
                zone_id=aws_route53_zone["example"]["zone_id"]))
        ```

        ## Import

        Certificates can be imported using their ARN, e.g.,

        ```sh
         $ pulumi import aws:acm/certificate:Certificate cert arn:aws:acm:eu-central-1:123456789012:certificate/7e7a28d2-163f-4b8f-b9cd-822f96c08d6a
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] certificate_authority_arn: ARN of an ACM PCA
        :param pulumi.Input[str] certificate_body: The certificate's PEM-formatted public key
        :param pulumi.Input[str] certificate_chain: The certificate's PEM-formatted chain
               * Creating a private CA issued certificate
        :param pulumi.Input[str] domain_name: A domain name for which the certificate should be issued
        :param pulumi.Input[pulumi.InputType['CertificateOptionsArgs']] options: Configuration block used to set certificate options. Detailed below.
               * Importing an existing certificate
        :param pulumi.Input[str] private_key: The certificate's PEM-formatted private key
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subject_alternative_names: Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource..
        :param pulumi.Input[str] validation_method: Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[CertificateArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        The ACM certificate resource allows requesting and management of certificates
        from the Amazon Certificate Manager.

        It deals with requesting certificates and managing their attributes and life-cycle.
        This resource does not deal with validation of a certificate but can provide inputs
        for other resources implementing the validation. It does not wait for a certificate to be issued.
        Use a `acm.CertificateValidation` resource for this.

        Most commonly, this resource is used together with `route53.Record` and
        `acm.CertificateValidation` to request a DNS validated certificate,
        deploy the required validation records and wait for validation to complete.

        Domain validation through E-Mail is also supported but should be avoided as it requires a manual step outside
        of this provider.

        ## Example Usage
        ### Create Certificate

        ```python
        import pulumi
        import pulumi_aws as aws

        cert = aws.acm.Certificate("cert",
            domain_name="example.com",
            tags={
                "Environment": "test",
            },
            validation_method="DNS")
        ```
        ### Existing Certificate Body Import

        ```python
        import pulumi
        import pulumi_aws as aws
        import pulumi_tls as tls

        example_private_key = tls.PrivateKey("examplePrivateKey", algorithm="RSA")
        example_self_signed_cert = tls.SelfSignedCert("exampleSelfSignedCert",
            key_algorithm="RSA",
            private_key_pem=example_private_key.private_key_pem,
            subjects=[tls.SelfSignedCertSubjectArgs(
                common_name="example.com",
                organization="ACME Examples, Inc",
            )],
            validity_period_hours=12,
            allowed_uses=[
                "key_encipherment",
                "digital_signature",
                "server_auth",
            ])
        cert = aws.acm.Certificate("cert",
            private_key=example_private_key.private_key_pem,
            certificate_body=example_self_signed_cert.cert_pem)
        ```
        ### Referencing domain_validation_options With for_each Based Resources

        See the `acm.CertificateValidation` resource for a full example of performing DNS validation.

        ```python
        import pulumi
        import pulumi_aws as aws

        example = []
        for range in [{"key": k, "value": v} for [k, v] in enumerate({dvo.domainName: {
            name: dvo.resourceRecordName,
            record: dvo.resourceRecordValue,
            type: dvo.resourceRecordType,
        } for dvo in aws_acm_certificate.example.domain_validation_options})]:
            example.append(aws.route53.Record(f"example-{range['key']}",
                allow_overwrite=True,
                name=range["value"]["name"],
                records=[range["value"]["record"]],
                ttl=60,
                type=range["value"]["type"],
                zone_id=aws_route53_zone["example"]["zone_id"]))
        ```

        ## Import

        Certificates can be imported using their ARN, e.g.,

        ```sh
         $ pulumi import aws:acm/certificate:Certificate cert arn:aws:acm:eu-central-1:123456789012:certificate/7e7a28d2-163f-4b8f-b9cd-822f96c08d6a
        ```

        :param str resource_name: The name of the resource.
        :param CertificateArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(CertificateArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 certificate_authority_arn: Optional[pulumi.Input[str]] = None,
                 certificate_body: Optional[pulumi.Input[str]] = None,
                 certificate_chain: Optional[pulumi.Input[str]] = None,
                 domain_name: Optional[pulumi.Input[str]] = None,
                 options: Optional[pulumi.Input[pulumi.InputType['CertificateOptionsArgs']]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 subject_alternative_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 validation_method: Optional[pulumi.Input[str]] = None,
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
            __props__ = CertificateArgs.__new__(CertificateArgs)

            __props__.__dict__["certificate_authority_arn"] = certificate_authority_arn
            __props__.__dict__["certificate_body"] = certificate_body
            __props__.__dict__["certificate_chain"] = certificate_chain
            __props__.__dict__["domain_name"] = domain_name
            __props__.__dict__["options"] = options
            __props__.__dict__["private_key"] = private_key
            __props__.__dict__["subject_alternative_names"] = subject_alternative_names
            __props__.__dict__["tags"] = tags
            __props__.__dict__["validation_method"] = validation_method
            __props__.__dict__["arn"] = None
            __props__.__dict__["domain_validation_options"] = None
            __props__.__dict__["status"] = None
            __props__.__dict__["tags_all"] = None
            __props__.__dict__["validation_emails"] = None
        super(Certificate, __self__).__init__(
            'aws:acm/certificate:Certificate',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            certificate_authority_arn: Optional[pulumi.Input[str]] = None,
            certificate_body: Optional[pulumi.Input[str]] = None,
            certificate_chain: Optional[pulumi.Input[str]] = None,
            domain_name: Optional[pulumi.Input[str]] = None,
            domain_validation_options: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['CertificateDomainValidationOptionArgs']]]]] = None,
            options: Optional[pulumi.Input[pulumi.InputType['CertificateOptionsArgs']]] = None,
            private_key: Optional[pulumi.Input[str]] = None,
            status: Optional[pulumi.Input[str]] = None,
            subject_alternative_names: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            validation_emails: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            validation_method: Optional[pulumi.Input[str]] = None) -> 'Certificate':
        """
        Get an existing Certificate resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The ARN of the certificate
        :param pulumi.Input[str] certificate_authority_arn: ARN of an ACM PCA
        :param pulumi.Input[str] certificate_body: The certificate's PEM-formatted public key
        :param pulumi.Input[str] certificate_chain: The certificate's PEM-formatted chain
               * Creating a private CA issued certificate
        :param pulumi.Input[str] domain_name: A domain name for which the certificate should be issued
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['CertificateDomainValidationOptionArgs']]]] domain_validation_options: Set of domain validation objects which can be used to complete certificate validation. Can have more than one element, e.g., if SANs are defined. Only set if `DNS`-validation was used.
        :param pulumi.Input[pulumi.InputType['CertificateOptionsArgs']] options: Configuration block used to set certificate options. Detailed below.
               * Importing an existing certificate
        :param pulumi.Input[str] private_key: The certificate's PEM-formatted private key
        :param pulumi.Input[str] status: Status of the certificate.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] subject_alternative_names: Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource..
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider .
        :param pulumi.Input[Sequence[pulumi.Input[str]]] validation_emails: A list of addresses that received a validation E-Mail. Only set if `EMAIL`-validation was used.
        :param pulumi.Input[str] validation_method: Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _CertificateState.__new__(_CertificateState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["certificate_authority_arn"] = certificate_authority_arn
        __props__.__dict__["certificate_body"] = certificate_body
        __props__.__dict__["certificate_chain"] = certificate_chain
        __props__.__dict__["domain_name"] = domain_name
        __props__.__dict__["domain_validation_options"] = domain_validation_options
        __props__.__dict__["options"] = options
        __props__.__dict__["private_key"] = private_key
        __props__.__dict__["status"] = status
        __props__.__dict__["subject_alternative_names"] = subject_alternative_names
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        __props__.__dict__["validation_emails"] = validation_emails
        __props__.__dict__["validation_method"] = validation_method
        return Certificate(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The ARN of the certificate
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="certificateAuthorityArn")
    def certificate_authority_arn(self) -> pulumi.Output[Optional[str]]:
        """
        ARN of an ACM PCA
        """
        return pulumi.get(self, "certificate_authority_arn")

    @property
    @pulumi.getter(name="certificateBody")
    def certificate_body(self) -> pulumi.Output[Optional[str]]:
        """
        The certificate's PEM-formatted public key
        """
        return pulumi.get(self, "certificate_body")

    @property
    @pulumi.getter(name="certificateChain")
    def certificate_chain(self) -> pulumi.Output[Optional[str]]:
        """
        The certificate's PEM-formatted chain
        * Creating a private CA issued certificate
        """
        return pulumi.get(self, "certificate_chain")

    @property
    @pulumi.getter(name="domainName")
    def domain_name(self) -> pulumi.Output[str]:
        """
        A domain name for which the certificate should be issued
        """
        return pulumi.get(self, "domain_name")

    @property
    @pulumi.getter(name="domainValidationOptions")
    def domain_validation_options(self) -> pulumi.Output[Sequence['outputs.CertificateDomainValidationOption']]:
        """
        Set of domain validation objects which can be used to complete certificate validation. Can have more than one element, e.g., if SANs are defined. Only set if `DNS`-validation was used.
        """
        return pulumi.get(self, "domain_validation_options")

    @property
    @pulumi.getter
    def options(self) -> pulumi.Output[Optional['outputs.CertificateOptions']]:
        """
        Configuration block used to set certificate options. Detailed below.
        * Importing an existing certificate
        """
        return pulumi.get(self, "options")

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> pulumi.Output[Optional[str]]:
        """
        The certificate's PEM-formatted private key
        """
        return pulumi.get(self, "private_key")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        Status of the certificate.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter(name="subjectAlternativeNames")
    def subject_alternative_names(self) -> pulumi.Output[Sequence[str]]:
        """
        Set of domains that should be SANs in the issued certificate. To remove all elements of a previously configured list, set this value equal to an empty list (`[]`).
        """
        return pulumi.get(self, "subject_alternative_names")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of tags to assign to the resource..
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider .
        """
        return pulumi.get(self, "tags_all")

    @property
    @pulumi.getter(name="validationEmails")
    def validation_emails(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of addresses that received a validation E-Mail. Only set if `EMAIL`-validation was used.
        """
        return pulumi.get(self, "validation_emails")

    @property
    @pulumi.getter(name="validationMethod")
    def validation_method(self) -> pulumi.Output[str]:
        """
        Which method to use for validation. `DNS` or `EMAIL` are valid, `NONE` can be used for certificates that were imported into ACM and then into the provider.
        """
        return pulumi.get(self, "validation_method")

