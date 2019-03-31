# Changelog

Every noteable change is logged here.

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
