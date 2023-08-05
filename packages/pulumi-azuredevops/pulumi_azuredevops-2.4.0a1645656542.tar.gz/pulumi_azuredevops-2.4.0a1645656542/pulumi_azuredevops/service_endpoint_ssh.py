# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['ServiceEndpointSshArgs', 'ServiceEndpointSsh']

@pulumi.input_type
class ServiceEndpointSshArgs:
    def __init__(__self__, *,
                 host: pulumi.Input[str],
                 project_id: pulumi.Input[str],
                 service_endpoint_name: pulumi.Input[str],
                 username: pulumi.Input[str],
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 private_key: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ServiceEndpointSsh resource.
        :param pulumi.Input[str] host: The Host name or IP address of the remote machine.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        :param pulumi.Input[str] username: Username for connecting to the endpoint.
        :param pulumi.Input[str] password: Password for connecting to the endpoint.
        :param pulumi.Input[int] port: Port number on the remote machine to use for connecting. Defaults to `22`.
        :param pulumi.Input[str] private_key: Private Key for connecting to the endpoint.
        """
        pulumi.set(__self__, "host", host)
        pulumi.set(__self__, "project_id", project_id)
        pulumi.set(__self__, "service_endpoint_name", service_endpoint_name)
        pulumi.set(__self__, "username", username)
        if authorization is not None:
            pulumi.set(__self__, "authorization", authorization)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if password is not None:
            pulumi.set(__self__, "password", password)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)

    @property
    @pulumi.getter
    def host(self) -> pulumi.Input[str]:
        """
        The Host name or IP address of the remote machine.
        """
        return pulumi.get(self, "host")

    @host.setter
    def host(self, value: pulumi.Input[str]):
        pulumi.set(self, "host", value)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Input[str]:
        """
        The project ID or project name.
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter(name="serviceEndpointName")
    def service_endpoint_name(self) -> pulumi.Input[str]:
        """
        The Service Endpoint name.
        """
        return pulumi.get(self, "service_endpoint_name")

    @service_endpoint_name.setter
    def service_endpoint_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "service_endpoint_name", value)

    @property
    @pulumi.getter
    def username(self) -> pulumi.Input[str]:
        """
        Username for connecting to the endpoint.
        """
        return pulumi.get(self, "username")

    @username.setter
    def username(self, value: pulumi.Input[str]):
        pulumi.set(self, "username", value)

    @property
    @pulumi.getter
    def authorization(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        return pulumi.get(self, "authorization")

    @authorization.setter
    def authorization(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "authorization", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def password(self) -> Optional[pulumi.Input[str]]:
        """
        Password for connecting to the endpoint.
        """
        return pulumi.get(self, "password")

    @password.setter
    def password(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        """
        Port number on the remote machine to use for connecting. Defaults to `22`.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        Private Key for connecting to the endpoint.
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)


@pulumi.input_type
class _ServiceEndpointSshState:
    def __init__(__self__, *,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 host: Optional[pulumi.Input[str]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 password_hash: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 private_key_hash: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None,
                 username: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ServiceEndpointSsh resources.
        :param pulumi.Input[str] host: The Host name or IP address of the remote machine.
        :param pulumi.Input[str] password: Password for connecting to the endpoint.
        :param pulumi.Input[str] password_hash: A bcrypted hash of the attribute 'password'
        :param pulumi.Input[int] port: Port number on the remote machine to use for connecting. Defaults to `22`.
        :param pulumi.Input[str] private_key: Private Key for connecting to the endpoint.
        :param pulumi.Input[str] private_key_hash: A bcrypted hash of the attribute 'private_key'
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        :param pulumi.Input[str] username: Username for connecting to the endpoint.
        """
        if authorization is not None:
            pulumi.set(__self__, "authorization", authorization)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if host is not None:
            pulumi.set(__self__, "host", host)
        if password is not None:
            pulumi.set(__self__, "password", password)
        if password_hash is not None:
            pulumi.set(__self__, "password_hash", password_hash)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if private_key is not None:
            pulumi.set(__self__, "private_key", private_key)
        if private_key_hash is not None:
            pulumi.set(__self__, "private_key_hash", private_key_hash)
        if project_id is not None:
            pulumi.set(__self__, "project_id", project_id)
        if service_endpoint_name is not None:
            pulumi.set(__self__, "service_endpoint_name", service_endpoint_name)
        if username is not None:
            pulumi.set(__self__, "username", username)

    @property
    @pulumi.getter
    def authorization(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        return pulumi.get(self, "authorization")

    @authorization.setter
    def authorization(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "authorization", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def host(self) -> Optional[pulumi.Input[str]]:
        """
        The Host name or IP address of the remote machine.
        """
        return pulumi.get(self, "host")

    @host.setter
    def host(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "host", value)

    @property
    @pulumi.getter
    def password(self) -> Optional[pulumi.Input[str]]:
        """
        Password for connecting to the endpoint.
        """
        return pulumi.get(self, "password")

    @password.setter
    def password(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password", value)

    @property
    @pulumi.getter(name="passwordHash")
    def password_hash(self) -> Optional[pulumi.Input[str]]:
        """
        A bcrypted hash of the attribute 'password'
        """
        return pulumi.get(self, "password_hash")

    @password_hash.setter
    def password_hash(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "password_hash", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        """
        Port number on the remote machine to use for connecting. Defaults to `22`.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> Optional[pulumi.Input[str]]:
        """
        Private Key for connecting to the endpoint.
        """
        return pulumi.get(self, "private_key")

    @private_key.setter
    def private_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key", value)

    @property
    @pulumi.getter(name="privateKeyHash")
    def private_key_hash(self) -> Optional[pulumi.Input[str]]:
        """
        A bcrypted hash of the attribute 'private_key'
        """
        return pulumi.get(self, "private_key_hash")

    @private_key_hash.setter
    def private_key_hash(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "private_key_hash", value)

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> Optional[pulumi.Input[str]]:
        """
        The project ID or project name.
        """
        return pulumi.get(self, "project_id")

    @project_id.setter
    def project_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "project_id", value)

    @property
    @pulumi.getter(name="serviceEndpointName")
    def service_endpoint_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Service Endpoint name.
        """
        return pulumi.get(self, "service_endpoint_name")

    @service_endpoint_name.setter
    def service_endpoint_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "service_endpoint_name", value)

    @property
    @pulumi.getter
    def username(self) -> Optional[pulumi.Input[str]]:
        """
        Username for connecting to the endpoint.
        """
        return pulumi.get(self, "username")

    @username.setter
    def username(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "username", value)


class ServiceEndpointSsh(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 host: Optional[pulumi.Input[str]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None,
                 username: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a SSH service endpoint within Azure DevOps.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azuredevops as azuredevops

        project = azuredevops.Project("project",
            visibility="private",
            version_control="Git",
            work_item_template="Agile")
        test = azuredevops.ServiceEndpointSsh("test",
            project_id=project.id,
            service_endpoint_name="Sample SSH",
            host="1.2.3.4",
            username="username",
            description="Managed by Terraform")
        ```
        ## Relevant Links

        - [Azure DevOps Service REST API 5.1 - Service Endpoints](https://docs.microsoft.com/en-us/rest/api/azure/devops/serviceendpoint/endpoints?view=azure-devops-rest-5.1)

        ## Import

        Azure DevOps Service Endpoint SSH can be imported using **projectID/serviceEndpointID** or ** projectName/serviceEndpointID**

        ```sh
         $ pulumi import azuredevops:index/serviceEndpointSsh:ServiceEndpointSsh serviceendpoint 00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] host: The Host name or IP address of the remote machine.
        :param pulumi.Input[str] password: Password for connecting to the endpoint.
        :param pulumi.Input[int] port: Port number on the remote machine to use for connecting. Defaults to `22`.
        :param pulumi.Input[str] private_key: Private Key for connecting to the endpoint.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        :param pulumi.Input[str] username: Username for connecting to the endpoint.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ServiceEndpointSshArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a SSH service endpoint within Azure DevOps.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azuredevops as azuredevops

        project = azuredevops.Project("project",
            visibility="private",
            version_control="Git",
            work_item_template="Agile")
        test = azuredevops.ServiceEndpointSsh("test",
            project_id=project.id,
            service_endpoint_name="Sample SSH",
            host="1.2.3.4",
            username="username",
            description="Managed by Terraform")
        ```
        ## Relevant Links

        - [Azure DevOps Service REST API 5.1 - Service Endpoints](https://docs.microsoft.com/en-us/rest/api/azure/devops/serviceendpoint/endpoints?view=azure-devops-rest-5.1)

        ## Import

        Azure DevOps Service Endpoint SSH can be imported using **projectID/serviceEndpointID** or ** projectName/serviceEndpointID**

        ```sh
         $ pulumi import azuredevops:index/serviceEndpointSsh:ServiceEndpointSsh serviceendpoint 00000000-0000-0000-0000-000000000000/00000000-0000-0000-0000-000000000000
        ```

        :param str resource_name: The name of the resource.
        :param ServiceEndpointSshArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ServiceEndpointSshArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 host: Optional[pulumi.Input[str]] = None,
                 password: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 private_key: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None,
                 username: Optional[pulumi.Input[str]] = None,
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
            __props__ = ServiceEndpointSshArgs.__new__(ServiceEndpointSshArgs)

            __props__.__dict__["authorization"] = authorization
            __props__.__dict__["description"] = description
            if host is None and not opts.urn:
                raise TypeError("Missing required property 'host'")
            __props__.__dict__["host"] = host
            __props__.__dict__["password"] = password
            __props__.__dict__["port"] = port
            __props__.__dict__["private_key"] = private_key
            if project_id is None and not opts.urn:
                raise TypeError("Missing required property 'project_id'")
            __props__.__dict__["project_id"] = project_id
            if service_endpoint_name is None and not opts.urn:
                raise TypeError("Missing required property 'service_endpoint_name'")
            __props__.__dict__["service_endpoint_name"] = service_endpoint_name
            if username is None and not opts.urn:
                raise TypeError("Missing required property 'username'")
            __props__.__dict__["username"] = username
            __props__.__dict__["password_hash"] = None
            __props__.__dict__["private_key_hash"] = None
        super(ServiceEndpointSsh, __self__).__init__(
            'azuredevops:index/serviceEndpointSsh:ServiceEndpointSsh',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            description: Optional[pulumi.Input[str]] = None,
            host: Optional[pulumi.Input[str]] = None,
            password: Optional[pulumi.Input[str]] = None,
            password_hash: Optional[pulumi.Input[str]] = None,
            port: Optional[pulumi.Input[int]] = None,
            private_key: Optional[pulumi.Input[str]] = None,
            private_key_hash: Optional[pulumi.Input[str]] = None,
            project_id: Optional[pulumi.Input[str]] = None,
            service_endpoint_name: Optional[pulumi.Input[str]] = None,
            username: Optional[pulumi.Input[str]] = None) -> 'ServiceEndpointSsh':
        """
        Get an existing ServiceEndpointSsh resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] host: The Host name or IP address of the remote machine.
        :param pulumi.Input[str] password: Password for connecting to the endpoint.
        :param pulumi.Input[str] password_hash: A bcrypted hash of the attribute 'password'
        :param pulumi.Input[int] port: Port number on the remote machine to use for connecting. Defaults to `22`.
        :param pulumi.Input[str] private_key: Private Key for connecting to the endpoint.
        :param pulumi.Input[str] private_key_hash: A bcrypted hash of the attribute 'private_key'
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        :param pulumi.Input[str] username: Username for connecting to the endpoint.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ServiceEndpointSshState.__new__(_ServiceEndpointSshState)

        __props__.__dict__["authorization"] = authorization
        __props__.__dict__["description"] = description
        __props__.__dict__["host"] = host
        __props__.__dict__["password"] = password
        __props__.__dict__["password_hash"] = password_hash
        __props__.__dict__["port"] = port
        __props__.__dict__["private_key"] = private_key
        __props__.__dict__["private_key_hash"] = private_key_hash
        __props__.__dict__["project_id"] = project_id
        __props__.__dict__["service_endpoint_name"] = service_endpoint_name
        __props__.__dict__["username"] = username
        return ServiceEndpointSsh(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def authorization(self) -> pulumi.Output[Mapping[str, str]]:
        return pulumi.get(self, "authorization")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def host(self) -> pulumi.Output[str]:
        """
        The Host name or IP address of the remote machine.
        """
        return pulumi.get(self, "host")

    @property
    @pulumi.getter
    def password(self) -> pulumi.Output[Optional[str]]:
        """
        Password for connecting to the endpoint.
        """
        return pulumi.get(self, "password")

    @property
    @pulumi.getter(name="passwordHash")
    def password_hash(self) -> pulumi.Output[str]:
        """
        A bcrypted hash of the attribute 'password'
        """
        return pulumi.get(self, "password_hash")

    @property
    @pulumi.getter
    def port(self) -> pulumi.Output[Optional[int]]:
        """
        Port number on the remote machine to use for connecting. Defaults to `22`.
        """
        return pulumi.get(self, "port")

    @property
    @pulumi.getter(name="privateKey")
    def private_key(self) -> pulumi.Output[Optional[str]]:
        """
        Private Key for connecting to the endpoint.
        """
        return pulumi.get(self, "private_key")

    @property
    @pulumi.getter(name="privateKeyHash")
    def private_key_hash(self) -> pulumi.Output[str]:
        """
        A bcrypted hash of the attribute 'private_key'
        """
        return pulumi.get(self, "private_key_hash")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> pulumi.Output[str]:
        """
        The project ID or project name.
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter(name="serviceEndpointName")
    def service_endpoint_name(self) -> pulumi.Output[str]:
        """
        The Service Endpoint name.
        """
        return pulumi.get(self, "service_endpoint_name")

    @property
    @pulumi.getter
    def username(self) -> pulumi.Output[str]:
        """
        Username for connecting to the endpoint.
        """
        return pulumi.get(self, "username")

