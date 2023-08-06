"""Main module."""
import logging
import shutil
import sys
import tempfile
import typing as t
import zipfile
from pathlib import Path

from flywheel_gear_toolkit.utils.qc import add_qc_info
from fw_file.dicom.series import DICOMCollection, fileglob

from . import rules, validation

log = logging.getLogger(__name__)


default_rules = [
    "check_series_consistency",
    "check_instance_number_uniqueness",
    "check_embedded_localizer",
    "check_bed_moving",
    "check_slice_consistency",
    "check_dciodvfy",
]


def eval_rules(
    dcms: DICOMCollection, rule_dict: t.Dict[str, bool]
) -> t.List[rules.RuleReport]:
    """Evaluate qc rules on the given file.

    Args:
        file_path (AnyPath): Path to file
        rule_dict (t.Dict[str, bool]): Dictionary of rules and whether or not
            to run them.

    Returns:
        t.List[rules.RuleReport]: Results of evalution of each rule.
    """
    # Evaluate all rules and keep list of reports.
    reports: t.List[rules.RuleReport] = []
    rules_list = [rule for rule, val in rule_dict.items() if val]
    for rule in rules_list:
        rule_fn = getattr(rules, rule)
        result = rule_fn(dcms)
        reports.append(result)

    return reports


def run(dicom: t.Dict, schema: t.Dict, rule_dict: t.Dict):
    """Run dicom-qc entrypoint."""
    log.info("Checking format of provided schema")
    if not validation.validate_schema(schema):
        # Exit immediately if schema not valid
        raise ValueError("Schema is not valid")
    log.info("Validating file.info.header")
    validation_results = validation.validate_header(
        dicom.get("object", {}).get("info", {}).get("header", {}), schema
    )
    log.info("Determining rules to run.")
    log.info("Evaluating qc rules.")
    dicom_path = dicom.get("location").get("path")
    if zipfile.is_zipfile(dicom_path):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(dicom.get("location").get("path")) as zipf:
            zipf.extractall(temp_dir)
        check_0_report = rules.check_0_byte(fileglob(temp_dir, recurse=True))
        dcms = DICOMCollection.from_dir(temp_dir, stop_when=None, force=True)
        log.info(f"Found {len(dcms)} slices in archive")
        rule_results = eval_rules(dcms, rule_dict)
        rule_results.append(check_0_report)
        shutil.rmtree(temp_dir)
    else:
        dcms = [dicom_path]
        check_0_report = rules.check_0_byte(dcms)
        dcms = DICOMCollection(stop_when=None, force=True)
        if dcms:
            dcms.extend(dcms)
        else:
            log.error("Single dicom file 0-byte")
            sys.exit(1)
        log.info(f"Found {len(dcms)} slices in archive")
        rule_results = eval_rules(dcms, rule_dict)
    validation_results = [result.__dict__ for result in validation_results]
    formatted_results = {}
    for result in rule_results:
        val = result.__dict__
        rule = val.pop("rule")
        formatted_results[rule] = val

    return validation_results, formatted_results
