# Black and White

## Semantic Release

Format of commit message:

```
<tag>(scope): subject

body

footer
```

### Tags

* feat: A new feature
* fix: A bug fix
* docs: Documentation only changes
* style: Changes that do not affect the meaning of the code, e.g. whitespaces
* refactor: No functional change
* perf: A change that improves performances
* test: Add missing or correcting existing test
* chore: Changes to the buildprocess or auxiliary tools, e.g. doc generation

### Subject

* use imperative, present tense: "Change"
* dont use capitalize first letter
* no dot (.) at the end

### Body

* motivation for the change and contrast to old behavior

### Footer

* BREAKING CHANGE:
* Solves, refer etc.

## Docker

```
repository = os.environ.get(
    'BAW_PIPELINE_REPO',
    '169.254.149.20:6001',
)
imagename = os.environ.get(
    'BAW_PIPELINE_NAME',
    'arch_python_baw',
)
version = os.environ.get(
    'BAW_PIPELINE_VERSION',
    '0.8.1',
)
name = os.environ.get(
    'BAW_PIPELINE_TEST_ARGS',
    '--privileged -u root -v $WORKSPACE:/var/workdir',
)
```
