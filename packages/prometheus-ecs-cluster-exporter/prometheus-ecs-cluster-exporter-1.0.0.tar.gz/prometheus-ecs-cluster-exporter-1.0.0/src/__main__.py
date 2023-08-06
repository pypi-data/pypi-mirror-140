# Maintainer: Gabriel M. Dutra <0xdutra@gmail.com>

#!/usr/bin/env python

"""
    Prometheus ECS exporter
"""

import argparse
import time
import sys
import os

from src.get_metrics import ECSMetrics
from src.logger import get_logger
from src.prom_metrics import PromMetrics
from prometheus_client import start_http_server


logger = get_logger()

HELP_MESSAGE = '''
Prometheus ECS exporter

Usage:
    export ECS_CLUSTERS="cluster-example-01 cluster-example-02"
    export REFRESH_INTERVAL=20
    export PORT=9095
    export REGION=sa-east-1

Command:
    prometheus-ecs-cluster-exporter
'''

CLUSTERS = os.environ["ECS_CLUSTERS"].split()
REFRESH_INTERVAL = int(os.environ.get("REFRESH_INTERVAL", 60))
PORT = int(os.environ.get("PORT", 8420))
REGION = os.environ.get("AWS_REGION", "us-east-1")

def main():
    prom = PromMetrics()
    ecs = ECSMetrics(region_name=REGION)

    try:
        start_http_server(PORT)
    except OSError as error:
        print(f"error: {error}")
        sys.exit(1)

    logger.info(f"HTTP server started! http://127.0.0.1:{PORT}")

    while True:
        prom.prom_metrics(ecs, CLUSTERS)
        time.sleep(REFRESH_INTERVAL)

if __name__=='__main__':
    main()
