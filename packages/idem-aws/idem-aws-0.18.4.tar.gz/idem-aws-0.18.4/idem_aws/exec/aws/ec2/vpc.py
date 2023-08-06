import copy
from typing import Any
from typing import Dict
from typing import List


async def update_cidr_blocks(
    hub,
    ctx,
    vpc_id: str,
    old_ipv4_cidr_blocks: List[Dict[str, Any]],
    old_ipv6_cidr_blocks: List[Dict[str, Any]],
    new_ipv4_cidr_blocks: List[Dict[str, Any]],
    new_ipv6_cidr_blocks: List[Dict[str, Any]],
):
    """
    Update associated cidr blocks of a vpc. This function compares the existing(old) cidr blocks and the
    new cidr blocks. Cidr blocks that are in the new_cidr_blocks but not in the old_cidr_blocks will be associated to
    vpc. Cidr blocks that are in the old_cidr_blocks but not in the new_cidr_blocks will be disassociated from vpc.

    Args:
        hub:
        ctx:
        vpc_id: The AWS resource id of the existing vpc
        old_ipv4_cidr_blocks: The ipv4 cidr blocks on the existing vpc
        old_ipv6_cidr_blocks: The ipv6 cidr blocks on the existing vpc
        new_ipv4_cidr_blocks: The expected ipv4 cidr blocks on the existing vpc
        new_ipv6_cidr_blocks: The expected ipv6 cidr blocks on the existing vpc

    Returns:
        {"result": True|False, "comment": "A message", "ret": Dict}

    """
    # If a block is None, we'll skip updating such cidr block.
    if new_ipv4_cidr_blocks is None:
        new_ipv4_cidr_blocks = old_ipv4_cidr_blocks
    if new_ipv6_cidr_blocks is None:
        new_ipv6_cidr_blocks = old_ipv6_cidr_blocks
    result = dict(comment="", result=True, ret=None)
    ipv4_cidr_block_map = {
        cidr_block.get("CidrBlock"): cidr_block for cidr_block in old_ipv4_cidr_blocks
    }
    ipv6_cidr_block_map = {
        cidr_block.get("Ipv6CidrBlock"): cidr_block
        for cidr_block in old_ipv6_cidr_blocks
    }
    cidr_blocks_to_add = []
    ipv4_cidr_block_results = copy.deepcopy(ipv4_cidr_block_map)
    ipv6_cidr_block_results = copy.deepcopy(ipv6_cidr_block_map)
    for cidr_block_set in new_ipv4_cidr_blocks:
        if cidr_block_set.get("CidrBlock") not in ipv4_cidr_block_map:
            cidr_blocks_to_add.append(
                hub.tool.aws.network_utils.generate_cidr_request_payload_for_vpc(
                    cidr_block_set, "ipv4"
                )
            )
            ipv4_cidr_block_results[cidr_block_set.get("CidrBlock")] = cidr_block_set
        else:
            ipv4_cidr_block_map.pop(cidr_block_set.get("CidrBlock"), None)
    for ipv6_cidr_block_set in new_ipv6_cidr_blocks:
        if ipv6_cidr_block_set.get("Ipv6CidrBlock") not in ipv6_cidr_block_map:
            cidr_blocks_to_add.append(
                hub.tool.aws.network_utils.generate_cidr_request_payload_for_vpc(
                    ipv6_cidr_block_set, "ipv6"
                )
            )
            ipv6_cidr_block_results[
                ipv6_cidr_block_set.get("Ipv6CidrBlock")
            ] = ipv6_cidr_block_set
        else:
            ipv6_cidr_block_map.pop(ipv6_cidr_block_set.get("Ipv6CidrBlock"), None)
            ipv6_cidr_block_results.pop(ipv6_cidr_block_set.get("Ipv6CidrBlock"), None)
    cidr_blocks_to_remove = list(ipv4_cidr_block_map.values()) + list(
        ipv6_cidr_block_map.values()
    )
    if (not cidr_blocks_to_remove) and (not cidr_blocks_to_add):
        return result
    if not ctx.get("test", False):
        for cidr_block in cidr_blocks_to_remove:
            ret = await hub.exec.boto3.client.ec2.disassociate_vpc_cidr_block(
                ctx, AssociationId=cidr_block.get("AssociationId")
            )
            if not ret.get("result"):
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
        for request_payload in cidr_blocks_to_add:
            ret = await hub.exec.boto3.client.ec2.associate_vpc_cidr_block(
                ctx, VpcId=vpc_id, **request_payload
            )
            if not ret.get("result"):
                result["comment"] = ret["comment"]
                result["result"] = False
                return result
    result[
        "comment"
    ] = f"Update tags: Add [{cidr_blocks_to_add}] Remove [{cidr_blocks_to_remove}]"
    result["ret"] = {
        "cidr_block_association_set": list(ipv4_cidr_block_results.values()),
        "ipv6_cidr_block_association_set": list(ipv6_cidr_block_results.values()),
    }
    return result
