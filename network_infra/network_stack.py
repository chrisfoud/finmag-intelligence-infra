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
        for vpc_conf in config.VPC_LIST:
            self.vpc = ec2.Vpc(
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

            vpc_id_parameter = ssm.StringParameter(
                self, f'{vpc_conf.VPC_NAME}-vpc-id',
                parameter_name = '/' + common_config.ENV + '/' + vpc_conf.VPC_NAME + '/' + 'vpc-id',
                string_value = self.vpc.vpc_id,
                description = 'VPC ID Parameter'
            )



# ###################################################################################
#                                  # Security Groups #
# ###################################################################################


# ## Security Group Configuration
#         for sg_conf in config.SG_LIST:
#             sg = ec2.SecurityGroup(
#                 self, sg_conf.SG_ID,
#                 security_group_name = sg_conf.SG_NAME,
#                 description = sg_conf.SG_DESCRIPTION,
#                 vpc = self.vpc,
#                 allow_all_outbound = sg_conf.SG_ALLOW_ALL_OUTBOUND,             # Allow IPv4 outbound traffic
#                 allow_all_ipv6_outbound = sg_conf.SG_ALLOW_ALL_IPV6_OUTBOUND    # Allow IPv6 outbound traffic
#             )

#             for ingress_rule in sg_conf.SG_INGRESS_RULES:
#                 sg.add_ingress_rule(
#                     peer = ingress_rule.INGRESS_RULE_PEER,
#                     connection = ingress_rule.INGRESS_RULE_PORT,
#                     description = ingress_rule.INGRESS_RULE_DESCRIPTION
#                 )
            
#         tag_sg = Tags.of(self)



############################################################################################################
############################################################################################################


###################################################################################
                                 # Security Groups #
###################################################################################

# ## Load Balancer - Security Group ##
#         alb_sg = ec2.SecurityGroup(
#             self, config.LOAD_BALANCER_SG_ID,
#             security_group_name = f"{config.LOAD_BALANCER_SG_NAME}-alb-sg",
#             description = config.LOAD_BALANCER_SG_DESCRIPTION,
#             vpc = self.vpc,
#             allow_all_outbound = config.LOAD_BALANCER_SG_ALLOW_ALL_OUTBOUND,  # Allow outbound traffic
#             allow_all_ipv6_outbound = config.LOAD_BALANCER_SG_ALLOW_ALL_IPV6_OUTBOUND  # Allow IPv6 traffic
#         )

#     # Load Balancer Security Group Ingress Rule 
#     # IPv4 Ingress
#         alb_sg.add_ingress_rule(
#             peer = config.LOAD_BALANCER_SG_INGRESS_RULE_PEER_IPV4,
#             connection = config.LOAD_BALANCER_SG_INGRESS_RULE_PORT_IPV4,
#             description = config.LOAD_BALANCER_SG_INGRESS_RULE_DESCRIPTION_IPV4
#         )

#     # IPv6 Ingress
#         alb_sg.add_ingress_rule(
#             peer = config.LOAD_BALANCER_SG_INGRESS_RULE_PEER_IPV6,
#             connection = config.LOAD_BALANCER_SG_INGRESS_RULE_PORT_IPV6,
#             description = config.LOAD_BALANCER_SG_INGRESS_RULE_DESCRIPTION_IPV6
#         )


# ## Service - Security Group ##
#         service_sg = ec2.SecurityGroup(
#             self, config.SERVICE_SG_ID,
#             security_group_name = f"{config.SERVICE_SG_NAME}-svc-sg",
#             description = config.SERVICE_SG_DESCRIPTION,
#             vpc = self.vpc,
#             allow_all_outbound = config.SERVICE_SG_ALLOW_ALL_OUTBOUND,  # Allow outbound traffic
#             allow_all_ipv6_outbound = config.SERVICE_SG_ALLOW_ALL_IPV6_OUTBOUND  # Allow IPv6 traffic
#         )

#     # Service Security Group Ingress Rule
#     # Backend traffic from ALB
#         service_sg.add_ingress_rule(
#             peer = ec2.Peer.security_group_id(alb_sg.security_group_id),
#             connection = config.SERVICE_SG_INGRESS_RULE_PORT_BACKEND,
#             description = config.SERVICE_SG_INGRESS_RULE_DESCRIPTION_BACKEND,
#         )

#     # Frontend traffic from ALB
#         service_sg.add_ingress_rule(
#             peer = ec2.Peer.security_group_id(alb_sg.security_group_id),
#             connection = config.SERVICE_SG_INGRESS_RULE_PORT_FRONTEND,
#             description = config.SERVICE_SG_INGRESS_RULE_DESCRIPTION_FRONTEND
#         )


# ## Database RDS - Security Group ##
#         db_sg = ec2.SecurityGroup(
#             self, config.DATABASE_SG_ID,
#             security_group_name = f"{config.DATABASE_SG_NAME}-db-sg",
#             description = config.DATABASE_SG_DESCRIPTION,
#             vpc = self.vpc,
#             allow_all_outbound = config.DATABASE_SG_ALLOW_ALL_OUTBOUND,  # Allow outbound traffic
#             allow_all_ipv6_outbound = config.DATABASE_SG_ALLOW_ALL_IPV6_OUTBOUND  # Allow IPv6 traffic
#         )

#     # Database Security Group Ingress Rule
#         db_sg.add_ingress_rule(
#             peer = ec2.Peer.security_group_id(service_sg.security_group_id),
#             connection = config.DATABASE_SG_INGRESS_RULE_PORT,
#             description = config.DATABASE_SG_INGRESS_RULE_DESCRIPTION,
#         )


# ## Redis - Security Group ##
#         redis_sg = ec2.SecurityGroup(
#             self, config.REDIS_SG_ID,
#             security_group_name = f"{config.REDIS_SG_NAME}-redis-sg",
#             description = config.REDIS_SG_DESCRIPTION,
#             vpc = self.vpc,
#             allow_all_outbound = config.REDIS_SG_ALLOW_ALL_OUTBOUND,  # Allow outbound traffic
#             allow_all_ipv6_outbound = config.REDIS_SG_ALLOW_ALL_IPV6_OUTBOUND  # Allow IPv6 traffic
#         )

#     # Redis Security Group Ingress Rule
#         redis_sg.add_ingress_rule(
#             peer = ec2.Peer.security_group_id(service_sg.security_group_id),
#             connection = config.REDIS_SG_INGRESS_RULE_PORT_ALB,
#             description = config.REDIS_SG_INGRESS_RULE_DESCRIPTION_ALB
#         )