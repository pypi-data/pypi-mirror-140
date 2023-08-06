import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post158"
version_tuple = (0, 1, 0, 158)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post158")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post32"
data_version_tuple = (0, 1, 0, 32)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post32")
except ImportError:
    pass
data_git_hash = "b8dea46f8da85dad209f5d8f73bfbfc5d345e61c"
data_git_describe = "0.1.0-32-gb8dea46"
data_git_msg = """\
commit b8dea46f8da85dad209f5d8f73bfbfc5d345e61c
Merge: 7240216 097a84d
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Fri Feb 25 14:14:46 2022 +0100

    Merge pull request #459 from silabs-halfdan/doc_rvfi_intr_multibit
    
    Made rvfi_intr multibit

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
