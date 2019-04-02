#==============================================================================
# C O P Y R I G H T
#------------------------------------------------------------------------------
# Copyright (c) 2019 by Helmut Konrad Fahrendholz. All rights reserved.
# Tis file is property of Helmut Konrad Fahrendholz. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
#==============================================================================

from os.path import exists
from os.path import join

from tests import assert_run
from tests import skip_cmd
from tests import skip_longrunning

@skip_cmd
def test_init_project_in_empty_folder(tmpdir):
    """Run --init in empty folder

    Intitialize project and check if documentation is generated."""
    with assert_run('baw --init xcd "I Like This Project"', cwd=tmpdir):
        assert exists(join(tmpdir, 'docs/pages/bugs.rst'))
        assert exists(join(tmpdir, 'docs/pages/changelog.rst'))
        assert exists(join(tmpdir, 'docs/pages/readme.rst'))
        assert exists(join(tmpdir, 'docs/pages/todo.rst'))


@skip_cmd
@skip_longrunning
def test_doc_command(tmpdir):
    """Run --doc command to generate documentation."""
    with assert_run('baw --init xcd "I Like This Project"', cwd=tmpdir):
        pass
    with assert_run('baw --doc', cwd=tmpdir):
        assert exists(join(tmpdir, 'docs/html'))
