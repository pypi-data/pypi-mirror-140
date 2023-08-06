"""Rules module."""
import dataclasses
import logging
import os
import shutil
import subprocess
import typing as t
from pathlib import Path

import numpy as np
from fw_file.dicom import DICOMCollection
from scipy import stats

log = logging.getLogger(__name__)


@dataclasses.dataclass
class RuleReport:
    """Class to hold rule results."""

    rule: str
    state: str
    description: str


def fail_rule(rule: str, desc: t.Optional[str] = None) -> RuleReport:
    """Helper function to mark a rule as failed.

    Args:
        rule (str): Rule name
        desc (t.Optional[str]): Description of failure.

    Returns:
        RuleReport: Generated report on given rule
    """
    log.warning(f"{rule} FAILED {desc}")
    return RuleReport(rule, "failed", desc)


def pass_rule(rule: str, desc: t.Optional[str] = None) -> RuleReport:
    """Helper function to mark a rule as passed.

    Args:
        rule (str): Rule name
        desc (t.Optional[str]): Description.

    Returns:
        RuleReport: Generated report on given rule
    """
    log.info(f"{rule} PASSED {desc or ''}")
    return RuleReport(rule, "passed", desc)


def na_rule(rule: str, desc: t.Optional[str] = None) -> RuleReport:
    """Helper function to mark a rule as na.

    Args:
        rule (str): Rule name
        desc (t.Optional[str]): Description.

    Returns:
        RuleReport: Generated report on given rule
    """
    log.info(f"{rule} NOT APPLICABLE {desc or ''}")
    return RuleReport(rule, "na", desc)


def check_0_byte(dcms: t.List[Path]) -> RuleReport:
    """Rule to check for zero-byte file.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    rule = "check_zero_byte"
    zero_paths = []
    for dcm in dcms:
        size = os.path.getsize(dcm)
        if size < 1:
            zero_paths.append(dcm)
    if len(zero_paths):
        for path in zero_paths:
            log.debug(f"Removing {path}")
            os.unlink(str(path))

        return fail_rule(
            rule, "Found zero-byte files: \n" + "\t".join([str(p) for p in zero_paths])
        )
    return pass_rule(rule)


def check_series_consistency(dcms: DICOMCollection) -> RuleReport:
    """Rule to check for consistency of slices.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    rule = "series_consistency"
    if len(dcms) < 2:
        return pass_rule(rule)
    series_uids = np.array(dcms.bulk_get("SeriesInstanceUID"))
    unique_uids = np.unique(series_uids)
    if unique_uids.shape[0] != 1:
        return fail_rule(
            rule, f"{unique_uids.shape[0]} unique SeriesInstanceUIDs found"
        )
    else:
        return pass_rule(rule)


def check_instance_number_uniqueness(dcms: DICOMCollection) -> RuleReport:
    """Rule to check for instance number uniqueness.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    rule = "instance_number_uniqueness"
    if len(dcms) < 2:
        return pass_rule(rule)

    instance_numbers = np.array(dcms.bulk_get("InstanceNumber"))
    # Check to make sure each slice has an instance number
    i_num_present = np.array([num is not None for num in instance_numbers])
    if not all(i_num_present):
        num_not_present = i_num_present[~i_num_present].shape[0]
        msg = f"InstanceNumbers not present on {num_not_present} frames."
        return fail_rule(rule, msg)

    num_unique = np.unique(instance_numbers).shape[0]
    if num_unique != instance_numbers.shape[0]:
        msg = f"Found {num_unique} InstanceNumbers across {instance_numbers.shape[0]} frames."
        return fail_rule(rule, msg)

    return pass_rule(rule)


def check_embedded_localizer(dcms: DICOMCollection) -> RuleReport:
    """Rule to check for presence of embedded localizer.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    from fw_gear_splitter.main import split_dicom

    rule = "embedded_localizer"
    if len(dcms) < 2:
        return pass_rule(rule)
    # Include pixel_data in collection
    # Run split algorithm with no group_by and attempt to split localizer
    outputs = split_dicom(  # pragma: no cover
        dcms, None, True  # Set an arbitrary file path
    )
    if len(outputs.keys()) > 1:
        return fail_rule(rule, f"Found localizer within archive.")
    else:
        return pass_rule(rule)


