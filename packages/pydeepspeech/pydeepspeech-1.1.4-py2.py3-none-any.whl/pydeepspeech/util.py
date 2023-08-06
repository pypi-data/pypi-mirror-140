# type: ignore
import os
from distutils.version import LooseVersion

import pip

if LooseVersion(pip.__version__) < LooseVersion("10"):
    # older pip version
    from pip.utils.appdirs import (  # pylint: disable=import-error,no-name-in-module
        user_cache_dir,
    )
else:
    # newer pip version
    from pip._internal.utils.appdirs import user_cache_dir


# create your program's directory
def get_appdatadir() -> str:
    return os.path.join(user_cache_dir("pip"), "pydeepspeech_models")
