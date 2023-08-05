# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = ['WafOverrideArgs', 'WafOverride']

@pulumi.input_type
class WafOverrideArgs:
    def __init__(__self__, *,
                 urls: pulumi.Input[Sequence[pulumi.Input[str]]],
                 zone_id: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 groups: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 paused: Optional[pulumi.Input[bool]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 rewrite_action: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rules: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a WafOverride resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] urls: An array of URLs to apply the WAF override to.
        :param pulumi.Input[str] zone_id: The DNS zone to which the WAF override condition should be added.
        :param pulumi.Input[str] description: Description of what the WAF override does.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] groups: Similar to `rules`; which WAF groups you want to alter.
        :param pulumi.Input[bool] paused: Whether this package is currently paused.
        :param pulumi.Input[int] priority: Relative priority of this configuration when multiple configurations match a single URL.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rewrite_action: When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rules: A list of WAF rule ID to rule action you intend to apply.
        """
        pulumi.set(__self__, "urls", urls)
        pulumi.set(__self__, "zone_id", zone_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if groups is not None:
            pulumi.set(__self__, "groups", groups)
        if paused is not None:
            pulumi.set(__self__, "paused", paused)
        if priority is not None:
            pulumi.set(__self__, "priority", priority)
        if rewrite_action is not None:
            pulumi.set(__self__, "rewrite_action", rewrite_action)
        if rules is not None:
            pulumi.set(__self__, "rules", rules)

    @property
    @pulumi.getter
    def urls(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        An array of URLs to apply the WAF override to.
        """
        return pulumi.get(self, "urls")

    @urls.setter
    def urls(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "urls", value)

    @property
    @pulumi.getter(name="zoneId")
    def zone_id(self) -> pulumi.Input[str]:
        """
        The DNS zone to which the WAF override condition should be added.
        """
        return pulumi.get(self, "zone_id")

    @zone_id.setter
    def zone_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "zone_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of what the WAF override does.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def groups(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Similar to `rules`; which WAF groups you want to alter.
        """
        return pulumi.get(self, "groups")

    @groups.setter
    def groups(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "groups", value)

    @property
    @pulumi.getter
    def paused(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether this package is currently paused.
        """
        return pulumi.get(self, "paused")

    @paused.setter
    def paused(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "paused", value)

    @property
    @pulumi.getter
    def priority(self) -> Optional[pulumi.Input[int]]:
        """
        Relative priority of this configuration when multiple configurations match a single URL.
        """
        return pulumi.get(self, "priority")

    @priority.setter
    def priority(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "priority", value)

    @property
    @pulumi.getter(name="rewriteAction")
    def rewrite_action(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        """
        return pulumi.get(self, "rewrite_action")

    @rewrite_action.setter
    def rewrite_action(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "rewrite_action", value)

    @property
    @pulumi.getter
    def rules(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A list of WAF rule ID to rule action you intend to apply.
        """
        return pulumi.get(self, "rules")

    @rules.setter
    def rules(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "rules", value)


@pulumi.input_type
class _WafOverrideState:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 groups: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 override_id: Optional[pulumi.Input[str]] = None,
                 paused: Optional[pulumi.Input[bool]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 rewrite_action: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rules: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 urls: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 zone_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering WafOverride resources.
        :param pulumi.Input[str] description: Description of what the WAF override does.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] groups: Similar to `rules`; which WAF groups you want to alter.
        :param pulumi.Input[bool] paused: Whether this package is currently paused.
        :param pulumi.Input[int] priority: Relative priority of this configuration when multiple configurations match a single URL.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rewrite_action: When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rules: A list of WAF rule ID to rule action you intend to apply.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] urls: An array of URLs to apply the WAF override to.
        :param pulumi.Input[str] zone_id: The DNS zone to which the WAF override condition should be added.
        """
        if description is not None:
            pulumi.set(__self__, "description", description)
        if groups is not None:
            pulumi.set(__self__, "groups", groups)
        if override_id is not None:
            pulumi.set(__self__, "override_id", override_id)
        if paused is not None:
            pulumi.set(__self__, "paused", paused)
        if priority is not None:
            pulumi.set(__self__, "priority", priority)
        if rewrite_action is not None:
            pulumi.set(__self__, "rewrite_action", rewrite_action)
        if rules is not None:
            pulumi.set(__self__, "rules", rules)
        if urls is not None:
            pulumi.set(__self__, "urls", urls)
        if zone_id is not None:
            pulumi.set(__self__, "zone_id", zone_id)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of what the WAF override does.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def groups(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Similar to `rules`; which WAF groups you want to alter.
        """
        return pulumi.get(self, "groups")

    @groups.setter
    def groups(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "groups", value)

    @property
    @pulumi.getter(name="overrideId")
    def override_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "override_id")

    @override_id.setter
    def override_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "override_id", value)

    @property
    @pulumi.getter
    def paused(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether this package is currently paused.
        """
        return pulumi.get(self, "paused")

    @paused.setter
    def paused(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "paused", value)

    @property
    @pulumi.getter
    def priority(self) -> Optional[pulumi.Input[int]]:
        """
        Relative priority of this configuration when multiple configurations match a single URL.
        """
        return pulumi.get(self, "priority")

    @priority.setter
    def priority(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "priority", value)

    @property
    @pulumi.getter(name="rewriteAction")
    def rewrite_action(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        """
        return pulumi.get(self, "rewrite_action")

    @rewrite_action.setter
    def rewrite_action(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "rewrite_action", value)

    @property
    @pulumi.getter
    def rules(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A list of WAF rule ID to rule action you intend to apply.
        """
        return pulumi.get(self, "rules")

    @rules.setter
    def rules(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "rules", value)

    @property
    @pulumi.getter
    def urls(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        An array of URLs to apply the WAF override to.
        """
        return pulumi.get(self, "urls")

    @urls.setter
    def urls(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "urls", value)

    @property
    @pulumi.getter(name="zoneId")
    def zone_id(self) -> Optional[pulumi.Input[str]]:
        """
        The DNS zone to which the WAF override condition should be added.
        """
        return pulumi.get(self, "zone_id")

    @zone_id.setter
    def zone_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zone_id", value)


class WafOverride(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 groups: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 paused: Optional[pulumi.Input[bool]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 rewrite_action: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rules: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 urls: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 zone_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a Cloudflare WAF override resource. This enables the ability to toggle
        WAF rules and groups on or off based on URIs.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_cloudflare as cloudflare

        shop_ecxample = cloudflare.WafOverride("shopEcxample",
            zone_id="1d5fdc9e88c8a8c4518b068cd94331fe",
            urls=[
                "example.com/no-waf-here",
                "example.com/another/path/*",
            ],
            rules={
                "100015": "disable",
            },
            groups={
                "ea8687e59929c1fd05ba97574ad43f77": "default",
            },
            rewrite_action={
                "default": "block",
                "challenge": "block",
            })
        ```

        ## Import

        WAF Overrides can be imported using a composite ID formed of zone ID and override ID.

        ```sh
         $ pulumi import cloudflare:index/wafOverride:WafOverride my_example_waf_override 3abe5b950053dbddf1516d89f9ef1e8a/9d4e66d7649c178663bf62e06dbacb23
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: Description of what the WAF override does.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] groups: Similar to `rules`; which WAF groups you want to alter.
        :param pulumi.Input[bool] paused: Whether this package is currently paused.
        :param pulumi.Input[int] priority: Relative priority of this configuration when multiple configurations match a single URL.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rewrite_action: When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rules: A list of WAF rule ID to rule action you intend to apply.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] urls: An array of URLs to apply the WAF override to.
        :param pulumi.Input[str] zone_id: The DNS zone to which the WAF override condition should be added.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: WafOverrideArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Cloudflare WAF override resource. This enables the ability to toggle
        WAF rules and groups on or off based on URIs.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_cloudflare as cloudflare

        shop_ecxample = cloudflare.WafOverride("shopEcxample",
            zone_id="1d5fdc9e88c8a8c4518b068cd94331fe",
            urls=[
                "example.com/no-waf-here",
                "example.com/another/path/*",
            ],
            rules={
                "100015": "disable",
            },
            groups={
                "ea8687e59929c1fd05ba97574ad43f77": "default",
            },
            rewrite_action={
                "default": "block",
                "challenge": "block",
            })
        ```

        ## Import

        WAF Overrides can be imported using a composite ID formed of zone ID and override ID.

        ```sh
         $ pulumi import cloudflare:index/wafOverride:WafOverride my_example_waf_override 3abe5b950053dbddf1516d89f9ef1e8a/9d4e66d7649c178663bf62e06dbacb23
        ```

        :param str resource_name: The name of the resource.
        :param WafOverrideArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(WafOverrideArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 groups: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 paused: Optional[pulumi.Input[bool]] = None,
                 priority: Optional[pulumi.Input[int]] = None,
                 rewrite_action: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 rules: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 urls: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 zone_id: Optional[pulumi.Input[str]] = None,
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
            __props__ = WafOverrideArgs.__new__(WafOverrideArgs)

            __props__.__dict__["description"] = description
            __props__.__dict__["groups"] = groups
            __props__.__dict__["paused"] = paused
            __props__.__dict__["priority"] = priority
            __props__.__dict__["rewrite_action"] = rewrite_action
            __props__.__dict__["rules"] = rules
            if urls is None and not opts.urn:
                raise TypeError("Missing required property 'urls'")
            __props__.__dict__["urls"] = urls
            if zone_id is None and not opts.urn:
                raise TypeError("Missing required property 'zone_id'")
            __props__.__dict__["zone_id"] = zone_id
            __props__.__dict__["override_id"] = None
        super(WafOverride, __self__).__init__(
            'cloudflare:index/wafOverride:WafOverride',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            description: Optional[pulumi.Input[str]] = None,
            groups: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            override_id: Optional[pulumi.Input[str]] = None,
            paused: Optional[pulumi.Input[bool]] = None,
            priority: Optional[pulumi.Input[int]] = None,
            rewrite_action: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            rules: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            urls: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            zone_id: Optional[pulumi.Input[str]] = None) -> 'WafOverride':
        """
        Get an existing WafOverride resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: Description of what the WAF override does.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] groups: Similar to `rules`; which WAF groups you want to alter.
        :param pulumi.Input[bool] paused: Whether this package is currently paused.
        :param pulumi.Input[int] priority: Relative priority of this configuration when multiple configurations match a single URL.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rewrite_action: When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] rules: A list of WAF rule ID to rule action you intend to apply.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] urls: An array of URLs to apply the WAF override to.
        :param pulumi.Input[str] zone_id: The DNS zone to which the WAF override condition should be added.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _WafOverrideState.__new__(_WafOverrideState)

        __props__.__dict__["description"] = description
        __props__.__dict__["groups"] = groups
        __props__.__dict__["override_id"] = override_id
        __props__.__dict__["paused"] = paused
        __props__.__dict__["priority"] = priority
        __props__.__dict__["rewrite_action"] = rewrite_action
        __props__.__dict__["rules"] = rules
        __props__.__dict__["urls"] = urls
        __props__.__dict__["zone_id"] = zone_id
        return WafOverride(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        Description of what the WAF override does.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def groups(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Similar to `rules`; which WAF groups you want to alter.
        """
        return pulumi.get(self, "groups")

    @property
    @pulumi.getter(name="overrideId")
    def override_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "override_id")

    @property
    @pulumi.getter
    def paused(self) -> pulumi.Output[Optional[bool]]:
        """
        Whether this package is currently paused.
        """
        return pulumi.get(self, "paused")

    @property
    @pulumi.getter
    def priority(self) -> pulumi.Output[Optional[int]]:
        """
        Relative priority of this configuration when multiple configurations match a single URL.
        """
        return pulumi.get(self, "priority")

    @property
    @pulumi.getter(name="rewriteAction")
    def rewrite_action(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        When a WAF rule matches, substitute its configured action for a different action specified by this definition.
        """
        return pulumi.get(self, "rewrite_action")

    @property
    @pulumi.getter
    def rules(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A list of WAF rule ID to rule action you intend to apply.
        """
        return pulumi.get(self, "rules")

    @property
    @pulumi.getter
    def urls(self) -> pulumi.Output[Sequence[str]]:
        """
        An array of URLs to apply the WAF override to.
        """
        return pulumi.get(self, "urls")

    @property
    @pulumi.getter(name="zoneId")
    def zone_id(self) -> pulumi.Output[str]:
        """
        The DNS zone to which the WAF override condition should be added.
        """
        return pulumi.get(self, "zone_id")

