# Changelog

Every noteable change is logged here.

## v0.7.2

### Feature

* log raw value of process in verbose mode, exclude from normal mode (d024512914df)
* let stash on empty repository fail (5c21c1030f60)
* extend vim temp files to clean (c091377f7fc3)
* add pylint rcfile with project style configuration (4b92822c9052)
* extend --format to format imports of repository (b4b52cf90bf1)

### Fix

* use logging instead of print (ddfca1467794)
* stash at the first time is forbidden, when repo not exists (9a8ec75902eb)
* create command folder only when adding cmdline (d4452611055e)
* add source path, that sphinx can locate the package (05f3d433b3e3)
* always stash when running release (24f2ee8c27c0)

## v0.7.1

### Feature

* when upgrade fails, reset requirements.txt (997aa7128bcf)
* hide run from importing via outer scope (8d3650f4f991)
* add checkout files to sync them with repository state (1cb2e43041e9)
* enable fetching stdout/stderr by pytest capsys (835f7fd5318f)
* support multiple sources for code coverage due project.config (ee338fdda608)

### Fix

* sync and test is not only used for releasing (f62d9df6ea9f)
* flush error imminently to ensure log logic/order (cc79532aae76)
* remove not used shortcuts to increase simplicity (7f4922590920)
* fix not escaped special char ' (65a86077e025)

## v0.7.0

### Feature

* ensures that every operation is executed in project root (5f95546b1c44)
* split requirements in minimal(dev) and maximal(dev + doc) (1311e374690a)
* include resource into delivery, make setup independent from location (2f6c96af7a9d)
* support commands with only long names (e26aa98c84e5)
* add feature to drop release (24f08df39ed0)
* add temps from python build process (df72ea31328c)
* always overwrite current installation (44827e67c146)
* write dependencies to requirements.txt if needed (bf847702892b)
* detect when there is nothing to stash and do nothing (c436e8a4f0f2)

### Fix

* always run --release in virtual environment (fbd49cbb47bc)
* stop upgrading process when all requirements are fulfilled (597b4256b7b8)
* ensure that --upgrade can run in a virtual environment (7688c69cb839)

## v0.6.3

### Feature

* add --upgrade option to update --requirements.txt (b9ab6a78ed29)

### Fix

* reduce verbosity of test logging (3d6abe0d61eb)
* use default run_target for running git commands (51c91f827bf8)

## v0.6.2

### Feature

* fail when --init on initialized project (4b9ee3381767)
* do not run --virtual and --sync when --init (06a6b2e14f97)
* add install command to install current project (dff9baab3fdc)
* add option to generate std command line (a976607f329c)

### Fix

* use secure https connection (6993358766fa)

## v0.6.1

### Fix

* change author mail to checkitweg (baafca845bc5)
* remove outdated __init__ template (18dc4401beca)
* run release always in virtual mode, sync before release (366191ba5161)
* extend global git ignore with vim tmp-files (0f71be5303f2)

## v0.6.0

### Feature

* ensure that cwd exists and is an folder (b16652a667f1)
* add --raw flag to avoid replacing \\ character (7d1b5b0d7d5e)
* expose VIRTUAL environment with --virtual flag (5493c64ec2cb)
* add --format-cmd to format the project (21f9ecd4fba7)
* abort release if version does not changed (c9b618899594)
* add message and return error when no release is made (c03a33255318)

### Fix

* use .tmp folder instead the old temp one (9db24a88ec62)
* publishing is complete not release (e63615e75e20)

## v0.5.3

### Feature

* add meta url to package-template (5a7556ae0fa9)
* running test in root, use custom test-tempdir (b97ec8dda0fc)

### Fix

* remove read-only flag to enable removing test tmp data. (73b064c891d7)
* ensure that tests run in virtual environment (0c903ad19c6f)

## v0.5.2

### Fix

* auto-flag. Semantic release about version-change (a926d77a6eed)

## v0.5.1

### Feature

* add optional type to --release (c1f5b1427870)
* deliver setup.py in init step (83ee8702d20b)
* inform user about error while stashing. (dded5b6a92f0)

