# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities
from . import outputs

__all__ = [
    'GetProjectLoggingResult',
    'AwaitableGetProjectLoggingResult',
    'get_project_logging',
    'get_project_logging_output',
]

@pulumi.output_type
class GetProjectLoggingResult:
    """
    A collection of values returned by getProjectLogging.
    """
    def __init__(__self__, annotations=None, custom_target_config=None, elasticsearch_config=None, enable_json_parsing=None, fluentd_config=None, id=None, kafka_config=None, kind=None, labels=None, name=None, namespace_id=None, output_flush_interval=None, output_tags=None, project_id=None, splunk_config=None, syslog_config=None):
        if annotations and not isinstance(annotations, dict):
            raise TypeError("Expected argument 'annotations' to be a dict")
        pulumi.set(__self__, "annotations", annotations)
        if custom_target_config and not isinstance(custom_target_config, dict):
            raise TypeError("Expected argument 'custom_target_config' to be a dict")
        pulumi.set(__self__, "custom_target_config", custom_target_config)
        if elasticsearch_config and not isinstance(elasticsearch_config, dict):
            raise TypeError("Expected argument 'elasticsearch_config' to be a dict")
        pulumi.set(__self__, "elasticsearch_config", elasticsearch_config)
        if enable_json_parsing and not isinstance(enable_json_parsing, bool):
            raise TypeError("Expected argument 'enable_json_parsing' to be a bool")
        pulumi.set(__self__, "enable_json_parsing", enable_json_parsing)
        if fluentd_config and not isinstance(fluentd_config, dict):
            raise TypeError("Expected argument 'fluentd_config' to be a dict")
        pulumi.set(__self__, "fluentd_config", fluentd_config)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if kafka_config and not isinstance(kafka_config, dict):
            raise TypeError("Expected argument 'kafka_config' to be a dict")
        pulumi.set(__self__, "kafka_config", kafka_config)
        if kind and not isinstance(kind, str):
            raise TypeError("Expected argument 'kind' to be a str")
        pulumi.set(__self__, "kind", kind)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if namespace_id and not isinstance(namespace_id, str):
            raise TypeError("Expected argument 'namespace_id' to be a str")
        pulumi.set(__self__, "namespace_id", namespace_id)
        if output_flush_interval and not isinstance(output_flush_interval, int):
            raise TypeError("Expected argument 'output_flush_interval' to be a int")
        pulumi.set(__self__, "output_flush_interval", output_flush_interval)
        if output_tags and not isinstance(output_tags, dict):
            raise TypeError("Expected argument 'output_tags' to be a dict")
        pulumi.set(__self__, "output_tags", output_tags)
        if project_id and not isinstance(project_id, str):
            raise TypeError("Expected argument 'project_id' to be a str")
        pulumi.set(__self__, "project_id", project_id)
        if splunk_config and not isinstance(splunk_config, dict):
            raise TypeError("Expected argument 'splunk_config' to be a dict")
        pulumi.set(__self__, "splunk_config", splunk_config)
        if syslog_config and not isinstance(syslog_config, dict):
            raise TypeError("Expected argument 'syslog_config' to be a dict")
        pulumi.set(__self__, "syslog_config", syslog_config)

    @property
    @pulumi.getter
    def annotations(self) -> Mapping[str, Any]:
        """
        (Computed) Annotations for Cluster Logging object (map)
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="customTargetConfig")
    def custom_target_config(self) -> 'outputs.GetProjectLoggingCustomTargetConfigResult':
        return pulumi.get(self, "custom_target_config")

    @property
    @pulumi.getter(name="elasticsearchConfig")
    def elasticsearch_config(self) -> 'outputs.GetProjectLoggingElasticsearchConfigResult':
        """
        (Computed) The elasticsearch config for Cluster Logging. For `kind = elasticsearch`  (list maxitems:1)
        """
        return pulumi.get(self, "elasticsearch_config")

    @property
    @pulumi.getter(name="enableJsonParsing")
    def enable_json_parsing(self) -> bool:
        return pulumi.get(self, "enable_json_parsing")

    @property
    @pulumi.getter(name="fluentdConfig")
    def fluentd_config(self) -> 'outputs.GetProjectLoggingFluentdConfigResult':
        """
        (Computed) The fluentd config for Cluster Logging. For `kind = fluentd` (list maxitems:1)
        """
        return pulumi.get(self, "fluentd_config")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="kafkaConfig")
    def kafka_config(self) -> 'outputs.GetProjectLoggingKafkaConfigResult':
        """
        (Computed) The kafka config for Cluster Logging. For `kind = kafka` (list maxitems:1)
        """
        return pulumi.get(self, "kafka_config")

    @property
    @pulumi.getter
    def kind(self) -> str:
        """
        (Computed) The kind of the Cluster Logging. `elasticsearch`, `fluentd`, `kafka`, `splunk` and `syslog` are supported (string)
        """
        return pulumi.get(self, "kind")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, Any]:
        """
        (Computed) Labels for Cluster Logging object (map)
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        (Computed) The name of the cluster logging config (string)
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="namespaceId")
    def namespace_id(self) -> str:
        """
        (Computed) The namespace id from cluster logging (string)
        """
        return pulumi.get(self, "namespace_id")

    @property
    @pulumi.getter(name="outputFlushInterval")
    def output_flush_interval(self) -> int:
        """
        (Computed) How often buffered logs would be flushed. Default: `3` seconds (int)
        """
        return pulumi.get(self, "output_flush_interval")

    @property
    @pulumi.getter(name="outputTags")
    def output_tags(self) -> Mapping[str, Any]:
        """
        (computed) The output tags for Cluster Logging (map)
        """
        return pulumi.get(self, "output_tags")

    @property
    @pulumi.getter(name="projectId")
    def project_id(self) -> str:
        return pulumi.get(self, "project_id")

    @property
    @pulumi.getter(name="splunkConfig")
    def splunk_config(self) -> 'outputs.GetProjectLoggingSplunkConfigResult':
        """
        (Computed) The splunk config for Cluster Logging. For `kind = splunk` (list maxitems:1)
        """
        return pulumi.get(self, "splunk_config")

    @property
    @pulumi.getter(name="syslogConfig")
    def syslog_config(self) -> 'outputs.GetProjectLoggingSyslogConfigResult':
        """
        (Computed) The syslog config for Cluster Logging. For `kind = syslog` (list maxitems:1)
        """
        return pulumi.get(self, "syslog_config")


