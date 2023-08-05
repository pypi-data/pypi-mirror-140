# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['ConsumerJwtAuthArgs', 'ConsumerJwtAuth']

@pulumi.input_type
class ConsumerJwtAuthArgs:
    def __init__(__self__, *,
                 consumer_id: pulumi.Input[str],
                 rsa_public_key: pulumi.Input[str],
                 algorithm: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 secret: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ConsumerJwtAuth resource.
        :param pulumi.Input[str] consumer_id: the id of the consumer to be configured with jwt auth
        :param pulumi.Input[str] rsa_public_key: If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        :param pulumi.Input[str] algorithm: The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        :param pulumi.Input[str] key: A unique string identifying the credential. If left out, it will be auto-generated.
        :param pulumi.Input[str] secret: If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        pulumi.set(__self__, "consumer_id", consumer_id)
        pulumi.set(__self__, "rsa_public_key", rsa_public_key)
        if algorithm is not None:
            pulumi.set(__self__, "algorithm", algorithm)
        if key is not None:
            pulumi.set(__self__, "key", key)
        if secret is not None:
            pulumi.set(__self__, "secret", secret)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> pulumi.Input[str]:
        """
        the id of the consumer to be configured with jwt auth
        """
        return pulumi.get(self, "consumer_id")

    @consumer_id.setter
    def consumer_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "consumer_id", value)

    @property
    @pulumi.getter(name="rsaPublicKey")
    def rsa_public_key(self) -> pulumi.Input[str]:
        """
        If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        """
        return pulumi.get(self, "rsa_public_key")

    @rsa_public_key.setter
    def rsa_public_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "rsa_public_key", value)

    @property
    @pulumi.getter
    def algorithm(self) -> Optional[pulumi.Input[str]]:
        """
        The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        """
        return pulumi.get(self, "algorithm")

    @algorithm.setter
    def algorithm(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "algorithm", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        """
        A unique string identifying the credential. If left out, it will be auto-generated.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter
    def secret(self) -> Optional[pulumi.Input[str]]:
        """
        If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        """
        return pulumi.get(self, "secret")

    @secret.setter
    def secret(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "secret", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _ConsumerJwtAuthState:
    def __init__(__self__, *,
                 algorithm: Optional[pulumi.Input[str]] = None,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 rsa_public_key: Optional[pulumi.Input[str]] = None,
                 secret: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering ConsumerJwtAuth resources.
        :param pulumi.Input[str] algorithm: The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        :param pulumi.Input[str] consumer_id: the id of the consumer to be configured with jwt auth
        :param pulumi.Input[str] key: A unique string identifying the credential. If left out, it will be auto-generated.
        :param pulumi.Input[str] rsa_public_key: If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        :param pulumi.Input[str] secret: If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        if algorithm is not None:
            pulumi.set(__self__, "algorithm", algorithm)
        if consumer_id is not None:
            pulumi.set(__self__, "consumer_id", consumer_id)
        if key is not None:
            pulumi.set(__self__, "key", key)
        if rsa_public_key is not None:
            pulumi.set(__self__, "rsa_public_key", rsa_public_key)
        if secret is not None:
            pulumi.set(__self__, "secret", secret)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def algorithm(self) -> Optional[pulumi.Input[str]]:
        """
        The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        """
        return pulumi.get(self, "algorithm")

    @algorithm.setter
    def algorithm(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "algorithm", value)

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> Optional[pulumi.Input[str]]:
        """
        the id of the consumer to be configured with jwt auth
        """
        return pulumi.get(self, "consumer_id")

    @consumer_id.setter
    def consumer_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "consumer_id", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[pulumi.Input[str]]:
        """
        A unique string identifying the credential. If left out, it will be auto-generated.
        """
        return pulumi.get(self, "key")

    @key.setter
    def key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "key", value)

    @property
    @pulumi.getter(name="rsaPublicKey")
    def rsa_public_key(self) -> Optional[pulumi.Input[str]]:
        """
        If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        """
        return pulumi.get(self, "rsa_public_key")

    @rsa_public_key.setter
    def rsa_public_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rsa_public_key", value)

    @property
    @pulumi.getter
    def secret(self) -> Optional[pulumi.Input[str]]:
        """
        If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        """
        return pulumi.get(self, "secret")

    @secret.setter
    def secret(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "secret", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


class ConsumerJwtAuth(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 algorithm: Optional[pulumi.Input[str]] = None,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 rsa_public_key: Optional[pulumi.Input[str]] = None,
                 secret: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        ## # ConsumerJwtAuth

        Consumer jwt auth is a resource that allows you to configure the jwt auth plugin for a consumer.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_kong as kong

        my_consumer = kong.Consumer("myConsumer",
            custom_id="123",
            username="User1")
        jwt_plugin = kong.Plugin("jwtPlugin", config_json=\"\"\"	{
        		"claims_to_verify": ["exp"]
        	}

        \"\"\")
        consumer_jwt_config = kong.ConsumerJwtAuth("consumerJwtConfig",
            algorithm="HS256",
            consumer_id=my_consumer.id,
            key="my_key",
            rsa_public_key="foo",
            secret="my_secret")
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] algorithm: The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        :param pulumi.Input[str] consumer_id: the id of the consumer to be configured with jwt auth
        :param pulumi.Input[str] key: A unique string identifying the credential. If left out, it will be auto-generated.
        :param pulumi.Input[str] rsa_public_key: If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        :param pulumi.Input[str] secret: If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ConsumerJwtAuthArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## # ConsumerJwtAuth

        Consumer jwt auth is a resource that allows you to configure the jwt auth plugin for a consumer.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_kong as kong

        my_consumer = kong.Consumer("myConsumer",
            custom_id="123",
            username="User1")
        jwt_plugin = kong.Plugin("jwtPlugin", config_json=\"\"\"	{
        		"claims_to_verify": ["exp"]
        	}

        \"\"\")
        consumer_jwt_config = kong.ConsumerJwtAuth("consumerJwtConfig",
            algorithm="HS256",
            consumer_id=my_consumer.id,
            key="my_key",
            rsa_public_key="foo",
            secret="my_secret")
        ```

        :param str resource_name: The name of the resource.
        :param ConsumerJwtAuthArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConsumerJwtAuthArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 algorithm: Optional[pulumi.Input[str]] = None,
                 consumer_id: Optional[pulumi.Input[str]] = None,
                 key: Optional[pulumi.Input[str]] = None,
                 rsa_public_key: Optional[pulumi.Input[str]] = None,
                 secret: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
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
            __props__ = ConsumerJwtAuthArgs.__new__(ConsumerJwtAuthArgs)

            __props__.__dict__["algorithm"] = algorithm
            if consumer_id is None and not opts.urn:
                raise TypeError("Missing required property 'consumer_id'")
            __props__.__dict__["consumer_id"] = consumer_id
            __props__.__dict__["key"] = key
            if rsa_public_key is None and not opts.urn:
                raise TypeError("Missing required property 'rsa_public_key'")
            __props__.__dict__["rsa_public_key"] = rsa_public_key
            __props__.__dict__["secret"] = secret
            __props__.__dict__["tags"] = tags
        super(ConsumerJwtAuth, __self__).__init__(
            'kong:index/consumerJwtAuth:ConsumerJwtAuth',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            algorithm: Optional[pulumi.Input[str]] = None,
            consumer_id: Optional[pulumi.Input[str]] = None,
            key: Optional[pulumi.Input[str]] = None,
            rsa_public_key: Optional[pulumi.Input[str]] = None,
            secret: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'ConsumerJwtAuth':
        """
        Get an existing ConsumerJwtAuth resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] algorithm: The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        :param pulumi.Input[str] consumer_id: the id of the consumer to be configured with jwt auth
        :param pulumi.Input[str] key: A unique string identifying the credential. If left out, it will be auto-generated.
        :param pulumi.Input[str] rsa_public_key: If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        :param pulumi.Input[str] secret: If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        :param pulumi.Input[Sequence[pulumi.Input[str]]] tags: A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ConsumerJwtAuthState.__new__(_ConsumerJwtAuthState)

        __props__.__dict__["algorithm"] = algorithm
        __props__.__dict__["consumer_id"] = consumer_id
        __props__.__dict__["key"] = key
        __props__.__dict__["rsa_public_key"] = rsa_public_key
        __props__.__dict__["secret"] = secret
        __props__.__dict__["tags"] = tags
        return ConsumerJwtAuth(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def algorithm(self) -> pulumi.Output[Optional[str]]:
        """
        The algorithm used to verify the token’s signature. Can be HS256, HS384, HS512, RS256, or ES256, Default is `HS256`
        """
        return pulumi.get(self, "algorithm")

    @property
    @pulumi.getter(name="consumerId")
    def consumer_id(self) -> pulumi.Output[str]:
        """
        the id of the consumer to be configured with jwt auth
        """
        return pulumi.get(self, "consumer_id")

    @property
    @pulumi.getter
    def key(self) -> pulumi.Output[Optional[str]]:
        """
        A unique string identifying the credential. If left out, it will be auto-generated.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter(name="rsaPublicKey")
    def rsa_public_key(self) -> pulumi.Output[str]:
        """
        If algorithm is `RS256` or `ES256`, the public key (in PEM format) to use to verify the token’s signature
        """
        return pulumi.get(self, "rsa_public_key")

    @property
    @pulumi.getter
    def secret(self) -> pulumi.Output[Optional[str]]:
        """
        If algorithm is `HS256` or `ES256`, the secret used to sign JWTs for this credential. If left out, will be auto-generated
        """
        return pulumi.get(self, "secret")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of strings associated with the consumer JWT auth for grouping and filtering
        """
        return pulumi.get(self, "tags")