### Fix

* do not stash while --init. There is nothing to stash (ab291d78e6d8)
* remove overriding of --stash flag (f0e3046da235)
* add missing import, remove longname from README template (fdeed29acac5)
* change default behavior from verbose to non verbose (6be17b9fd2fb)

## v0.5.0

### Feature

* use --test=fast to exclude baw-tests from unittest (94a0de4b885c)
* install baw in virtual environment (2f3cd950d960)
* --verbose leads to measure and print the runtime (85ad5db2f6e2)
* add --clean_venv-flag to clean virtual environment (6f294940bd46)
* deliver template-dependencies with installing baw (28e67fbfaf8d)
* add test-flag --fast to skip medium range tests (53698354ca9c)
* make process more stable and transparent (4d0ef684f78e)
* extend file ignore list (e46db4e71547)

### Fix

* clean up some missing refactorings (df477681d63b)
* clean virtual environment first (2c6517af8c04)
* package is available, activate skipped test (056e2398ecc3)
* record stdout/stderr of test-run (facfa6f00eaa)
* PIPE in CompletedProcess to read stdout/stderr (8dcbc3f12eee)
* correct output of skipping requirements (57324c6de2be)
* avoid error when removing python executable (84e2001ef099)
* always print test-output and if no tests return success (6d0d97db4d29)
* do not import from pytest to reduce package dependencies (dc9237d5aff6)
* __init__ file is generated by template mechanism (f72e55c478d0)
* entree point to __init__ to enable as package (c83bdfc7c99d)
* add new template files (73795f05eb53)

## v0.4.2

### Fix

* synchronize from baw-project not from local project (bf7257d87888)
* correct path to .tmp (54bf5f086972)

## v0.4.1

### Fix

* use version of current project not of baw-tool (765e4830325b)

## v0.4.0

### Feature

* sync common gitexclude via --sync, remove common (5eba7a3dac90)

### Fix

* print only when verbose or errors occurs (cfe6477024c1)
* do not stash .virtual-folder (257028ec4c9b)

## v0.3.1

### Fix

* wrong template parameter on doc-index (b65b68f16f3f)

## v0.3.0

### Feature

* add required templates for creating new repo (a1c025fc5bd9)
* replace file if content changed (11840a74b236)
* show the 10 slowest tests (7c11ee79faa5)
* clean removes .pytest_cache-folder (4f89c1043542)
* init project on empty folder (f40683cf4ec3)
* use projectname in workspace-template (3555250321f6)

### Fix

* ignore non-utf8-chars from invoked subprocess (09c946f7e727)
* ensure that parent folder of template where generated (a3de72f489d2)
* activate non running test (b4680558e21a)
* use test=cov instead of test=coverage to reduce effort (6ec025335755)
* no input return successful and print help (59d217d62afb)
* rename template to requirements.txt (bd3f21d3fa15)
* pass --test=pdb to invoke debugger after failure (293785f19c8b)
* do not generate setup.cfg on init (b88112943045)
* enable open workspace (77c66af79411)

### Documentation

* format documentation to fit into sphinx release (aee6c1062fa5)

## v0.2.0

### Feature

* use temporary config in semantic release (a8c92eead8f9)
* commit generated files as first a release (1b78d3e1c655)
* add verbose flag, no test = no error (55335b9ade25)
* add workspace-template (9f4738b0b0f1)

### Fix

* avoid bug in activation, add deactivate after execution (83d7086cc2e2)
* exit after problems while cleaning (273800dda3ac)
* wrong newlines after changing config (8ac3a0224dbb)
* use docs instead of doc-folder (5dadcab9db26)

### Documentation

* add header and cleanup (6f9a4e66058f)
* activate venv and semantic release  commit message (363c8860add6)
* make linter happy (3ab24a4992b9)

## v0.1.1

### Fix

* store stdout and stderr in completed process (80f9a52330f1)
* add missing templates to distribution (e1e0f0fb2a8e)

## v0.0.1

### Features

* Basic control: clean, doc, publish, release, sync, test, virtual
* Automated tests
* Installable
