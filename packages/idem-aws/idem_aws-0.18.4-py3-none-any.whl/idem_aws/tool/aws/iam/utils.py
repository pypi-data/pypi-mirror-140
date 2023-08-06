import json
from collections import OrderedDict
from typing import Any
from typing import Dict


def convert_raw_instance_profile_to_present(
    hub, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    resource_parameters = OrderedDict(
        {
            "InstanceProfileName": "name",
            "InstanceProfileId": "id",
            "Path": "path",
            "Tags": "tags",
        }
    )

    # Name is the unique identifier for instance_profile so it is set as resource_id
    translated_resource = {"resource_id": raw_resource.get("InstanceProfileName")}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    translated_resource["roles"] = []
    for role in raw_resource.get("Roles"):
        translated_resource["roles"].append({"RoleName": role.get("RoleName")})

    return translated_resource


async def convert_raw_policy_to_present(
    hub, ctx, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    resource_parameters = OrderedDict(
        {
            "PolicyName": "name",
            "Arn": "arn",
            "PolicyId": "id",
            "Path": "path",
            "Description": "description",
            "Tags": "tags",
        }
    )

    policy_arn = raw_resource.get("Arn")
    # Arn is the unique identifier for policy so it is set as resource_id
    translated_resource = {"resource_id": policy_arn}

    default_version_id = raw_resource.get("DefaultVersionId")
    ret_get = await hub.exec.boto3.client.iam.get_policy(ctx, PolicyArn=policy_arn)
    if not ret_get["result"]:
        hub.log.warning(
            f"Failed on fetching policy with arn {policy_arn} with error {ret_get['comment']}."
        )
        return None

    ret_get_version = await hub.exec.boto3.client.iam.get_policy_version(
        ctx, PolicyArn=policy_arn, VersionId=default_version_id
    )
    if not ret_get_version["result"]:
        hub.log.warning(
            f"Failed on fetching policy document with arn {policy_arn} and version {default_version_id} "
            f"with error {ret_get_version['comment']} Describe will skip this policy and continue."
        )
        return None

    document = json.dumps(ret_get_version["ret"]["PolicyVersion"].get("Document"))
    translated_resource["policy_document"] = document
    translated_resource["default_version_id"] = default_version_id

    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    return translated_resource


def convert_raw_role_to_present(hub, raw_resource: Dict[str, Any]) -> Dict[str, Any]:
    resource_parameters = OrderedDict(
        {
            "RoleName": "name",
            "Arn": "arn",
            "RoleId": "id",
            "Path": "path",
            "Description": "description",
            "MaxSessionDuration": "max_session_duration",
            "Tags": "tags",
        }
    )

    # RoleName is the unique identifier for policy so it is set as resource_id
    translated_resource = {"resource_id": raw_resource.get("RoleName")}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    if raw_resource.get("PermissionsBoundary"):
        translated_resource["permissions_boundary"] = raw_resource.get(
            "PermissionsBoundary"
        ).get("PermissionsBoundaryArn")

    if raw_resource.get("AssumeRolePolicyDocument"):
        translated_resource["assume_role_policy_document"] = json.dumps(
            raw_resource.get("AssumeRolePolicyDocument")
        )

    return translated_resource


def convert_raw_role_policy_to_present(
    hub, raw_resource: Dict[str, Any]
) -> Dict[str, Any]:
    # Policy name is the 'name' and 'resource_id' of the role_policy
    resource_parameters = OrderedDict(
        {
            "RoleName": "role_name",
            "PolicyName": "name",
        }
    )

    # Use policy name as resource_id
    translated_resource = {"resource_id": raw_resource.get("PolicyName")}
    for parameter_raw, parameter_present in resource_parameters.items():
        if parameter_raw in raw_resource:
            translated_resource[parameter_present] = raw_resource.get(parameter_raw)

    if raw_resource.get("PolicyDocument"):
        translated_resource["policy_document"] = json.dumps(
            raw_resource.get("PolicyDocument")
        )

    return translated_resource


def convert_raw_role_policy_attachment_to_present(
    hub, role_name: str, policy_arn: str
) -> Dict[str, Any]:

    translated_resource = {"role_name": role_name, "policy_arn": policy_arn}

    return translated_resource
