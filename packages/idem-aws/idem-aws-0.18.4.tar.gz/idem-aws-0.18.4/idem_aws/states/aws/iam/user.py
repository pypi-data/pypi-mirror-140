import copy
from collections import OrderedDict
from typing import Any
from typing import Dict

from dict_tools import differ

SERVICE = "iam"
RESOURCE = "User"

__contracts__ = ["resource"]


async def absent(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    ret = {
        "comment": "",
        "old_state": None,
        "new_state": None,
        "name": name,
        "result": True,
    }
    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, name=name)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        ret["comment"] = f"{RESOURCE} '{name}' already absent"
    else:
        try:
            before.pop("ResponseMetadata", None)
            ret["old_state"] = before
            # Attempt to delete the User
            await hub.tool.boto3.resource.exec(resource, "delete", **kwargs)
            ret["comment"] = f"Delete {RESOURCE} '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            ret["comment"] = f"{e.__class__.__name__: {e}}"
            ret["result"] = False
    return ret


async def present(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    ret = {
        "comment": "",
        "old_state": None,
        "new_state": None,
        "name": name,
        "result": True,
    }
    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, name=name)
    before = await hub.tool.boto3.resource.describe(resource)

    if before:
        ret["comment"] = f"{RESOURCE} '{name}' already exists"
        before.pop("ResponseMetadata", None)
        ret["old_state"] = before
        ret["new_state"] = copy.deepcopy(before)
    else:
        try:
            # Attempt to create the User
            await hub.tool.boto3.resource.exec(resource, "create", **kwargs)
            ret["comment"] = f"Created {RESOURCE}, '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            # User already exists
            ret["comment"] = f"{e.__class__.__name__: {e}}"

        await hub.tool.boto3.client.wait(ctx, SERVICE, "user_exists", UserName=name)

        after = await hub.tool.boto3.resource.describe(resource)
        if after:
            ret["result"] = True
            after.pop("ResponseMetadata", None)
            ret["new_state"] = after
        else:
            ret["result"] = False
    return ret


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    result = {}
    ret = await hub.exec.boto3.client.iam.list_users(ctx)

    if not ret["result"]:
        hub.log.debug(f"Could not describe user {ret['comment']}")
        return {}

    # Arn is not used for present but required for arg binding
    describe_parameters = OrderedDict(
        {
            "Arn": "arn",
            "CreateDate": "create_date",
            "PasswordLastUsed": "password_last_used",
            "Path": "path",
            "PermissionsBoundary": "permissions_boundary",
            "Tags": "tags",
            "UserId": "user_id",
            "UserName": "user_name",
        }
    )

    for user in ret["ret"]["Users"]:
        resource_name = user.get("UserName")
        # This is required to get tags for each user
        boto2_resource = hub.tool.boto3.resource.create(
            ctx, "iam", "User", resource_name
        )
        resource = await hub.tool.boto3.resource.describe(boto2_resource)
        resource_translated = []
        for parameter_old_key, parameter_new_key in describe_parameters.items():
            if resource.get(parameter_old_key) is not None:
                resource_translated.append(
                    {parameter_new_key: resource.get(parameter_old_key)}
                )
        if resource.get("PermissionsBoundary"):
            resource_translated.append(
                {
                    "permissions_boundary": resource.get("PermissionsBoundary").get(
                        "PermissionsBoundaryArn"
                    )
                }
            )
        result[resource_name] = {"aws.iam.user.present": resource_translated}
    return result
