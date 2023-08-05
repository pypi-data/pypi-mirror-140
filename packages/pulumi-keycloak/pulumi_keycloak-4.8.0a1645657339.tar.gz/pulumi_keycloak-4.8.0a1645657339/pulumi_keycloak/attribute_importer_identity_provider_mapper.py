# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['AttributeImporterIdentityProviderMapperArgs', 'AttributeImporterIdentityProviderMapper']

@pulumi.input_type
class AttributeImporterIdentityProviderMapperArgs:
    def __init__(__self__, *,
                 identity_provider_alias: pulumi.Input[str],
                 realm: pulumi.Input[str],
                 user_attribute: pulumi.Input[str],
                 attribute_friendly_name: Optional[pulumi.Input[str]] = None,
                 attribute_name: Optional[pulumi.Input[str]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 extra_config: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a AttributeImporterIdentityProviderMapper resource.
        :param pulumi.Input[str] identity_provider_alias: The alias of the associated identity provider.
        :param pulumi.Input[str] realm: The name of the realm.
        :param pulumi.Input[str] user_attribute: The user attribute or property name to store the mapped result.
        :param pulumi.Input[str] attribute_friendly_name: For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        :param pulumi.Input[str] attribute_name: For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        :param pulumi.Input[str] claim_name: For OIDC based providers, this is the name of the claim to use.
        :param pulumi.Input[Mapping[str, Any]] extra_config: Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        :param pulumi.Input[str] name: The name of the mapper.
        """
        pulumi.set(__self__, "identity_provider_alias", identity_provider_alias)
        pulumi.set(__self__, "realm", realm)
        pulumi.set(__self__, "user_attribute", user_attribute)
        if attribute_friendly_name is not None:
            pulumi.set(__self__, "attribute_friendly_name", attribute_friendly_name)
        if attribute_name is not None:
            pulumi.set(__self__, "attribute_name", attribute_name)
        if claim_name is not None:
            pulumi.set(__self__, "claim_name", claim_name)
        if extra_config is not None:
            pulumi.set(__self__, "extra_config", extra_config)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="identityProviderAlias")
    def identity_provider_alias(self) -> pulumi.Input[str]:
        """
        The alias of the associated identity provider.
        """
        return pulumi.get(self, "identity_provider_alias")

    @identity_provider_alias.setter
    def identity_provider_alias(self, value: pulumi.Input[str]):
        pulumi.set(self, "identity_provider_alias", value)

    @property
    @pulumi.getter
    def realm(self) -> pulumi.Input[str]:
        """
        The name of the realm.
        """
        return pulumi.get(self, "realm")

    @realm.setter
    def realm(self, value: pulumi.Input[str]):
        pulumi.set(self, "realm", value)

    @property
    @pulumi.getter(name="userAttribute")
    def user_attribute(self) -> pulumi.Input[str]:
        """
        The user attribute or property name to store the mapped result.
        """
        return pulumi.get(self, "user_attribute")

    @user_attribute.setter
    def user_attribute(self, value: pulumi.Input[str]):
        pulumi.set(self, "user_attribute", value)

    @property
    @pulumi.getter(name="attributeFriendlyName")
    def attribute_friendly_name(self) -> Optional[pulumi.Input[str]]:
        """
        For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        """
        return pulumi.get(self, "attribute_friendly_name")

    @attribute_friendly_name.setter
    def attribute_friendly_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "attribute_friendly_name", value)

    @property
    @pulumi.getter(name="attributeName")
    def attribute_name(self) -> Optional[pulumi.Input[str]]:
        """
        For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        """
        return pulumi.get(self, "attribute_name")

    @attribute_name.setter
    def attribute_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "attribute_name", value)

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> Optional[pulumi.Input[str]]:
        """
        For OIDC based providers, this is the name of the claim to use.
        """
        return pulumi.get(self, "claim_name")

    @claim_name.setter
    def claim_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "claim_name", value)

    @property
    @pulumi.getter(name="extraConfig")
    def extra_config(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        """
        return pulumi.get(self, "extra_config")

    @extra_config.setter
    def extra_config(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "extra_config", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the mapper.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class _AttributeImporterIdentityProviderMapperState:
    def __init__(__self__, *,
                 attribute_friendly_name: Optional[pulumi.Input[str]] = None,
                 attribute_name: Optional[pulumi.Input[str]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 extra_config: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 identity_provider_alias: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm: Optional[pulumi.Input[str]] = None,
                 user_attribute: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering AttributeImporterIdentityProviderMapper resources.
        :param pulumi.Input[str] attribute_friendly_name: For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        :param pulumi.Input[str] attribute_name: For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        :param pulumi.Input[str] claim_name: For OIDC based providers, this is the name of the claim to use.
        :param pulumi.Input[Mapping[str, Any]] extra_config: Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        :param pulumi.Input[str] identity_provider_alias: The alias of the associated identity provider.
        :param pulumi.Input[str] name: The name of the mapper.
        :param pulumi.Input[str] realm: The name of the realm.
        :param pulumi.Input[str] user_attribute: The user attribute or property name to store the mapped result.
        """
        if attribute_friendly_name is not None:
            pulumi.set(__self__, "attribute_friendly_name", attribute_friendly_name)
        if attribute_name is not None:
            pulumi.set(__self__, "attribute_name", attribute_name)
        if claim_name is not None:
            pulumi.set(__self__, "claim_name", claim_name)
        if extra_config is not None:
            pulumi.set(__self__, "extra_config", extra_config)
        if identity_provider_alias is not None:
            pulumi.set(__self__, "identity_provider_alias", identity_provider_alias)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if realm is not None:
            pulumi.set(__self__, "realm", realm)
        if user_attribute is not None:
            pulumi.set(__self__, "user_attribute", user_attribute)

    @property
    @pulumi.getter(name="attributeFriendlyName")
    def attribute_friendly_name(self) -> Optional[pulumi.Input[str]]:
        """
        For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        """
        return pulumi.get(self, "attribute_friendly_name")

    @attribute_friendly_name.setter
    def attribute_friendly_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "attribute_friendly_name", value)

    @property
    @pulumi.getter(name="attributeName")
    def attribute_name(self) -> Optional[pulumi.Input[str]]:
        """
        For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        """
        return pulumi.get(self, "attribute_name")

    @attribute_name.setter
    def attribute_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "attribute_name", value)

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> Optional[pulumi.Input[str]]:
        """
        For OIDC based providers, this is the name of the claim to use.
        """
        return pulumi.get(self, "claim_name")

    @claim_name.setter
    def claim_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "claim_name", value)

    @property
    @pulumi.getter(name="extraConfig")
    def extra_config(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        """
        return pulumi.get(self, "extra_config")

    @extra_config.setter
    def extra_config(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "extra_config", value)

    @property
    @pulumi.getter(name="identityProviderAlias")
    def identity_provider_alias(self) -> Optional[pulumi.Input[str]]:
        """
        The alias of the associated identity provider.
        """
        return pulumi.get(self, "identity_provider_alias")

    @identity_provider_alias.setter
    def identity_provider_alias(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "identity_provider_alias", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the mapper.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def realm(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the realm.
        """
        return pulumi.get(self, "realm")

    @realm.setter
    def realm(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "realm", value)

    @property
    @pulumi.getter(name="userAttribute")
    def user_attribute(self) -> Optional[pulumi.Input[str]]:
        """
        The user attribute or property name to store the mapped result.
        """
        return pulumi.get(self, "user_attribute")

    @user_attribute.setter
    def user_attribute(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_attribute", value)


class AttributeImporterIdentityProviderMapper(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 attribute_friendly_name: Optional[pulumi.Input[str]] = None,
                 attribute_name: Optional[pulumi.Input[str]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 extra_config: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 identity_provider_alias: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm: Optional[pulumi.Input[str]] = None,
                 user_attribute: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Allows for creating and managing an attribute importer identity provider mapper within Keycloak.

        The attribute importer mapper can be used to map attributes from externally defined users to attributes or properties of the imported Keycloak user:
        - For the OIDC identity provider, this will map a claim on the ID or access token to an attribute for the imported Keycloak user.
        - For the SAML identity provider, this will map a SAML attribute found within the assertion to an attribute for the imported Keycloak user.
        - For social identity providers, this will map a JSON field from the user profile to an attribute for the imported Keycloak user.

        > If you are using Keycloak 10 or higher, you will need to specify the `extra_config` argument in order to define a `syncMode` for the mapper.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        oidc_identity_provider = keycloak.oidc.IdentityProvider("oidcIdentityProvider",
            realm=realm.id,
            alias="oidc",
            authorization_url="https://example.com/auth",
            token_url="https://example.com/token",
            client_id="example_id",
            client_secret="example_token",
            default_scopes="openid random profile")
        oidc_attribute_importer_identity_provider_mapper = keycloak.AttributeImporterIdentityProviderMapper("oidcAttributeImporterIdentityProviderMapper",
            realm=realm.id,
            claim_name="my-email-claim",
            identity_provider_alias=oidc_identity_provider.alias,
            user_attribute="email",
            extra_config={
                "syncMode": "INHERIT",
            })
        ```

        ## Import

        Identity provider mappers can be imported using the format `{{realm_id}}/{{idp_alias}}/{{idp_mapper_id}}`, where `idp_alias` is the identity provider alias, and `idp_mapper_id` is the unique ID that Keycloak assigns to the mapper upon creation. This value can be found in the URI when editing this mapper in the GUI, and is typically a GUID. Examplebash

        ```sh
         $ pulumi import keycloak:index/attributeImporterIdentityProviderMapper:AttributeImporterIdentityProviderMapper test_mapper my-realm/my-mapper/f446db98-7133-4e30-b18a-3d28fde7ca1b
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] attribute_friendly_name: For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        :param pulumi.Input[str] attribute_name: For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        :param pulumi.Input[str] claim_name: For OIDC based providers, this is the name of the claim to use.
        :param pulumi.Input[Mapping[str, Any]] extra_config: Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        :param pulumi.Input[str] identity_provider_alias: The alias of the associated identity provider.
        :param pulumi.Input[str] name: The name of the mapper.
        :param pulumi.Input[str] realm: The name of the realm.
        :param pulumi.Input[str] user_attribute: The user attribute or property name to store the mapped result.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: AttributeImporterIdentityProviderMapperArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Allows for creating and managing an attribute importer identity provider mapper within Keycloak.

        The attribute importer mapper can be used to map attributes from externally defined users to attributes or properties of the imported Keycloak user:
        - For the OIDC identity provider, this will map a claim on the ID or access token to an attribute for the imported Keycloak user.
        - For the SAML identity provider, this will map a SAML attribute found within the assertion to an attribute for the imported Keycloak user.
        - For social identity providers, this will map a JSON field from the user profile to an attribute for the imported Keycloak user.

        > If you are using Keycloak 10 or higher, you will need to specify the `extra_config` argument in order to define a `syncMode` for the mapper.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        oidc_identity_provider = keycloak.oidc.IdentityProvider("oidcIdentityProvider",
            realm=realm.id,
            alias="oidc",
            authorization_url="https://example.com/auth",
            token_url="https://example.com/token",
            client_id="example_id",
            client_secret="example_token",
            default_scopes="openid random profile")
        oidc_attribute_importer_identity_provider_mapper = keycloak.AttributeImporterIdentityProviderMapper("oidcAttributeImporterIdentityProviderMapper",
            realm=realm.id,
            claim_name="my-email-claim",
            identity_provider_alias=oidc_identity_provider.alias,
            user_attribute="email",
            extra_config={
                "syncMode": "INHERIT",
            })
        ```

        ## Import

        Identity provider mappers can be imported using the format `{{realm_id}}/{{idp_alias}}/{{idp_mapper_id}}`, where `idp_alias` is the identity provider alias, and `idp_mapper_id` is the unique ID that Keycloak assigns to the mapper upon creation. This value can be found in the URI when editing this mapper in the GUI, and is typically a GUID. Examplebash

        ```sh
         $ pulumi import keycloak:index/attributeImporterIdentityProviderMapper:AttributeImporterIdentityProviderMapper test_mapper my-realm/my-mapper/f446db98-7133-4e30-b18a-3d28fde7ca1b
        ```

        :param str resource_name: The name of the resource.
        :param AttributeImporterIdentityProviderMapperArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AttributeImporterIdentityProviderMapperArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 attribute_friendly_name: Optional[pulumi.Input[str]] = None,
                 attribute_name: Optional[pulumi.Input[str]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 extra_config: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 identity_provider_alias: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm: Optional[pulumi.Input[str]] = None,
                 user_attribute: Optional[pulumi.Input[str]] = None,
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
            __props__ = AttributeImporterIdentityProviderMapperArgs.__new__(AttributeImporterIdentityProviderMapperArgs)

            __props__.__dict__["attribute_friendly_name"] = attribute_friendly_name
            __props__.__dict__["attribute_name"] = attribute_name
            __props__.__dict__["claim_name"] = claim_name
            __props__.__dict__["extra_config"] = extra_config
            if identity_provider_alias is None and not opts.urn:
                raise TypeError("Missing required property 'identity_provider_alias'")
            __props__.__dict__["identity_provider_alias"] = identity_provider_alias
            __props__.__dict__["name"] = name
            if realm is None and not opts.urn:
                raise TypeError("Missing required property 'realm'")
            __props__.__dict__["realm"] = realm
            if user_attribute is None and not opts.urn:
                raise TypeError("Missing required property 'user_attribute'")
            __props__.__dict__["user_attribute"] = user_attribute
        super(AttributeImporterIdentityProviderMapper, __self__).__init__(
            'keycloak:index/attributeImporterIdentityProviderMapper:AttributeImporterIdentityProviderMapper',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            attribute_friendly_name: Optional[pulumi.Input[str]] = None,
            attribute_name: Optional[pulumi.Input[str]] = None,
            claim_name: Optional[pulumi.Input[str]] = None,
            extra_config: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            identity_provider_alias: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            realm: Optional[pulumi.Input[str]] = None,
            user_attribute: Optional[pulumi.Input[str]] = None) -> 'AttributeImporterIdentityProviderMapper':
        """
        Get an existing AttributeImporterIdentityProviderMapper resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] attribute_friendly_name: For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        :param pulumi.Input[str] attribute_name: For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        :param pulumi.Input[str] claim_name: For OIDC based providers, this is the name of the claim to use.
        :param pulumi.Input[Mapping[str, Any]] extra_config: Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        :param pulumi.Input[str] identity_provider_alias: The alias of the associated identity provider.
        :param pulumi.Input[str] name: The name of the mapper.
        :param pulumi.Input[str] realm: The name of the realm.
        :param pulumi.Input[str] user_attribute: The user attribute or property name to store the mapped result.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AttributeImporterIdentityProviderMapperState.__new__(_AttributeImporterIdentityProviderMapperState)

        __props__.__dict__["attribute_friendly_name"] = attribute_friendly_name
        __props__.__dict__["attribute_name"] = attribute_name
        __props__.__dict__["claim_name"] = claim_name
        __props__.__dict__["extra_config"] = extra_config
        __props__.__dict__["identity_provider_alias"] = identity_provider_alias
        __props__.__dict__["name"] = name
        __props__.__dict__["realm"] = realm
        __props__.__dict__["user_attribute"] = user_attribute
        return AttributeImporterIdentityProviderMapper(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="attributeFriendlyName")
    def attribute_friendly_name(self) -> pulumi.Output[Optional[str]]:
        """
        For SAML based providers, this is the friendly name of the attribute to search for in the assertion. Conflicts with `attribute_name`.
        """
        return pulumi.get(self, "attribute_friendly_name")

    @property
    @pulumi.getter(name="attributeName")
    def attribute_name(self) -> pulumi.Output[Optional[str]]:
        """
        For SAML based providers, this is the name of the attribute to search for in the assertion. Conflicts with `attribute_friendly_name`.
        """
        return pulumi.get(self, "attribute_name")

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> pulumi.Output[Optional[str]]:
        """
        For OIDC based providers, this is the name of the claim to use.
        """
        return pulumi.get(self, "claim_name")

    @property
    @pulumi.getter(name="extraConfig")
    def extra_config(self) -> pulumi.Output[Optional[Mapping[str, Any]]]:
        """
        Key/value attributes to add to the identity provider mapper model that is persisted to Keycloak. This can be used to extend the base model with new Keycloak features.
        """
        return pulumi.get(self, "extra_config")

    @property
    @pulumi.getter(name="identityProviderAlias")
    def identity_provider_alias(self) -> pulumi.Output[str]:
        """
        The alias of the associated identity provider.
        """
        return pulumi.get(self, "identity_provider_alias")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the mapper.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def realm(self) -> pulumi.Output[str]:
        """
        The name of the realm.
        """
        return pulumi.get(self, "realm")

    @property
    @pulumi.getter(name="userAttribute")
    def user_attribute(self) -> pulumi.Output[str]:
        """
        The user attribute or property name to store the mapped result.
        """
        return pulumi.get(self, "user_attribute")

