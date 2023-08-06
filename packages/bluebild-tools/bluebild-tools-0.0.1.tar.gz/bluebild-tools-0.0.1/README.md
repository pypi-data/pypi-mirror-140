# bluebild-tools

Tools around Bluebild@EPFL

## Installation

pip install bluebild-tools --upgrade

## Usage

### Check whether CuPy can be used

import bluebild_tools import as bbt

use_cupy = bbt.cupy.is_cupy_available()

You can set the MUST_CUPY environment variable to influence the behavior of the function. With MUST_CUPY unset or set to 0, the puse_cupy with be set to False if CuPy can't be used and set to True if CuPy can be used. If MUST_CUIPY is set to 1, the process will be killed if CuPy is not usable. With MUST_CUPY set to 0, no attempt will be made to use CuPy (i.e. use_cupy will be set to False, always).