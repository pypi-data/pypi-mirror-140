# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['SentinelPolicyArgs', 'SentinelPolicy']

@pulumi.input_type
class SentinelPolicyArgs:
    def __init__(__self__, *,
                 enforcement_level: pulumi.Input[str],
                 policy: pulumi.Input[str],
                 scope: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a SentinelPolicy resource.
        :param pulumi.Input[str] enforcement_level: `(strings: <required>)` - The [enforcement level][enforcement-level]
               for this policy.
        :param pulumi.Input[str] policy: `(string: <required>)` - The contents of the policy to register.
        :param pulumi.Input[str] scope: `(strings: <required>)` - The [scope][scope] for this policy.
        :param pulumi.Input[str] description: `(string: "")` - A description of the policy.
        :param pulumi.Input[str] name: `(string: <required>)` - A unique name for the policy.
        """
        pulumi.set(__self__, "enforcement_level", enforcement_level)
        pulumi.set(__self__, "policy", policy)
        pulumi.set(__self__, "scope", scope)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="enforcementLevel")
    def enforcement_level(self) -> pulumi.Input[str]:
        """
        `(strings: <required>)` - The [enforcement level][enforcement-level]
        for this policy.
        """
        return pulumi.get(self, "enforcement_level")

    @enforcement_level.setter
    def enforcement_level(self, value: pulumi.Input[str]):
        pulumi.set(self, "enforcement_level", value)

    @property
    @pulumi.getter
    def policy(self) -> pulumi.Input[str]:
        """
        `(string: <required>)` - The contents of the policy to register.
        """
        return pulumi.get(self, "policy")

    @policy.setter
    def policy(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy", value)

    @property
    @pulumi.getter
    def scope(self) -> pulumi.Input[str]:
        """
        `(strings: <required>)` - The [scope][scope] for this policy.
        """
        return pulumi.get(self, "scope")

    @scope.setter
    def scope(self, value: pulumi.Input[str]):
        pulumi.set(self, "scope", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        `(string: "")` - A description of the policy.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        `(string: <required>)` - A unique name for the policy.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class _SentinelPolicyState:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 enforcement_level: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy: Optional[pulumi.Input[str]] = None,
                 scope: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering SentinelPolicy resources.
        :param pulumi.Input[str] description: `(string: "")` - A description of the policy.
        :param pulumi.Input[str] enforcement_level: `(strings: <required>)` - The [enforcement level][enforcement-level]
               for this policy.
        :param pulumi.Input[str] name: `(string: <required>)` - A unique name for the policy.
        :param pulumi.Input[str] policy: `(string: <required>)` - The contents of the policy to register.
        :param pulumi.Input[str] scope: `(strings: <required>)` - The [scope][scope] for this policy.
        """
        if description is not None:
            pulumi.set(__self__, "description", description)
        if enforcement_level is not None:
            pulumi.set(__self__, "enforcement_level", enforcement_level)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if policy is not None:
            pulumi.set(__self__, "policy", policy)
        if scope is not None:
            pulumi.set(__self__, "scope", scope)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        `(string: "")` - A description of the policy.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="enforcementLevel")
    def enforcement_level(self) -> Optional[pulumi.Input[str]]:
        """
        `(strings: <required>)` - The [enforcement level][enforcement-level]
        for this policy.
        """
        return pulumi.get(self, "enforcement_level")

    @enforcement_level.setter
    def enforcement_level(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "enforcement_level", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        `(string: <required>)` - A unique name for the policy.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def policy(self) -> Optional[pulumi.Input[str]]:
        """
        `(string: <required>)` - The contents of the policy to register.
        """
        return pulumi.get(self, "policy")

    @policy.setter
    def policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy", value)

    @property
    @pulumi.getter
    def scope(self) -> Optional[pulumi.Input[str]]:
        """
        `(strings: <required>)` - The [scope][scope] for this policy.
        """
        return pulumi.get(self, "scope")

    @scope.setter
    def scope(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "scope", value)


class SentinelPolicy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enforcement_level: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy: Optional[pulumi.Input[str]] = None,
                 scope: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages a Sentinel policy registered in Nomad.

        > **Enterprise Only!** This API endpoint and functionality only exists in
           Nomad Enterprise. This is not present in the open source version of Nomad.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_nomad as nomad

        exec_only = nomad.SentinelPolicy("exec-only",
            description="Only allow jobs that are based on an exec driver.",
            enforcement_level="soft-mandatory",
            policy=\"\"\"main = rule { all_drivers_exec }

        # all_drivers_exec checks that all the drivers in use are exec
        all_drivers_exec = rule {
            all job.task_groups as tg {
                all tg.tasks as task {
                    task.driver is "exec"
                }
            }
        }

        \"\"\",
            scope="submit-job")
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: `(string: "")` - A description of the policy.
        :param pulumi.Input[str] enforcement_level: `(strings: <required>)` - The [enforcement level][enforcement-level]
               for this policy.
        :param pulumi.Input[str] name: `(string: <required>)` - A unique name for the policy.
        :param pulumi.Input[str] policy: `(string: <required>)` - The contents of the policy to register.
        :param pulumi.Input[str] scope: `(strings: <required>)` - The [scope][scope] for this policy.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SentinelPolicyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages a Sentinel policy registered in Nomad.

        > **Enterprise Only!** This API endpoint and functionality only exists in
           Nomad Enterprise. This is not present in the open source version of Nomad.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_nomad as nomad

        exec_only = nomad.SentinelPolicy("exec-only",
            description="Only allow jobs that are based on an exec driver.",
            enforcement_level="soft-mandatory",
            policy=\"\"\"main = rule { all_drivers_exec }

        # all_drivers_exec checks that all the drivers in use are exec
        all_drivers_exec = rule {
            all job.task_groups as tg {
                all tg.tasks as task {
                    task.driver is "exec"
                }
            }
        }

        \"\"\",
            scope="submit-job")
        ```

        :param str resource_name: The name of the resource.
        :param SentinelPolicyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SentinelPolicyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enforcement_level: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 policy: Optional[pulumi.Input[str]] = None,
                 scope: Optional[pulumi.Input[str]] = None,
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
            __props__ = SentinelPolicyArgs.__new__(SentinelPolicyArgs)

            __props__.__dict__["description"] = description
            if enforcement_level is None and not opts.urn:
                raise TypeError("Missing required property 'enforcement_level'")
            __props__.__dict__["enforcement_level"] = enforcement_level
            __props__.__dict__["name"] = name
            if policy is None and not opts.urn:
                raise TypeError("Missing required property 'policy'")
            __props__.__dict__["policy"] = policy
            if scope is None and not opts.urn:
                raise TypeError("Missing required property 'scope'")
            __props__.__dict__["scope"] = scope
        super(SentinelPolicy, __self__).__init__(
            'nomad:index/sentinelPolicy:SentinelPolicy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            description: Optional[pulumi.Input[str]] = None,
            enforcement_level: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            policy: Optional[pulumi.Input[str]] = None,
            scope: Optional[pulumi.Input[str]] = None) -> 'SentinelPolicy':
        """
        Get an existing SentinelPolicy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: `(string: "")` - A description of the policy.
        :param pulumi.Input[str] enforcement_level: `(strings: <required>)` - The [enforcement level][enforcement-level]
               for this policy.
        :param pulumi.Input[str] name: `(string: <required>)` - A unique name for the policy.
        :param pulumi.Input[str] policy: `(string: <required>)` - The contents of the policy to register.
        :param pulumi.Input[str] scope: `(strings: <required>)` - The [scope][scope] for this policy.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SentinelPolicyState.__new__(_SentinelPolicyState)

        __props__.__dict__["description"] = description
        __props__.__dict__["enforcement_level"] = enforcement_level
        __props__.__dict__["name"] = name
        __props__.__dict__["policy"] = policy
        __props__.__dict__["scope"] = scope
        return SentinelPolicy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        `(string: "")` - A description of the policy.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="enforcementLevel")
    def enforcement_level(self) -> pulumi.Output[str]:
        """
        `(strings: <required>)` - The [enforcement level][enforcement-level]
        for this policy.
        """
        return pulumi.get(self, "enforcement_level")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        `(string: <required>)` - A unique name for the policy.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def policy(self) -> pulumi.Output[str]:
        """
        `(string: <required>)` - The contents of the policy to register.
        """
        return pulumi.get(self, "policy")

    @property
    @pulumi.getter
    def scope(self) -> pulumi.Output[str]:
        """
        `(strings: <required>)` - The [scope][scope] for this policy.
        """
        return pulumi.get(self, "scope")

