# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'BuildDefinitionCiTrigger',
    'BuildDefinitionCiTriggerOverride',
    'BuildDefinitionCiTriggerOverrideBranchFilter',
    'BuildDefinitionCiTriggerOverridePathFilter',
    'BuildDefinitionPullRequestTrigger',
    'BuildDefinitionPullRequestTriggerForks',
    'BuildDefinitionPullRequestTriggerOverride',
    'BuildDefinitionPullRequestTriggerOverrideBranchFilter',
    'BuildDefinitionPullRequestTriggerOverridePathFilter',
    'BuildDefinitionRepository',
    'BuildDefinitionSchedule',
    'BuildDefinitionScheduleBranchFilter',
    'BuildDefinitionVariable',
]

@pulumi.output_type
class BuildDefinitionCiTrigger(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "useYaml":
            suggest = "use_yaml"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionCiTrigger. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionCiTrigger.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionCiTrigger.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 override: Optional['outputs.BuildDefinitionCiTriggerOverride'] = None,
                 use_yaml: Optional[bool] = None):
        """
        :param 'BuildDefinitionCiTriggerOverrideArgs' override: Override the azure-pipeline file and use a this configuration for all builds.
        :param bool use_yaml: Use the azure-pipeline file for the build configuration. Defaults to `false`.
        """
        if override is not None:
            pulumi.set(__self__, "override", override)
        if use_yaml is not None:
            pulumi.set(__self__, "use_yaml", use_yaml)

    @property
    @pulumi.getter
    def override(self) -> Optional['outputs.BuildDefinitionCiTriggerOverride']:
        """
        Override the azure-pipeline file and use a this configuration for all builds.
        """
        return pulumi.get(self, "override")

    @property
    @pulumi.getter(name="useYaml")
    def use_yaml(self) -> Optional[bool]:
        """
        Use the azure-pipeline file for the build configuration. Defaults to `false`.
        """
        return pulumi.get(self, "use_yaml")


@pulumi.output_type
class BuildDefinitionCiTriggerOverride(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "branchFilters":
            suggest = "branch_filters"
        elif key == "maxConcurrentBuildsPerBranch":
            suggest = "max_concurrent_builds_per_branch"
        elif key == "pathFilters":
            suggest = "path_filters"
        elif key == "pollingInterval":
            suggest = "polling_interval"
        elif key == "pollingJobId":
            suggest = "polling_job_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionCiTriggerOverride. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionCiTriggerOverride.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionCiTriggerOverride.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 batch: Optional[bool] = None,
                 branch_filters: Optional[Sequence['outputs.BuildDefinitionCiTriggerOverrideBranchFilter']] = None,
                 max_concurrent_builds_per_branch: Optional[int] = None,
                 path_filters: Optional[Sequence['outputs.BuildDefinitionCiTriggerOverridePathFilter']] = None,
                 polling_interval: Optional[int] = None,
                 polling_job_id: Optional[str] = None):
        """
        :param bool batch: If you set batch to true, when a pipeline is running, the system waits until the run is completed, then starts another run with all changes that have not yet been built. Defaults to `true`.
        :param Sequence['BuildDefinitionCiTriggerOverrideBranchFilterArgs'] branch_filters: The branches to include and exclude from the trigger.
        :param int max_concurrent_builds_per_branch: The number of max builds per branch. Defaults to `1`.
        :param Sequence['BuildDefinitionCiTriggerOverridePathFilterArgs'] path_filters: Specify file paths to include or exclude. Note that the wildcard syntax is different between branches/tags and file paths.
        :param int polling_interval: How often the external repository is polled. Defaults to `0`.
        :param str polling_job_id: This is the ID of the polling job that polls the external repository. Once the build definition is saved/updated, this value is set.
        """
        if batch is not None:
            pulumi.set(__self__, "batch", batch)
        if branch_filters is not None:
            pulumi.set(__self__, "branch_filters", branch_filters)
        if max_concurrent_builds_per_branch is not None:
            pulumi.set(__self__, "max_concurrent_builds_per_branch", max_concurrent_builds_per_branch)
        if path_filters is not None:
            pulumi.set(__self__, "path_filters", path_filters)
        if polling_interval is not None:
            pulumi.set(__self__, "polling_interval", polling_interval)
        if polling_job_id is not None:
            pulumi.set(__self__, "polling_job_id", polling_job_id)

    @property
    @pulumi.getter
    def batch(self) -> Optional[bool]:
        """
        If you set batch to true, when a pipeline is running, the system waits until the run is completed, then starts another run with all changes that have not yet been built. Defaults to `true`.
        """
        return pulumi.get(self, "batch")

    @property
    @pulumi.getter(name="branchFilters")
    def branch_filters(self) -> Optional[Sequence['outputs.BuildDefinitionCiTriggerOverrideBranchFilter']]:
        """
        The branches to include and exclude from the trigger.
        """
        return pulumi.get(self, "branch_filters")

    @property
    @pulumi.getter(name="maxConcurrentBuildsPerBranch")
    def max_concurrent_builds_per_branch(self) -> Optional[int]:
        """
        The number of max builds per branch. Defaults to `1`.
        """
        return pulumi.get(self, "max_concurrent_builds_per_branch")

    @property
    @pulumi.getter(name="pathFilters")
    def path_filters(self) -> Optional[Sequence['outputs.BuildDefinitionCiTriggerOverridePathFilter']]:
        """
        Specify file paths to include or exclude. Note that the wildcard syntax is different between branches/tags and file paths.
        """
        return pulumi.get(self, "path_filters")

    @property
    @pulumi.getter(name="pollingInterval")
    def polling_interval(self) -> Optional[int]:
        """
        How often the external repository is polled. Defaults to `0`.
        """
        return pulumi.get(self, "polling_interval")

    @property
    @pulumi.getter(name="pollingJobId")
    def polling_job_id(self) -> Optional[str]:
        """
        This is the ID of the polling job that polls the external repository. Once the build definition is saved/updated, this value is set.
        """
        return pulumi.get(self, "polling_job_id")


