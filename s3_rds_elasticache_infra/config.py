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
class ElasticacheConfig:
    ELASTICACHE_ID: str
    ELASTICACHE_DESCRIPTION: str
    ELASTICACHE_ENGINE: str
    ELASTICACHE_NODE_TYPE: str
    ELASTICACHE_NUM_NODES: int
    ELASTICACHE_AUTOMATIC_FAILOVER_ENABLED: bool
    ELASTICACHE_PORT: int
    ELASTICACHE_PARAMETER_GROUP_NAME: str
    ELASTICACHE_SUBNET_GROUP_NAME: str
    ELASTICACHE_SECURITY_GROUP_NAME: str
    ELASTICACHE_AT_REST_ENCRYPTION_ENABLED: bool
    ELASTICACHE_TRANSIT_ENCRYPTION_ENABLED: bool
    ELASTICACHE_AUTH_TOKEN_CFN_ID: str
    ELASTICACHE_AUTH_TOKEN_DESCRIPTION: str
    ELASTICACHE_AUTH_TOKEN_LENGTH: int
    ELASTICACHE_AUTH_TOKEN_EXCLUDE_CHARS: str

@dataclass
class IngressRuleConfig:
    INGRESS_RULE_PEER: ec2.IPeer
    INGRESS_RULE_PORT: ec2.Port
    INGRESS_RULE_DESCRIPTION: str 

@dataclass
class SgConfig:
    SG_ID: str
    SG_NAME: str
    SG_DESCRIPTION: str
    SG_ALLOW_ALL_OUTBOUND: bool
    SG_ALLOW_ALL_IPV6_OUTBOUND: bool
    SG_INGRESS_RULES: list[IngressRuleConfig]
    
@dataclass
class RDSConfig:
    RDS_ID: str
    RDS_USERNAME: str
    RDS_ENGINE_VERSION: rds.PostgresEngineVersion
    RDS_INSTANCE_TYPE: str
    RDS_SECURITY_GROUP_NAME: list[str]
    RDS_ALLOCATED_STORAGE: int
    RDS_STORAGE_TYPE: rds.StorageType
    RDS_MULTI_AZ: bool
    RDS_SUBNET_GROUP_NAME: str
    RDS_DATABASE_NAME: str
    RDS_MASTER_USERNAME: str
    RDS_MASTER_USER_PASSWORD_CFN_ID: str
    RDS_MASTER_USER_PASSWORD_DESCRIPTION: str
    RDS_BACKUP_RETENTION: Duration
    RDS_DELETION_PROTECTION: bool
   

#################################################################
"""
Configuration for S3 bucket.

Defines bucket characteristics including name, public access, removal policy, encryption and lifecycle

"""
INTELLIGENCE_BUCKET = S3Config(
    S3_BUCKET_ID = 'IntelligenceBucket',
    S3_BUCKET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME +'-s3',  # Specify your desired bucket name
    S3_BLOCK_PUBLIC_ACCESS = s3.BlockPublicAccess.BLOCK_ALL ,  # Block all public access
    S3_REMOVAL_POLICY = RemovalPolicy.RETAIN,
    S3_ENCRYPTION = s3.BucketEncryption.S3_MANAGED,  # Enable S3 managed encryption
    S3_LIFECYCLE_RULES = [s3.LifecycleRule(abort_incomplete_multipart_upload_after=Duration.days(7))]
)

BUCKET_LIST = [INTELLIGENCE_BUCKET]


################################################################
"""
Configuration for ElastiCache.

Defines ElastiCache characteristics including engine, node type, version, number of nodes, port, parameter group, subnet group, and security group.
"""

INTELLIGENCE_REDIS_CACHE = ElasticacheConfig(
    ELASTICACHE_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-Redis-Cache',
    ELASTICACHE_DESCRIPTION = 'Redis Cache for RDS postgre',
    ELASTICACHE_ENGINE = 'redis',
    ELASTICACHE_NODE_TYPE = 'cache.t4g.micro',
    ELASTICACHE_NUM_NODES = 1,
    ELASTICACHE_AUTOMATIC_FAILOVER_ENABLED = False,
    ELASTICACHE_PORT = 6379,
    ELASTICACHE_PARAMETER_GROUP_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-redis-params',
    ELASTICACHE_SUBNET_GROUP_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-redis-subnet-group',
    ELASTICACHE_SECURITY_GROUP_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-redis-sg',
    ELASTICACHE_AT_REST_ENCRYPTION_ENABLED= True,   # Enable encryption at rest
    ELASTICACHE_TRANSIT_ENCRYPTION_ENABLED= True,   # Enable encryption in transit
    # Auth token for Redis
    ELASTICACHE_AUTH_TOKEN_CFN_ID  = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-redis-auth-token',
    ELASTICACHE_AUTH_TOKEN_DESCRIPTION = 'Redis Auth Token',
    ELASTICACHE_AUTH_TOKEN_LENGTH  = 32,
    ELASTICACHE_AUTH_TOKEN_EXCLUDE_CHARS = r'/@"\ '
)

ELASTICACHE_LIST = [INTELLIGENCE_REDIS_CACHE]



INTELLIGENCE_SG_RDS = SgConfig(
    SG_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-rds-sg',
    SG_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-rds-sg',
    SG_DESCRIPTION = 'ALB security group',
    SG_ALLOW_ALL_OUTBOUND = True,
    SG_ALLOW_ALL_IPV6_OUTBOUND = True,
    SG_INGRESS_RULES = [
        IngressRuleConfig(
            INGRESS_RULE_PEER = ec2.Peer.any_ipv4(),
            INGRESS_RULE_PORT = ec2.Port.tcp(80),
            INGRESS_RULE_DESCRIPTION = 'HTTP'
        ),
        IngressRuleConfig(
            INGRESS_RULE_PEER = ec2.Peer.any_ipv6(),
            INGRESS_RULE_PORT = ec2.Port.tcp(80),
            INGRESS_RULE_DESCRIPTION = 'HTTP'
        )
    ]
)

SG_LIST = [INTELLIGENCE_SG_RDS]

#################################################################

# amazonq-ignore-next-line
INTELLIGENCE_RDS_INSTANCE = RDSConfig(
    RDS_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-RDS',
    RDS_USERNAME = 'XXXXX',
    RDS_ENGINE_VERSION = rds.PostgresEngineVersion.VER_16_3,
    RDS_INSTANCE_TYPE = 't4g.small',
    RDS_SECURITY_GROUP_NAME = [INTELLIGENCE_SG_RDS.SG_NAME],
    RDS_ALLOCATED_STORAGE = 20,
    )

RDS_LIST = [INTELLIGENCE_RDS_INSTANCE]