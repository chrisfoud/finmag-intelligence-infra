#!/usr/bin/env python3
import aws_cdk as cdk
import os

from aws_cdk import App, Environment
from network_infra.network_stack import NetworkStack
# from s3_rds_elasticache_infra.s3_rds_elasticahce_stack import S3_RDS_Elasticache

app = App()

# Get environment
env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION")
)

network_stack = NetworkStack(app, "Network-Stack", env=env)
# s3_rds_elasticache = S3_RDS_Elasticache(app, "S3-RDS-Elasticache-Stack", env=env)


# Add dependency
s3_rds_elasticache.add_dependency(network_stack)

app.synth()
