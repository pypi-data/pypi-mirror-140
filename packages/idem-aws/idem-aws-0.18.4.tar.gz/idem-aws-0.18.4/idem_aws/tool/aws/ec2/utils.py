from collections import OrderedDict
from typing import Any
from typing import Dict

"""
Util functions to convert raw resource state from AWS EC2 to present input format.
"""


def convert_raw_vpc_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("VpcId")
    resource_parameters = OrderedDict(
        {"InstanceTenancy": "instance_tenancy", "Tags": "tags"}
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    # The following code block is to make sure to only output the associated/associating cidr blocks and
    # dis-regard the disassociated cidr blocks.
    if raw_resource.get("CidrBlockAssociationSet"):
        ipv4_cidr_block_association_set = []
        for cidr_block in raw_resource.get("CidrBlockAssociationSet"):
            if cidr_block.get("CidrBlockState").get("State") in [
                "associated",
                "associating",
            ]:
                ipv4_cidr_block_association_set.append(cidr_block)
        resource_translated[
            "cidr_block_association_set"
        ] = ipv4_cidr_block_association_set
    if raw_resource.get("Ipv6CidrBlockAssociationSet"):
        ipv6_cidr_block_association_set = []
        for cidr_block in raw_resource.get("Ipv6CidrBlockAssociationSet"):
            if cidr_block.get("Ipv6CidrBlockState").get("State") in [
                "associated",
                "associating",
            ]:
                if "NetworkBorderGroup" in cidr_block:
                    # Translate describe output to the correct present input format
                    ipv6_cidr_block_network_border_group = cidr_block.pop(
                        "NetworkBorderGroup"
                    )
                    cidr_block[
                        "Ipv6CidrBlockNetworkBorderGroup"
                    ] = ipv6_cidr_block_network_border_group
                ipv6_cidr_block_association_set.append(cidr_block)
        resource_translated[
            "ipv6_cidr_block_association_set"
        ] = ipv6_cidr_block_association_set
    return resource_translated


def convert_raw_subnet_to_present(
    hub, raw_resource: Dict[str, Any], idem_resource_name: str = None
) -> Dict[str, Any]:
    resource_id = raw_resource.get("SubnetId")
    resource_parameters = OrderedDict(
        {
            "VpcId": "vpc_id",
            "CidrBlock": "cidr_block",
            "AvailabilityZone": "availability_zone",
            "OutpostArn": "outpost_arn",
            "Tags": "tags",
        }
    )
    resource_translated = {"name": idem_resource_name, "resource_id": resource_id}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            resource_translated[parameter_present] = raw_resource.get(parameter_raw)
    if (not raw_resource.get("AvailabilityZone")) and raw_resource.get(
        "AvailabilityZoneId"
    ):
        # Only populate availability_zone_id field when availability_zone doesn't exist
        resource_translated["availability_zone_id"] = raw_resource.get(
            "AvailabilityZoneId"
        )
    if raw_resource.get("Ipv6CidrBlockAssociationSet"):
        ipv6_cidr_block_association_set = (
            hub.tool.aws.network_utils.get_associated_ipv6_cidr_blocks(
                raw_resource.get("Ipv6CidrBlockAssociationSet")
            )
        )
        # We should only output the associated ipv6 cidr block, and theoretically there should only be one,
        # since AWS only supports one ipv6 cidr block association on a subnet
        if ipv6_cidr_block_association_set:
            resource_translated["ipv6_cidr_block"] = ipv6_cidr_block_association_set[
                0
            ].get("Ipv6CidrBlock")
    return resource_translated