class AwaitableGetProjectLoggingResult(GetProjectLoggingResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetProjectLoggingResult(
            annotations=self.annotations,
            custom_target_config=self.custom_target_config,
            elasticsearch_config=self.elasticsearch_config,
            enable_json_parsing=self.enable_json_parsing,
            fluentd_config=self.fluentd_config,
            id=self.id,
            kafka_config=self.kafka_config,
            kind=self.kind,
            labels=self.labels,
            name=self.name,
            namespace_id=self.namespace_id,
            output_flush_interval=self.output_flush_interval,
            output_tags=self.output_tags,
            project_id=self.project_id,
            splunk_config=self.splunk_config,
            syslog_config=self.syslog_config)


def get_project_logging(project_id: Optional[str] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetProjectLoggingResult:
    """
    Use this data source to retrieve information about a Rancher v2 Project Logging.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_rancher2 as rancher2

    foo = rancher2.get_project_logging(project_id="<project_id>")
    ```


    :param str project_id: The project id to configure logging (string)
    """
    __args__ = dict()
    __args__['projectId'] = project_id
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('rancher2:index/getProjectLogging:getProjectLogging', __args__, opts=opts, typ=GetProjectLoggingResult).value

    return AwaitableGetProjectLoggingResult(
        annotations=__ret__.annotations,
        custom_target_config=__ret__.custom_target_config,
        elasticsearch_config=__ret__.elasticsearch_config,
        enable_json_parsing=__ret__.enable_json_parsing,
        fluentd_config=__ret__.fluentd_config,
        id=__ret__.id,
        kafka_config=__ret__.kafka_config,
        kind=__ret__.kind,
        labels=__ret__.labels,
        name=__ret__.name,
        namespace_id=__ret__.namespace_id,
        output_flush_interval=__ret__.output_flush_interval,
        output_tags=__ret__.output_tags,
        project_id=__ret__.project_id,
        splunk_config=__ret__.splunk_config,
        syslog_config=__ret__.syslog_config)


@_utilities.lift_output_func(get_project_logging)
def get_project_logging_output(project_id: Optional[pulumi.Input[str]] = None,
                               opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetProjectLoggingResult]:
    """
    Use this data source to retrieve information about a Rancher v2 Project Logging.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_rancher2 as rancher2

    foo = rancher2.get_project_logging(project_id="<project_id>")
    ```


    :param str project_id: The project id to configure logging (string)
    """
    ...
