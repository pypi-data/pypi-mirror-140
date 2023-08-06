import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post176"
version_tuple = (0, 1, 0, 176)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post176")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post50"
data_version_tuple = (0, 1, 0, 50)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post50")
except ImportError:
    pass
data_git_hash = "97b67b6ccb125b0fbdd29bd1cb25e0c34b300653"
data_git_describe = "0.1.0-50-g97b67b6"
data_git_msg = """\
commit 97b67b6ccb125b0fbdd29bd1cb25e0c34b300653
Merge: 1fa469a 8662185
Author: silabs-oysteink <66771756+silabs-oysteink@users.noreply.github.com>
Date:   Mon Feb 28 19:13:48 2022 +0100

    Merge pull request #465 from Silabs-ArjanB/ArjanB_xiff
    
    Syntax fix + IF stage fix

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
