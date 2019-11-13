import os

import baw
import baw.runtime
import baw.utils

pytest_plugins = 'pytester'  # pylint: disable=invalid-name

if not 'PYTEST_XDIST_WORKER' in os.environ:
    # master process only
    if 'VIRTUAL' in os.environ:
        cleaninstall = 'pip uninstall baw -y && python setup.py install'
        completed = baw.runtime._run(command=cleaninstall, cwd=baw.utils.ROOT)

        assert completed.returncode == baw.utils.SUCCESS
