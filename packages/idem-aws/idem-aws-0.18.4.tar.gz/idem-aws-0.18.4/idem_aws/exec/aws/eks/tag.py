from typing import Any
from typing import Dict


async def update_eks_tags(
    hub,
    ctx,
    resource_arn,
    old_tags: Dict[str, Any],
    new_tags: Dict[str, Any],
):
    """

    Args:
        hub:
        ctx:
        resource_arn: aws resource arn
        old_tags: Dict of old tags
        new_tags: Dict of new tags

    Returns:
        {"result": True|False, "comment": "A message", "ret": None}

    """
    tags_to_add = {}
    tags_to_remove = []
    if new_tags is not None:
        for tag in new_tags:
            if new_tags[tag] == old_tags.get(tag):
                del old_tags[tag]
            else:
                tags_to_add.update({tag: new_tags.get(tag)})
        tags_to_remove = list(old_tags.keys())

    result = dict(comment="", result=True, ret=None)
    if tags_to_remove:
        delete_ret = await hub.exec.boto3.client.eks.untag_resource(
            ctx, resourceArn=resource_arn, tagKeys=tags_to_remove
        )
        if not delete_ret["result"]:
            result["comment"] = delete_ret["comment"]
            result["result"] = False
            return result
        result["ret"] = delete_ret["ret"]
    if tags_to_add:
        add_ret = await hub.exec.boto3.client.eks.tag_resource(
            ctx, resourceArn=resource_arn, tags=tags_to_add
        )
        if not add_ret["result"]:
            result["comment"] = add_ret["comment"]
            result["result"] = False
            return result
        result["ret"] = add_ret["ret"]

    result["comment"] = f"Update tags: Add [{tags_to_add}] Remove [{tags_to_remove}]"
    return result
