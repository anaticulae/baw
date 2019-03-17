from os.path import exists
from os.path import join
from subprocess import run

import pytest

from tests import PROJECT
from tests import skip_longrunning


@skip_longrunning
def test_creating_venv(tmpdir):
    completed = run(
        'baw --init xkcd "Longtime project"',
        cwd=tmpdir,
        shell=True,
    )
    assert completed.returncode == 0, completed.stderr

    assert exists(join(tmpdir, '.git'))


if __name__ == "__main__":
    test_creating_venv()