@pulumi.output_type
class BuildDefinitionCiTriggerOverrideBranchFilter(dict):
    def __init__(__self__, *,
                 excludes: Optional[Sequence[str]] = None,
                 includes: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] excludes: List of branch patterns to exclude.
        :param Sequence[str] includes: List of branch patterns to include.
        """
        if excludes is not None:
            pulumi.set(__self__, "excludes", excludes)
        if includes is not None:
            pulumi.set(__self__, "includes", includes)

    @property
    @pulumi.getter
    def excludes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to exclude.
        """
        return pulumi.get(self, "excludes")

    @property
    @pulumi.getter
    def includes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to include.
        """
        return pulumi.get(self, "includes")


@pulumi.output_type
class BuildDefinitionCiTriggerOverridePathFilter(dict):
    def __init__(__self__, *,
                 excludes: Optional[Sequence[str]] = None,
                 includes: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] excludes: List of branch patterns to exclude.
        :param Sequence[str] includes: List of branch patterns to include.
        """
        if excludes is not None:
            pulumi.set(__self__, "excludes", excludes)
        if includes is not None:
            pulumi.set(__self__, "includes", includes)

    @property
    @pulumi.getter
    def excludes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to exclude.
        """
        return pulumi.get(self, "excludes")

    @property
    @pulumi.getter
    def includes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to include.
        """
        return pulumi.get(self, "includes")