def check_bed_moving(dcms: DICOMCollection) -> RuleReport:
    """Rule to check for whether or not the scan bed is moving.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    rule = "bed_moving"
    if len(dcms) < 2:
        return pass_rule(rule)

    im_types = dcms.bulk_get("ImageType")
    im_type_present = ["ORIGINAL" in im_type for im_type in im_types if im_type]
    if all(im_type_present) and len(im_types) == len(im_type_present):
        ipps = dcms.bulk_get("ImagePositionPatient")
        if not all(ipps) or len(ipps) != len(dcms):
            return fail_rule(rule, "ImagePositionPatient missing.")

        unique_ipps = np.unique(ipps, axis=0)
        if unique_ipps.shape[0] != len(dcms):
            return fail_rule(rule, "Multiple slices at the same position.")
        else:
            return pass_rule(rule)
    else:
        return na_rule(
            rule, "'ORIGINAL' Image Type not in all frames, assuming not axial."
        )


def check_slice_consistency(dcms: DICOMCollection) -> RuleReport:
    """Rule to check for Slice Location consistency.

    Args:
        dcms (DICOMCollection): DICOM

    Returns:
        RuleReport: Report of result.
    """
    from fw_gear_splitter.utils import collection_to_df

    rule = "slice_consistency"
    if len(dcms) < 2:
        return pass_rule(rule)
    slices = collection_to_df(dcms, ["ImageOrientationPatient", "ImagePositionPatient"])
    # Populate locations with either SliceLocation tag, or calculating
    # using IOP and IPP
    locations = None
    iops = slices.loc[:, "ImageOrientationPatient"].dropna().values
    ipps = slices.loc[:, "ImagePositionPatient"].dropna().values
    # If we don't have IOPs or IPPs we can't perform check.  Fail
    if iops.shape[0] != slices.shape[0] or ipps.shape[0] != slices.shape[0]:
        missing_iops = slices.shape[0] - iops.shape[0]
        missing_ipps = slices.shape[0] - ipps.shape[0]
        log.info(
            f"Could not find ImageOrientationPatient on {missing_iops} slices, "
            + f"ImagePositionPatient on {missing_ipps} slices."
        )
        return fail_rule(rule, "Could not determine slice locations.")
    iops = np.array([*iops])
    ipps = np.array([*ipps])
    # Normal vector is first three values of ImageOrientationPatient
    # crossed with the second three.
    normal = np.cross(iops[:, 0:3], iops[:, 3:])
    # Get slice locations by dotting the ImagePositionPatient with
    # normal vector
    locations = np.sum(normal * ipps, axis=1)

    if len(locations) > 1:
        # Sort locations and calculate intervals between slices
        locations = np.sort(locations)
        intervals = np.diff(locations)
        # Filter out small intervals, most likely same slice.
        intervals = np.round(intervals, decimals=3)
        res = stats.mode(intervals)
        mode = res.mode[0]
        count = res.count[0]

        tol = 0.001 * mode

        abnormal_intervals = np.unique(intervals[np.abs(intervals - mode) > tol])

        if abnormal_intervals.shape[0] > 0:
            return fail_rule(
                rule,
                f"Inconsistent slice intervals.  Majority are ~{mode:.4f}mm"
                + f"({count}), but also found \n"
                + ", ".join(f"{val:.4f}" for val in abnormal_intervals),
            )
        return pass_rule(rule)


def check_dciodvfy(dcms: DICOMCollection) -> RuleReport:
    """Run dciodvfy."""
    rule = "dciodvfy"
    cmd = [shutil.which("dciodvfy"), "-new"]
    tot_errs = 0
    tot_warns = 0
    num_to_show = 1
    for i, dcm in enumerate(dcms):
        proc = subprocess.Popen(
            [*cmd, dcm.filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        err_descr = []
        n_warn = 0
        n_err = 0
        in_char_invalid_err = False
        _, err = proc.communicate()
        for line in err.decode("utf-8").split("\n"):
            # Log every line in debug mode.
            log.debug(line)
            if line.startswith("Warning"):
                n_warn += 1
            # Only print first line with Char invalid error
            elif line.startswith("Error"):
                if "Character invalid for this VR" in line:
                    if not in_char_invalid_err:
                        err_descr.append(line)
                        in_char_invalid_err = True
                        n_err += 1
                    continue
                err_descr.append(line)
                n_err += 1
            # Any other line, reset in_char_invalid_error
            in_char_invalid_err = False
        # Only show the errors for the first file.
        if i < num_to_show:
            log.warning("\n".join(err_descr))
        tot_errs += n_err
        tot_warns += n_warn
    if tot_errs:
        return fail_rule(
            rule, f"Found {tot_errs} errors and {tot_warns} warnings across archive."
        )
    return pass_rule(rule)
