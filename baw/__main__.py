"""Evaluate cmd-args and execute commands"""

import baw

try:
    exit(baw.main())
except KeyboardInterrupt:
    print('\nOperation cancelled by user')
    exit(1)