@pulumi.output_type
class BuildDefinitionPullRequestTrigger(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "commentRequired":
            suggest = "comment_required"
        elif key == "initialBranch":
            suggest = "initial_branch"
        elif key == "useYaml":
            suggest = "use_yaml"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionPullRequestTrigger. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionPullRequestTrigger.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionPullRequestTrigger.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 forks: 'outputs.BuildDefinitionPullRequestTriggerForks',
                 comment_required: Optional[str] = None,
                 initial_branch: Optional[str] = None,
                 override: Optional['outputs.BuildDefinitionPullRequestTriggerOverride'] = None,
                 use_yaml: Optional[bool] = None):
        """
        :param 'BuildDefinitionPullRequestTriggerForksArgs' forks: Set permissions for Forked repositories.
        :param 'BuildDefinitionPullRequestTriggerOverrideArgs' override: Override the azure-pipeline file and use this configuration for all builds.
        :param bool use_yaml: Use the azure-pipeline file for the build configuration. Defaults to `false`.
        """
        pulumi.set(__self__, "forks", forks)
        if comment_required is not None:
            pulumi.set(__self__, "comment_required", comment_required)
        if initial_branch is not None:
            pulumi.set(__self__, "initial_branch", initial_branch)
        if override is not None:
            pulumi.set(__self__, "override", override)
        if use_yaml is not None:
            pulumi.set(__self__, "use_yaml", use_yaml)

    @property
    @pulumi.getter
    def forks(self) -> 'outputs.BuildDefinitionPullRequestTriggerForks':
        """
        Set permissions for Forked repositories.
        """
        return pulumi.get(self, "forks")

    @property
    @pulumi.getter(name="commentRequired")
    def comment_required(self) -> Optional[str]:
        return pulumi.get(self, "comment_required")

    @property
    @pulumi.getter(name="initialBranch")
    def initial_branch(self) -> Optional[str]:
        return pulumi.get(self, "initial_branch")

    @property
    @pulumi.getter
    def override(self) -> Optional['outputs.BuildDefinitionPullRequestTriggerOverride']:
        """
        Override the azure-pipeline file and use this configuration for all builds.
        """
        return pulumi.get(self, "override")

    @property
    @pulumi.getter(name="useYaml")
    def use_yaml(self) -> Optional[bool]:
        """
        Use the azure-pipeline file for the build configuration. Defaults to `false`.
        """
        return pulumi.get(self, "use_yaml")


@pulumi.output_type
class BuildDefinitionPullRequestTriggerForks(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "shareSecrets":
            suggest = "share_secrets"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionPullRequestTriggerForks. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionPullRequestTriggerForks.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionPullRequestTriggerForks.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 enabled: bool,
                 share_secrets: bool):
        """
        :param bool enabled: Build pull requests form forms of this repository.
        :param bool share_secrets: Make secrets available to builds of forks.
        """
        pulumi.set(__self__, "enabled", enabled)
        pulumi.set(__self__, "share_secrets", share_secrets)

    @property
    @pulumi.getter
    def enabled(self) -> bool:
        """
        Build pull requests form forms of this repository.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter(name="shareSecrets")
    def share_secrets(self) -> bool:
        """
        Make secrets available to builds of forks.
        """
        return pulumi.get(self, "share_secrets")


@pulumi.output_type
class BuildDefinitionPullRequestTriggerOverride(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "autoCancel":
            suggest = "auto_cancel"
        elif key == "branchFilters":
            suggest = "branch_filters"
        elif key == "pathFilters":
            suggest = "path_filters"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionPullRequestTriggerOverride. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionPullRequestTriggerOverride.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionPullRequestTriggerOverride.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 auto_cancel: Optional[bool] = None,
                 branch_filters: Optional[Sequence['outputs.BuildDefinitionPullRequestTriggerOverrideBranchFilter']] = None,
                 path_filters: Optional[Sequence['outputs.BuildDefinitionPullRequestTriggerOverridePathFilter']] = None):
        """
        :param bool auto_cancel: . Defaults to `true`.
        :param Sequence['BuildDefinitionPullRequestTriggerOverrideBranchFilterArgs'] branch_filters: The branches to include and exclude from the trigger.
        :param Sequence['BuildDefinitionPullRequestTriggerOverridePathFilterArgs'] path_filters: Specify file paths to include or exclude. Note that the wildcard syntax is different between branches/tags and file paths.
        """
        if auto_cancel is not None:
            pulumi.set(__self__, "auto_cancel", auto_cancel)
        if branch_filters is not None:
            pulumi.set(__self__, "branch_filters", branch_filters)
        if path_filters is not None:
            pulumi.set(__self__, "path_filters", path_filters)

    @property
    @pulumi.getter(name="autoCancel")
    def auto_cancel(self) -> Optional[bool]:
        """
        . Defaults to `true`.
        """
        return pulumi.get(self, "auto_cancel")

    @property
    @pulumi.getter(name="branchFilters")
    def branch_filters(self) -> Optional[Sequence['outputs.BuildDefinitionPullRequestTriggerOverrideBranchFilter']]:
        """
        The branches to include and exclude from the trigger.
        """
        return pulumi.get(self, "branch_filters")

    @property
    @pulumi.getter(name="pathFilters")
    def path_filters(self) -> Optional[Sequence['outputs.BuildDefinitionPullRequestTriggerOverridePathFilter']]:
        """
        Specify file paths to include or exclude. Note that the wildcard syntax is different between branches/tags and file paths.
        """
        return pulumi.get(self, "path_filters")


@pulumi.output_type
class BuildDefinitionPullRequestTriggerOverrideBranchFilter(dict):
    def __init__(__self__, *,
                 excludes: Optional[Sequence[str]] = None,
                 includes: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] excludes: List of branch patterns to exclude.
        :param Sequence[str] includes: List of branch patterns to include.
        """
        if excludes is not None:
            pulumi.set(__self__, "excludes", excludes)
        if includes is not None:
            pulumi.set(__self__, "includes", includes)

    @property
    @pulumi.getter
    def excludes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to exclude.
        """
        return pulumi.get(self, "excludes")

    @property
    @pulumi.getter
    def includes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to include.
        """
        return pulumi.get(self, "includes")


