import boto3
import datetime
from src.logger import get_logger

logger = get_logger()

class ECSMetrics():
    def __init__(self, region_name):
        self._region_name = region_name

    def _get_client(self, scope):
        try:
            self._client = boto3.client(scope, region_name=self._region_name)
        except Exception as error:
            print(f"Boto3 client error: {error}")

        return self._client

    def get_cluster_metrics(self, cluster, metric):
        client = self._get_client('cloudwatch')

        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=5)

        dims = [
            {
                'Name': "ClusterName",
                'Value': cluster
            }
        ]

        res = self._client.get_metric_statistics(
            Namespace="AWS/ECS",
            MetricName=metric,
            Dimensions=dims,
            StartTime=start,
            EndTime=end,
            Period=60,
            Statistics=["Average"]
        )

        datapoints = res.get('Datapoints')
        average = datapoints[-1].get('Average')
        average = "%.4f" % average

        logger.debug(f"ClusterName: {cluster} - MetricName: {metric} - Value: {average}")

        return average

    def _describe_cluster(self, cluster):
        client = self._get_client('ecs')

        response = client.describe_clusters(
            clusters=[cluster]
        )

        return response

    def get_cluster_status(self, cluster, metric):
        clusters = self._describe_cluster(cluster)['clusters']

        for cluster in clusters:
            logger.debug(f"ClusterName: {cluster} - MetricName: {metric} - Value: {cluster.get(metric)}")

            return cluster.get(metric)
