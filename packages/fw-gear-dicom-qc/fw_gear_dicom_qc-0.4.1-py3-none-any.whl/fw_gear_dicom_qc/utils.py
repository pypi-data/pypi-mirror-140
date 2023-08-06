"""Utilities module for fw_gear_dicom_qc."""
import copy
import typing as t

from flywheel_gear_toolkit import GearToolkitContext


def create_metadata(context: GearToolkitContext, info: t.Dict, tags: t.List):
    """Populates .metadata.json.

    Args:
        context (GearToolkitContext): The gear context.
        info (t.Dict): Updated file information.
        tags (t.List): Tags to be add to input-file.
    """
    file_ = context.get_input("dicom")
    file_name = file_["location"]["name"]
    existing_info = copy.deepcopy(file_["object"]["info"])

    existing_info.update(info)

    context.update_file_metadata(
        file_name,
        {"modality": file_["object"].get("modality")},
        info=existing_info,
        tags=tags,
    )
