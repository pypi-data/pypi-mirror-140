"""Parser module to parse gear config.json."""
import json
import pathlib
import typing as t

from flywheel_gear_toolkit import GearToolkitContext


def parse_config(
    gear_context: GearToolkitContext,
) -> t.Tuple[t.Dict, t.Dict, t.Dict]:
    """Parses gear config file and returns relevant inputs and config.

    Args:
        gear_context (GearToolkitContext): Context

    Returns:
        t.Tuple[t.Dict, t.Dict, t.Dict]:
            - File info dictionary
            - Loaded schema
            - Rules dictionary in the format <rule>:<bool>
    """
    dicom = gear_context.get_input("dicom")
    schema = dict()
    with open(gear_context.get_input_path("validation-schema"), "r") as fp:
        schema = json.load(fp)

    # Rule values are copied directly from gear config, except debug option.
    rules = gear_context.config.copy()
    rules.pop("debug")
    rules.pop("tag")

    return dicom, schema, rules
