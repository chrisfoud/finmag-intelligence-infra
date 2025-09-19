from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_elasticache as elasticache,
    aws_secretsmanager as secretsmanager,
    aws_rds as rds,
    RemovalPolicy
)
from typing import Any
from constructs import Construct
from s3_rds_elasticache_infra import config
import common_config

class S3(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 Buckets
        for s3_conf in config.BUCKET_LIST:
            bucket = s3.Bucket(self,
                s3_conf.S3_BUCKET_ID,
                bucket_name = s3_conf.S3_BUCKET_NAME,
                block_public_access = s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=s3_conf.S3_REMOVAL_POLICY,
                encryption = s3_conf.S3_ENCRYPTION,
                lifecycle_rules = s3_conf.S3_LIFECYCLE_RULES
            )


class Redis(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ######################################################################################################
        # Import VPC IDs
        imported_vpc_id = ssm.StringParameter.value_from_lookup(self, '/' + common_config.ENV + '/' + config.IMPORTED_VPC_NAME + '/' + 'vpc-id')
        
        imported_vpc = ec2.Vpc.from_lookup(self, 'ImportedVpcId', vpc_id = imported_vpc_id,)

        ######################################################################################################
        # Create Redis
        for redis_conf in config.REDIS_LIST:

            redis_security_groups = []
            for sg_name in redis_conf.REDIS_SECURITY_GROUP_IDS:
                redis_security_groups.append(ec2.SecurityGroup.from_lookup_by_name(self, f'ImportedSG-{sg_name}', sg_name,imported_vpc))


            redis_subnet_group = elasticache.CfnSubnetGroup(
                self, redis_conf.REDIS_ID + '-subnet-group',
                cache_subnet_group_name = redis_conf.REDIS_ID + '-subnet-group',
                description = "Redis Cache Subnet Group",
                subnet_ids = imported_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnet_ids,
            )

            redis_auth_token = secretsmanager.Secret(self, 
                redis_conf.REDIS_AUTH_TOKEN_CFN_ID,
                description=redis_conf.REDIS_AUTH_TOKEN_DESCRIPTION,
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    password_length= redis_conf.REDIS_AUTH_TOKEN_LENGTH,
                    exclude_characters= redis_conf.REDIS_AUTH_TOKEN_EXCLUDE_CHARS,
                    exclude_punctuation=True,
                    include_space=False
                )
            )


            # amazonq-ignore-next-line
            redis_cluster = elasticache.CfnReplicationGroup(
                self, redis_conf.REDIS_ID,
                replication_group_id = redis_conf.REDIS_ID,
                replication_group_description = redis_conf.REDIS_DESCRIPTION,
                engine = redis_conf.REDIS_ENGINE,
                cache_node_type = redis_conf.REDIS_NODE_TYPE,
                num_node_groups = redis_conf.REDIS_NUM_NODES,
                automatic_failover_enabled = redis_conf.REDIS_AUTOMATIC_FAILOVER_ENABLED,
                port = redis_conf.REDIS_PORT,
                cache_subnet_group_name = redis_subnet_group.ref,
                security_group_ids = [sg.security_group_id for sg in redis_security_group],
                at_rest_encryption_enabled = redis_conf.REDIS_AT_REST_ENCRYPTION_ENABLED,
                transit_encryption_enabled = redis_conf.REDIS_TRANSIT_ENCRYPTION_ENABLED,
                auth_token = redis_auth_token.secret_value.unsafe_unwrap(),
            )


class RDS(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ######################################################################################################
        # Import VPC IDs
        imported_vpc_id = ssm.StringParameter.value_from_lookup(self, '/' + common_config.ENV + '/' + config.IMPORTED_VPC_NAME + '/' + 'vpc-id')
        
        imported_vpc = ec2.Vpc.from_lookup(self, 'ImportedVpcId', vpc_id = imported_vpc_id,)

        ######################################################################################################
        # RDS Instance Creation
        for rds_conf in config.RDS_LIST:
            
            rds_security_groups = []
            for sg_name in rds_conf.RDS_SECURITY_GROUP_NAME:
                rds_security_groups.append(ec2.SecurityGroup.from_lookup_by_name(self, f'ImportedSG-{sg_name}', sg_name,imported_vpc))

            rds_subnet_group = rds.SubnetGroup(
                self, rds_conf.RDS_ID + '-subnet-group',
                vpc = imported_vpc,
                description = "RDS Subnet Group",
                vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                subnet_group_name = rds_conf.RDS_ID + '-subnet-group',
                ) 

            rds_secret = secretsmanager.Secret(
                self, rds_conf.RDS_ID + '-secret',
                generate_secret_string = secretsmanager.SecretStringGenerator(
                    exclude_characters = '"@/',
                    generate_string_key = 'password',
                    secret_string_template='{"username": "admin"}',
                    ),
                removal_policy = RemovalPolicy.DESTROY,
                secret_name = rds_conf.RDS_ID + '-secret',
                )
            
            rds_credentials = rds.Credentials.from_secret(
                secret = rds_secret,
                username = rds_conf.RDS_USERNAME
                )

            # amazonq-ignore-next-line
            rds_instance = rds.DatabaseInstance(
                self, rds_conf.RDS_ID,
                database_name = rds_conf.RDS_DATABASE_NAME,
                instance_identifier = rds_conf.RDS_ID,
                credentials = rds_credentials,
                engine = rds.DatabaseInstanceEngine.postgres(version=rds_conf.RDS_ENGINE_VERSION),
                instance_type = ec2.InstanceType(rds_conf.RDS_INSTANCE_TYPE),
                vpc = imported_vpc,
                vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                security_groups = rds_security_groups,
                allocated_storage = rds_conf.RDS_ALLOCATED_STORAGE,
                subnet_group = rds_subnet_group
            )