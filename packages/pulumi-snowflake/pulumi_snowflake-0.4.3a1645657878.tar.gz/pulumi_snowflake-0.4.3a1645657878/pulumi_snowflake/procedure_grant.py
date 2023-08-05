# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs
from ._inputs import *

__all__ = ['ProcedureGrantArgs', 'ProcedureGrant']

@pulumi.input_type
class ProcedureGrantArgs:
    def __init__(__self__, *,
                 database_name: pulumi.Input[str],
                 schema_name: pulumi.Input[str],
                 arguments: Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]] = None,
                 on_future: Optional[pulumi.Input[bool]] = None,
                 privilege: Optional[pulumi.Input[str]] = None,
                 procedure_name: Optional[pulumi.Input[str]] = None,
                 return_type: Optional[pulumi.Input[str]] = None,
                 roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 shares: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 with_grant_option: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a ProcedureGrant resource.
        :param pulumi.Input[str] database_name: The name of the database containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[str] schema_name: The name of the schema containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]] arguments: List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        :param pulumi.Input[bool] on_future: When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        :param pulumi.Input[str] privilege: The privilege to grant on the current or future procedure.
        :param pulumi.Input[str] procedure_name: The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        :param pulumi.Input[str] return_type: The return type of the procedure (must be present if procedure_name is present)
        :param pulumi.Input[Sequence[pulumi.Input[str]]] roles: Grants privilege to these roles.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] shares: Grants privilege to these shares (only valid if on_future is false).
        :param pulumi.Input[bool] with_grant_option: When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        pulumi.set(__self__, "database_name", database_name)
        pulumi.set(__self__, "schema_name", schema_name)
        if arguments is not None:
            pulumi.set(__self__, "arguments", arguments)
        if on_future is not None:
            pulumi.set(__self__, "on_future", on_future)
        if privilege is not None:
            pulumi.set(__self__, "privilege", privilege)
        if procedure_name is not None:
            pulumi.set(__self__, "procedure_name", procedure_name)
        if return_type is not None:
            pulumi.set(__self__, "return_type", return_type)
        if roles is not None:
            pulumi.set(__self__, "roles", roles)
        if shares is not None:
            pulumi.set(__self__, "shares", shares)
        if with_grant_option is not None:
            pulumi.set(__self__, "with_grant_option", with_grant_option)

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> pulumi.Input[str]:
        """
        The name of the database containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "database_name")

    @database_name.setter
    def database_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "database_name", value)

    @property
    @pulumi.getter(name="schemaName")
    def schema_name(self) -> pulumi.Input[str]:
        """
        The name of the schema containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "schema_name")

    @schema_name.setter
    def schema_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "schema_name", value)

    @property
    @pulumi.getter
    def arguments(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]]:
        """
        List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        """
        return pulumi.get(self, "arguments")

    @arguments.setter
    def arguments(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]]):
        pulumi.set(self, "arguments", value)

    @property
    @pulumi.getter(name="onFuture")
    def on_future(self) -> Optional[pulumi.Input[bool]]:
        """
        When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        """
        return pulumi.get(self, "on_future")

    @on_future.setter
    def on_future(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "on_future", value)

    @property
    @pulumi.getter
    def privilege(self) -> Optional[pulumi.Input[str]]:
        """
        The privilege to grant on the current or future procedure.
        """
        return pulumi.get(self, "privilege")

    @privilege.setter
    def privilege(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "privilege", value)

    @property
    @pulumi.getter(name="procedureName")
    def procedure_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        """
        return pulumi.get(self, "procedure_name")

    @procedure_name.setter
    def procedure_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "procedure_name", value)

    @property
    @pulumi.getter(name="returnType")
    def return_type(self) -> Optional[pulumi.Input[str]]:
        """
        The return type of the procedure (must be present if procedure_name is present)
        """
        return pulumi.get(self, "return_type")

    @return_type.setter
    def return_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "return_type", value)

    @property
    @pulumi.getter
    def roles(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Grants privilege to these roles.
        """
        return pulumi.get(self, "roles")

    @roles.setter
    def roles(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "roles", value)

    @property
    @pulumi.getter
    def shares(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Grants privilege to these shares (only valid if on_future is false).
        """
        return pulumi.get(self, "shares")

    @shares.setter
    def shares(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "shares", value)

    @property
    @pulumi.getter(name="withGrantOption")
    def with_grant_option(self) -> Optional[pulumi.Input[bool]]:
        """
        When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        return pulumi.get(self, "with_grant_option")

    @with_grant_option.setter
    def with_grant_option(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "with_grant_option", value)


@pulumi.input_type
class _ProcedureGrantState:
    def __init__(__self__, *,
                 arguments: Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 on_future: Optional[pulumi.Input[bool]] = None,
                 privilege: Optional[pulumi.Input[str]] = None,
                 procedure_name: Optional[pulumi.Input[str]] = None,
                 return_type: Optional[pulumi.Input[str]] = None,
                 roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schema_name: Optional[pulumi.Input[str]] = None,
                 shares: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 with_grant_option: Optional[pulumi.Input[bool]] = None):
        """
        Input properties used for looking up and filtering ProcedureGrant resources.
        :param pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]] arguments: List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        :param pulumi.Input[str] database_name: The name of the database containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[bool] on_future: When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        :param pulumi.Input[str] privilege: The privilege to grant on the current or future procedure.
        :param pulumi.Input[str] procedure_name: The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        :param pulumi.Input[str] return_type: The return type of the procedure (must be present if procedure_name is present)
        :param pulumi.Input[Sequence[pulumi.Input[str]]] roles: Grants privilege to these roles.
        :param pulumi.Input[str] schema_name: The name of the schema containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] shares: Grants privilege to these shares (only valid if on_future is false).
        :param pulumi.Input[bool] with_grant_option: When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        if arguments is not None:
            pulumi.set(__self__, "arguments", arguments)
        if database_name is not None:
            pulumi.set(__self__, "database_name", database_name)
        if on_future is not None:
            pulumi.set(__self__, "on_future", on_future)
        if privilege is not None:
            pulumi.set(__self__, "privilege", privilege)
        if procedure_name is not None:
            pulumi.set(__self__, "procedure_name", procedure_name)
        if return_type is not None:
            pulumi.set(__self__, "return_type", return_type)
        if roles is not None:
            pulumi.set(__self__, "roles", roles)
        if schema_name is not None:
            pulumi.set(__self__, "schema_name", schema_name)
        if shares is not None:
            pulumi.set(__self__, "shares", shares)
        if with_grant_option is not None:
            pulumi.set(__self__, "with_grant_option", with_grant_option)

    @property
    @pulumi.getter
    def arguments(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]]:
        """
        List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        """
        return pulumi.get(self, "arguments")

    @arguments.setter
    def arguments(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ProcedureGrantArgumentArgs']]]]):
        pulumi.set(self, "arguments", value)

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the database containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "database_name")

    @database_name.setter
    def database_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "database_name", value)

    @property
    @pulumi.getter(name="onFuture")
    def on_future(self) -> Optional[pulumi.Input[bool]]:
        """
        When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        """
        return pulumi.get(self, "on_future")

    @on_future.setter
    def on_future(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "on_future", value)

    @property
    @pulumi.getter
    def privilege(self) -> Optional[pulumi.Input[str]]:
        """
        The privilege to grant on the current or future procedure.
        """
        return pulumi.get(self, "privilege")

    @privilege.setter
    def privilege(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "privilege", value)

    @property
    @pulumi.getter(name="procedureName")
    def procedure_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        """
        return pulumi.get(self, "procedure_name")

    @procedure_name.setter
    def procedure_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "procedure_name", value)

    @property
    @pulumi.getter(name="returnType")
    def return_type(self) -> Optional[pulumi.Input[str]]:
        """
        The return type of the procedure (must be present if procedure_name is present)
        """
        return pulumi.get(self, "return_type")

    @return_type.setter
    def return_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "return_type", value)

    @property
    @pulumi.getter
    def roles(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Grants privilege to these roles.
        """
        return pulumi.get(self, "roles")

    @roles.setter
    def roles(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "roles", value)

    @property
    @pulumi.getter(name="schemaName")
    def schema_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the schema containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "schema_name")

    @schema_name.setter
    def schema_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "schema_name", value)

    @property
    @pulumi.getter
    def shares(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Grants privilege to these shares (only valid if on_future is false).
        """
        return pulumi.get(self, "shares")

    @shares.setter
    def shares(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "shares", value)

    @property
    @pulumi.getter(name="withGrantOption")
    def with_grant_option(self) -> Optional[pulumi.Input[bool]]:
        """
        When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        return pulumi.get(self, "with_grant_option")

    @with_grant_option.setter
    def with_grant_option(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "with_grant_option", value)


class ProcedureGrant(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 arguments: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ProcedureGrantArgumentArgs']]]]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 on_future: Optional[pulumi.Input[bool]] = None,
                 privilege: Optional[pulumi.Input[str]] = None,
                 procedure_name: Optional[pulumi.Input[str]] = None,
                 return_type: Optional[pulumi.Input[str]] = None,
                 roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schema_name: Optional[pulumi.Input[str]] = None,
                 shares: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 with_grant_option: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        ## Example Usage

        ```python
        import pulumi
        import pulumi_snowflake as snowflake

        grant = snowflake.ProcedureGrant("grant",
            database_name="db",
            schema_name="schema",
            procedure_name="procedure",
            arguments=[
                snowflake.ProcedureGrantArgumentArgs(
                    %!v(PANIC=Format method: interface conversion: model.Expression is *model.TemplateExpression, not *model.LiteralValueExpression),
                    snowflake.ProcedureGrantArgumentArgs(
                        %!v(PANIC=Format method: interface conversion: model.Expression is *model.TemplateExpression, not *model.LiteralValueExpression),
                    ],
                    return_type="string",
                    privilege="select",
                    roles=[
                        "role1",
                        "role2",
                    ],
                    shares=[
                        "share1",
                        "share2",
                    ],
                    on_future=False,
                    with_grant_option=False)
        ```

        ## Import

        # format is database name | schema name | procedure signature | privilege | true/false for with_grant_option

        ```sh
         $ pulumi import snowflake:index/procedureGrant:ProcedureGrant example 'dbName|schemaName|procedureName(ARG1 ARG1TYPE, ARG2 ARG2TYPE):RETURNTYPE|USAGE|false'
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ProcedureGrantArgumentArgs']]]] arguments: List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        :param pulumi.Input[str] database_name: The name of the database containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[bool] on_future: When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        :param pulumi.Input[str] privilege: The privilege to grant on the current or future procedure.
        :param pulumi.Input[str] procedure_name: The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        :param pulumi.Input[str] return_type: The return type of the procedure (must be present if procedure_name is present)
        :param pulumi.Input[Sequence[pulumi.Input[str]]] roles: Grants privilege to these roles.
        :param pulumi.Input[str] schema_name: The name of the schema containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] shares: Grants privilege to these shares (only valid if on_future is false).
        :param pulumi.Input[bool] with_grant_option: When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProcedureGrantArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        ## Example Usage

        ```python
        import pulumi
        import pulumi_snowflake as snowflake

        grant = snowflake.ProcedureGrant("grant",
            database_name="db",
            schema_name="schema",
            procedure_name="procedure",
            arguments=[
                snowflake.ProcedureGrantArgumentArgs(
                    %!v(PANIC=Format method: interface conversion: model.Expression is *model.TemplateExpression, not *model.LiteralValueExpression),
                    snowflake.ProcedureGrantArgumentArgs(
                        %!v(PANIC=Format method: interface conversion: model.Expression is *model.TemplateExpression, not *model.LiteralValueExpression),
                    ],
                    return_type="string",
                    privilege="select",
                    roles=[
                        "role1",
                        "role2",
                    ],
                    shares=[
                        "share1",
                        "share2",
                    ],
                    on_future=False,
                    with_grant_option=False)
        ```

        ## Import

        # format is database name | schema name | procedure signature | privilege | true/false for with_grant_option

        ```sh
         $ pulumi import snowflake:index/procedureGrant:ProcedureGrant example 'dbName|schemaName|procedureName(ARG1 ARG1TYPE, ARG2 ARG2TYPE):RETURNTYPE|USAGE|false'
        ```

        :param str resource_name: The name of the resource.
        :param ProcedureGrantArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProcedureGrantArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 arguments: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ProcedureGrantArgumentArgs']]]]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 on_future: Optional[pulumi.Input[bool]] = None,
                 privilege: Optional[pulumi.Input[str]] = None,
                 procedure_name: Optional[pulumi.Input[str]] = None,
                 return_type: Optional[pulumi.Input[str]] = None,
                 roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 schema_name: Optional[pulumi.Input[str]] = None,
                 shares: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 with_grant_option: Optional[pulumi.Input[bool]] = None,
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
            __props__ = ProcedureGrantArgs.__new__(ProcedureGrantArgs)

            __props__.__dict__["arguments"] = arguments
            if database_name is None and not opts.urn:
                raise TypeError("Missing required property 'database_name'")
            __props__.__dict__["database_name"] = database_name
            __props__.__dict__["on_future"] = on_future
            __props__.__dict__["privilege"] = privilege
            __props__.__dict__["procedure_name"] = procedure_name
            __props__.__dict__["return_type"] = return_type
            __props__.__dict__["roles"] = roles
            if schema_name is None and not opts.urn:
                raise TypeError("Missing required property 'schema_name'")
            __props__.__dict__["schema_name"] = schema_name
            __props__.__dict__["shares"] = shares
            __props__.__dict__["with_grant_option"] = with_grant_option
        super(ProcedureGrant, __self__).__init__(
            'snowflake:index/procedureGrant:ProcedureGrant',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arguments: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ProcedureGrantArgumentArgs']]]]] = None,
            database_name: Optional[pulumi.Input[str]] = None,
            on_future: Optional[pulumi.Input[bool]] = None,
            privilege: Optional[pulumi.Input[str]] = None,
            procedure_name: Optional[pulumi.Input[str]] = None,
            return_type: Optional[pulumi.Input[str]] = None,
            roles: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            schema_name: Optional[pulumi.Input[str]] = None,
            shares: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            with_grant_option: Optional[pulumi.Input[bool]] = None) -> 'ProcedureGrant':
        """
        Get an existing ProcedureGrant resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ProcedureGrantArgumentArgs']]]] arguments: List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        :param pulumi.Input[str] database_name: The name of the database containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[bool] on_future: When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        :param pulumi.Input[str] privilege: The privilege to grant on the current or future procedure.
        :param pulumi.Input[str] procedure_name: The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        :param pulumi.Input[str] return_type: The return type of the procedure (must be present if procedure_name is present)
        :param pulumi.Input[Sequence[pulumi.Input[str]]] roles: Grants privilege to these roles.
        :param pulumi.Input[str] schema_name: The name of the schema containing the current or future procedures on which to grant privileges.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] shares: Grants privilege to these shares (only valid if on_future is false).
        :param pulumi.Input[bool] with_grant_option: When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ProcedureGrantState.__new__(_ProcedureGrantState)

        __props__.__dict__["arguments"] = arguments
        __props__.__dict__["database_name"] = database_name
        __props__.__dict__["on_future"] = on_future
        __props__.__dict__["privilege"] = privilege
        __props__.__dict__["procedure_name"] = procedure_name
        __props__.__dict__["return_type"] = return_type
        __props__.__dict__["roles"] = roles
        __props__.__dict__["schema_name"] = schema_name
        __props__.__dict__["shares"] = shares
        __props__.__dict__["with_grant_option"] = with_grant_option
        return ProcedureGrant(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arguments(self) -> pulumi.Output[Optional[Sequence['outputs.ProcedureGrantArgument']]]:
        """
        List of the arguments for the procedure (must be present if procedure has arguments and procedure_name is present)
        """
        return pulumi.get(self, "arguments")

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> pulumi.Output[str]:
        """
        The name of the database containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "database_name")

    @property
    @pulumi.getter(name="onFuture")
    def on_future(self) -> pulumi.Output[Optional[bool]]:
        """
        When this is set to true and a schema*name is provided, apply this grant on all future procedures in the given schema. When this is true and no schema*name is provided apply this grant on all future procedures in the given database. The procedure*name and shares fields must be unset in order to use on*future.
        """
        return pulumi.get(self, "on_future")

    @property
    @pulumi.getter
    def privilege(self) -> pulumi.Output[Optional[str]]:
        """
        The privilege to grant on the current or future procedure.
        """
        return pulumi.get(self, "privilege")

    @property
    @pulumi.getter(name="procedureName")
    def procedure_name(self) -> pulumi.Output[Optional[str]]:
        """
        The name of the procedure on which to grant privileges immediately (only valid if on_future is false).
        """
        return pulumi.get(self, "procedure_name")

    @property
    @pulumi.getter(name="returnType")
    def return_type(self) -> pulumi.Output[Optional[str]]:
        """
        The return type of the procedure (must be present if procedure_name is present)
        """
        return pulumi.get(self, "return_type")

    @property
    @pulumi.getter
    def roles(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Grants privilege to these roles.
        """
        return pulumi.get(self, "roles")

    @property
    @pulumi.getter(name="schemaName")
    def schema_name(self) -> pulumi.Output[str]:
        """
        The name of the schema containing the current or future procedures on which to grant privileges.
        """
        return pulumi.get(self, "schema_name")

    @property
    @pulumi.getter
    def shares(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        Grants privilege to these shares (only valid if on_future is false).
        """
        return pulumi.get(self, "shares")

    @property
    @pulumi.getter(name="withGrantOption")
    def with_grant_option(self) -> pulumi.Output[Optional[bool]]:
        """
        When this is set to true, allows the recipient role to grant the privileges to other roles.
        """
        return pulumi.get(self, "with_grant_option")

