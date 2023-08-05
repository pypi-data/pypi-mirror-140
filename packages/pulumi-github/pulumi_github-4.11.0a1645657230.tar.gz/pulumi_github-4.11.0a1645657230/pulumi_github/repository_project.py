# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['RepositoryProjectArgs', 'RepositoryProject']

@pulumi.input_type
class RepositoryProjectArgs:
    def __init__(__self__, *,
                 repository: pulumi.Input[str],
                 body: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a RepositoryProject resource.
        :param pulumi.Input[str] repository: The repository of the project.
        :param pulumi.Input[str] body: The body of the project.
        :param pulumi.Input[str] name: The name of the project.
        """
        pulumi.set(__self__, "repository", repository)
        if body is not None:
            pulumi.set(__self__, "body", body)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def repository(self) -> pulumi.Input[str]:
        """
        The repository of the project.
        """
        return pulumi.get(self, "repository")

    @repository.setter
    def repository(self, value: pulumi.Input[str]):
        pulumi.set(self, "repository", value)

    @property
    @pulumi.getter
    def body(self) -> Optional[pulumi.Input[str]]:
        """
        The body of the project.
        """
        return pulumi.get(self, "body")

    @body.setter
    def body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "body", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the project.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class _RepositoryProjectState:
    def __init__(__self__, *,
                 body: Optional[pulumi.Input[str]] = None,
                 etag: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 repository: Optional[pulumi.Input[str]] = None,
                 url: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering RepositoryProject resources.
        :param pulumi.Input[str] body: The body of the project.
        :param pulumi.Input[str] name: The name of the project.
        :param pulumi.Input[str] repository: The repository of the project.
        :param pulumi.Input[str] url: URL of the project
        """
        if body is not None:
            pulumi.set(__self__, "body", body)
        if etag is not None:
            pulumi.set(__self__, "etag", etag)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if repository is not None:
            pulumi.set(__self__, "repository", repository)
        if url is not None:
            pulumi.set(__self__, "url", url)

    @property
    @pulumi.getter
    def body(self) -> Optional[pulumi.Input[str]]:
        """
        The body of the project.
        """
        return pulumi.get(self, "body")

    @body.setter
    def body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "body", value)

    @property
    @pulumi.getter
    def etag(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "etag")

    @etag.setter
    def etag(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "etag", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the project.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def repository(self) -> Optional[pulumi.Input[str]]:
        """
        The repository of the project.
        """
        return pulumi.get(self, "repository")

    @repository.setter
    def repository(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repository", value)

    @property
    @pulumi.getter
    def url(self) -> Optional[pulumi.Input[str]]:
        """
        URL of the project
        """
        return pulumi.get(self, "url")

    @url.setter
    def url(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "url", value)


class RepositoryProject(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 body: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 repository: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        This resource allows you to create and manage projects for GitHub repository.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        example = github.Repository("example",
            description="My awesome codebase",
            has_projects=True)
        project = github.RepositoryProject("project",
            body="This is a repository project.",
            repository=example.name)
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] body: The body of the project.
        :param pulumi.Input[str] name: The name of the project.
        :param pulumi.Input[str] repository: The repository of the project.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RepositoryProjectArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        This resource allows you to create and manage projects for GitHub repository.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_github as github

        example = github.Repository("example",
            description="My awesome codebase",
            has_projects=True)
        project = github.RepositoryProject("project",
            body="This is a repository project.",
            repository=example.name)
        ```

        :param str resource_name: The name of the resource.
        :param RepositoryProjectArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RepositoryProjectArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 body: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 repository: Optional[pulumi.Input[str]] = None,
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
            __props__ = RepositoryProjectArgs.__new__(RepositoryProjectArgs)

            __props__.__dict__["body"] = body
            __props__.__dict__["name"] = name
            if repository is None and not opts.urn:
                raise TypeError("Missing required property 'repository'")
            __props__.__dict__["repository"] = repository
            __props__.__dict__["etag"] = None
            __props__.__dict__["url"] = None
        super(RepositoryProject, __self__).__init__(
            'github:index/repositoryProject:RepositoryProject',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            body: Optional[pulumi.Input[str]] = None,
            etag: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            repository: Optional[pulumi.Input[str]] = None,
            url: Optional[pulumi.Input[str]] = None) -> 'RepositoryProject':
        """
        Get an existing RepositoryProject resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] body: The body of the project.
        :param pulumi.Input[str] name: The name of the project.
        :param pulumi.Input[str] repository: The repository of the project.
        :param pulumi.Input[str] url: URL of the project
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RepositoryProjectState.__new__(_RepositoryProjectState)

        __props__.__dict__["body"] = body
        __props__.__dict__["etag"] = etag
        __props__.__dict__["name"] = name
        __props__.__dict__["repository"] = repository
        __props__.__dict__["url"] = url
        return RepositoryProject(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def body(self) -> pulumi.Output[Optional[str]]:
        """
        The body of the project.
        """
        return pulumi.get(self, "body")

    @property
    @pulumi.getter
    def etag(self) -> pulumi.Output[str]:
        return pulumi.get(self, "etag")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the project.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def repository(self) -> pulumi.Output[str]:
        """
        The repository of the project.
        """
        return pulumi.get(self, "repository")

    @property
    @pulumi.getter
    def url(self) -> pulumi.Output[str]:
        """
        URL of the project
        """
        return pulumi.get(self, "url")

