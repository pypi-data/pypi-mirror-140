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

__all__ = ['RemoteImageArgs', 'RemoteImage']

@pulumi.input_type
class RemoteImageArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 build: Optional[pulumi.Input['RemoteImageBuildArgs']] = None,
                 force_remove: Optional[pulumi.Input[bool]] = None,
                 keep_locally: Optional[pulumi.Input[bool]] = None,
                 pull_trigger: Optional[pulumi.Input[str]] = None,
                 pull_triggers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a RemoteImage resource.
        :param pulumi.Input[str] name: The name of the Docker image, including any tags or SHA256 repo digests.
        :param pulumi.Input['RemoteImageBuildArgs'] build: Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        :param pulumi.Input[bool] force_remove: If true, then the image is removed forcibly when the resource is destroyed.
        :param pulumi.Input[bool] keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        :param pulumi.Input[str] pull_trigger: A value which cause an image pull when changed
        :param pulumi.Input[Sequence[pulumi.Input[str]]] pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        """
        pulumi.set(__self__, "name", name)
        if build is not None:
            pulumi.set(__self__, "build", build)
        if force_remove is not None:
            pulumi.set(__self__, "force_remove", force_remove)
        if keep_locally is not None:
            pulumi.set(__self__, "keep_locally", keep_locally)
        if pull_trigger is not None:
            warnings.warn("""Use field pull_triggers instead""", DeprecationWarning)
            pulumi.log.warn("""pull_trigger is deprecated: Use field pull_triggers instead""")
        if pull_trigger is not None:
            pulumi.set(__self__, "pull_trigger", pull_trigger)
        if pull_triggers is not None:
            pulumi.set(__self__, "pull_triggers", pull_triggers)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        The name of the Docker image, including any tags or SHA256 repo digests.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def build(self) -> Optional[pulumi.Input['RemoteImageBuildArgs']]:
        """
        Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        """
        return pulumi.get(self, "build")

    @build.setter
    def build(self, value: Optional[pulumi.Input['RemoteImageBuildArgs']]):
        pulumi.set(self, "build", value)

    @property
    @pulumi.getter(name="forceRemove")
    def force_remove(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, then the image is removed forcibly when the resource is destroyed.
        """
        return pulumi.get(self, "force_remove")

    @force_remove.setter
    def force_remove(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "force_remove", value)

    @property
    @pulumi.getter(name="keepLocally")
    def keep_locally(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        """
        return pulumi.get(self, "keep_locally")

    @keep_locally.setter
    def keep_locally(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "keep_locally", value)

    @property
    @pulumi.getter(name="pullTrigger")
    def pull_trigger(self) -> Optional[pulumi.Input[str]]:
        """
        A value which cause an image pull when changed
        """
        return pulumi.get(self, "pull_trigger")

    @pull_trigger.setter
    def pull_trigger(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "pull_trigger", value)

    @property
    @pulumi.getter(name="pullTriggers")
    def pull_triggers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        """
        return pulumi.get(self, "pull_triggers")

    @pull_triggers.setter
    def pull_triggers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "pull_triggers", value)


