bugs
====

open
----

* No open bugs.

closed
------

stash removes untracked content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

baw --venv --test=stash: It stashes every untracked change, the venv is
also an untracked change and there removed.

activating venv on windows
~~~~~~~~~~~~~~~~~~~~~~~~~~

Pay attation to the dot (.) after page with id 850 this will leads to an
error, when deactivating at the end.

.. code-block:: none

    **C:\Users\workbench** >chcp
    Aktive Codepage: 850.

.. code-block:: none

    C:\Users\workbench>chcp 850.
    Parameterformat falsch - 850.

.. code-block:: none

    :END
    if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" %_OLD_CODEPAGE% > nul
    set "_OLD_CODEPAGE="
    )

Solution:

Remove deactivation code. Better solution will to fix it with cmd in venv
package.

version tag v0.0.0 after using `baw --init`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: none

    commit 97762ada745a40fc5751f34a5e898a71f01f917d (HEAD -> refs/heads/master, tag: refs/tags/v0.0.0)
    Author: Helmut Konrad Fahrendholz <kiwi@derspanier.de>
    Date:   Fri Mar 29 08:32:21 2019 +0100

        0.0.0 automatically generated release

        v0.0.0 Initial release
