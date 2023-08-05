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
    'GetClusterScanResult',
    'AwaitableGetClusterScanResult',
    'get_cluster_scan',
    'get_cluster_scan_output',
]

@pulumi.output_type
class GetClusterScanResult:
    """
    A collection of values returned by getClusterScan.
    """
    def __init__(__self__, annotations=None, cluster_id=None, id=None, labels=None, name=None, run_type=None, scan_config=None, scan_type=None, status=None):
        if annotations and not isinstance(annotations, dict):
            raise TypeError("Expected argument 'annotations' to be a dict")
        pulumi.set(__self__, "annotations", annotations)
        if cluster_id and not isinstance(cluster_id, str):
            raise TypeError("Expected argument 'cluster_id' to be a str")
        pulumi.set(__self__, "cluster_id", cluster_id)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if labels and not isinstance(labels, dict):
            raise TypeError("Expected argument 'labels' to be a dict")
        pulumi.set(__self__, "labels", labels)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if run_type and not isinstance(run_type, str):
            raise TypeError("Expected argument 'run_type' to be a str")
        pulumi.set(__self__, "run_type", run_type)
        if scan_config and not isinstance(scan_config, dict):
            raise TypeError("Expected argument 'scan_config' to be a dict")
        pulumi.set(__self__, "scan_config", scan_config)
        if scan_type and not isinstance(scan_type, str):
            raise TypeError("Expected argument 'scan_type' to be a str")
        pulumi.set(__self__, "scan_type", scan_type)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter
    def annotations(self) -> Mapping[str, Any]:
        """
        (Computed) Annotations of the resource (map)
        """
        return pulumi.get(self, "annotations")

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> str:
        return pulumi.get(self, "cluster_id")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def labels(self) -> Mapping[str, Any]:
        """
        (Computed) Labels of the resource (map)
        """
        return pulumi.get(self, "labels")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="runType")
    def run_type(self) -> str:
        """
        (Computed) Cluster Scan run type (string)
        """
        return pulumi.get(self, "run_type")

    @property
    @pulumi.getter(name="scanConfig")
    def scan_config(self) -> 'outputs.GetClusterScanScanConfigResult':
        """
        (Computed) Cluster Scan config (bool)
        """
        return pulumi.get(self, "scan_config")

    @property
    @pulumi.getter(name="scanType")
    def scan_type(self) -> str:
        """
        (Computed) Cluster Scan type (string)
        """
        return pulumi.get(self, "scan_type")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        (Computed) Cluster Scan status (string)
        """
        return pulumi.get(self, "status")


class AwaitableGetClusterScanResult(GetClusterScanResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetClusterScanResult(
            annotations=self.annotations,
            cluster_id=self.cluster_id,
            id=self.id,
            labels=self.labels,
            name=self.name,
            run_type=self.run_type,
            scan_config=self.scan_config,
            scan_type=self.scan_type,
            status=self.status)


def get_cluster_scan(cluster_id: Optional[str] = None,
                     name: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetClusterScanResult:
    """
    Use this data source to retrieve information about a Rancher v2 Cluster CIS Scan resource.


    :param str cluster_id: Cluster ID for CIS Scan (string)
    :param str name: Name of the cluster Scan (string)
    """
    __args__ = dict()
    __args__['clusterId'] = cluster_id
    __args__['name'] = name
    if opts is None:
        opts = pulumi.InvokeOptions()
    if opts.version is None:
        opts.version = _utilities.get_version()
    __ret__ = pulumi.runtime.invoke('rancher2:index/getClusterScan:getClusterScan', __args__, opts=opts, typ=GetClusterScanResult).value

    return AwaitableGetClusterScanResult(
        annotations=__ret__.annotations,
        cluster_id=__ret__.cluster_id,
        id=__ret__.id,
        labels=__ret__.labels,
        name=__ret__.name,
        run_type=__ret__.run_type,
        scan_config=__ret__.scan_config,
        scan_type=__ret__.scan_type,
        status=__ret__.status)


@_utilities.lift_output_func(get_cluster_scan)
def get_cluster_scan_output(cluster_id: Optional[pulumi.Input[str]] = None,
                            name: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetClusterScanResult]:
    """
    Use this data source to retrieve information about a Rancher v2 Cluster CIS Scan resource.


    :param str cluster_id: Cluster ID for CIS Scan (string)
    :param str name: Name of the cluster Scan (string)
    """
    ...