@pulumi.output_type
class BuildDefinitionPullRequestTriggerOverridePathFilter(dict):
    def __init__(__self__, *,
                 excludes: Optional[Sequence[str]] = None,
                 includes: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] excludes: List of branch patterns to exclude.
        :param Sequence[str] includes: List of branch patterns to include.
        """
        if excludes is not None:
            pulumi.set(__self__, "excludes", excludes)
        if includes is not None:
            pulumi.set(__self__, "includes", includes)

    @property
    @pulumi.getter
    def excludes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to exclude.
        """
        return pulumi.get(self, "excludes")

    @property
    @pulumi.getter
    def includes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to include.
        """
        return pulumi.get(self, "includes")


@pulumi.output_type
class BuildDefinitionRepository(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "repoId":
            suggest = "repo_id"
        elif key == "repoType":
            suggest = "repo_type"
        elif key == "ymlPath":
            suggest = "yml_path"
        elif key == "branchName":
            suggest = "branch_name"
        elif key == "githubEnterpriseUrl":
            suggest = "github_enterprise_url"
        elif key == "reportBuildStatus":
            suggest = "report_build_status"
        elif key == "serviceConnectionId":
            suggest = "service_connection_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionRepository. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionRepository.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionRepository.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 repo_id: str,
                 repo_type: str,
                 yml_path: str,
                 branch_name: Optional[str] = None,
                 github_enterprise_url: Optional[str] = None,
                 report_build_status: Optional[bool] = None,
                 service_connection_id: Optional[str] = None):
        """
        :param str repo_id: The id of the repository. For `TfsGit` repos, this is simply the ID of the repository. For `Github` repos, this will take the form of `<GitHub Org>/<Repo Name>`. For `Bitbucket` repos, this will take the form of `<Workspace ID>/<Repo Name>`.
        :param str repo_type: The repository type. Valid values: `GitHub` or `TfsGit` or `Bitbucket` or `GitHub Enterprise`. Defaults to `GitHub`. If `repo_type` is `GitHubEnterprise`, must use existing project and GitHub Enterprise service connection.
        :param str yml_path: The path of the Yaml file describing the build definition.
        :param str branch_name: The branch name for which builds are triggered. Defaults to `master`.
        :param str github_enterprise_url: The Github Enterprise URL. Used if `repo_type` is `GithubEnterprise`.
        :param bool report_build_status: Report build status. Default is true.
        :param str service_connection_id: The service connection ID. Used if the `repo_type` is `GitHub` or `GitHubEnterprise`.
        """
        pulumi.set(__self__, "repo_id", repo_id)
        pulumi.set(__self__, "repo_type", repo_type)
        pulumi.set(__self__, "yml_path", yml_path)
        if branch_name is not None:
            pulumi.set(__self__, "branch_name", branch_name)
        if github_enterprise_url is not None:
            pulumi.set(__self__, "github_enterprise_url", github_enterprise_url)
        if report_build_status is not None:
            pulumi.set(__self__, "report_build_status", report_build_status)
        if service_connection_id is not None:
            pulumi.set(__self__, "service_connection_id", service_connection_id)

    @property
    @pulumi.getter(name="repoId")
    def repo_id(self) -> str:
        """
        The id of the repository. For `TfsGit` repos, this is simply the ID of the repository. For `Github` repos, this will take the form of `<GitHub Org>/<Repo Name>`. For `Bitbucket` repos, this will take the form of `<Workspace ID>/<Repo Name>`.
        """
        return pulumi.get(self, "repo_id")

    @property
    @pulumi.getter(name="repoType")
    def repo_type(self) -> str:
        """
        The repository type. Valid values: `GitHub` or `TfsGit` or `Bitbucket` or `GitHub Enterprise`. Defaults to `GitHub`. If `repo_type` is `GitHubEnterprise`, must use existing project and GitHub Enterprise service connection.
        """
        return pulumi.get(self, "repo_type")

    @property
    @pulumi.getter(name="ymlPath")
    def yml_path(self) -> str:
        """
        The path of the Yaml file describing the build definition.
        """
        return pulumi.get(self, "yml_path")

    @property
    @pulumi.getter(name="branchName")
    def branch_name(self) -> Optional[str]:
        """
        The branch name for which builds are triggered. Defaults to `master`.
        """
        return pulumi.get(self, "branch_name")

    @property
    @pulumi.getter(name="githubEnterpriseUrl")
    def github_enterprise_url(self) -> Optional[str]:
        """
        The Github Enterprise URL. Used if `repo_type` is `GithubEnterprise`.
        """
        return pulumi.get(self, "github_enterprise_url")

    @property
    @pulumi.getter(name="reportBuildStatus")
    def report_build_status(self) -> Optional[bool]:
        """
        Report build status. Default is true.
        """
        return pulumi.get(self, "report_build_status")

    @property
    @pulumi.getter(name="serviceConnectionId")
    def service_connection_id(self) -> Optional[str]:
        """
        The service connection ID. Used if the `repo_type` is `GitHub` or `GitHubEnterprise`.
        """
        return pulumi.get(self, "service_connection_id")


@pulumi.output_type
class BuildDefinitionSchedule(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "daysToBuilds":
            suggest = "days_to_builds"
        elif key == "branchFilters":
            suggest = "branch_filters"
        elif key == "scheduleJobId":
            suggest = "schedule_job_id"
        elif key == "scheduleOnlyWithChanges":
            suggest = "schedule_only_with_changes"
        elif key == "startHours":
            suggest = "start_hours"
        elif key == "startMinutes":
            suggest = "start_minutes"
        elif key == "timeZone":
            suggest = "time_zone"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionSchedule. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionSchedule.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionSchedule.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 days_to_builds: Sequence[str],
                 branch_filters: Optional[Sequence['outputs.BuildDefinitionScheduleBranchFilter']] = None,
                 schedule_job_id: Optional[str] = None,
                 schedule_only_with_changes: Optional[bool] = None,
                 start_hours: Optional[int] = None,
                 start_minutes: Optional[int] = None,
                 time_zone: Optional[str] = None):
        """
        :param Sequence['BuildDefinitionScheduleBranchFilterArgs'] branch_filters: block supports the following:
        :param str schedule_job_id: The ID of the schedule job
        """
        pulumi.set(__self__, "days_to_builds", days_to_builds)
        if branch_filters is not None:
            pulumi.set(__self__, "branch_filters", branch_filters)
        if schedule_job_id is not None:
            pulumi.set(__self__, "schedule_job_id", schedule_job_id)
        if schedule_only_with_changes is not None:
            pulumi.set(__self__, "schedule_only_with_changes", schedule_only_with_changes)
        if start_hours is not None:
            pulumi.set(__self__, "start_hours", start_hours)
        if start_minutes is not None:
            pulumi.set(__self__, "start_minutes", start_minutes)
        if time_zone is not None:
            pulumi.set(__self__, "time_zone", time_zone)

    @property
    @pulumi.getter(name="daysToBuilds")
    def days_to_builds(self) -> Sequence[str]:
        return pulumi.get(self, "days_to_builds")

    @property
    @pulumi.getter(name="branchFilters")
    def branch_filters(self) -> Optional[Sequence['outputs.BuildDefinitionScheduleBranchFilter']]:
        """
        block supports the following:
        """
        return pulumi.get(self, "branch_filters")

    @property
    @pulumi.getter(name="scheduleJobId")
    def schedule_job_id(self) -> Optional[str]:
        """
        The ID of the schedule job
        """
        return pulumi.get(self, "schedule_job_id")

    @property
    @pulumi.getter(name="scheduleOnlyWithChanges")
    def schedule_only_with_changes(self) -> Optional[bool]:
        return pulumi.get(self, "schedule_only_with_changes")

    @property
    @pulumi.getter(name="startHours")
    def start_hours(self) -> Optional[int]:
        return pulumi.get(self, "start_hours")

    @property
    @pulumi.getter(name="startMinutes")
    def start_minutes(self) -> Optional[int]:
        return pulumi.get(self, "start_minutes")

    @property
    @pulumi.getter(name="timeZone")
    def time_zone(self) -> Optional[str]:
        return pulumi.get(self, "time_zone")


@pulumi.output_type
class BuildDefinitionScheduleBranchFilter(dict):
    def __init__(__self__, *,
                 excludes: Optional[Sequence[str]] = None,
                 includes: Optional[Sequence[str]] = None):
        """
        :param Sequence[str] excludes: List of branch patterns to exclude.
        :param Sequence[str] includes: List of branch patterns to include.
        """
        if excludes is not None:
            pulumi.set(__self__, "excludes", excludes)
        if includes is not None:
            pulumi.set(__self__, "includes", includes)

    @property
    @pulumi.getter
    def excludes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to exclude.
        """
        return pulumi.get(self, "excludes")

    @property
    @pulumi.getter
    def includes(self) -> Optional[Sequence[str]]:
        """
        List of branch patterns to include.
        """
        return pulumi.get(self, "includes")


