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

__all__ = ['ServiceEndpointPipelineArgs', 'ServiceEndpointPipeline']

@pulumi.input_type
class ServiceEndpointPipelineArgs:
    def __init__(__self__, *,
                 auth_personal: pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs'],
                 organization_name: pulumi.Input[str],
                 project_id: pulumi.Input[str],
                 service_endpoint_name: pulumi.Input[str],
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ServiceEndpointPipeline resource.
        :param pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs'] auth_personal: An `auth_personal` block as documented below. Allows connecting using a personal access token.
        :param pulumi.Input[str] organization_name: The organization name used for `Organization Url` and `Release API Url` fields.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        """
        pulumi.set(__self__, "auth_personal", auth_personal)
        pulumi.set(__self__, "organization_name", organization_name)
        pulumi.set(__self__, "project_id", project_id)
        pulumi.set(__self__, "service_endpoint_name", service_endpoint_name)
        if authorization is not None:
            pulumi.set(__self__, "authorization", authorization)
        if description is not None:
            pulumi.set(__self__, "description", description)

    @property
    @pulumi.getter(name="authPersonal")
    def auth_personal(self) -> pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs']:
        """
        An `auth_personal` block as documented below. Allows connecting using a personal access token.
        """
        return pulumi.get(self, "auth_personal")

    @auth_personal.setter
    def auth_personal(self, value: pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs']):
        pulumi.set(self, "auth_personal", value)

    @property
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> pulumi.Input[str]:
        """
        The organization name used for `Organization Url` and `Release API Url` fields.
        """
        return pulumi.get(self, "organization_name")

    @organization_name.setter
    def organization_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "organization_name", value)

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


@pulumi.input_type
class _ServiceEndpointPipelineState:
    def __init__(__self__, *,
                 auth_personal: Optional[pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs']] = None,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ServiceEndpointPipeline resources.
        :param pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs'] auth_personal: An `auth_personal` block as documented below. Allows connecting using a personal access token.
        :param pulumi.Input[str] organization_name: The organization name used for `Organization Url` and `Release API Url` fields.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        """
        if auth_personal is not None:
            pulumi.set(__self__, "auth_personal", auth_personal)
        if authorization is not None:
            pulumi.set(__self__, "authorization", authorization)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if organization_name is not None:
            pulumi.set(__self__, "organization_name", organization_name)
        if project_id is not None:
            pulumi.set(__self__, "project_id", project_id)
        if service_endpoint_name is not None:
            pulumi.set(__self__, "service_endpoint_name", service_endpoint_name)

    @property
    @pulumi.getter(name="authPersonal")
    def auth_personal(self) -> Optional[pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs']]:
        """
        An `auth_personal` block as documented below. Allows connecting using a personal access token.
        """
        return pulumi.get(self, "auth_personal")

    @auth_personal.setter
    def auth_personal(self, value: Optional[pulumi.Input['ServiceEndpointPipelineAuthPersonalArgs']]):
        pulumi.set(self, "auth_personal", value)

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
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> Optional[pulumi.Input[str]]:
        """
        The organization name used for `Organization Url` and `Release API Url` fields.
        """
        return pulumi.get(self, "organization_name")

    @organization_name.setter
    def organization_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organization_name", value)

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


class ServiceEndpointPipeline(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auth_personal: Optional[pulumi.Input[pulumi.InputType['ServiceEndpointPipelineAuthPersonalArgs']]] = None,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Azure DevOps Service Connection service endpoint within Azure DevOps. Allows to run downstream pipelines, monitoring their execution, collecting and consolidating artefacts produced in the delegate pipelines (yaml block `task: RunPipelines@1`). More details on Marketplace page: [RunPipelines](https://marketplace.visualstudio.com/items?itemName=CSE-DevOps.RunPipelines)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azuredevops as azuredevops

        project = azuredevops.Project("project",
            visibility="private",
            version_control="Git",
            work_item_template="Agile")
        serviceendpoint = azuredevops.ServiceEndpointPipeline("serviceendpoint",
            project_id=project.id,
            service_endpoint_name="Sample Pipeline Runner",
            organization_name="MyOrganization",
            auth_personal=azuredevops.ServiceEndpointPipelineAuthPersonalArgs(
                personal_access_token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            ),
            description="Managed by Terraform")
        ```
        ## Relevant Links

        - [Azure DevOps Service REST API 5.1 - Agent Pools](https://docs.microsoft.com/en-us/rest/api/azure/devops/serviceendpoint/endpoints?view=azure-devops-rest-5.1)

        ## Import

        Azure DevOps Service Endpoint can be imported using the `project id`, `service connection id`, e.g.

        ```sh
         $ pulumi import azuredevops:index/serviceEndpointPipeline:ServiceEndpointPipeline serviceendpoint projectID/00000000-0000-0000-0000-000000000000
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['ServiceEndpointPipelineAuthPersonalArgs']] auth_personal: An `auth_personal` block as documented below. Allows connecting using a personal access token.
        :param pulumi.Input[str] organization_name: The organization name used for `Organization Url` and `Release API Url` fields.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ServiceEndpointPipelineArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Azure DevOps Service Connection service endpoint within Azure DevOps. Allows to run downstream pipelines, monitoring their execution, collecting and consolidating artefacts produced in the delegate pipelines (yaml block `task: RunPipelines@1`). More details on Marketplace page: [RunPipelines](https://marketplace.visualstudio.com/items?itemName=CSE-DevOps.RunPipelines)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_azuredevops as azuredevops

        project = azuredevops.Project("project",
            visibility="private",
            version_control="Git",
            work_item_template="Agile")
        serviceendpoint = azuredevops.ServiceEndpointPipeline("serviceendpoint",
            project_id=project.id,
            service_endpoint_name="Sample Pipeline Runner",
            organization_name="MyOrganization",
            auth_personal=azuredevops.ServiceEndpointPipelineAuthPersonalArgs(
                personal_access_token="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            ),
            description="Managed by Terraform")
        ```
        ## Relevant Links

        - [Azure DevOps Service REST API 5.1 - Agent Pools](https://docs.microsoft.com/en-us/rest/api/azure/devops/serviceendpoint/endpoints?view=azure-devops-rest-5.1)

        ## Import

        Azure DevOps Service Endpoint can be imported using the `project id`, `service connection id`, e.g.

        ```sh
         $ pulumi import azuredevops:index/serviceEndpointPipeline:ServiceEndpointPipeline serviceendpoint projectID/00000000-0000-0000-0000-000000000000
        ```

        :param str resource_name: The name of the resource.
        :param ServiceEndpointPipelineArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ServiceEndpointPipelineArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auth_personal: Optional[pulumi.Input[pulumi.InputType['ServiceEndpointPipelineAuthPersonalArgs']]] = None,
                 authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 project_id: Optional[pulumi.Input[str]] = None,
                 service_endpoint_name: Optional[pulumi.Input[str]] = None,
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
            __props__ = ServiceEndpointPipelineArgs.__new__(ServiceEndpointPipelineArgs)

            if auth_personal is None and not opts.urn:
                raise TypeError("Missing required property 'auth_personal'")
            __props__.__dict__["auth_personal"] = auth_personal
            __props__.__dict__["authorization"] = authorization
            __props__.__dict__["description"] = description
            if organization_name is None and not opts.urn:
                raise TypeError("Missing required property 'organization_name'")
            __props__.__dict__["organization_name"] = organization_name
            if project_id is None and not opts.urn:
                raise TypeError("Missing required property 'project_id'")
            __props__.__dict__["project_id"] = project_id
            if service_endpoint_name is None and not opts.urn:
                raise TypeError("Missing required property 'service_endpoint_name'")
            __props__.__dict__["service_endpoint_name"] = service_endpoint_name
        super(ServiceEndpointPipeline, __self__).__init__(
            'azuredevops:index/serviceEndpointPipeline:ServiceEndpointPipeline',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            auth_personal: Optional[pulumi.Input[pulumi.InputType['ServiceEndpointPipelineAuthPersonalArgs']]] = None,
            authorization: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            description: Optional[pulumi.Input[str]] = None,
            organization_name: Optional[pulumi.Input[str]] = None,
            project_id: Optional[pulumi.Input[str]] = None,
            service_endpoint_name: Optional[pulumi.Input[str]] = None) -> 'ServiceEndpointPipeline':
        """
        Get an existing ServiceEndpointPipeline resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['ServiceEndpointPipelineAuthPersonalArgs']] auth_personal: An `auth_personal` block as documented below. Allows connecting using a personal access token.
        :param pulumi.Input[str] organization_name: The organization name used for `Organization Url` and `Release API Url` fields.
        :param pulumi.Input[str] project_id: The project ID or project name.
        :param pulumi.Input[str] service_endpoint_name: The Service Endpoint name.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ServiceEndpointPipelineState.__new__(_ServiceEndpointPipelineState)

        __props__.__dict__["auth_personal"] = auth_personal
        __props__.__dict__["authorization"] = authorization
        __props__.__dict__["description"] = description
        __props__.__dict__["organization_name"] = organization_name
        __props__.__dict__["project_id"] = project_id
        __props__.__dict__["service_endpoint_name"] = service_endpoint_name
        return ServiceEndpointPipeline(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="authPersonal")
    def auth_personal(self) -> pulumi.Output['outputs.ServiceEndpointPipelineAuthPersonal']:
        """
        An `auth_personal` block as documented below. Allows connecting using a personal access token.
        """
        return pulumi.get(self, "auth_personal")

    @property
    @pulumi.getter
    def authorization(self) -> pulumi.Output[Mapping[str, str]]:
        return pulumi.get(self, "authorization")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> pulumi.Output[str]:
        """
        The organization name used for `Organization Url` and `Release API Url` fields.
        """
        return pulumi.get(self, "organization_name")

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