@pulumi.input_type
class _RemoteImageState:
    def __init__(__self__, *,
                 build: Optional[pulumi.Input['RemoteImageBuildArgs']] = None,
                 force_remove: Optional[pulumi.Input[bool]] = None,
                 keep_locally: Optional[pulumi.Input[bool]] = None,
                 latest: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 output: Optional[pulumi.Input[str]] = None,
                 pull_trigger: Optional[pulumi.Input[str]] = None,
                 pull_triggers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 repo_digest: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering RemoteImage resources.
        :param pulumi.Input['RemoteImageBuildArgs'] build: Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        :param pulumi.Input[bool] force_remove: If true, then the image is removed forcibly when the resource is destroyed.
        :param pulumi.Input[bool] keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        :param pulumi.Input[str] latest: The ID of the image in the form of `sha256:<hash>` image digest. Do not confuse it with the default `latest` tag.
        :param pulumi.Input[str] name: The name of the Docker image, including any tags or SHA256 repo digests.
        :param pulumi.Input[str] pull_trigger: A value which cause an image pull when changed
        :param pulumi.Input[Sequence[pulumi.Input[str]]] pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        :param pulumi.Input[str] repo_digest: The image sha256 digest in the form of `repo[:tag]@sha256:<hash>`.
        """
        if build is not None:
            pulumi.set(__self__, "build", build)
        if force_remove is not None:
            pulumi.set(__self__, "force_remove", force_remove)
        if keep_locally is not None:
            pulumi.set(__self__, "keep_locally", keep_locally)
        if latest is not None:
            warnings.warn("""Use repo_digest instead""", DeprecationWarning)
            pulumi.log.warn("""latest is deprecated: Use repo_digest instead""")
        if latest is not None:
            pulumi.set(__self__, "latest", latest)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if output is not None:
            warnings.warn("""Is unused and will be removed.""", DeprecationWarning)
            pulumi.log.warn("""output is deprecated: Is unused and will be removed.""")
        if output is not None:
            pulumi.set(__self__, "output", output)
        if pull_trigger is not None:
            warnings.warn("""Use field pull_triggers instead""", DeprecationWarning)
            pulumi.log.warn("""pull_trigger is deprecated: Use field pull_triggers instead""")
        if pull_trigger is not None:
            pulumi.set(__self__, "pull_trigger", pull_trigger)
        if pull_triggers is not None:
            pulumi.set(__self__, "pull_triggers", pull_triggers)
        if repo_digest is not None:
            pulumi.set(__self__, "repo_digest", repo_digest)

    @property
    @pulumi.getter
    def build(self) -> Optional[pulumi.Input['RemoteImageBuildArgs']]:
        """
        Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        """
        return pulumi.get(self, "build")

    @build.setter
    def build(self, value: Optional[pulumi.Input['RemoteImageBuildArgs']]):
        pulumi.set(self, "build", value)

    @property
    @pulumi.getter(name="forceRemove")
    def force_remove(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, then the image is removed forcibly when the resource is destroyed.
        """
        return pulumi.get(self, "force_remove")

    @force_remove.setter
    def force_remove(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "force_remove", value)

    @property
    @pulumi.getter(name="keepLocally")
    def keep_locally(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        """
        return pulumi.get(self, "keep_locally")

    @keep_locally.setter
    def keep_locally(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "keep_locally", value)

    @property
    @pulumi.getter
    def latest(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the image in the form of `sha256:<hash>` image digest. Do not confuse it with the default `latest` tag.
        """
        return pulumi.get(self, "latest")

    @latest.setter
    def latest(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "latest", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Docker image, including any tags or SHA256 repo digests.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def output(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "output")

    @output.setter
    def output(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "output", value)

    @property
    @pulumi.getter(name="pullTrigger")
    def pull_trigger(self) -> Optional[pulumi.Input[str]]:
        """
        A value which cause an image pull when changed
        """
        return pulumi.get(self, "pull_trigger")

    @pull_trigger.setter
    def pull_trigger(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "pull_trigger", value)

    @property
    @pulumi.getter(name="pullTriggers")
    def pull_triggers(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        """
        return pulumi.get(self, "pull_triggers")

    @pull_triggers.setter
    def pull_triggers(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "pull_triggers", value)

    @property
    @pulumi.getter(name="repoDigest")
    def repo_digest(self) -> Optional[pulumi.Input[str]]:
        """
        The image sha256 digest in the form of `repo[:tag]@sha256:<hash>`.
        """
        return pulumi.get(self, "repo_digest")

    @repo_digest.setter
    def repo_digest(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repo_digest", value)


class RemoteImage(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 build: Optional[pulumi.Input[pulumi.InputType['RemoteImageBuildArgs']]] = None,
                 force_remove: Optional[pulumi.Input[bool]] = None,
                 keep_locally: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pull_trigger: Optional[pulumi.Input[str]] = None,
                 pull_triggers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        <!-- Bug: Type and Name are switched -->
        Pulls a Docker image to a given Docker host from a Docker Registry.
         This resource will *not* pull new layers of the image automatically unless used in conjunction with RegistryImage data source to update the `pull_triggers` field.

        ## Example Usage
        ### Basic

        Finds and downloads the latest `ubuntu:precise` image but does not check
        for further updates of the image

        ```python
        import pulumi
        import pulumi_docker as docker

        ubuntu = docker.RemoteImage("ubuntu", name="ubuntu:precise")
        ```
        ### Dynamic updates

        To be able to update an image dynamically when the `sha256` sum changes,
        you need to use it in combination with `RegistryImage` as follows:

        ```python
        import pulumi
        import pulumi_docker as docker

        ubuntu_registry_image = docker.get_registry_image(name="ubuntu:precise")
        ubuntu_remote_image = docker.RemoteImage("ubuntuRemoteImage",
            name=ubuntu_registry_image.name,
            pull_triggers=[ubuntu_registry_image.sha256_digest])
        ```
        ### Build

        You can also use the resource to build an image.
        In this case the image "zoo" and "zoo:develop" are built.

        ```python
        import pulumi
        import pulumi_docker as docker

        zoo = docker.RemoteImage("zoo",
            name="zoo",
            build=docker.RemoteImageBuildArgs(
                path=".",
                tags=["zoo:develop"],
                build_arg={
                    "foo": "zoo",
                },
                label={
                    "author": "zoo",
                },
            ))
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['RemoteImageBuildArgs']] build: Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        :param pulumi.Input[bool] force_remove: If true, then the image is removed forcibly when the resource is destroyed.
        :param pulumi.Input[bool] keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        :param pulumi.Input[str] name: The name of the Docker image, including any tags or SHA256 repo digests.
        :param pulumi.Input[str] pull_trigger: A value which cause an image pull when changed
        :param pulumi.Input[Sequence[pulumi.Input[str]]] pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RemoteImageArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        <!-- Bug: Type and Name are switched -->
        Pulls a Docker image to a given Docker host from a Docker Registry.
         This resource will *not* pull new layers of the image automatically unless used in conjunction with RegistryImage data source to update the `pull_triggers` field.

        ## Example Usage
        ### Basic

        Finds and downloads the latest `ubuntu:precise` image but does not check
        for further updates of the image

        ```python
        import pulumi
        import pulumi_docker as docker

        ubuntu = docker.RemoteImage("ubuntu", name="ubuntu:precise")
        ```
        ### Dynamic updates

        To be able to update an image dynamically when the `sha256` sum changes,
        you need to use it in combination with `RegistryImage` as follows:

        ```python
        import pulumi
        import pulumi_docker as docker

        ubuntu_registry_image = docker.get_registry_image(name="ubuntu:precise")
        ubuntu_remote_image = docker.RemoteImage("ubuntuRemoteImage",
            name=ubuntu_registry_image.name,
            pull_triggers=[ubuntu_registry_image.sha256_digest])
        ```
        ### Build

        You can also use the resource to build an image.
        In this case the image "zoo" and "zoo:develop" are built.

        ```python
        import pulumi
        import pulumi_docker as docker

        zoo = docker.RemoteImage("zoo",
            name="zoo",
            build=docker.RemoteImageBuildArgs(
                path=".",
                tags=["zoo:develop"],
                build_arg={
                    "foo": "zoo",
                },
                label={
                    "author": "zoo",
                },
            ))
        ```

        :param str resource_name: The name of the resource.
        :param RemoteImageArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RemoteImageArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 build: Optional[pulumi.Input[pulumi.InputType['RemoteImageBuildArgs']]] = None,
                 force_remove: Optional[pulumi.Input[bool]] = None,
                 keep_locally: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pull_trigger: Optional[pulumi.Input[str]] = None,
                 pull_triggers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
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
            __props__ = RemoteImageArgs.__new__(RemoteImageArgs)

            __props__.__dict__["build"] = build
            __props__.__dict__["force_remove"] = force_remove
            __props__.__dict__["keep_locally"] = keep_locally
            if name is None and not opts.urn:
                raise TypeError("Missing required property 'name'")
            __props__.__dict__["name"] = name
            if pull_trigger is not None and not opts.urn:
                warnings.warn("""Use field pull_triggers instead""", DeprecationWarning)
                pulumi.log.warn("""pull_trigger is deprecated: Use field pull_triggers instead""")
            __props__.__dict__["pull_trigger"] = pull_trigger
            __props__.__dict__["pull_triggers"] = pull_triggers
            __props__.__dict__["latest"] = None
            __props__.__dict__["output"] = None
            __props__.__dict__["repo_digest"] = None
        super(RemoteImage, __self__).__init__(
            'docker:index/remoteImage:RemoteImage',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            build: Optional[pulumi.Input[pulumi.InputType['RemoteImageBuildArgs']]] = None,
            force_remove: Optional[pulumi.Input[bool]] = None,
            keep_locally: Optional[pulumi.Input[bool]] = None,
            latest: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            output: Optional[pulumi.Input[str]] = None,
            pull_trigger: Optional[pulumi.Input[str]] = None,
            pull_triggers: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            repo_digest: Optional[pulumi.Input[str]] = None) -> 'RemoteImage':
        """
        Get an existing RemoteImage resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['RemoteImageBuildArgs']] build: Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        :param pulumi.Input[bool] force_remove: If true, then the image is removed forcibly when the resource is destroyed.
        :param pulumi.Input[bool] keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        :param pulumi.Input[str] latest: The ID of the image in the form of `sha256:<hash>` image digest. Do not confuse it with the default `latest` tag.
        :param pulumi.Input[str] name: The name of the Docker image, including any tags or SHA256 repo digests.
        :param pulumi.Input[str] pull_trigger: A value which cause an image pull when changed
        :param pulumi.Input[Sequence[pulumi.Input[str]]] pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        :param pulumi.Input[str] repo_digest: The image sha256 digest in the form of `repo[:tag]@sha256:<hash>`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RemoteImageState.__new__(_RemoteImageState)

        __props__.__dict__["build"] = build
        __props__.__dict__["force_remove"] = force_remove
        __props__.__dict__["keep_locally"] = keep_locally
        __props__.__dict__["latest"] = latest
        __props__.__dict__["name"] = name
        __props__.__dict__["output"] = output
        __props__.__dict__["pull_trigger"] = pull_trigger
        __props__.__dict__["pull_triggers"] = pull_triggers
        __props__.__dict__["repo_digest"] = repo_digest
        return RemoteImage(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def build(self) -> pulumi.Output[Optional['outputs.RemoteImageBuild']]:
        """
        Configuration to build an image. Please see [docker build command reference](https://docs.docker.com/engine/reference/commandline/build/#options) too.
        """
        return pulumi.get(self, "build")

    @property
    @pulumi.getter(name="forceRemove")
    def force_remove(self) -> pulumi.Output[Optional[bool]]:
        """
        If true, then the image is removed forcibly when the resource is destroyed.
        """
        return pulumi.get(self, "force_remove")

    @property
    @pulumi.getter(name="keepLocally")
    def keep_locally(self) -> pulumi.Output[Optional[bool]]:
        """
        If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation.
        """
        return pulumi.get(self, "keep_locally")

    @property
    @pulumi.getter
    def latest(self) -> pulumi.Output[str]:
        """
        The ID of the image in the form of `sha256:<hash>` image digest. Do not confuse it with the default `latest` tag.
        """
        return pulumi.get(self, "latest")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the Docker image, including any tags or SHA256 repo digests.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def output(self) -> pulumi.Output[str]:
        return pulumi.get(self, "output")

    @property
    @pulumi.getter(name="pullTrigger")
    def pull_trigger(self) -> pulumi.Output[Optional[str]]:
        """
        A value which cause an image pull when changed
        """
        return pulumi.get(self, "pull_trigger")

    @property
    @pulumi.getter(name="pullTriggers")
    def pull_triggers(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the docker*registry*image.
        """
        return pulumi.get(self, "pull_triggers")

    @property
    @pulumi.getter(name="repoDigest")
    def repo_digest(self) -> pulumi.Output[str]:
        """
        The image sha256 digest in the form of `repo[:tag]@sha256:<hash>`.
        """
        return pulumi.get(self, "repo_digest")

