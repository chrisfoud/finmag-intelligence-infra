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

class S3_RDS_Elasticache(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ######################################################################################################
        # Import VPC IDs
        imported_vpc_id = ssm.StringParameter.value_from_lookup(self, '/' + common_config.ENV + '/' + config.IMPORTED_VPC_NAME + '/' + 'vpc-id')
        
        imported_vpc = ec2.Vpc.from_lookup(self, 'ImportedVpcId', vpc_id = imported_vpc_id,)

        ######################################################################################################
        # Create S3 Buckets
        for s3_conf in config.BUCKET_LIST:
            # amazonq-ignore-next-line
            bucket = s3.Bucket(self,
                s3_conf.S3_BUCKET_ID,
                bucket_name = s3_conf.S3_BUCKET_NAME,
                block_public_access = s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=s3_conf.S3_REMOVAL_POLICY,
                encryption = s3_conf.S3_ENCRYPTION,
                lifecycle_rules = s3_conf.S3_LIFECYCLE_RULES
            )

        
        ######################################################################################################
        # Create Security Groups

        for sg_conf in config.SG_LIST:
            sg = ec2.SecurityGroup(
                self, sg_conf.SG_ID,
                security_group_name = sg_conf.SG_NAME,
                description = sg_conf.SG_DESCRIPTION,
                vpc = imported_vpc,
                allow_all_outbound = sg_conf.SG_ALLOW_ALL_OUTBOUND,
                allow_all_ipv6_outbound = sg_conf.SG_ALLOW_ALL_IPV6_OUTBOUND
            )
            for ingress_rule in sg_conf.SG_INGRESS_RULES:
                sg.add_ingress_rule(
                    peer = ingress_rule.INGRESS_RULE_PEER,
                    connection = ingress_rule.INGRESS_RULE_PORT,
                    description = ingress_rule.INGRESS_RULE_DESCRIPTION
                )


        ######################################################################################################
        # Create ElastiCache
        for redis_conf in config.ELASTICACHE_LIST:

            elasticache_security_groups = ec2.SecurityGroup.from_lookup_by_name(scope, id, redis_conf.ELASTICACHE_SECURITY_GROUP_NAME, imported_vpc)

            redis_subnet_group = elasticache.CfnSubnetGroup(
                self, redis_conf.ELASTICACHE_ID + '-subnet-group',
                cache_subnet_group_name = redis_conf.ELASTICACHE_ID + '-subnet-group',
                description = "Redis Cache Subnet Group",
                subnet_ids = imported_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED).subnet_ids,
            )

            redis_auth_token = secretsmanager.Secret(self, 
                redis_conf.ELASTICACHE_AUTH_TOKEN_CFN_ID,
                description=redis_conf.ELASTICACHE_AUTH_TOKEN_DESCRIPTION,
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    password_length= redis_conf.ELASTICACHE_AUTH_TOKEN_LENGTH,
                    exclude_characters= redis_conf.ELASTICACHE_AUTH_TOKEN_EXCLUDE_CHARS
                )
            )


            # amazonq-ignore-next-line
            redis_cluster = elasticache.CfnReplicationGroup(
                self, redis_conf.ELASTICACHE_ID,
                replication_group_id = redis_conf.ELASTICACHE_ID,
                replication_group_description = redis_conf.ELASTICACHE_DESCRIPTION,
                engine = redis_conf.ELASTICACHE_ENGINE,
                cache_node_type = redis_conf.ELASTICACHE_NODE_TYPE,
                num_node_groups = redis_conf.ELASTICACHE_NUM_NODES,
                automatic_failover_enabled = redis_conf.ELASTICACHE_AUTOMATIC_FAILOVER_ENABLED,
                port = redis_conf.ELASTICACHE_PORT,
                cache_subnet_group_name = redis_subnet_group.ref,
                # amazonq-ignore-next-line
                security_group_ids = elasticache_security_groups,
                at_rest_encryption_enabled = redis_conf.ELASTICACHE_AT_REST_ENCRYPTION_ENABLED,
                transit_encryption_enabled = redis_conf.ELASTICACHE_TRANSIT_ENCRYPTION_ENABLED,
                auth_token = redis_auth_token.secret_value.unsafe_unwrap(),
            )


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