@pulumi.output_type
class BuildDefinitionVariable(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "allowOverride":
            suggest = "allow_override"
        elif key == "isSecret":
            suggest = "is_secret"
        elif key == "secretValue":
            suggest = "secret_value"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in BuildDefinitionVariable. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        BuildDefinitionVariable.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        BuildDefinitionVariable.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 name: str,
                 allow_override: Optional[bool] = None,
                 is_secret: Optional[bool] = None,
                 secret_value: Optional[str] = None,
                 value: Optional[str] = None):
        """
        :param str name: The name of the variable.
        :param bool allow_override: True if the variable can be overridden. Defaults to `true`.
        :param bool is_secret: True if the variable is a secret. Defaults to `false`.
        :param str secret_value: The secret value of the variable. Used when `is_secret` set to `true`.
        :param str value: The value of the variable.
        """
        pulumi.set(__self__, "name", name)
        if allow_override is not None:
            pulumi.set(__self__, "allow_override", allow_override)
        if is_secret is not None:
            pulumi.set(__self__, "is_secret", is_secret)
        if secret_value is not None:
            pulumi.set(__self__, "secret_value", secret_value)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the variable.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="allowOverride")
    def allow_override(self) -> Optional[bool]:
        """
        True if the variable can be overridden. Defaults to `true`.
        """
        return pulumi.get(self, "allow_override")

    @property
    @pulumi.getter(name="isSecret")
    def is_secret(self) -> Optional[bool]:
        """
        True if the variable is a secret. Defaults to `false`.
        """
        return pulumi.get(self, "is_secret")

    @property
    @pulumi.getter(name="secretValue")
    def secret_value(self) -> Optional[str]:
        """
        The secret value of the variable. Used when `is_secret` set to `true`.
        """
        return pulumi.get(self, "secret_value")

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        """
        The value of the variable.
        """
        return pulumi.get(self, "value")


