import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post151"
version_tuple = (0, 1, 0, 151)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post151")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post25"
data_version_tuple = (0, 1, 0, 25)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post25")
except ImportError:
    pass
data_git_hash = "3575f67321af51a8b370116bfed80215c9490c22"
data_git_describe = "0.1.0-25-g3575f67"
data_git_msg = """\
commit 3575f67321af51a8b370116bfed80215c9490c22
Merge: f612df5 53ec738
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Thu Feb 24 16:31:18 2022 +0100

    Merge pull request #457 from silabs-halfdan/rvfi_sim_trace_cast
    
    Fixed dsim/vsim compatibility

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
