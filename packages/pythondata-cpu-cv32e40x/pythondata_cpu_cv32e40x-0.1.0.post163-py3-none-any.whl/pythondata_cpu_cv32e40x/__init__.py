import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post163"
version_tuple = (0, 1, 0, 163)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post163")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post37"
data_version_tuple = (0, 1, 0, 37)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post37")
except ImportError:
    pass
data_git_hash = "efd9817c57272e78547754f07881fa41d30ba9b4"
data_git_describe = "0.1.0-37-gefd9817"
data_git_msg = """\
commit efd9817c57272e78547754f07881fa41d30ba9b4
Merge: a3bb291 4cf64eb
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Mon Feb 28 08:59:33 2022 +0100

    Merge pull request #461 from Silabs-ArjanB/ArjanB_mimpid2
    
    Split mimpid into major, minor,patch

"""

# Tool version info
tool_version_str = "0.0.post126"
tool_version_tuple = (0, 0, 126)
try:
    from packaging.version import Version as V
    ptool_version = V("0.0.post126")
except ImportError:
    pass


def data_file(f):
    """Get absolute path for file inside pythondata_cpu_cv32e40x."""
    fn = os.path.join(data_location, f)
    fn = os.path.abspath(fn)
    if not os.path.exists(fn):
        raise IOError("File {f} doesn't exist in pythondata_cpu_cv32e40x".format(f))
    return fn
