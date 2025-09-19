#!/usr/bin/env python3
import aws_cdk as cdk
import os

from aws_cdk import App, Environment
from network_infra.network_stack import NetworkStack
from s3_rds_elasticache_infra.s3_rds_elasticahce_stack import S3
from s3_rds_elasticache_infra.s3_rds_elasticahce_stack import RDS
from s3_rds_elasticache_infra.s3_rds_elasticahce_stack import Redis

app = App()

# Get environment
env = cdk.Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=os.environ.get("CDK_DEFAULT_REGION")
)

network_stack = NetworkStack(app, "Network-Stack", env=env)
s3_stack = S3(app, "S3-Stack", env=env)
rds_stack = RDS(app, "RDS-Stack", env=env)
redis_stack = Redis(app, "Redis-Stack", env=env)


# Add dependency when S3-RDS-Elasticache stack is uncommented
rds_stack.add_dependency(network_stack)
redis_stack.add_dependency(network_stack)

app.synth()
