from setuptools import setup, find_packages

setup(
    name='prometheus-ecs-cluster-exporter',
    version='0.0.1',
    description='Prometheus exporter for ECS clusters',
    url='https://github.com/nulldutra/prometheus-ecs-cluster-exporter',
    author='Gabriel M. Dutra',
    author_email="nulldutra@gmail.com",
    entry_points={"console_scripts": ["prometheus-ecs-cluster-exporter=src.__main__:main"]},
    install_requires=[
        'boto3',
        'prometheus_client'
    ],
    zip_safe=False,
    packages=find_packages()
)
