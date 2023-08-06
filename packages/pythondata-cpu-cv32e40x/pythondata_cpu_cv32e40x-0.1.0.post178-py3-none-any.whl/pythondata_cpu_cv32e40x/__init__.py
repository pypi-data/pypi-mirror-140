import os.path
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
data_location = os.path.join(__dir__, "system_verilog")
src = "https://github.com/openhwgroup/cv32e40x"

# Module version
version_str = "0.1.0.post178"
version_tuple = (0, 1, 0, 178)
try:
    from packaging.version import Version as V
    pversion = V("0.1.0.post178")
except ImportError:
    pass

# Data version info
data_version_str = "0.1.0.post52"
data_version_tuple = (0, 1, 0, 52)
try:
    from packaging.version import Version as V
    pdata_version = V("0.1.0.post52")
except ImportError:
    pass
data_git_hash = "b4edeee7ae002f80fe6e977b6f4c07f57495665d"
data_git_describe = "0.1.0-52-gb4edeee"
data_git_msg = """\
commit b4edeee7ae002f80fe6e977b6f4c07f57495665d
Merge: 97b67b6 50f6558
Author: Arjan Bink <40633348+Silabs-ArjanB@users.noreply.github.com>
Date:   Wed Mar 2 15:54:44 2022 +0100

    Merge pull request #467 from silabs-halfdan/doc_rvfi_struct_desctiption_update
    
    Updated documentation of rvfi trap and intr structs

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
