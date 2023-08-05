# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetRepositoryMilestoneResult',
    'AwaitableGetRepositoryMilestoneResult',
    'get_repository_milestone',
    'get_repository_milestone_output',
]

@pulumi.output_type
class GetRepositoryMilestoneResult:
    """
    A collection of values returned by getRepositoryMilestone.
    """
    def __init__(__self__, description=None, due_date=None, id=None, number=None, owner=None, repository=None, state=None, title=None):
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if due_date and not isinstance(due_date, str):
            raise TypeError("Expected argument 'due_date' to be a str")
        pulumi.set(__self__, "due_date", due_date)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if number and not isinstance(number, int):
            raise TypeError("Expected argument 'number' to be a int")
        pulumi.set(__self__, "number", number)
        if owner and not isinstance(owner, str):
            raise TypeError("Expected argument 'owner' to be a str")
        pulumi.set(__self__, "owner", owner)
        if repository and not isinstance(repository, str):
            raise TypeError("Expected argument 'repository' to be a str")
        pulumi.set(__self__, "repository", repository)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if title and not isinstance(title, str):
            raise TypeError("Expected argument 'title' to be a str")
        pulumi.set(__self__, "title", title)

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Description of the milestone.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="dueDate")
    def due_date(self) -> str:
        """
        The milestone due date (in ISO-8601 `yyyy-mm-dd` format).
        """
        return pulumi.get(self, "due_date")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def number(self) -> int:
        return pulumi.get(self, "number")

    @property
    @pulumi.getter
    def owner(self) -> str:
        return pulumi.get(self, "owner")

    @property
    @pulumi.getter
    def repository(self) -> str:
        return pulumi.get(self, "repository")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        State of the milestone.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def title(self) -> str:
        """
        Title of the milestone.
        """
        return pulumi.get(self, "title")


class AwaitableGetRepositoryMilestoneResult(GetRepositoryMilestoneResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRepositoryMilestoneResult(
            description=self.description,
            due_date=self.due_date,
            id=self.id,
            number=self.number,
            owner=self.owner,
            repository=self.repository,
            state=self.state,
            title=self.title)


def get_repository_milestone(number: Optional[int] = None,
                             owner: Optional[str] = None,
                             repository: Optional[str] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRepositoryMilestoneResult:
    """
    Use this data source to retrieve information about a specific GitHub milestone in a repository.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_github as github

    example = github.get_repository_milestone(number=1,
        owner="example-owner",
        repository="example-repository")
    ```


    :param int number: The number of the milestone.
    :param str owner: Owner of the repository.
    :param str repository: Name of the repository to retrieve the milestone from.
    """
    __args__ = dict()
    __args__['number'] = number
    __args__['owner'] = owner
    __args__['repository'] = repository
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('github:index/getRepositoryMilestone:getRepositoryMilestone', __args__, opts=opts, typ=GetRepositoryMilestoneResult).value

    return AwaitableGetRepositoryMilestoneResult(
        description=__ret__.description,
        due_date=__ret__.due_date,
        id=__ret__.id,
        number=__ret__.number,
        owner=__ret__.owner,
        repository=__ret__.repository,
        state=__ret__.state,
        title=__ret__.title)


@_utilities.lift_output_func(get_repository_milestone)
def get_repository_milestone_output(number: Optional[pulumi.Input[int]] = None,
                                    owner: Optional[pulumi.Input[str]] = None,
                                    repository: Optional[pulumi.Input[str]] = None,
                                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRepositoryMilestoneResult]:
    """
    Use this data source to retrieve information about a specific GitHub milestone in a repository.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_github as github

    example = github.get_repository_milestone(number=1,
        owner="example-owner",
        repository="example-repository")
    ```


    :param int number: The number of the milestone.
    :param str owner: Owner of the repository.
    :param str repository: Name of the repository to retrieve the milestone from.
    """
    ...
