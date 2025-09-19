from aws_cdk import (
    Stack,   # Base class for all CDK stacks
    aws_ec2 as ec2,  # EC2 inventory source
    aws_ssm as ssm,
    Tags

)

from constructs import Construct  # CDK Construct base class
from network_infra import config    # Configuration parameters
import common_config


class NetworkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)


###################################################################################
                                     # VPC #
###################################################################################

        ## VPC Configuration
        vpcs = {}
        for vpc_conf in config.VPC_LIST:
            vpc = ec2.Vpc(
                self, vpc_conf.VPC_ID,
                vpc_name = vpc_conf.VPC_NAME,
                ip_addresses = ec2.IpAddresses.cidr(vpc_conf.VPC_CIDR),   # VPC's CIDR block range
                max_azs = vpc_conf.MAX_AZS,                               # Deploy across 3 Availability Zones
                nat_gateways = vpc_conf.NAT_GATEWAYS,                     # Deploy number of NAT Gateways
                create_internet_gateway = vpc_conf.INTERNET_GATEWAY,      # Create an IGW for public access
                subnet_configuration = [
                    ec2.SubnetConfiguration(
                        name = subnet.SUBNET_NAME,
                        subnet_type = subnet.SUBNET_TYPE,
                        cidr_mask = subnet.SUBNET_MASK
                    )for subnet in vpc_conf.SUBNET_LIST
                ]
            )

            vpcs[vpc_conf.VPC_NAME] = vpc
            
            vpc_id_parameter = ssm.StringParameter(
                self, f'{vpc_conf.VPC_NAME}-vpc-id',
                parameter_name = '/' + common_config.ENV + '/' + vpc_conf.VPC_NAME + '/' + 'vpc-id',
                string_value = vpc.vpc_id,
                description = 'VPC ID Parameter'
            )

        
        ######################################################################################################
        # Create Security Groups



        for sg_conf in config.SG_LIST:
            
            sg_vpc = vpcs[sg_conf.SG_VPC_NAME]

            sg = ec2.SecurityGroup(
                self, sg_conf.SG_ID,
                security_group_name = sg_conf.SG_NAME,
                description = sg_conf.SG_DESCRIPTION,
                vpc = sg_vpc,
                allow_all_outbound = sg_conf.SG_ALLOW_ALL_OUTBOUND,
                allow_all_ipv6_outbound = sg_conf.SG_ALLOW_ALL_IPV6_OUTBOUND
            )
            for ingress_rule in sg_conf.SG_INGRESS_RULES:
                sg.add_ingress_rule(
                    peer = ingress_rule.INGRESS_RULE_PEER,
                    connection = ingress_rule.INGRESS_RULE_PORT,
                    description = ingress_rule.INGRESS_RULE_DESCRIPTION
                )