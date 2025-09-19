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


##############################################################################################
                            # VPC Configurations #
##############################################################################################

INTELLIGENCE_VPC = VpcConfig(
    VPC_ID = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-vpc',
    VPC_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-vpc',
    VPC_CIDR = '10.0.0.0/16',    # VPC's CIDR block range
    MAX_AZS = 3,                 # Maximum number of Availability Zones to deploy
    NAT_GATEWAYS = 0,            # Number of NAT Gateways to deploy
    INTERNET_GATEWAY = False,     # Create an IGW for public access
    SUBNET_LIST = [
        SubnetConfig(
            SUBNET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-egress-ext-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 24
        ),
        
        SubnetConfig(
            SUBNET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-egress-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 24
        ),
        SubnetConfig(
            SUBNET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-isolated-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_ISOLATED,
            SUBNET_MASK = 24
        ),
        SubnetConfig(
            SUBNET_NAME = common_config.ENV + '-' + common_config.COMMON_NAME + '-' + common_config.APP_NAME + '-tgw-',
            SUBNET_TYPE = ec2.SubnetType.PRIVATE_WITH_EGRESS,
            SUBNET_MASK = 24
        )
    ]
)


VPC_LIST = [INTELLIGENCE_VPC]
