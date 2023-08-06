<p align="center">
  <h3 align="center">Prometheus ECS clusters Exporter</h3>
  <p align="center">
    <a href="https://twitter.com/0xdutra">
      <img src="https://img.shields.io/badge/twitter-@0xdutra-blue.svg">
    </a>
  </p>
</p>

<hr>

## Metrics

| Metric                                | Description                   |
|---------------------------------------|-------------------------------|
| CPUReservation                        | Cluster CPU reservation is measured as the total CPU units that are reserved by Amazon ECS tasks on the cluster. |
| CPUUtilization    |Cluster CPU utilization is measured as the total CPU units in use by Amazon ECS tasks on the cluster|
| MemoryReservation |Cluster memory reservation is measured as the total memory that is reserved by Amazon ECS tasks on the cluster|
| MemoryUtilization |Cluster memory utilization is measured as the total memory in use by Amazon ECS tasks on the cluster|
| RegisteredContainerInstancesCount |The number of container instances registered into the cluster. This includes container instances in both ACTIVE and DRAINING status|
| RunningTasksCount |The number of tasks in the cluster that are in the RUNNING state|
| PendingTasksCount |The number of tasks in the cluster that are in the PENDING state|
| ActiveServicesCount |The number of services that are running on the cluster in an ACTIVE state|

## Installation

```bash
python setup.py install
```

## Usage

```bash
Prometheus ECS exporter

Usage:
    export ECS_CLUSTERS="cluster-example-01 cluster-example-02"
    export REFRESH_INTERVAL=20
    export PORT=9095
    export REGION=sa-east-1

Command:
    prometheus-ecs-cluster-exporter
```

| Env variable     | Default value |
|------------------|---------------|
| ECS_CLUSTERS     | Required      |
| REFRESH_INTERVAL | 60            |
| PORT             | 8420          |
| REGION           | us-east-1     |

<hr>

## Running the exporter

```bash
prometheus-ecs-clusters-exporter
```

## Grafana dashboard

![](./screenshot/screenshot.png)
