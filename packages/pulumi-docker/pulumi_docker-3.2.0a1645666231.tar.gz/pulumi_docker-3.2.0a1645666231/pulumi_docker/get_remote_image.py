# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetRemoteImageResult',
    'AwaitableGetRemoteImageResult',
    'get_remote_image',
    'get_remote_image_output',
]

@pulumi.output_type
class GetRemoteImageResult:
    """
    A collection of values returned by getRemoteImage.
    """
    def __init__(__self__, id=None, name=None, repo_digest=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if repo_digest and not isinstance(repo_digest, str):
            raise TypeError("Expected argument 'repo_digest' to be a str")
        pulumi.set(__self__, "repo_digest", repo_digest)

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The name of the Docker image, including any tags or SHA256 repo digests.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="repoDigest")
    def repo_digest(self) -> str:
        """
        The image sha256 digest in the form of `repo[:tag]@sha256:<hash>`. It may be empty in the edge case where the local image was pulled from a repo, tagged locally, and then referred to in the data source by that local name/tag.
        """
        return pulumi.get(self, "repo_digest")


class AwaitableGetRemoteImageResult(GetRemoteImageResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetRemoteImageResult(
            id=self.id,
            name=self.name,
            repo_digest=self.repo_digest)


def get_remote_image(name: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetRemoteImageResult:
    """
    `RemoteImage` provides details about a specific Docker Image which need to be presend on the Docker Host

    ## Example Usage

    ```python
    import pulumi
    import pulumi_docker as docker

    latest = docker.get_remote_image(name="nginx")
    specific = docker.get_remote_image(name="nginx:1.17.6")
    digest = docker.get_remote_image(name="nginx@sha256:36b74457bccb56fbf8b05f79c85569501b721d4db813b684391d63e02287c0b2")
    tag_and_digest = docker.get_remote_image(name="nginx:1.19.1@sha256:36b74457bccb56fbf8b05f79c85569501b721d4db813b684391d63e02287c0b2")
    ```


    :param str name: The name of the Docker image, including any tags or SHA256 repo digests.
    """
    __args__ = dict()
    __args__['name'] = name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('docker:index/getRemoteImage:getRemoteImage', __args__, opts=opts, typ=GetRemoteImageResult).value

    return AwaitableGetRemoteImageResult(
        id=__ret__.id,
        name=__ret__.name,
        repo_digest=__ret__.repo_digest)


@_utilities.lift_output_func(get_remote_image)
def get_remote_image_output(name: Optional[pulumi.Input[str]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetRemoteImageResult]:
    """
    `RemoteImage` provides details about a specific Docker Image which need to be presend on the Docker Host

    ## Example Usage

    ```python
    import pulumi
    import pulumi_docker as docker

    latest = docker.get_remote_image(name="nginx")
    specific = docker.get_remote_image(name="nginx:1.17.6")
    digest = docker.get_remote_image(name="nginx@sha256:36b74457bccb56fbf8b05f79c85569501b721d4db813b684391d63e02287c0b2")
    tag_and_digest = docker.get_remote_image(name="nginx:1.19.1@sha256:36b74457bccb56fbf8b05f79c85569501b721d4db813b684391d63e02287c0b2")
    ```


    :param str name: The name of the Docker image, including any tags or SHA256 repo digests.
    """
    ...
