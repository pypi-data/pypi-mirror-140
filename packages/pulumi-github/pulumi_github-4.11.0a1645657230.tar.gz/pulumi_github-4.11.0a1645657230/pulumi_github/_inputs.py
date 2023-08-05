# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'ActionsOrganizationPermissionsAllowedActionsConfigArgs',
    'ActionsOrganizationPermissionsEnabledRepositoriesConfigArgs',
    'BranchProtectionRequiredPullRequestReviewArgs',
    'BranchProtectionRequiredStatusCheckArgs',
    'BranchProtectionV3RequiredPullRequestReviewsArgs',
    'BranchProtectionV3RequiredStatusChecksArgs',
    'BranchProtectionV3RestrictionsArgs',
    'OrganizationWebhookConfigurationArgs',
    'ProviderAppAuthArgs',
    'RepositoryBranchArgs',
    'RepositoryEnvironmentDeploymentBranchPolicyArgs',
    'RepositoryEnvironmentReviewerArgs',
    'RepositoryPagesArgs',
    'RepositoryPagesSourceArgs',
    'RepositoryTemplateArgs',
    'RepositoryWebhookConfigurationArgs',
    'TeamMembersMemberArgs',
    'TeamSyncGroupMappingGroupArgs',
]

@pulumi.input_type
class ActionsOrganizationPermissionsAllowedActionsConfigArgs:
    def __init__(__self__, *,
                 github_owned_allowed: pulumi.Input[bool],
                 patterns_alloweds: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 verified_allowed: Optional[pulumi.Input[bool]] = None):
        """
        :param pulumi.Input[bool] github_owned_allowed: Whether GitHub-owned actions are allowed in the organization.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] patterns_alloweds: Specifies a list of string-matching patterns to allow specific action(s). Wildcards, tags, and SHAs are allowed. For example, monalisa/octocat@*, monalisa/octocat@v2, monalisa/*."
        :param pulumi.Input[bool] verified_allowed: Whether actions in GitHub Marketplace from verified creators are allowed. Set to true to allow all GitHub Marketplace actions by verified creators.
        """
        pulumi.set(__self__, "github_owned_allowed", github_owned_allowed)
        if patterns_alloweds is not None:
            pulumi.set(__self__, "patterns_alloweds", patterns_alloweds)
        if verified_allowed is not None:
            pulumi.set(__self__, "verified_allowed", verified_allowed)

    @property
    @pulumi.getter(name="githubOwnedAllowed")
    def github_owned_allowed(self) -> pulumi.Input[bool]:
        """
        Whether GitHub-owned actions are allowed in the organization.
        """
        return pulumi.get(self, "github_owned_allowed")

    @github_owned_allowed.setter
    def github_owned_allowed(self, value: pulumi.Input[bool]):
        pulumi.set(self, "github_owned_allowed", value)

    @property
    @pulumi.getter(name="patternsAlloweds")
    def patterns_alloweds(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Specifies a list of string-matching patterns to allow specific action(s). Wildcards, tags, and SHAs are allowed. For example, monalisa/octocat@*, monalisa/octocat@v2, monalisa/*."
        """
        return pulumi.get(self, "patterns_alloweds")

    @patterns_alloweds.setter
    def patterns_alloweds(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "patterns_alloweds", value)

    @property
    @pulumi.getter(name="verifiedAllowed")
    def verified_allowed(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether actions in GitHub Marketplace from verified creators are allowed. Set to true to allow all GitHub Marketplace actions by verified creators.
        """
        return pulumi.get(self, "verified_allowed")

    @verified_allowed.setter
    def verified_allowed(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "verified_allowed", value)


@pulumi.input_type
class ActionsOrganizationPermissionsEnabledRepositoriesConfigArgs:
    def __init__(__self__, *,
                 repository_ids: pulumi.Input[Sequence[pulumi.Input[int]]]):
        """
        :param pulumi.Input[Sequence[pulumi.Input[int]]] repository_ids: List of repository IDs to enable for GitHub Actions.
        """
        pulumi.set(__self__, "repository_ids", repository_ids)

    @property
    @pulumi.getter(name="repositoryIds")
    def repository_ids(self) -> pulumi.Input[Sequence[pulumi.Input[int]]]:
        """
        List of repository IDs to enable for GitHub Actions.
        """
        return pulumi.get(self, "repository_ids")

    @repository_ids.setter
    def repository_ids(self, value: pulumi.Input[Sequence[pulumi.Input[int]]]):
        pulumi.set(self, "repository_ids", value)


@pulumi.input_type
class BranchProtectionRequiredPullRequestReviewArgs:
    def __init__(__self__, *,
                 dismiss_stale_reviews: Optional[pulumi.Input[bool]] = None,
                 dismissal_restrictions: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 require_code_owner_reviews: Optional[pulumi.Input[bool]] = None,
                 required_approving_review_count: Optional[pulumi.Input[int]] = None,
                 restrict_dismissals: Optional[pulumi.Input[bool]] = None):
        if dismiss_stale_reviews is not None:
            pulumi.set(__self__, "dismiss_stale_reviews", dismiss_stale_reviews)
        if dismissal_restrictions is not None:
            pulumi.set(__self__, "dismissal_restrictions", dismissal_restrictions)
        if require_code_owner_reviews is not None:
            pulumi.set(__self__, "require_code_owner_reviews", require_code_owner_reviews)
        if required_approving_review_count is not None:
            pulumi.set(__self__, "required_approving_review_count", required_approving_review_count)
        if restrict_dismissals is not None:
            pulumi.set(__self__, "restrict_dismissals", restrict_dismissals)

    @property
    @pulumi.getter(name="dismissStaleReviews")
    def dismiss_stale_reviews(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "dismiss_stale_reviews")

    @dismiss_stale_reviews.setter
    def dismiss_stale_reviews(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dismiss_stale_reviews", value)

    @property
    @pulumi.getter(name="dismissalRestrictions")
    def dismissal_restrictions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "dismissal_restrictions")

    @dismissal_restrictions.setter
    def dismissal_restrictions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "dismissal_restrictions", value)

    @property
    @pulumi.getter(name="requireCodeOwnerReviews")
    def require_code_owner_reviews(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "require_code_owner_reviews")

    @require_code_owner_reviews.setter
    def require_code_owner_reviews(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "require_code_owner_reviews", value)

    @property
    @pulumi.getter(name="requiredApprovingReviewCount")
    def required_approving_review_count(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "required_approving_review_count")

    @required_approving_review_count.setter
    def required_approving_review_count(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "required_approving_review_count", value)

    @property
    @pulumi.getter(name="restrictDismissals")
    def restrict_dismissals(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "restrict_dismissals")

    @restrict_dismissals.setter
    def restrict_dismissals(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "restrict_dismissals", value)


@pulumi.input_type
class BranchProtectionRequiredStatusCheckArgs:
    def __init__(__self__, *,
                 contexts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 strict: Optional[pulumi.Input[bool]] = None):
        if contexts is not None:
            pulumi.set(__self__, "contexts", contexts)
        if strict is not None:
            pulumi.set(__self__, "strict", strict)

    @property
    @pulumi.getter
    def contexts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "contexts")

    @contexts.setter
    def contexts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "contexts", value)

    @property
    @pulumi.getter
    def strict(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "strict")

    @strict.setter
    def strict(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "strict", value)


@pulumi.input_type
class BranchProtectionV3RequiredPullRequestReviewsArgs:
    def __init__(__self__, *,
                 dismiss_stale_reviews: Optional[pulumi.Input[bool]] = None,
                 dismissal_teams: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 dismissal_users: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 include_admins: Optional[pulumi.Input[bool]] = None,
                 require_code_owner_reviews: Optional[pulumi.Input[bool]] = None,
                 required_approving_review_count: Optional[pulumi.Input[int]] = None):
        if dismiss_stale_reviews is not None:
            pulumi.set(__self__, "dismiss_stale_reviews", dismiss_stale_reviews)
        if dismissal_teams is not None:
            pulumi.set(__self__, "dismissal_teams", dismissal_teams)
        if dismissal_users is not None:
            pulumi.set(__self__, "dismissal_users", dismissal_users)
        if include_admins is not None:
            warnings.warn("""Use enforce_admins instead""", DeprecationWarning)
            pulumi.log.warn("""include_admins is deprecated: Use enforce_admins instead""")
        if include_admins is not None:
            pulumi.set(__self__, "include_admins", include_admins)
        if require_code_owner_reviews is not None:
            pulumi.set(__self__, "require_code_owner_reviews", require_code_owner_reviews)
        if required_approving_review_count is not None:
            pulumi.set(__self__, "required_approving_review_count", required_approving_review_count)

    @property
    @pulumi.getter(name="dismissStaleReviews")
    def dismiss_stale_reviews(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "dismiss_stale_reviews")

    @dismiss_stale_reviews.setter
    def dismiss_stale_reviews(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "dismiss_stale_reviews", value)

    @property
    @pulumi.getter(name="dismissalTeams")
    def dismissal_teams(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "dismissal_teams")

    @dismissal_teams.setter
    def dismissal_teams(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "dismissal_teams", value)

    @property
    @pulumi.getter(name="dismissalUsers")
    def dismissal_users(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "dismissal_users")

    @dismissal_users.setter
    def dismissal_users(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "dismissal_users", value)

    @property
    @pulumi.getter(name="includeAdmins")
    def include_admins(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "include_admins")

    @include_admins.setter
    def include_admins(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "include_admins", value)

    @property
    @pulumi.getter(name="requireCodeOwnerReviews")
    def require_code_owner_reviews(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "require_code_owner_reviews")

    @require_code_owner_reviews.setter
    def require_code_owner_reviews(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "require_code_owner_reviews", value)

    @property
    @pulumi.getter(name="requiredApprovingReviewCount")
    def required_approving_review_count(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "required_approving_review_count")

    @required_approving_review_count.setter
    def required_approving_review_count(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "required_approving_review_count", value)


@pulumi.input_type
class BranchProtectionV3RequiredStatusChecksArgs:
    def __init__(__self__, *,
                 contexts: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 include_admins: Optional[pulumi.Input[bool]] = None,
                 strict: Optional[pulumi.Input[bool]] = None):
        if contexts is not None:
            pulumi.set(__self__, "contexts", contexts)
        if include_admins is not None:
            warnings.warn("""Use enforce_admins instead""", DeprecationWarning)
            pulumi.log.warn("""include_admins is deprecated: Use enforce_admins instead""")
        if include_admins is not None:
            pulumi.set(__self__, "include_admins", include_admins)
        if strict is not None:
            pulumi.set(__self__, "strict", strict)

    @property
    @pulumi.getter
    def contexts(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "contexts")

    @contexts.setter
    def contexts(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "contexts", value)

    @property
    @pulumi.getter(name="includeAdmins")
    def include_admins(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "include_admins")

    @include_admins.setter
    def include_admins(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "include_admins", value)

    @property
    @pulumi.getter
    def strict(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "strict")

    @strict.setter
    def strict(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "strict", value)


@pulumi.input_type
class BranchProtectionV3RestrictionsArgs:
    def __init__(__self__, *,
                 apps: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 teams: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        if apps is not None:
            pulumi.set(__self__, "apps", apps)
        if teams is not None:
            pulumi.set(__self__, "teams", teams)
        if users is not None:
            pulumi.set(__self__, "users", users)

    @property
    @pulumi.getter
    def apps(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "apps")

    @apps.setter
    def apps(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "apps", value)

    @property
    @pulumi.getter
    def teams(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "teams")

    @teams.setter
    def teams(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "teams", value)

    @property
    @pulumi.getter
    def users(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "users")

    @users.setter
    def users(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "users", value)


@pulumi.input_type
class OrganizationWebhookConfigurationArgs:
    def __init__(__self__, *,
                 url: pulumi.Input[str],
                 content_type: Optional[pulumi.Input[str]] = None,
                 insecure_ssl: Optional[pulumi.Input[bool]] = None,
                 secret: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] url: URL of the webhook
        """
        pulumi.set(__self__, "url", url)
        if content_type is not None:
            pulumi.set(__self__, "content_type", content_type)
        if insecure_ssl is not None:
            pulumi.set(__self__, "insecure_ssl", insecure_ssl)
        if secret is not None:
            pulumi.set(__self__, "secret", secret)

    @property
    @pulumi.getter
    def url(self) -> pulumi.Input[str]:
        """
        URL of the webhook
        """
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: pulumi.Input[str]):
        pulumi.set(self, "url", value)

    @property
    @pulumi.getter(name="contentType")
    def content_type(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "content_type")

    @content_type.setter
    def content_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "content_type", value)

    @property
    @pulumi.getter(name="insecureSsl")
    def insecure_ssl(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "insecure_ssl")

    @insecure_ssl.setter
    def insecure_ssl(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "insecure_ssl", value)

    @property
    @pulumi.getter
    def secret(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "secret")

    @secret.setter
    def secret(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "secret", value)


@pulumi.input_type
class ProviderAppAuthArgs:
    def __init__(__self__, *,
                 id: pulumi.Input[str],
                 installation_id: pulumi.Input[str],
                 pem_file: pulumi.Input[str]):
        pulumi.set(__self__, "id", id)
        pulumi.set(__self__, "installation_id", installation_id)
        pulumi.set(__self__, "pem_file", pem_file)

    @property
    @pulumi.getter
    def id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "id")

    @id.setter
    def id(self, value: pulumi.Input[str]):
        pulumi.set(self, "id", value)

    @property
    @pulumi.getter(name="installationId")
    def installation_id(self) -> pulumi.Input[str]:
        return pulumi.get(self, "installation_id")

    @installation_id.setter
    def installation_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "installation_id", value)

    @property
    @pulumi.getter(name="pemFile")
    def pem_file(self) -> pulumi.Input[str]:
        return pulumi.get(self, "pem_file")

    @pem_file.setter
    def pem_file(self, value: pulumi.Input[str]):
        pulumi.set(self, "pem_file", value)


@pulumi.input_type
class RepositoryBranchArgs:
    def __init__(__self__, *,
                 name: Optional[pulumi.Input[str]] = None,
                 protected: Optional[pulumi.Input[bool]] = None):
        """
        :param pulumi.Input[str] name: The name of the repository.
        :param pulumi.Input[bool] protected: Whether the branch is protected.
        """
        if name is not None:
            pulumi.set(__self__, "name", name)
        if protected is not None:
            pulumi.set(__self__, "protected", protected)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the repository.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def protected(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether the branch is protected.
        """
        return pulumi.get(self, "protected")

    @protected.setter
    def protected(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "protected", value)


@pulumi.input_type
class RepositoryEnvironmentDeploymentBranchPolicyArgs:
    def __init__(__self__, *,
                 custom_branch_policies: pulumi.Input[bool],
                 protected_branches: pulumi.Input[bool]):
        """
        :param pulumi.Input[bool] custom_branch_policies: Whether only branches that match the specified name patterns can deploy to this environment.
        :param pulumi.Input[bool] protected_branches: Whether only branches with branch protection rules can deploy to this environment.
        """
        pulumi.set(__self__, "custom_branch_policies", custom_branch_policies)
        pulumi.set(__self__, "protected_branches", protected_branches)

    @property
    @pulumi.getter(name="customBranchPolicies")
    def custom_branch_policies(self) -> pulumi.Input[bool]:
        """
        Whether only branches that match the specified name patterns can deploy to this environment.
        """
        return pulumi.get(self, "custom_branch_policies")

    @custom_branch_policies.setter
    def custom_branch_policies(self, value: pulumi.Input[bool]):
        pulumi.set(self, "custom_branch_policies", value)

    @property
    @pulumi.getter(name="protectedBranches")
    def protected_branches(self) -> pulumi.Input[bool]:
        """
        Whether only branches with branch protection rules can deploy to this environment.
        """
        return pulumi.get(self, "protected_branches")

    @protected_branches.setter
    def protected_branches(self, value: pulumi.Input[bool]):
        pulumi.set(self, "protected_branches", value)


@pulumi.input_type
class RepositoryEnvironmentReviewerArgs:
    def __init__(__self__, *,
                 teams: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None,
                 users: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]] = None):
        """
        :param pulumi.Input[Sequence[pulumi.Input[int]]] teams: Up to 6 IDs for teams who may review jobs that reference the environment. Reviewers must have at least read access to the repository. Only one of the required reviewers needs to approve the job for it to proceed.
        :param pulumi.Input[Sequence[pulumi.Input[int]]] users: Up to 6 IDs for users who may review jobs that reference the environment. Reviewers must have at least read access to the repository. Only one of the required reviewers needs to approve the job for it to proceed.
        """
        if teams is not None:
            pulumi.set(__self__, "teams", teams)
        if users is not None:
            pulumi.set(__self__, "users", users)

    @property
    @pulumi.getter
    def teams(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]:
        """
        Up to 6 IDs for teams who may review jobs that reference the environment. Reviewers must have at least read access to the repository. Only one of the required reviewers needs to approve the job for it to proceed.
        """
        return pulumi.get(self, "teams")

    @teams.setter
    def teams(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]):
        pulumi.set(self, "teams", value)

    @property
    @pulumi.getter
    def users(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]:
        """
        Up to 6 IDs for users who may review jobs that reference the environment. Reviewers must have at least read access to the repository. Only one of the required reviewers needs to approve the job for it to proceed.
        """
        return pulumi.get(self, "users")

    @users.setter
    def users(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[int]]]]):
        pulumi.set(self, "users", value)


@pulumi.input_type
class RepositoryPagesArgs:
    def __init__(__self__, *,
                 source: pulumi.Input['RepositoryPagesSourceArgs'],
                 cname: Optional[pulumi.Input[str]] = None,
                 custom404: Optional[pulumi.Input[bool]] = None,
                 html_url: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 url: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input['RepositoryPagesSourceArgs'] source: The source branch and directory for the rendered Pages site. See GitHub Pages Source below for details.
        :param pulumi.Input[str] cname: The custom domain for the repository. This can only be set after the repository has been created.
        :param pulumi.Input[bool] custom404: Whether the rendered GitHub Pages site has a custom 404 page.
        :param pulumi.Input[str] html_url: The absolute URL (including scheme) of the rendered GitHub Pages site e.g. `https://username.github.io`.
        :param pulumi.Input[str] status: The GitHub Pages site's build status e.g. `building` or `built`.
        """
        pulumi.set(__self__, "source", source)
        if cname is not None:
            pulumi.set(__self__, "cname", cname)
        if custom404 is not None:
            pulumi.set(__self__, "custom404", custom404)
        if html_url is not None:
            pulumi.set(__self__, "html_url", html_url)
        if status is not None:
            pulumi.set(__self__, "status", status)
        if url is not None:
            pulumi.set(__self__, "url", url)

    @property
    @pulumi.getter
    def source(self) -> pulumi.Input['RepositoryPagesSourceArgs']:
        """
        The source branch and directory for the rendered Pages site. See GitHub Pages Source below for details.
        """
        return pulumi.get(self, "source")

    @source.setter
    def source(self, value: pulumi.Input['RepositoryPagesSourceArgs']):
        pulumi.set(self, "source", value)

    @property
    @pulumi.getter
    def cname(self) -> Optional[pulumi.Input[str]]:
        """
        The custom domain for the repository. This can only be set after the repository has been created.
        """
        return pulumi.get(self, "cname")

    @cname.setter
    def cname(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cname", value)

    @property
    @pulumi.getter
    def custom404(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether the rendered GitHub Pages site has a custom 404 page.
        """
        return pulumi.get(self, "custom404")

    @custom404.setter
    def custom404(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "custom404", value)

    @property
    @pulumi.getter(name="htmlUrl")
    def html_url(self) -> Optional[pulumi.Input[str]]:
        """
        The absolute URL (including scheme) of the rendered GitHub Pages site e.g. `https://username.github.io`.
        """
        return pulumi.get(self, "html_url")

    @html_url.setter
    def html_url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "html_url", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        The GitHub Pages site's build status e.g. `building` or `built`.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def url(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "url", value)


@pulumi.input_type
class RepositoryPagesSourceArgs:
    def __init__(__self__, *,
                 branch: pulumi.Input[str],
                 path: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] branch: The repository branch used to publish the site's source files. (i.e. `main` or `gh-pages`.
        :param pulumi.Input[str] path: The repository directory from which the site publishes (Default: `/`).
        """
        pulumi.set(__self__, "branch", branch)
        if path is not None:
            pulumi.set(__self__, "path", path)

    @property
    @pulumi.getter
    def branch(self) -> pulumi.Input[str]:
        """
        The repository branch used to publish the site's source files. (i.e. `main` or `gh-pages`.
        """
        return pulumi.get(self, "branch")

    @branch.setter
    def branch(self, value: pulumi.Input[str]):
        pulumi.set(self, "branch", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        """
        The repository directory from which the site publishes (Default: `/`).
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)


@pulumi.input_type
class RepositoryTemplateArgs:
    def __init__(__self__, *,
                 owner: pulumi.Input[str],
                 repository: pulumi.Input[str]):
        pulumi.set(__self__, "owner", owner)
        pulumi.set(__self__, "repository", repository)

    @property
    @pulumi.getter
    def owner(self) -> pulumi.Input[str]:
        return pulumi.get(self, "owner")

    @owner.setter
    def owner(self, value: pulumi.Input[str]):
        pulumi.set(self, "owner", value)

    @property
    @pulumi.getter
    def repository(self) -> pulumi.Input[str]:
        return pulumi.get(self, "repository")

    @repository.setter
    def repository(self, value: pulumi.Input[str]):
        pulumi.set(self, "repository", value)


@pulumi.input_type
class RepositoryWebhookConfigurationArgs:
    def __init__(__self__, *,
                 url: pulumi.Input[str],
                 content_type: Optional[pulumi.Input[str]] = None,
                 insecure_ssl: Optional[pulumi.Input[bool]] = None,
                 secret: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] url: The URL of the webhook.
        :param pulumi.Input[str] content_type: The content type for the payload. Valid values are either `form` or `json`.
        :param pulumi.Input[bool] insecure_ssl: Insecure SSL boolean toggle. Defaults to `false`.
        :param pulumi.Input[str] secret: The shared secret for the webhook. [See API documentation](https://developer.github.com/v3/repos/hooks/#create-a-hook).
        """
        pulumi.set(__self__, "url", url)
        if content_type is not None:
            pulumi.set(__self__, "content_type", content_type)
        if insecure_ssl is not None:
            pulumi.set(__self__, "insecure_ssl", insecure_ssl)
        if secret is not None:
            pulumi.set(__self__, "secret", secret)

    @property
    @pulumi.getter
    def url(self) -> pulumi.Input[str]:
        """
        The URL of the webhook.
        """
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: pulumi.Input[str]):
        pulumi.set(self, "url", value)

    @property
    @pulumi.getter(name="contentType")
    def content_type(self) -> Optional[pulumi.Input[str]]:
        """
        The content type for the payload. Valid values are either `form` or `json`.
        """
        return pulumi.get(self, "content_type")

    @content_type.setter
    def content_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "content_type", value)

    @property
    @pulumi.getter(name="insecureSsl")
    def insecure_ssl(self) -> Optional[pulumi.Input[bool]]:
        """
        Insecure SSL boolean toggle. Defaults to `false`.
        """
        return pulumi.get(self, "insecure_ssl")

    @insecure_ssl.setter
    def insecure_ssl(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "insecure_ssl", value)

    @property
    @pulumi.getter
    def secret(self) -> Optional[pulumi.Input[str]]:
        """
        The shared secret for the webhook. [See API documentation](https://developer.github.com/v3/repos/hooks/#create-a-hook).
        """
        return pulumi.get(self, "secret")

    @secret.setter
    def secret(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "secret", value)


@pulumi.input_type
class TeamMembersMemberArgs:
    def __init__(__self__, *,
                 username: pulumi.Input[str],
                 role: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] username: The user to add to the team.
        :param pulumi.Input[str] role: The role of the user within the team.
               Must be one of `member` or `maintainer`. Defaults to `member`.
        """
        pulumi.set(__self__, "username", username)
        if role is not None:
            pulumi.set(__self__, "role", role)

    @property
    @pulumi.getter
    def username(self) -> pulumi.Input[str]:
        """
        The user to add to the team.
        """
        return pulumi.get(self, "username")

    @username.setter
    def username(self, value: pulumi.Input[str]):
        pulumi.set(self, "username", value)

    @property
    @pulumi.getter
    def role(self) -> Optional[pulumi.Input[str]]:
        """
        The role of the user within the team.
        Must be one of `member` or `maintainer`. Defaults to `member`.
        """
        return pulumi.get(self, "role")

    @role.setter
    def role(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "role", value)


@pulumi.input_type
class TeamSyncGroupMappingGroupArgs:
    def __init__(__self__, *,
                 group_description: pulumi.Input[str],
                 group_id: pulumi.Input[str],
                 group_name: pulumi.Input[str]):
        """
        :param pulumi.Input[str] group_description: The description of the IdP group.
        :param pulumi.Input[str] group_id: The ID of the IdP group.
        :param pulumi.Input[str] group_name: The name of the IdP group.
        """
        pulumi.set(__self__, "group_description", group_description)
        pulumi.set(__self__, "group_id", group_id)
        pulumi.set(__self__, "group_name", group_name)

    @property
    @pulumi.getter(name="groupDescription")
    def group_description(self) -> pulumi.Input[str]:
        """
        The description of the IdP group.
        """
        return pulumi.get(self, "group_description")

    @group_description.setter
    def group_description(self, value: pulumi.Input[str]):
        pulumi.set(self, "group_description", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Input[str]:
        """
        The ID of the IdP group.
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="groupName")
    def group_name(self) -> pulumi.Input[str]:
        """
        The name of the IdP group.
        """
        return pulumi.get(self, "group_name")

    @group_name.setter
    def group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "group_name", value)


