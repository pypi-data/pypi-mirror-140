import copy


async def update_rules_in_sg(hub, ctx, created_sg_id, sg_rules, resource):
    """
    Modify, Add or Delete rules in the security group.

    Args:
         hub:
         ctx:
         created_sg_id: Security group ID to which the rules are attached.
         sg_rules: List of new security group rules
         resource: Security group resource to perform operation on
    """
    result = dict(comment="", result=True, ret=None)
    new_rules = []
    modify_rules = []
    result["comment"] = f"'{created_sg_id}' already exists"
    existing_sg_rules_result = (
        await hub.exec.boto3.client.ec2.describe_security_group_rules(
            ctx,
            Filters=[{"Name": "group-id", "Values": [created_sg_id]}],
        )
    )
    if existing_sg_rules_result["result"]:
        existing_sg_rules = existing_sg_rules_result["ret"].get("SecurityGroupRules")
        delete_egress_sg_rule_ids = []
        delete_ingress_sg_rule_ids = []
        for rule in existing_sg_rules:
            if rule["IsEgress"]:
                delete_egress_sg_rule_ids.append(rule["SecurityGroupRuleId"])
            else:
                delete_ingress_sg_rule_ids.append(rule["SecurityGroupRuleId"])
        if existing_sg_rules != sg_rules:
            for security_grp_rule in sg_rules:
                if "SecurityGroupRuleId" in security_grp_rule:
                    if security_grp_rule["IsEgress"]:
                        delete_egress_sg_rule_ids.remove(
                            security_grp_rule["SecurityGroupRuleId"]
                        )
                    else:
                        delete_ingress_sg_rule_ids.remove(
                            security_grp_rule["SecurityGroupRuleId"]
                        )
                    if security_grp_rule not in existing_sg_rules:
                        modify_rules.append(security_grp_rule)
                else:
                    new_rules.append(security_grp_rule)
        if new_rules:
            new_rules_dict = hub.tool.aws.security_group_utils.convert_sg_rules_to_ingress_and_egress(
                new_rules
            )
            existing_rules_dict = hub.tool.aws.security_group_utils.convert_sg_rules_to_ingress_and_egress(
                existing_sg_rules
            )
            existing_ingress_rules = existing_rules_dict["ingress"]
            converted_ingress_existed_rules = (
                hub.tool.aws.security_group_utils.remove_unwanted_attributes_from_rule(
                    existing_ingress_rules
                )
            )
            for rule in converted_ingress_existed_rules:
                rule.pop("SecurityGroupRuleId", None)
            if new_rules_dict["ingress"]:
                new_ingress_rules = new_rules_dict["ingress"]
                final_ingress_rules = [
                    item
                    for item in new_ingress_rules
                    if item not in converted_ingress_existed_rules
                ]
                new_ingress_rules = hub.tool.aws.security_group_utils.remove_unwanted_attributes_from_rule(
                    final_ingress_rules
                )
                ingress_result = (
                    await hub.exec.boto3.client.ec2.authorize_security_group_ingress(
                        ctx,
                        GroupId=created_sg_id,
                        IpPermissions=new_ingress_rules,
                    )
                )

                if not ingress_result[
                    "result"
                ] and "InvalidPermission.Duplicate" not in str(
                    ingress_result["comment"]
                ):
                    result["comment"] = ingress_result["comment"]
                    result["result"] = False
            if new_rules_dict["egress"]:
                new_egress_rules = hub.tool.aws.security_group_utils.remove_unwanted_attributes_from_rule(
                    new_rules_dict["egress"]
                )
                existing_egress_rules = existing_rules_dict["egress"]
                converted_egress_existed_rules = hub.tool.aws.security_group_utils.remove_unwanted_attributes_from_rule(
                    existing_egress_rules
                )
                for rule in converted_egress_existed_rules:
                    rule.pop("SecurityGroupRuleId", None)
                final_egress_rules = [
                    item
                    for item in new_egress_rules
                    if item not in converted_egress_existed_rules
                ]
                egress_result = (
                    await hub.exec.boto3.client.ec2.authorize_security_group_egress(
                        ctx,
                        GroupId=created_sg_id,
                        IpPermissions=final_egress_rules,
                    )
                )
                if not egress_result[
                    "result"
                ] and "InvalidPermission.Duplicate" not in str(
                    egress_result["comment"]
                ):
                    result["comment"] = egress_result["comment"]
                    result["result"] = False
        if modify_rules:
            new_modified_rules = []
            existing_sg_rules_copy = copy.deepcopy(existing_sg_rules)
            for rule in existing_sg_rules_copy:
                rule.pop("SecurityGroupRuleId", None)
            final_modified_rules = [
                item for item in modify_rules if item not in existing_sg_rules_copy
            ]
            for modify_rule in final_modified_rules:
                new_modified_rule = dict(
                    SecurityGroupRuleId=None, SecurityGroupRule=None
                )
                new_modified_rule["SecurityGroupRuleId"] = modify_rule[
                    "SecurityGroupRuleId"
                ]
                updated_rule = {}
                if modify_rule.get("IpProtocol"):
                    updated_rule["IpProtocol"] = modify_rule.get("IpProtocol")
                if modify_rule.get("FromPort"):
                    updated_rule["FromPort"] = modify_rule.get("FromPort")
                if modify_rule.get("ToPort"):
                    updated_rule["ToPort"] = modify_rule.get("ToPort")
                if modify_rule.get("CidrIpv4"):
                    updated_rule["CidrIpv4"] = modify_rule.get("CidrIpv4")
                if modify_rule.get("CidrIpv6"):
                    updated_rule["CidrIpv6"] = modify_rule.get("CidrIpv6")
                if modify_rule.get("PrefixListId"):
                    updated_rule["PrefixListId"] = modify_rule.get("PrefixListId")
                if modify_rule.get("ReferencedGroupId"):
                    updated_rule["ReferencedGroupId"] = modify_rule.get(
                        "ReferencedGroupId"
                    )
                if modify_rule.get("Description"):
                    updated_rule["Description"] = modify_rule.get("Description")
                new_modified_rule["SecurityGroupRule"] = updated_rule
                new_modified_rules.append(new_modified_rule)
            modify_rules_result = (
                await hub.exec.boto3.client.ec2.modify_security_group_rules(
                    ctx,
                    GroupId=created_sg_id,
                    SecurityGroupRules=new_modified_rules,
                )
            )
            if not modify_rules_result[
                "result"
            ] and "InvalidPermission.Duplicate" not in str(
                modify_rules_result["comment"]
            ):
                result["comment"] = modify_rules_result["comment"]
                result["result"] = False
        if delete_ingress_sg_rule_ids:
            delete_ingress_result = resource.revoke_ingress(
                SecurityGroupRuleIds=delete_ingress_sg_rule_ids
            )
            if not delete_ingress_result["Return"]:
                result["comment"] = delete_ingress_result["ResponseMetadata"]
                result["result"] = False
        if delete_egress_sg_rule_ids:
            delete_egress_result = resource.revoke_egress(
                SecurityGroupRuleIds=delete_egress_sg_rule_ids
            )
            if not delete_egress_result["Return"]:
                result["comment"] = delete_egress_result["ResponseMetadata"]
                result["result"] = False
    else:
        result["comment"] = existing_sg_rules_result["comment"]
        result["result"] = False
    return result
