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

__all__ = ['ClusterAlertRuleArgs', 'ClusterAlertRule']

@pulumi.input_type
class ClusterAlertRuleArgs:
    def __init__(__self__, *,
                 cluster_id: pulumi.Input[str],
                 group_id: pulumi.Input[str],
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 event_rule: Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']] = None,
                 group_interval_seconds: Optional[pulumi.Input[int]] = None,
                 group_wait_seconds: Optional[pulumi.Input[int]] = None,
                 inherited: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 metric_rule: Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 node_rule: Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']] = None,
                 repeat_interval_seconds: Optional[pulumi.Input[int]] = None,
                 severity: Optional[pulumi.Input[str]] = None,
                 system_service_rule: Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']] = None):
        """
        The set of arguments for constructing a ClusterAlertRule resource.
        :param pulumi.Input[str] cluster_id: The cluster id where create cluster alert rule (string)
        :param pulumi.Input[str] group_id: The cluster alert rule alert group ID (string)
        :param pulumi.Input[Mapping[str, Any]] annotations: The cluster alert rule annotations (map)
        :param pulumi.Input['ClusterAlertRuleEventRuleArgs'] event_rule: The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[int] group_interval_seconds: The cluster alert rule group interval seconds. Default: `180` (int)
        :param pulumi.Input[int] group_wait_seconds: The cluster alert rule group wait seconds. Default: `180` (int)
        :param pulumi.Input[bool] inherited: The cluster alert rule inherited. Default: `true` (bool)
        :param pulumi.Input[Mapping[str, Any]] labels: The cluster alert rule labels (map)
        :param pulumi.Input['ClusterAlertRuleMetricRuleArgs'] metric_rule: The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] name: The cluster alert rule name (string)
        :param pulumi.Input['ClusterAlertRuleNodeRuleArgs'] node_rule: The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[int] repeat_interval_seconds: The cluster alert rule wait seconds. Default: `3600` (int)
        :param pulumi.Input[str] severity: The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        :param pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs'] system_service_rule: The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        pulumi.set(__self__, "cluster_id", cluster_id)
        pulumi.set(__self__, "group_id", group_id)
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if event_rule is not None:
            pulumi.set(__self__, "event_rule", event_rule)
        if group_interval_seconds is not None:
            pulumi.set(__self__, "group_interval_seconds", group_interval_seconds)
        if group_wait_seconds is not None:
            pulumi.set(__self__, "group_wait_seconds", group_wait_seconds)
        if inherited is not None:
            pulumi.set(__self__, "inherited", inherited)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if metric_rule is not None:
            pulumi.set(__self__, "metric_rule", metric_rule)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if node_rule is not None:
            pulumi.set(__self__, "node_rule", node_rule)
        if repeat_interval_seconds is not None:
            pulumi.set(__self__, "repeat_interval_seconds", repeat_interval_seconds)
        if severity is not None:
            pulumi.set(__self__, "severity", severity)
        if system_service_rule is not None:
            pulumi.set(__self__, "system_service_rule", system_service_rule)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Input[str]:
        """
        The cluster id where create cluster alert rule (string)
        """
        return pulumi.get(self, "cluster_id")

    @cluster_id.setter
    def cluster_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "cluster_id", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Input[str]:
        """
        The cluster alert rule alert group ID (string)
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        The cluster alert rule annotations (map)
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter(name="eventRule")
    def event_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']]:
        """
        The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "event_rule")

    @event_rule.setter
    def event_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']]):
        pulumi.set(self, "event_rule", value)

    @property
    @pulumi.getter(name="groupIntervalSeconds")
    def group_interval_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule group interval seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_interval_seconds")

    @group_interval_seconds.setter
    def group_interval_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "group_interval_seconds", value)

    @property
    @pulumi.getter(name="groupWaitSeconds")
    def group_wait_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule group wait seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_wait_seconds")

    @group_wait_seconds.setter
    def group_wait_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "group_wait_seconds", value)

    @property
    @pulumi.getter
    def inherited(self) -> Optional[pulumi.Input[bool]]:
        """
        The cluster alert rule inherited. Default: `true` (bool)
        """
        return pulumi.get(self, "inherited")

    @inherited.setter
    def inherited(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "inherited", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        The cluster alert rule labels (map)
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter(name="metricRule")
    def metric_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']]:
        """
        The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "metric_rule")

    @metric_rule.setter
    def metric_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']]):
        pulumi.set(self, "metric_rule", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster alert rule name (string)
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="nodeRule")
    def node_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']]:
        """
        The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "node_rule")

    @node_rule.setter
    def node_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']]):
        pulumi.set(self, "node_rule", value)

    @property
    @pulumi.getter(name="repeatIntervalSeconds")
    def repeat_interval_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule wait seconds. Default: `3600` (int)
        """
        return pulumi.get(self, "repeat_interval_seconds")

    @repeat_interval_seconds.setter
    def repeat_interval_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "repeat_interval_seconds", value)

    @property
    @pulumi.getter
    def severity(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        """
        return pulumi.get(self, "severity")

    @severity.setter
    def severity(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "severity", value)

    @property
    @pulumi.getter(name="systemServiceRule")
    def system_service_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']]:
        """
        The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        return pulumi.get(self, "system_service_rule")

    @system_service_rule.setter
    def system_service_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']]):
        pulumi.set(self, "system_service_rule", value)


@pulumi.input_type
class _ClusterAlertRuleState:
    def __init__(__self__, *,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 event_rule: Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_interval_seconds: Optional[pulumi.Input[int]] = None,
                 group_wait_seconds: Optional[pulumi.Input[int]] = None,
                 inherited: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 metric_rule: Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 node_rule: Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']] = None,
                 repeat_interval_seconds: Optional[pulumi.Input[int]] = None,
                 severity: Optional[pulumi.Input[str]] = None,
                 system_service_rule: Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']] = None):
        """
        Input properties used for looking up and filtering ClusterAlertRule resources.
        :param pulumi.Input[Mapping[str, Any]] annotations: The cluster alert rule annotations (map)
        :param pulumi.Input[str] cluster_id: The cluster id where create cluster alert rule (string)
        :param pulumi.Input['ClusterAlertRuleEventRuleArgs'] event_rule: The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] group_id: The cluster alert rule alert group ID (string)
        :param pulumi.Input[int] group_interval_seconds: The cluster alert rule group interval seconds. Default: `180` (int)
        :param pulumi.Input[int] group_wait_seconds: The cluster alert rule group wait seconds. Default: `180` (int)
        :param pulumi.Input[bool] inherited: The cluster alert rule inherited. Default: `true` (bool)
        :param pulumi.Input[Mapping[str, Any]] labels: The cluster alert rule labels (map)
        :param pulumi.Input['ClusterAlertRuleMetricRuleArgs'] metric_rule: The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] name: The cluster alert rule name (string)
        :param pulumi.Input['ClusterAlertRuleNodeRuleArgs'] node_rule: The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[int] repeat_interval_seconds: The cluster alert rule wait seconds. Default: `3600` (int)
        :param pulumi.Input[str] severity: The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        :param pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs'] system_service_rule: The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        if annotations is not None:
            pulumi.set(__self__, "annotations", annotations)
        if cluster_id is not None:
            pulumi.set(__self__, "cluster_id", cluster_id)
        if event_rule is not None:
            pulumi.set(__self__, "event_rule", event_rule)
        if group_id is not None:
            pulumi.set(__self__, "group_id", group_id)
        if group_interval_seconds is not None:
            pulumi.set(__self__, "group_interval_seconds", group_interval_seconds)
        if group_wait_seconds is not None:
            pulumi.set(__self__, "group_wait_seconds", group_wait_seconds)
        if inherited is not None:
            pulumi.set(__self__, "inherited", inherited)
        if labels is not None:
            pulumi.set(__self__, "labels", labels)
        if metric_rule is not None:
            pulumi.set(__self__, "metric_rule", metric_rule)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if node_rule is not None:
            pulumi.set(__self__, "node_rule", node_rule)
        if repeat_interval_seconds is not None:
            pulumi.set(__self__, "repeat_interval_seconds", repeat_interval_seconds)
        if severity is not None:
            pulumi.set(__self__, "severity", severity)
        if system_service_rule is not None:
            pulumi.set(__self__, "system_service_rule", system_service_rule)

    @property
    @pulumi.getter
    def annotations(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        The cluster alert rule annotations (map)
        """
        return pulumi.get(self, "annotations")

    @annotations.setter
    def annotations(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "annotations", value)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster id where create cluster alert rule (string)
        """
        return pulumi.get(self, "cluster_id")

    @cluster_id.setter
    def cluster_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cluster_id", value)

    @property
    @pulumi.getter(name="eventRule")
    def event_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']]:
        """
        The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "event_rule")

    @event_rule.setter
    def event_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleEventRuleArgs']]):
        pulumi.set(self, "event_rule", value)

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster alert rule alert group ID (string)
        """
        return pulumi.get(self, "group_id")

    @group_id.setter
    def group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "group_id", value)

    @property
    @pulumi.getter(name="groupIntervalSeconds")
    def group_interval_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule group interval seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_interval_seconds")

    @group_interval_seconds.setter
    def group_interval_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "group_interval_seconds", value)

    @property
    @pulumi.getter(name="groupWaitSeconds")
    def group_wait_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule group wait seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_wait_seconds")

    @group_wait_seconds.setter
    def group_wait_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "group_wait_seconds", value)

    @property
    @pulumi.getter
    def inherited(self) -> Optional[pulumi.Input[bool]]:
        """
        The cluster alert rule inherited. Default: `true` (bool)
        """
        return pulumi.get(self, "inherited")

    @inherited.setter
    def inherited(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "inherited", value)

    @property
    @pulumi.getter
    def labels(self) -> Optional[pulumi.Input[Mapping[str, Any]]]:
        """
        The cluster alert rule labels (map)
        """
        return pulumi.get(self, "labels")

    @labels.setter
    def labels(self, value: Optional[pulumi.Input[Mapping[str, Any]]]):
        pulumi.set(self, "labels", value)

    @property
    @pulumi.getter(name="metricRule")
    def metric_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']]:
        """
        The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "metric_rule")

    @metric_rule.setter
    def metric_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleMetricRuleArgs']]):
        pulumi.set(self, "metric_rule", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster alert rule name (string)
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="nodeRule")
    def node_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']]:
        """
        The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "node_rule")

    @node_rule.setter
    def node_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleNodeRuleArgs']]):
        pulumi.set(self, "node_rule", value)

    @property
    @pulumi.getter(name="repeatIntervalSeconds")
    def repeat_interval_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        The cluster alert rule wait seconds. Default: `3600` (int)
        """
        return pulumi.get(self, "repeat_interval_seconds")

    @repeat_interval_seconds.setter
    def repeat_interval_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "repeat_interval_seconds", value)

    @property
    @pulumi.getter
    def severity(self) -> Optional[pulumi.Input[str]]:
        """
        The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        """
        return pulumi.get(self, "severity")

    @severity.setter
    def severity(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "severity", value)

    @property
    @pulumi.getter(name="systemServiceRule")
    def system_service_rule(self) -> Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']]:
        """
        The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        return pulumi.get(self, "system_service_rule")

    @system_service_rule.setter
    def system_service_rule(self, value: Optional[pulumi.Input['ClusterAlertRuleSystemServiceRuleArgs']]):
        pulumi.set(self, "system_service_rule", value)


class ClusterAlertRule(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 event_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleEventRuleArgs']]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_interval_seconds: Optional[pulumi.Input[int]] = None,
                 group_wait_seconds: Optional[pulumi.Input[int]] = None,
                 inherited: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 metric_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleMetricRuleArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 node_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleNodeRuleArgs']]] = None,
                 repeat_interval_seconds: Optional[pulumi.Input[int]] = None,
                 severity: Optional[pulumi.Input[str]] = None,
                 system_service_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleSystemServiceRuleArgs']]] = None,
                 __props__=None):
        """
        Provides a Rancher v2 Cluster Alert Rule resource. This can be used to create Cluster Alert Rule for Rancher v2 environments and retrieve their information.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_rancher2 as rancher2

        # Create a new Rancher2 Cluster Alert Group
        foo_cluster_alert_group = rancher2.ClusterAlertGroup("fooClusterAlertGroup",
            cluster_id="<cluster_id>",
            description="Terraform cluster alert group",
            group_interval_seconds=300,
            repeat_interval_seconds=3600)
        # Create a new Rancher2 Cluster Alert Rule
        foo_cluster_alert_rule = rancher2.ClusterAlertRule("fooClusterAlertRule",
            cluster_id=foo_cluster_alert_group.cluster_id,
            group_id=foo_cluster_alert_group.id,
            group_interval_seconds=600,
            repeat_interval_seconds=6000)
        ```

        ## Import

        Cluster Alert Rule can be imported using the Rancher cluster alert rule ID

        ```sh
         $ pulumi import rancher2:index/clusterAlertRule:ClusterAlertRule foo &lt;CLUSTER_ALERT_RULE_ID&gt;
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, Any]] annotations: The cluster alert rule annotations (map)
        :param pulumi.Input[str] cluster_id: The cluster id where create cluster alert rule (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleEventRuleArgs']] event_rule: The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] group_id: The cluster alert rule alert group ID (string)
        :param pulumi.Input[int] group_interval_seconds: The cluster alert rule group interval seconds. Default: `180` (int)
        :param pulumi.Input[int] group_wait_seconds: The cluster alert rule group wait seconds. Default: `180` (int)
        :param pulumi.Input[bool] inherited: The cluster alert rule inherited. Default: `true` (bool)
        :param pulumi.Input[Mapping[str, Any]] labels: The cluster alert rule labels (map)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleMetricRuleArgs']] metric_rule: The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] name: The cluster alert rule name (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleNodeRuleArgs']] node_rule: The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[int] repeat_interval_seconds: The cluster alert rule wait seconds. Default: `3600` (int)
        :param pulumi.Input[str] severity: The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleSystemServiceRuleArgs']] system_service_rule: The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ClusterAlertRuleArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Rancher v2 Cluster Alert Rule resource. This can be used to create Cluster Alert Rule for Rancher v2 environments and retrieve their information.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_rancher2 as rancher2

        # Create a new Rancher2 Cluster Alert Group
        foo_cluster_alert_group = rancher2.ClusterAlertGroup("fooClusterAlertGroup",
            cluster_id="<cluster_id>",
            description="Terraform cluster alert group",
            group_interval_seconds=300,
            repeat_interval_seconds=3600)
        # Create a new Rancher2 Cluster Alert Rule
        foo_cluster_alert_rule = rancher2.ClusterAlertRule("fooClusterAlertRule",
            cluster_id=foo_cluster_alert_group.cluster_id,
            group_id=foo_cluster_alert_group.id,
            group_interval_seconds=600,
            repeat_interval_seconds=6000)
        ```

        ## Import

        Cluster Alert Rule can be imported using the Rancher cluster alert rule ID

        ```sh
         $ pulumi import rancher2:index/clusterAlertRule:ClusterAlertRule foo &lt;CLUSTER_ALERT_RULE_ID&gt;
        ```

        :param str resource_name: The name of the resource.
        :param ClusterAlertRuleArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ClusterAlertRuleArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 event_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleEventRuleArgs']]] = None,
                 group_id: Optional[pulumi.Input[str]] = None,
                 group_interval_seconds: Optional[pulumi.Input[int]] = None,
                 group_wait_seconds: Optional[pulumi.Input[int]] = None,
                 inherited: Optional[pulumi.Input[bool]] = None,
                 labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
                 metric_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleMetricRuleArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 node_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleNodeRuleArgs']]] = None,
                 repeat_interval_seconds: Optional[pulumi.Input[int]] = None,
                 severity: Optional[pulumi.Input[str]] = None,
                 system_service_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleSystemServiceRuleArgs']]] = None,
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
            __props__ = ClusterAlertRuleArgs.__new__(ClusterAlertRuleArgs)

            __props__.__dict__["annotations"] = annotations
            if cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'cluster_id'")
            __props__.__dict__["cluster_id"] = cluster_id
            __props__.__dict__["event_rule"] = event_rule
            if group_id is None and not opts.urn:
                raise TypeError("Missing required property 'group_id'")
            __props__.__dict__["group_id"] = group_id
            __props__.__dict__["group_interval_seconds"] = group_interval_seconds
            __props__.__dict__["group_wait_seconds"] = group_wait_seconds
            __props__.__dict__["inherited"] = inherited
            __props__.__dict__["labels"] = labels
            __props__.__dict__["metric_rule"] = metric_rule
            __props__.__dict__["name"] = name
            __props__.__dict__["node_rule"] = node_rule
            __props__.__dict__["repeat_interval_seconds"] = repeat_interval_seconds
            __props__.__dict__["severity"] = severity
            __props__.__dict__["system_service_rule"] = system_service_rule
        alias_opts = pulumi.ResourceOptions(aliases=[pulumi.Alias(type_="rancher2:index/clusterAlterRule:ClusterAlterRule")])
        opts = pulumi.ResourceOptions.merge(opts, alias_opts)
        super(ClusterAlertRule, __self__).__init__(
            'rancher2:index/clusterAlertRule:ClusterAlertRule',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            annotations: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            cluster_id: Optional[pulumi.Input[str]] = None,
            event_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleEventRuleArgs']]] = None,
            group_id: Optional[pulumi.Input[str]] = None,
            group_interval_seconds: Optional[pulumi.Input[int]] = None,
            group_wait_seconds: Optional[pulumi.Input[int]] = None,
            inherited: Optional[pulumi.Input[bool]] = None,
            labels: Optional[pulumi.Input[Mapping[str, Any]]] = None,
            metric_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleMetricRuleArgs']]] = None,
            name: Optional[pulumi.Input[str]] = None,
            node_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleNodeRuleArgs']]] = None,
            repeat_interval_seconds: Optional[pulumi.Input[int]] = None,
            severity: Optional[pulumi.Input[str]] = None,
            system_service_rule: Optional[pulumi.Input[pulumi.InputType['ClusterAlertRuleSystemServiceRuleArgs']]] = None) -> 'ClusterAlertRule':
        """
        Get an existing ClusterAlertRule resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Mapping[str, Any]] annotations: The cluster alert rule annotations (map)
        :param pulumi.Input[str] cluster_id: The cluster id where create cluster alert rule (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleEventRuleArgs']] event_rule: The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] group_id: The cluster alert rule alert group ID (string)
        :param pulumi.Input[int] group_interval_seconds: The cluster alert rule group interval seconds. Default: `180` (int)
        :param pulumi.Input[int] group_wait_seconds: The cluster alert rule group wait seconds. Default: `180` (int)
        :param pulumi.Input[bool] inherited: The cluster alert rule inherited. Default: `true` (bool)
        :param pulumi.Input[Mapping[str, Any]] labels: The cluster alert rule labels (map)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleMetricRuleArgs']] metric_rule: The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[str] name: The cluster alert rule name (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleNodeRuleArgs']] node_rule: The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        :param pulumi.Input[int] repeat_interval_seconds: The cluster alert rule wait seconds. Default: `3600` (int)
        :param pulumi.Input[str] severity: The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        :param pulumi.Input[pulumi.InputType['ClusterAlertRuleSystemServiceRuleArgs']] system_service_rule: The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ClusterAlertRuleState.__new__(_ClusterAlertRuleState)

        __props__.__dict__["annotations"] = annotations
        __props__.__dict__["cluster_id"] = cluster_id
        __props__.__dict__["event_rule"] = event_rule
        __props__.__dict__["group_id"] = group_id
        __props__.__dict__["group_interval_seconds"] = group_interval_seconds
        __props__.__dict__["group_wait_seconds"] = group_wait_seconds
        __props__.__dict__["inherited"] = inherited
        __props__.__dict__["labels"] = labels
        __props__.__dict__["metric_rule"] = metric_rule
        __props__.__dict__["name"] = name
        __props__.__dict__["node_rule"] = node_rule
        __props__.__dict__["repeat_interval_seconds"] = repeat_interval_seconds
        __props__.__dict__["severity"] = severity
        __props__.__dict__["system_service_rule"] = system_service_rule
        return ClusterAlertRule(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def annotations(self) -> pulumi.Output[Mapping[str, Any]]:
        """
        The cluster alert rule annotations (map)
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Output[str]:
        """
        The cluster id where create cluster alert rule (string)
        """
        return pulumi.get(self, "cluster_id")

    @property
    @pulumi.getter(name="eventRule")
    def event_rule(self) -> pulumi.Output[Optional['outputs.ClusterAlertRuleEventRule']]:
        """
        The cluster alert rule event rule. ConflictsWith: `"metric_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "event_rule")

    @property
    @pulumi.getter(name="groupId")
    def group_id(self) -> pulumi.Output[str]:
        """
        The cluster alert rule alert group ID (string)
        """
        return pulumi.get(self, "group_id")

    @property
    @pulumi.getter(name="groupIntervalSeconds")
    def group_interval_seconds(self) -> pulumi.Output[Optional[int]]:
        """
        The cluster alert rule group interval seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_interval_seconds")

    @property
    @pulumi.getter(name="groupWaitSeconds")
    def group_wait_seconds(self) -> pulumi.Output[Optional[int]]:
        """
        The cluster alert rule group wait seconds. Default: `180` (int)
        """
        return pulumi.get(self, "group_wait_seconds")

    @property
    @pulumi.getter
    def inherited(self) -> pulumi.Output[Optional[bool]]:
        """
        The cluster alert rule inherited. Default: `true` (bool)
        """
        return pulumi.get(self, "inherited")

    @property
    @pulumi.getter
    def labels(self) -> pulumi.Output[Mapping[str, Any]]:
        """
        The cluster alert rule labels (map)
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter(name="metricRule")
    def metric_rule(self) -> pulumi.Output[Optional['outputs.ClusterAlertRuleMetricRule']]:
        """
        The cluster alert rule metric rule. ConflictsWith: `"event_rule", "node_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "metric_rule")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The cluster alert rule name (string)
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="nodeRule")
    def node_rule(self) -> pulumi.Output[Optional['outputs.ClusterAlertRuleNodeRule']]:
        """
        The cluster alert rule node rule. ConflictsWith: `"event_rule", "metric_rule", "system_service_rule"`` (list Maxitems:1)
        """
        return pulumi.get(self, "node_rule")

    @property
    @pulumi.getter(name="repeatIntervalSeconds")
    def repeat_interval_seconds(self) -> pulumi.Output[Optional[int]]:
        """
        The cluster alert rule wait seconds. Default: `3600` (int)
        """
        return pulumi.get(self, "repeat_interval_seconds")

    @property
    @pulumi.getter
    def severity(self) -> pulumi.Output[Optional[str]]:
        """
        The cluster alert rule severity. Supported values : `"critical" | "info" | "warning"`. Default: `critical` (string)
        """
        return pulumi.get(self, "severity")

    @property
    @pulumi.getter(name="systemServiceRule")
    def system_service_rule(self) -> pulumi.Output[Optional['outputs.ClusterAlertRuleSystemServiceRule']]:
        """
        The cluster alert rule system service rule. ConflictsWith: `"event_rule", "metric_rule", "node_rule"` (list Maxitems:1)
        """
        return pulumi.get(self, "system_service_rule")

