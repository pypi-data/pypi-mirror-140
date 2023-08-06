import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post166"
version_tuple = (0, 1, 0, 166)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post166")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post40"
data_version_tuple = (0, 1, 0, 40)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post40")
except ImportError:
    pass
data_git_hash = "77a16e896d3f7091b564ec6ad368a8571e2fed02"
data_git_describe = "0.1.0-40-g77a16e8"
data_git_msg = """\
commit 77a16e896d3f7091b564ec6ad368a8571e2fed02
Merge: efd9817 1cc9220
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Mon Feb 28 15:13:01 2022 +0100

    Merge pull request #462 from silabs-halfdan/rvfi_intr_multibit
    
    Multibit rvfi_intr

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
