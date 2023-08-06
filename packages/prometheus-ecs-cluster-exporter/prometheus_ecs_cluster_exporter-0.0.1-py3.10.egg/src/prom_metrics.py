from dataclasses import dataclass
from prometheus_client import Gauge, Info


@dataclass
class PromMetrics():
    cpuReservation = Gauge(
        'cpuReservation',
        'ECS cluster CPU reservation',
        ['clusterName']
    )

    cpuUtilization = Gauge(
        'cpuUtilization',
        'ECS cluster CPU utilization',
        ['clusterName']
    )

    memoryReservation = Gauge(
        'memoryReservation',
        'ECS cluster memory reservation',
        ['clusterName']
    )

    memoryUtilization = Gauge(
        'memoryUtilization',
        'ECS cluster memory utilization',
        ['clusterName']
    )

    registeredContainerInstancesCount = Gauge(
        'registeredContainerInstancesCount',
        'ECS cluster instances count',
        ['clusterName']
    )

    runningTasksCount = Gauge(
        'runningTasksCount',
        'ECS cluster instances count',
        ['clusterName']
    )

    pendingTasksCount = Gauge(
        'pendingTasksCount',
        'ECS cluster pending tasks count',
        ['clusterName']
    )

    activeServicesCount = Gauge(
        'activeServicesCount',
        'ECS cluster running tasks count',
        ['clusterName']
    )

    def prom_metrics(self, ecs, clusters):

        for cluster in clusters:

            self.cpuReservation.labels(clusterName=cluster).set(
                ecs.get_cluster_metrics(cluster, 'CPUReservation')
            )

            self.cpuUtilization.labels(clusterName=cluster).set(
                ecs.get_cluster_metrics(cluster, 'CPUUtilization')
            )

            self.memoryReservation.labels(clusterName=cluster).set(
                ecs.get_cluster_metrics(cluster, 'MemoryReservation')
            )

            self.memoryUtilization.labels(clusterName=cluster).set(
                ecs.get_cluster_metrics(cluster, 'MemoryUtilization')
            )

            self.registeredContainerInstancesCount.labels(clusterName=cluster).set(
                ecs.get_cluster_status(cluster, 'registeredContainerInstancesCount')
            )

            self.runningTasksCount.labels(clusterName=cluster).set(
                ecs.get_cluster_status(cluster, 'runningTasksCount')
            )

            self.pendingTasksCount.labels(clusterName=cluster).set(
                ecs.get_cluster_status(cluster, 'pendingTasksCount')
            )

            self.activeServicesCount.labels(clusterName=cluster).set(
                ecs.get_cluster_status(cluster, 'activeServicesCount')
            )
