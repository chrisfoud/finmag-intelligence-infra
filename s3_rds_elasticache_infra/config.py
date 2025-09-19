from aws_cdk import (
    aws_s3 as s3,
    RemovalPolicy,
    Duration,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_ssm as ssm,
)
from dataclasses import dataclass
import common_config
import network_infra.config as network_config

IMPORTED_VPC_NAME = network_config.INTELLIGENCE_VPC.VPC_NAME

@dataclass
class S3Config:
    S3_BUCKET_ID: str
    S3_BUCKET_NAME: str
    S3_BLOCK_PUBLIC_ACCESS: s3.BlockPublicAccess
    S3_REMOVAL_POLICY: RemovalPolicy
    S3_ENCRYPTION: s3.BucketEncryption
    S3_LIFECYCLE_RULES: list[s3.LifecycleRule]

@dataclass
class RedisConfig:
    REDIS_ID: str
    REDIS_DESCRIPTION: str
    REDIS_ENGINE: str
    REDIS_NODE_TYPE: str
    REDIS_NUM_NODES: int
    REDIS_AUTOMATIC_FAILOVER_ENABLED: bool
    REDIS_PORT: int
    REDIS_SECURITY_GROUP_IDS: list[str]
    REDIS_AT_REST_ENCRYPTION_ENABLED: bool
    REDIS_TRANSIT_ENCRYPTION_ENABLED: bool
    REDIS_AUTH_TOKEN_CFN_ID: str
    REDIS_AUTH_TOKEN_DESCRIPTION: str
    REDIS_AUTH_TOKEN_LENGTH: int
    REDIS_AUTH_TOKEN_EXCLUDE_CHARS: str

    
@dataclass
class RDSConfig:
    RDS_ID: str
    RDS_DATABASE_NAME: str
    RDS_USERNAME: str
    RDS_ENGINE_VERSION: rds.PostgresEngineVersion
    RDS_INSTANCE_TYPE: str
    RDS_SECURITY_GROUP_NAME: list[str]
    RDS_ALLOCATED_STORAGE: int
    RDS_DATABASE_NAME: str


#################################################################
"""
Configuration for S3 bucket.

Defines bucket characteristics including name, public access, removal policy, encryption and lifecycle

"""
INTELLIGENCE_BUCKET = S3Config(
    S3_BUCKET_ID = 'IntelligenceBucket',
    S3_BUCKET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME +'-s3',  # Specify your desired bucket name
    S3_BLOCK_PUBLIC_ACCESS = s3.BlockPublicAccess.BLOCK_ALL ,  # Block all public access
    S3_REMOVAL_POLICY = RemovalPolicy.DESTROY,
    S3_ENCRYPTION = s3.BucketEncryption.S3_MANAGED,  # Enable S3 managed encryption
    S3_LIFECYCLE_RULES = [s3.LifecycleRule(abort_incomplete_multipart_upload_after=Duration.days(7))]
)

BUCKET_LIST = []


#################################################################

INTELLIGENCE_REDIS_CACHE = RedisConfig(
    REDIS_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-Redis-Cache',
    REDIS_DESCRIPTION = 'Redis Cache for RDS postgre',
    REDIS_ENGINE = 'redis',
    REDIS_NODE_TYPE = 'cache.t4g.micro',
    REDIS_NUM_NODES = 1,
    REDIS_AUTOMATIC_FAILOVER_ENABLED = False,
    REDIS_PORT = 6379,
    REDIS_SECURITY_GROUP_IDS = network_config.INTELLIGENCE_SG_REDIS.SG_NAME,
    REDIS_AT_REST_ENCRYPTION_ENABLED= True,   # Enable encryption at rest
    REDIS_TRANSIT_ENCRYPTION_ENABLED= True,   # Enable encryption in transit
    # Auth token for Redis
    REDIS_AUTH_TOKEN_CFN_ID  = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-redis-auth-token',
    REDIS_AUTH_TOKEN_DESCRIPTION = 'Redis Auth Token',
    REDIS_AUTH_TOKEN_LENGTH  = 32,
    REDIS_AUTH_TOKEN_EXCLUDE_CHARS = r'/@"\ '
)

REDIS_LIST = [INTELLIGENCE_REDIS_CACHE]


#################################################################

INTELLIGENCE_RDS_INSTANCE = RDSConfig(
    RDS_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-postgre-RDS',
    RDS_DATABASE_NAME= 'stagintelligencedb',
    RDS_USERNAME = 'XXXXX',
    RDS_ENGINE_VERSION = rds.PostgresEngineVersion.VER_16_3,
    RDS_INSTANCE_TYPE = 't4g.small',
    RDS_SECURITY_GROUP_NAME = [network_config.INTELLIGENCE_SG_RDS.SG_NAME],
    RDS_ALLOCATED_STORAGE = 20
    )

RDS_LIST = [INTELLIGENCE_RDS_INSTANCE]