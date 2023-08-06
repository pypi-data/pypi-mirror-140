def convert_sg_rules_to_ingress_and_egress(hub, sg_rules: list):
    """
    Convert list of security group rules into egress and ingress list

     Args:
        hub: required for functions in hub
        sg_rules: list of security group rules

    Returns: {"ingress": List, "egress": List}
    """
    result = {"ingress": None, "egress": None}
    ingress = []
    egress = []
    for sg_rule in sg_rules:
        if sg_rule.get("CidrIpv4"):
            cidr_ip = sg_rule["CidrIpv4"]
            sg_rule["IpRanges"] = [{"CidrIp": cidr_ip}]
        elif sg_rule.get("CidrIpv6"):
            cidr_ip = sg_rule["CidrIpv6"]
            sg_rule["Ipv6Ranges"] = [{"CidrIpv6": cidr_ip}]
        if bool(sg_rule["IsEgress"]):
            egress.append(sg_rule)
        else:
            ingress.append(sg_rule)
    result["ingress"] = ingress
    result["egress"] = egress
    return result


def remove_unwanted_attributes_from_rule(hub, rules: list):
    """
    Remove unwanted params from list of rules

     Args:
        hub: required for functions in hub
        rules: list of security group rules

    Returns: A list of security group rules
    """
    for rule in rules:
        rule.pop("IsEgress", None)
        rule.pop("Tags", None)
        rule.pop("CidrIpv4", None)
        rule.pop("CidrIpv6", None)
        rule.pop("GroupId", None)
        rule.pop("GroupOwnerId", None)
    return rules
