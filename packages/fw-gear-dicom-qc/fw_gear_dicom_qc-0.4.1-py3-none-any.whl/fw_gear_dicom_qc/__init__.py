"""The fw_gear_dicom_qc package."""
from importlib import metadata

pkg_name = __package__
try:  # pragma: no cover
    __version__ = metadata.version(__package__)
except:  # pragma: no cover
    try:
        __version__ = metadata.version(__package__.replace("_", "-"))
    except:
        __version__ = "0.1.0"
