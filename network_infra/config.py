from aws_cdk import (
    Stack,   # Base class for all CDK stacks
    aws_ec2 as ec2  # EC2 inventory source
    
)

from dataclasses import dataclass
import common_config


#################################################
             # VPC Datastructure #
#################################################

@dataclass
class SubnetConfig:
    SUBNET_NAME: str
    SUBNET_TYPE: ec2.SubnetType
    SUBNET_MASK: int

@dataclass
class VpcConfig:
    VPC_ID: str
    VPC_NAME: str
    VPC_CIDR: str
    MAX_AZS: int
    NAT_GATEWAYS: int
    INTERNET_GATEWAY: bool
    SUBNET_LIST: list[SubnetConfig]

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
    



##############################################################################################
                            # VPC Configurations #
##############################################################################################

INTELLIGENCE_VPC = VpcConfig(
    VPC_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-vpc',
    VPC_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-vpc',
    VPC_CIDR = '10.110.0.0/16',    # VPC's CIDR block range
    MAX_AZS = 3,                 # Maximum number of Availability Zones to deploy
    NAT_GATEWAYS = 0,            # Number of NAT Gateways to deploy
    INTERNET_GATEWAY = False,     # Create an IGW for public access
    SUBNET_LIST = [
        SubnetConfig(
            SUBNET_NAME = 'egress-ext-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 24
        ),
        
        SubnetConfig(
            SUBNET_NAME = 'egress-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 22
        ),
        SubnetConfig(
            SUBNET_NAME = 'isolated-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_ISOLATED,
            SUBNET_MASK = 22
        ),
        SubnetConfig(
            SUBNET_NAME = 'tgw-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 28
        )
    ]
)


VPC_LIST = [INTELLIGENCE_VPC]


################################################################
# Security Group Configuration

INTELLIGENCE_SG_RDS = SgConfig(
    SG_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-rds-sg',
    SG_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-rds-sg',
    SG_DESCRIPTION = 'RDS security group',
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

INTELLIGENCE_SG_REDIS = SgConfig(
    SG_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-REDIS-sg',
    SG_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-REDIS-sg',
    SG_DESCRIPTION = 'Redis SG',
    SG_ALLOW_ALL_OUTBOUND = True,
    SG_ALLOW_ALL_IPV6_OUTBOUND = True,
    SG_INGRESS_RULES = [
        IngressRuleConfig(
            INGRESS_RULE_PEER = ec2.Peer.any_ipv4(),
            INGRESS_RULE_PORT = ec2.Port.tcp(6379),
            INGRESS_RULE_DESCRIPTION = 'Redis from ECS services'
        ),
    ]
)

SG_LIST = [INTELLIGENCE_SG_RDS,INTELLIGENCE_SG_REDIS]
