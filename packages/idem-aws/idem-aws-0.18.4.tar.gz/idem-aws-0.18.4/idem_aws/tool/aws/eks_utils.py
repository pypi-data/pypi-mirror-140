from typing import Any
from typing import Dict

from dict_tools import differ


def get_resource_vpc_config_changes(
    hub, old_vpc_config: Dict, new_vpc_config: Dict
) -> Dict[str, Any]:
    """
    Returns updated resource vpc config changes

     Args:
        hub: required for functions in hub
        old_vpc_config(Dict): old resource vpc config changes
        new_vpc_config(Dict): new resource vpc config changes

    Returns: A dict with resource vpc config changes
    """
    final_vpc_config = {}
    if not old_vpc_config.get("endpointPrivateAccess") == new_vpc_config.get(
        "endpointPrivateAccess"
    ):
        final_vpc_config["endpointPrivateAccess"] = new_vpc_config.get(
            "endpointPrivateAccess"
        )

    if not old_vpc_config.get("endpointPublicAccess") == new_vpc_config.get(
        "endpointPublicAccess"
    ):
        final_vpc_config["endpointPublicAccess"] = new_vpc_config.get(
            "endpointPublicAccess"
        )

    if new_vpc_config.get("publicAccessCidrs") and not old_vpc_config.get(
        "publicAccessCidrs"
    ) == new_vpc_config.get("publicAccessCidrs"):
        final_vpc_config["publicAccessCidrs"] = new_vpc_config.get("publicAccessCidrs")
    return final_vpc_config


def update_labels(old_labels: list, new_labels: list) -> Dict[str, Any]:
    """
    Returns updated labels used in update node group config

     Args:
        old_labels(list): old labels
        new_labels(list): new labels

    Returns: A dict with labels
    """
    labels_to_add = {}
    labels_to_remove = list()
    if new_labels is not None:
        for label in new_labels:
            if new_labels[label] == old_labels.get(label):
                del new_labels[label]
            else:
                labels_to_add.update({label: new_labels.get(label)})
        labels_to_remove = list(new_labels.keys())
    final_labels = {}
    if labels_to_add:
        final_labels = {"addOrUpdateLabels": labels_to_add}
    if labels_to_remove:
        final_labels = {"removeLabels": labels_to_remove}
    return final_labels


def update_taints(old_taints: list, new_taints: list) -> Dict[str, Any]:
    """
    Returns updated taints used in update node group config

     Args:
        old_taints(list): old taints
        new_taints(list): new taints

    Returns: A dict with taints
    """
    taints_to_add = list()
    taints_to_remove = list()
    if new_taints is not None:
        for new_taint in new_taints:
            if old_taints is not None:
                is_matched = False
                for old_taint in old_taints:
                    if new_taint == old_taint:
                        taints_to_remove.append(new_taint)
                        is_matched = True
                if not is_matched:
                    taints_to_add.append(new_taint)
            else:
                taints_to_add.append(new_taint)
    final_taints = {}
    if taints_to_add:
        final_taints = {"addOrUpdateLabels": taints_to_add}
    if taints_to_remove:
        final_taints = {"removeLabels": taints_to_remove}
    return final_taints


def get_updated_node_group_config(
    hub,
    old_node_group_config: Dict,
    labels: list,
    taints: list,
    scaling_config: Dict,
    update_config: Dict,
) -> Dict[str, Any]:
    """
    Returns updated node group config

     Args:
        hub: required for functions in hub
        old_node_group_config(Dict): old node group config
        labels(list): new labels
        taints(List): new taints
        scaling_config(Dict): new scaling config
        update_config(Dict): new update config

    Returns: A dict with node group config
    """
    final_node_group_config = {}
    current_labels = update_labels(old_node_group_config.get("labels"), labels)
    if current_labels:
        final_node_group_config["labels"] = current_labels
    current_taints = update_taints(old_node_group_config.get("taints"), taints)
    if current_taints:
        final_node_group_config["taints"] = current_taints
    if differ.deep_diff(old_node_group_config.get("scalingConfig"), scaling_config):
        final_node_group_config["scalingConfig"] = scaling_config
    if differ.deep_diff(old_node_group_config.get("updateConfig"), update_config):
        final_node_group_config["updateConfig"] = update_config
    return final_node_group_config
