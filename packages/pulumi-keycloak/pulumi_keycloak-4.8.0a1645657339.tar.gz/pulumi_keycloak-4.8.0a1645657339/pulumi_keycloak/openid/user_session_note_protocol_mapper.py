# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['UserSessionNoteProtocolMapperArgs', 'UserSessionNoteProtocolMapper']

@pulumi.input_type
class UserSessionNoteProtocolMapperArgs:
    def __init__(__self__, *,
                 claim_name: pulumi.Input[str],
                 realm_id: pulumi.Input[str],
                 add_to_access_token: Optional[pulumi.Input[bool]] = None,
                 add_to_id_token: Optional[pulumi.Input[bool]] = None,
                 claim_value_type: Optional[pulumi.Input[str]] = None,
                 client_id: Optional[pulumi.Input[str]] = None,
                 client_scope_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 session_note: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a UserSessionNoteProtocolMapper resource.
        :param pulumi.Input[str] claim_name: The name of the claim to insert into a token.
        :param pulumi.Input[str] realm_id: The realm this protocol mapper exists within.
        :param pulumi.Input[bool] add_to_access_token: Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        :param pulumi.Input[bool] add_to_id_token: Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        :param pulumi.Input[str] claim_value_type: The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        :param pulumi.Input[str] client_id: The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] client_scope_id: The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] name: The display name of this protocol mapper in the GUI.
        :param pulumi.Input[str] session_note: String value being the name of stored user session note within the UserSessionModel.note map.
        """
        pulumi.set(__self__, "claim_name", claim_name)
        pulumi.set(__self__, "realm_id", realm_id)
        if add_to_access_token is not None:
            pulumi.set(__self__, "add_to_access_token", add_to_access_token)
        if add_to_id_token is not None:
            pulumi.set(__self__, "add_to_id_token", add_to_id_token)
        if claim_value_type is not None:
            pulumi.set(__self__, "claim_value_type", claim_value_type)
        if client_id is not None:
            pulumi.set(__self__, "client_id", client_id)
        if client_scope_id is not None:
            pulumi.set(__self__, "client_scope_id", client_scope_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if session_note is not None:
            pulumi.set(__self__, "session_note", session_note)

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> pulumi.Input[str]:
        """
        The name of the claim to insert into a token.
        """
        return pulumi.get(self, "claim_name")

    @claim_name.setter
    def claim_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "claim_name", value)

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Input[str]:
        """
        The realm this protocol mapper exists within.
        """
        return pulumi.get(self, "realm_id")

    @realm_id.setter
    def realm_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "realm_id", value)

    @property
    @pulumi.getter(name="addToAccessToken")
    def add_to_access_token(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_access_token")

    @add_to_access_token.setter
    def add_to_access_token(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_to_access_token", value)

    @property
    @pulumi.getter(name="addToIdToken")
    def add_to_id_token(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_id_token")

    @add_to_id_token.setter
    def add_to_id_token(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_to_id_token", value)

    @property
    @pulumi.getter(name="claimValueType")
    def claim_value_type(self) -> Optional[pulumi.Input[str]]:
        """
        The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        """
        return pulumi.get(self, "claim_value_type")

    @claim_value_type.setter
    def claim_value_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "claim_value_type", value)

    @property
    @pulumi.getter(name="clientId")
    def client_id(self) -> Optional[pulumi.Input[str]]:
        """
        The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_id")

    @client_id.setter
    def client_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "client_id", value)

    @property
    @pulumi.getter(name="clientScopeId")
    def client_scope_id(self) -> Optional[pulumi.Input[str]]:
        """
        The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_scope_id")

    @client_scope_id.setter
    def client_scope_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "client_scope_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The display name of this protocol mapper in the GUI.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="sessionNote")
    def session_note(self) -> Optional[pulumi.Input[str]]:
        """
        String value being the name of stored user session note within the UserSessionModel.note map.
        """
        return pulumi.get(self, "session_note")

    @session_note.setter
    def session_note(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_note", value)


@pulumi.input_type
class _UserSessionNoteProtocolMapperState:
    def __init__(__self__, *,
                 add_to_access_token: Optional[pulumi.Input[bool]] = None,
                 add_to_id_token: Optional[pulumi.Input[bool]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 claim_value_type: Optional[pulumi.Input[str]] = None,
                 client_id: Optional[pulumi.Input[str]] = None,
                 client_scope_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 session_note: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering UserSessionNoteProtocolMapper resources.
        :param pulumi.Input[bool] add_to_access_token: Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        :param pulumi.Input[bool] add_to_id_token: Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        :param pulumi.Input[str] claim_name: The name of the claim to insert into a token.
        :param pulumi.Input[str] claim_value_type: The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        :param pulumi.Input[str] client_id: The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] client_scope_id: The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] name: The display name of this protocol mapper in the GUI.
        :param pulumi.Input[str] realm_id: The realm this protocol mapper exists within.
        :param pulumi.Input[str] session_note: String value being the name of stored user session note within the UserSessionModel.note map.
        """
        if add_to_access_token is not None:
            pulumi.set(__self__, "add_to_access_token", add_to_access_token)
        if add_to_id_token is not None:
            pulumi.set(__self__, "add_to_id_token", add_to_id_token)
        if claim_name is not None:
            pulumi.set(__self__, "claim_name", claim_name)
        if claim_value_type is not None:
            pulumi.set(__self__, "claim_value_type", claim_value_type)
        if client_id is not None:
            pulumi.set(__self__, "client_id", client_id)
        if client_scope_id is not None:
            pulumi.set(__self__, "client_scope_id", client_scope_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if realm_id is not None:
            pulumi.set(__self__, "realm_id", realm_id)
        if session_note is not None:
            pulumi.set(__self__, "session_note", session_note)

    @property
    @pulumi.getter(name="addToAccessToken")
    def add_to_access_token(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_access_token")

    @add_to_access_token.setter
    def add_to_access_token(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_to_access_token", value)

    @property
    @pulumi.getter(name="addToIdToken")
    def add_to_id_token(self) -> Optional[pulumi.Input[bool]]:
        """
        Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_id_token")

    @add_to_id_token.setter
    def add_to_id_token(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_to_id_token", value)

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the claim to insert into a token.
        """
        return pulumi.get(self, "claim_name")

    @claim_name.setter
    def claim_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "claim_name", value)

    @property
    @pulumi.getter(name="claimValueType")
    def claim_value_type(self) -> Optional[pulumi.Input[str]]:
        """
        The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        """
        return pulumi.get(self, "claim_value_type")

    @claim_value_type.setter
    def claim_value_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "claim_value_type", value)

    @property
    @pulumi.getter(name="clientId")
    def client_id(self) -> Optional[pulumi.Input[str]]:
        """
        The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_id")

    @client_id.setter
    def client_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "client_id", value)

    @property
    @pulumi.getter(name="clientScopeId")
    def client_scope_id(self) -> Optional[pulumi.Input[str]]:
        """
        The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_scope_id")

    @client_scope_id.setter
    def client_scope_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "client_scope_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The display name of this protocol mapper in the GUI.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> Optional[pulumi.Input[str]]:
        """
        The realm this protocol mapper exists within.
        """
        return pulumi.get(self, "realm_id")

    @realm_id.setter
    def realm_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "realm_id", value)

    @property
    @pulumi.getter(name="sessionNote")
    def session_note(self) -> Optional[pulumi.Input[str]]:
        """
        String value being the name of stored user session note within the UserSessionModel.note map.
        """
        return pulumi.get(self, "session_note")

    @session_note.setter
    def session_note(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_note", value)


class UserSessionNoteProtocolMapper(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 add_to_access_token: Optional[pulumi.Input[bool]] = None,
                 add_to_id_token: Optional[pulumi.Input[bool]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 claim_value_type: Optional[pulumi.Input[str]] = None,
                 client_id: Optional[pulumi.Input[str]] = None,
                 client_scope_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 session_note: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Allows for creating and managing user session note protocol mappers within Keycloak.

        User session note protocol mappers map a custom user session note to a token claim.

        Protocol mappers can be defined for a single client, or they can be defined for a client scope which can be shared between
        multiple different clients.

        ## Example Usage
        ### Client)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        openid_client = keycloak.openid.Client("openidClient",
            realm_id=realm.id,
            client_id="client",
            enabled=True,
            access_type="CONFIDENTIAL",
            valid_redirect_uris=["http://localhost:8080/openid-callback"])
        user_session_note_mapper = keycloak.openid.UserSessionNoteProtocolMapper("userSessionNoteMapper",
            realm_id=realm.id,
            client_id=openid_client.id,
            claim_name="foo",
            claim_value_type="String",
            session_note="bar")
        ```
        ### Client Scope)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        client_scope = keycloak.openid.ClientScope("clientScope", realm_id=realm.id)
        user_session_note_mapper = keycloak.openid.UserSessionNoteProtocolMapper("userSessionNoteMapper",
            realm_id=realm.id,
            client_scope_id=client_scope.id,
            claim_name="foo",
            claim_value_type="String",
            session_note="bar")
        ```

        ## Import

        Protocol mappers can be imported using one of the following formats- Client`{{realm_id}}/client/{{client_keycloak_id}}/{{protocol_mapper_id}}` - Client Scope`{{realm_id}}/client-scope/{{client_scope_keycloak_id}}/{{protocol_mapper_id}}` Examplebash

        ```sh
         $ pulumi import keycloak:openid/userSessionNoteProtocolMapper:UserSessionNoteProtocolMapper user_session_note_mapper my-realm/client/a7202154-8793-4656-b655-1dd18c181e14/71602afa-f7d1-4788-8c49-ef8fd00af0f4
        ```

        ```sh
         $ pulumi import keycloak:openid/userSessionNoteProtocolMapper:UserSessionNoteProtocolMapper user_session_note_mapper my-realm/client-scope/b799ea7e-73ee-4a73-990a-1eafebe8e20a/71602afa-f7d1-4788-8c49-ef8fd00af0f4
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] add_to_access_token: Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        :param pulumi.Input[bool] add_to_id_token: Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        :param pulumi.Input[str] claim_name: The name of the claim to insert into a token.
        :param pulumi.Input[str] claim_value_type: The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        :param pulumi.Input[str] client_id: The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] client_scope_id: The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] name: The display name of this protocol mapper in the GUI.
        :param pulumi.Input[str] realm_id: The realm this protocol mapper exists within.
        :param pulumi.Input[str] session_note: String value being the name of stored user session note within the UserSessionModel.note map.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: UserSessionNoteProtocolMapperArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Allows for creating and managing user session note protocol mappers within Keycloak.

        User session note protocol mappers map a custom user session note to a token claim.

        Protocol mappers can be defined for a single client, or they can be defined for a client scope which can be shared between
        multiple different clients.

        ## Example Usage
        ### Client)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        openid_client = keycloak.openid.Client("openidClient",
            realm_id=realm.id,
            client_id="client",
            enabled=True,
            access_type="CONFIDENTIAL",
            valid_redirect_uris=["http://localhost:8080/openid-callback"])
        user_session_note_mapper = keycloak.openid.UserSessionNoteProtocolMapper("userSessionNoteMapper",
            realm_id=realm.id,
            client_id=openid_client.id,
            claim_name="foo",
            claim_value_type="String",
            session_note="bar")
        ```
        ### Client Scope)

        ```python
        import pulumi
        import pulumi_keycloak as keycloak

        realm = keycloak.Realm("realm",
            realm="my-realm",
            enabled=True)
        client_scope = keycloak.openid.ClientScope("clientScope", realm_id=realm.id)
        user_session_note_mapper = keycloak.openid.UserSessionNoteProtocolMapper("userSessionNoteMapper",
            realm_id=realm.id,
            client_scope_id=client_scope.id,
            claim_name="foo",
            claim_value_type="String",
            session_note="bar")
        ```

        ## Import

        Protocol mappers can be imported using one of the following formats- Client`{{realm_id}}/client/{{client_keycloak_id}}/{{protocol_mapper_id}}` - Client Scope`{{realm_id}}/client-scope/{{client_scope_keycloak_id}}/{{protocol_mapper_id}}` Examplebash

        ```sh
         $ pulumi import keycloak:openid/userSessionNoteProtocolMapper:UserSessionNoteProtocolMapper user_session_note_mapper my-realm/client/a7202154-8793-4656-b655-1dd18c181e14/71602afa-f7d1-4788-8c49-ef8fd00af0f4
        ```

        ```sh
         $ pulumi import keycloak:openid/userSessionNoteProtocolMapper:UserSessionNoteProtocolMapper user_session_note_mapper my-realm/client-scope/b799ea7e-73ee-4a73-990a-1eafebe8e20a/71602afa-f7d1-4788-8c49-ef8fd00af0f4
        ```

        :param str resource_name: The name of the resource.
        :param UserSessionNoteProtocolMapperArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(UserSessionNoteProtocolMapperArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 add_to_access_token: Optional[pulumi.Input[bool]] = None,
                 add_to_id_token: Optional[pulumi.Input[bool]] = None,
                 claim_name: Optional[pulumi.Input[str]] = None,
                 claim_value_type: Optional[pulumi.Input[str]] = None,
                 client_id: Optional[pulumi.Input[str]] = None,
                 client_scope_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 realm_id: Optional[pulumi.Input[str]] = None,
                 session_note: Optional[pulumi.Input[str]] = None,
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
            __props__ = UserSessionNoteProtocolMapperArgs.__new__(UserSessionNoteProtocolMapperArgs)

            __props__.__dict__["add_to_access_token"] = add_to_access_token
            __props__.__dict__["add_to_id_token"] = add_to_id_token
            if claim_name is None and not opts.urn:
                raise TypeError("Missing required property 'claim_name'")
            __props__.__dict__["claim_name"] = claim_name
            __props__.__dict__["claim_value_type"] = claim_value_type
            __props__.__dict__["client_id"] = client_id
            __props__.__dict__["client_scope_id"] = client_scope_id
            __props__.__dict__["name"] = name
            if realm_id is None and not opts.urn:
                raise TypeError("Missing required property 'realm_id'")
            __props__.__dict__["realm_id"] = realm_id
            __props__.__dict__["session_note"] = session_note
        super(UserSessionNoteProtocolMapper, __self__).__init__(
            'keycloak:openid/userSessionNoteProtocolMapper:UserSessionNoteProtocolMapper',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            add_to_access_token: Optional[pulumi.Input[bool]] = None,
            add_to_id_token: Optional[pulumi.Input[bool]] = None,
            claim_name: Optional[pulumi.Input[str]] = None,
            claim_value_type: Optional[pulumi.Input[str]] = None,
            client_id: Optional[pulumi.Input[str]] = None,
            client_scope_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            realm_id: Optional[pulumi.Input[str]] = None,
            session_note: Optional[pulumi.Input[str]] = None) -> 'UserSessionNoteProtocolMapper':
        """
        Get an existing UserSessionNoteProtocolMapper resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] add_to_access_token: Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        :param pulumi.Input[bool] add_to_id_token: Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        :param pulumi.Input[str] claim_name: The name of the claim to insert into a token.
        :param pulumi.Input[str] claim_value_type: The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        :param pulumi.Input[str] client_id: The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] client_scope_id: The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        :param pulumi.Input[str] name: The display name of this protocol mapper in the GUI.
        :param pulumi.Input[str] realm_id: The realm this protocol mapper exists within.
        :param pulumi.Input[str] session_note: String value being the name of stored user session note within the UserSessionModel.note map.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _UserSessionNoteProtocolMapperState.__new__(_UserSessionNoteProtocolMapperState)

        __props__.__dict__["add_to_access_token"] = add_to_access_token
        __props__.__dict__["add_to_id_token"] = add_to_id_token
        __props__.__dict__["claim_name"] = claim_name
        __props__.__dict__["claim_value_type"] = claim_value_type
        __props__.__dict__["client_id"] = client_id
        __props__.__dict__["client_scope_id"] = client_scope_id
        __props__.__dict__["name"] = name
        __props__.__dict__["realm_id"] = realm_id
        __props__.__dict__["session_note"] = session_note
        return UserSessionNoteProtocolMapper(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="addToAccessToken")
    def add_to_access_token(self) -> pulumi.Output[Optional[bool]]:
        """
        Indicates if the property should be added as a claim to the access token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_access_token")

    @property
    @pulumi.getter(name="addToIdToken")
    def add_to_id_token(self) -> pulumi.Output[Optional[bool]]:
        """
        Indicates if the property should be added as a claim to the id token. Defaults to `true`.
        """
        return pulumi.get(self, "add_to_id_token")

    @property
    @pulumi.getter(name="claimName")
    def claim_name(self) -> pulumi.Output[str]:
        """
        The name of the claim to insert into a token.
        """
        return pulumi.get(self, "claim_name")

    @property
    @pulumi.getter(name="claimValueType")
    def claim_value_type(self) -> pulumi.Output[Optional[str]]:
        """
        The claim type used when serializing JSON tokens. Can be one of `String`, `JSON`, `long`, `int`, or `boolean`. Defaults to `String`.
        """
        return pulumi.get(self, "claim_value_type")

    @property
    @pulumi.getter(name="clientId")
    def client_id(self) -> pulumi.Output[Optional[str]]:
        """
        The client this protocol mapper should be attached to. Conflicts with `client_scope_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_id")

    @property
    @pulumi.getter(name="clientScopeId")
    def client_scope_id(self) -> pulumi.Output[Optional[str]]:
        """
        The client scope this protocol mapper should be attached to. Conflicts with `client_id`. One of `client_id` or `client_scope_id` must be specified.
        """
        return pulumi.get(self, "client_scope_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The display name of this protocol mapper in the GUI.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="realmId")
    def realm_id(self) -> pulumi.Output[str]:
        """
        The realm this protocol mapper exists within.
        """
        return pulumi.get(self, "realm_id")

    @property
    @pulumi.getter(name="sessionNote")
    def session_note(self) -> pulumi.Output[Optional[str]]:
        """
        String value being the name of stored user session note within the UserSessionModel.note map.
        """
        return pulumi.get(self, "session_note")

