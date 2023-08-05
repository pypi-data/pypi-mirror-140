# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GitInitialization',
    'GetRepositoriesRepositoryResult',
]

@pulumi.output_type
class GitInitialization(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "initType":
            suggest = "init_type"
        elif key == "serviceConnectionId":
            suggest = "service_connection_id"
        elif key == "sourceType":
            suggest = "source_type"
        elif key == "sourceUrl":
            suggest = "source_url"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in GitInitialization. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        GitInitialization.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        GitInitialization.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 init_type: str,
                 service_connection_id: Optional[str] = None,
                 source_type: Optional[str] = None,
                 source_url: Optional[str] = None):
        """
        :param str init_type: The type of repository to create. Valid values: `Uninitialized`, `Clean` or `Import`.
        :param str service_connection_id: The id of service connection used to authenticate to a private repository for import initialization.
        :param str source_type: Type of the source repository. Used if the `init_type` is `Import`. Valid values: `Git`.
        :param str source_url: The URL of the source repository. Used if the `init_type` is `Import`.
        """
        pulumi.set(__self__, "init_type", init_type)
        if service_connection_id is not None:
            pulumi.set(__self__, "service_connection_id", service_connection_id)
        if source_type is not None:
            pulumi.set(__self__, "source_type", source_type)
        if source_url is not None:
            pulumi.set(__self__, "source_url", source_url)

    @property
    @pulumi.getter(name="initType")
    def init_type(self) -> str:
        """
        The type of repository to create. Valid values: `Uninitialized`, `Clean` or `Import`.
        """
        return pulumi.get(self, "init_type")

    @property
    @pulumi.getter(name="serviceConnectionId")
    def service_connection_id(self) -> Optional[str]:
        """
        The id of service connection used to authenticate to a private repository for import initialization.
        """
        return pulumi.get(self, "service_connection_id")

    @property
    @pulumi.getter(name="sourceType")
    def source_type(self) -> Optional[str]:
        """
        Type of the source repository. Used if the `init_type` is `Import`. Valid values: `Git`.
        """
        return pulumi.get(self, "source_type")

    @property
    @pulumi.getter(name="sourceUrl")
    def source_url(self) -> Optional[str]:
        """
        The URL of the source repository. Used if the `init_type` is `Import`.
        """
        return pulumi.get(self, "source_url")


@pulumi.output_type
class GetRepositoriesRepositoryResult(dict):
    def __init__(__self__, *,
                 default_branch: str,
                 id: str,
                 name: str,
                 project_id: str,
                 remote_url: str,
                 size: int,
                 ssh_url: str,
                 url: str,
                 web_url: str):
        """
        :param str default_branch: The ref of the default branch.
        :param str id: Git repository identifier.
        :param str name: Name of the Git repository to retrieve; requires `project_id` to be specified as well
        :param str project_id: ID of project to list Git repositories
        :param str remote_url: HTTPS Url to clone the Git repository
        :param int size: Compressed size (bytes) of the repository.
        :param str ssh_url: SSH Url to clone the Git repository
        :param str url: Details REST API endpoint for the Git Repository.
        :param str web_url: Url of the Git repository web view
        """
        pulumi.set(__self__, "default_branch", default_branch)
        pulumi.set(__self__, "id", id)
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "project_id", project_id)
        pulumi.set(__self__, "remote_url", remote_url)
        pulumi.set(__self__, "size", size)
        pulumi.set(__self__, "ssh_url", ssh_url)
        pulumi.set(__self__, "url", url)
        pulumi.set(__self__, "web_url", web_url)

    @property
    @pulumi.getter(name="defaultBranch")
    def default_branch(self) -> str:
        """
        The ref of the default branch.
        """
        return pulumi.get(self, "default_branch")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        Git repository identifier.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the Git repository to retrieve; requires `project_id` to be specified as well
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> str:
        """
        ID of project to list Git repositories
        """
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter(name="remoteUrl")
    def remote_url(self) -> str:
        """
        HTTPS Url to clone the Git repository
        """
        return pulumi.get(self, "remote_url")

    @property
    @pulumi.getter
    def size(self) -> int:
        """
        Compressed size (bytes) of the repository.
        """
        return pulumi.get(self, "size")

    @property
    @pulumi.getter(name="sshUrl")
    def ssh_url(self) -> str:
        """
        SSH Url to clone the Git repository
        """
        return pulumi.get(self, "ssh_url")

    @property
    @pulumi.getter
    def url(self) -> str:
        """
        Details REST API endpoint for the Git Repository.
        """
        return pulumi.get(self, "url")

    @property
    @pulumi.getter(name="webUrl")
    def web_url(self) -> str:
        """
        Url of the Git repository web view
        """
        return pulumi.get(self, "web_url")


