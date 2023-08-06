import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post173"
version_tuple = (0, 1, 0, 173)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post173")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post47"
data_version_tuple = (0, 1, 0, 47)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post47")
except ImportError:
    pass
data_git_hash = "1fa469ac7e6511e2c3be692bdb0f07890c720e8e"
data_git_describe = "0.1.0-47-g1fa469a"
data_git_msg = """\
commit 1fa469ac7e6511e2c3be692bdb0f07890c720e8e
Merge: 77a16e8 36c961e
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Mon Feb 28 16:30:12 2022 +0100

    Merge pull request #440 from michael-platzer/xif-mem-iface
    
    Add XIF memory interface

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
