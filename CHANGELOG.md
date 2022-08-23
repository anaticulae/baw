# Changelog

Every noteable change is logged here.

## v0.19.5

### Fix

* update to new virtual path (8bc101e3ae4a)
* skip version determining if git is not installed (1e2d23af5fd3)
* do not print any error if git is not installed (fbea1d29ce56)

## v0.19.4

### Fix

* disable utilasafe for the moment (8a4fa93b3365)

## v0.19.3

### Feature

* ensure that pip index is trusted (f330c16a0dc2)

### Fix

* use wheel to avoid MANIFEST file for the first time (3d9a7acc725c)
* increase required utilatest version (33e78cf87121)
* add missing resource for new tar format (beb667cf58fc)

## v0.19.2

### Feature

* adjust build format (3578988acccc)

## v0.19.1

### Fix

* rename template to avoid cleaning when running clean in baw (a9e1e816eacc)

## v0.19.0

### Feature

* extend valid name list (db0d8412e0c8)
* add copyright header (0534d8303080)
* add monkeypatch and testdir as valid var names (21b37b3c350a)
* add option to open venv dir (261c79368723)
* add option to print path to console (2f777747074d)
* increase accuracy (a9f5eb5cce18)
* add method to open last test (ee0cf01f44fc)
* ignore vs code python tmp files (f3b53a2ac92b)
* append log regeneration log (909787ef7f52)
* display progress to improve user feedback (e940677f1607)
* add info option (1406a55c816d)
* add cli to ease cprofile evaluation (af970d061603)
* add jenkins files (12c98e51cb1d)
* add pipeline step (46ca7962b713)
* use docker to run cmd if --docker is used (d0a8b65f4193)
* use baw version if no docker version is defined (2907afb27b00)
* add basic test docker file (3aa81798172d)
* add dockerfile template (721b988bc2f8)
* add method to determine docker image (f26812eff88d)
* use modern cli approach (41d676001e2b)

### Fix

* ensure that not fully defined version produces an error (99138f5017e2)
* skip replacement, no git repository (31917d2edaf7)
* adjust new version detector (57905e4fca9a)
* support ints as version value (1417e1897d17)
* make baw installable without semver (4ee8800b6bb7)
* equal requirement creator (f379dd36e83e)
* use improved testing verifier (c212e5b25e55)
* install utilatest to avoid problems with nightly (e7d62027320b)
* upgrade requires string selection (57251d6299a5)

## v0.18.0

### Feature

* clean modern docs path (fbee9ed074f0)
* do not lint branches count (0ed6680f68cb)
* extend valid name list (61be8f7bf433)
* add cli to run cmd on generated resource (520c6339ec53)
* enable fail on finding on default (596d4b102375)
* use custom setuptools (b0da472c5812)
* remove log, workspace files also (c96439e93474)
* add remove and dev option (4cb6b9d7005b)
* replace install option (adeb2b9d3078)
* add method to sort file and make content unique (283bf9de7f95)
* shrink commits to functional commits (35d40c0724c9)
* add small program to run any profile step (70e0f216e0ee)
* add option to hide git status message (6ca5f9c891ba)
* clean stack dumps (37ddc146a4c1)
* print error message and exit if path not exists (d9782a091082)
* generate docs outside source tree (ef80bfa5c466)
* update current year automatically (189405eee6ea)
* adjust current year (13fb902849ef)
* write tmp requirements file to tmp path (78250e8843ba)
* add hint that package index is not reachable (24ad9fbcb3c0)
* move project config (e5c33ab715d8)
* use absolute path, to make work dir independent (3623e628b00d)
* use baw tmp folder to store generated files (c61d9f8740c4)
* use more caching (a0fb6a65047d)
* use new venv folder and log old one as outdated (365571e916f9)
* add central baw tmp folder (fc1c1e5c6fc4)
* add option to do not run setup before testing (997fd6214630)
* add publish command without venv (52a714f468ac)
* add information about failing publishing (3527d0f644ca)

### Fix

* do not create changelog.rst anymore (bca5199cb8ed)
* do not copy readme (66ee661c7086)
* ensure equal name packages (77aee3ac7f34)
* fix template (0abf8dcfde41)
* add support for projects starting with n, like nltk (877d2cfa686f)
* use pragma to skip code (c3ce838fd728)
* do not skip .cov file (cee0f42cb12c)
* ensure alphabetic with upper and lower case (d043f5bac2c3)
* do not run invalid command (d2b6d0374d2c)
* show the end not the start of a test (a625cd836f7d)
* increase error view (21dc754bbc6d)
* adjust to new tmp path (d6b08df88559)
* do not fail on missing power installation (4a80f3644abb)
* adjust date to current year (065c78143823)
* do not clean workspace (0b042c8515a7)
* skip year as possible release (40b6e9168918)

### Documentation

* remove outdated files (d83914926771)
* include index page (b72662e7b37b)
* Happy New Year! (bfceb30df708)

## v0.17.0

### Feature

* use new release mechanism (e8768b0cf04c)
* enable no release and no test flag (089f0c2b0729)
* add complex release command (b9bd514d4c02)
* inform user about pour config (5ed00d00205e)
* add option to define additional test plugins (a6dd31aa79fe)
* add plugins option (dcb587467fe6)
* add option to select tests by package (a5c988ad4c16)
* skip outside import (7fde07abbc69)
* ignore global warning (0ec497d648cd)
* do not release dirty repositories (fabf17610e1c)
* add method to check if repository is clean (595c844f4e88)
* add option to open tmp path (90ded095b717)
* clean pytest directory (787b2c8f1ad5)
* add modern method to open root, project, tests and generated (978112139576)
* skip cyclic import warning (cc63342a2a7a)
* enable more checker (c0ac5c25e5e9)
* reduce required linter time (3dc4a4f90dde)
* extend valid linter names (ef33bd3cc529)
* use caching (430d219ae953)

### Fix

* cleanness of init is not checked (1f8108a302b7)
* add cov package if coverage is executed (d9bf38e37c5a)
* ensure to load xdist if using test worker count (d7a193fee277)
* fix clean generated resource (71f8be955009)
* normalize newlines (11527c4d7ddf)
* skip hash determining for first release (eb781c1dc949)
* change to lower case logging (7c9f66d6c983)

## v0.16.0

### Feature

* enable config collector to find .baw config file (73584df11b5e)
* move tested path outside of project root (244ff7431b8d)
* add method to determine project tmpdir (be4f4e6fb2b9)
* clean generated resources outside project root (fd711b026693)
* use improved template syntax (775c107afef0)
* move tmp dir to TMPDIR (056183c3a085)
* strip white spaces in linter command (d741dce9410e)
* add option to change linter (ac95149409f6)
* extend cleaning pattern (36e73140d3c0)
* enable parsing requirements with variant information (789959ea7432)
* add option to quit after first error (6d02b99a238d)
* add method to order two versions (1716de9fd9af)
* use local python version if defined (8f66e489049e)
* do no search for local config (158023fd40c2)
* disable too many instance attributes (6bb4d2760c96)
* do not look for duplicated code (7e00ed5711a4)
* increase debugging information (12593e27da23)
* makes requirements replacement more robust (36e62f61f8dc)
* make error message more verbose (e7fd2e668c80)
* use current python version to create virtual env (4a5b4a65a98d)
* extend valid variable name list (bf76de1ef672)
* add spelling option to linter run (b6e73e132c33)
* load config only once (bd22b5e55bd8)
* add spelling variable to config (94072cf74bd4)
* run linter with selected python version (c77b4de3950d)
* add verbose flag to increase logging (0f5607f379b9)
* use configured python version (dddda86b6616)
* add project.python entry to specify python version (e098b7408db3)
* add extra option (6d9b854113e4)
* handle server not reachable error (88786b3c78a2)
* ensure that all subprojects exists (9620d3b4e4c2)
* extend linter white list (dee63f995055)
* add x, y, z as valid names (4b96b8217c7a)
* adjust doc template (86b70c0e94fe)
* extend pytest ignore list (f0589c8d7db9)
* add verbose flag to display more test result information (3e1d0f6a128c)
* fork linter code (04bcdb051a35)
* disable xdist on single cpu selection (ac4fb95e4963)
* enable new clean command (b7ab98b51369)
* add new clean call (0362042ff0f4)
* add options to specialize delete call (2991e8721f29)

### Fix

* add missing project file message (a34ef680859a)
* fix method renaming (68aaaf66ed1a)
* use pytest test invocation (987abdc65e01)
* run application separately to avoid import errors (672155b94c79)
* add copyright header to requirements and adjust newline (4632aed11c31)
* do not upgrade with lower version number (e212429b8872)
* adjust to upgraded linter (f17920f90afb)
* introduce old patch to ensure backward compatibility (1ef54614c088)
* ensure that upgrading is possible without virtual env (e081d1a36752)
* add missing spaces (886c8ce28f4c)
* remove outdated python2 check (e369a85b9a72)
* solve duplicated requirement definition (b95844fbdf1b)
* handle lower bound requirement (50a2cfb2cd8a)
* remove outdated patch (1a673057342d)
* use virtual to use correct runtime (1a5b9ac5e1fc)
* fill version number without patch (aafd2e61ffa7)
* do not detect nltk_data as nltk package (dc8397bd7076)
* adjust already tested mechanism (f69150b2323e)
* do not run test when using skip (4df8c8c92e8a)

## v0.15.0

### Feature

* add option to select tests (ced3fa6e68fa)
* enable instafail flag (34c393c20300)
* test - use new command pattern (e32b43e04165)
* add instafail option to print error early (09e227fabb5c)
* fail on missing marker (89a6e68dc1a9)
* skip pylint temp folder (fa24af1a4d8c)

### Fix

* fix nightly selector (697c639b0e5d)
* use test invocation (c1bb7af4449e)
* adjust test after upgrading pytest (d9ac31b841d1)
* remove duplicated requirements (8e05d496be4f)

## v0.14.0

### Feature

* add new sync command to downgrade to minimal version (c718116f1511)
* add default release fail flag (d7c2f5b92557)
* update date in header (cd67d7773085)
* inform if using not wrong field in project config (fcab06f67eed)
* add first approach of greaterequal and lowerthan (004abda0c475)
* disable connection check (82af4cf52288)
* sync ranged requirements definition (7da0dba1c42d)
* add version range to requirements parser (7258743648d9)
* introduce environmental var to control parallel pip workers (abff5fd54fa0)
* add important line filter (1b161da4438c)
* add --bisect option to ease git bisect (7fa3064a8078)
* bandit: do not check python input (bc3e50b568a8)
* disable to many ancestors check (e73fae2a3aa6)
* increase number of tries to determine package version (55ca62ada20d)
* do not sync upgraded resources (ebd82c685ff5)
* extend and sort variable name white list (02300688b77a)
* reduce startup time due skipping visiting huge generated folder (398c19239de2)
* remove generated folder (71605acb362e)

### Fix

* add first release plan to releases list (3ed60460a87d)
* fix test setup (9f3e7303e701)
* adjust auto release message (7653a5ca4b11)
* support two different commit types (dea8ac8eed5c)
* handle patch version correctly (9c46d4c8bdbf)
* use lower _ in requirements definition (a9fd329797aa)
* fix upgrading ranged versions (c6e5d7f6a07c)
* fail fast on broken config (070679f3961b)
* extend pylint white list (d8f977c61837)
* unify requirements (59d04b537dda)
* fix yapf virtual bug (e74d1a5bc88d)
* extend linter white list (0ced950d10a9)
* upgrade multiple packages correctly (8d74caaa36c0)
* revert patch d5ca8af94e9617d5e0d67a5e1c301cffdb1112af (0449ef58ccde)
* tee overwrites error code, investigate later (8ce1ea246d84)
* remove wrong update log (3360b5ebddc0)

### Documentation

* Happy New Year! (6c7c8ef2fe55)
* fix docs (22a6f7af8240)
* remove outdated todo reference (0915bd72255d)

## v0.13.0

### Feature

* add some good words (ef74b5389e64)
* do not automatically upgrade dev requirements (07cd6923a175)
* fix handling virtual environment (71d05dfe24ed)
* update outdated templates (76e36266b219)
* add log file to separate folder (6b22334d0bd2)
* simplify error and logging command (33bf6d3f9eb3)
* write test log of every test to separate log file (b8c663665270)
* include security checker to validate code (8d7d5c6d5f40)
* adjust test location to avoid side effects with other project files (42c3bd1c9227)
* skip test if test was done in long/nightly successful before (a47ddd3487d3)
* mark successful tested commit hash's (13bc1d371d8d)
* add method to determine hash value of current head (89ce61c5bd6c)
* do not break imports (b46a92a4e114)
* extend use of verbose flag (6ad8a55f2798)
* add separate dev requirements file (2f09cebda2d4)
* ensure that doc generator fails when rst contain warnings (82470c3022df)
* inform that no features are committed (56decc7893b5)
* increase logging of verbose flag (1dd2f2f6b30a)
* publish releases as universal distribution (0a5edfe82ce9)
* enable doctests in all source code folder (3d3018572c08)
* support open ide up than project root (6522ee971bd2)
* add option to generate partial workspace configuration (c6e778529e7f)

### Fix

* do not open result page if baw is tested itself (62bfd140471f)
* separate hash's by newline character (1b4ddfc7ea88)
* fix upgrading dev resources only (98edfec6384f)
* fix upgrading default and dev requirements (55ab1ad81d90)
* ensure that single path is handled correctly (a836bb814f0f)
* check existence before using dev requirement file (24ec9e7e6639)
* use current working director instead of project root (a245d767b1e2)
* avoid invoking main when collecting due doctest (846147e9ba83)
* rename template to avoid collecting by pytest (df02bf7f79db)
* move pytest cache to tmp directory (db10b3e74a9d)
* rename log steps (75b831e8ce73)

## v0.12.0

### Feature

* use new sync approach (659e4830572c)
* use more worker to reduce required time (2f76f9c5c69d)
* extend parser to support comments at line ending (477551e010a1)
* add method to create freeze-style requirements (6e788de18974)
* add requirements diff to determine not installed packages (42fdb234921c)
* add method to determine install requirements via pip (bba29be50b95)
* run collecting dependencies with multiple threads (8cd0e1fa8d70)

### Fix

* fix required packages (ffe05a151b22)
* fix logging message (30637d53d3a2)
* clarify source of error (c746c023aeed)
* fix default factory (06f86056b245)
* fix error message (62f77ed81013)

## v0.11.2

### Fix

* do not log linting if everything is fine (2133c5e0fcfc)

## v0.11.1

### Fix

* set minimal as default (b3554d1c6240)

## v0.11.0

### Feature

* add optional linter step before running tests (a423088ce1a9)
* add `fail_on_finding` to configuration (288f0681bc83)
* extend linter command with different scopes (e3363fe32264)
* add option to specify linter scope (00dc6c7ad6ea)
* use new project.cfg naming (9435b05db80b)
* support project.cfg and project.config as configuration file (a69eb899df7d)
* exclude generated data folder (2072eb788d6e)

### Fix

* fix hiding import (f0e2dbfcad29)
* do not check code quality at project init (00c30b6bf08c)
* fix complete message (9586fdbd4f3d)
* suppress format command if not using verbose mode (906dfc9af333)
* print new lines (17ae2798be83)
* fix data in copyright header (b667b3e49d6b)

### Documentation

* remove duplicated backlog (fa55ba1e1a8e)
* extend module documentation (193f026950f9)
* correct version number of closed release (4de6b2d1fecc)

## v0.10.0

### Feature

* use multiple core to determine coverage (c0143fc5c7ef)
* uniform linter messages (fa0459b266b1)
* check that requirements are defined only once (7bc9da2dce47)
* add replacement of "greater than requirements" (67fe9006c92e)
* extend parser to support >= pattern (d444bd9f7822)
* support both string assignments to parse version tag (15fb1e4ad777)
* ensure that coverage and linting is detected (9c3b49ef6e2f)
* add verbose flag to --plan command (2482375d944c)
* add --plan=new to cli (792f2533f77f)
* add --plan to create and close release plans (de0dc2b2e494)
* commit plan after closing (3159b8e61630)
* add method to close current release plan (5cb09b9e4d33)
* add first release plan on project initialisation (a92e74141bc2)
* extend git API (72d2d0ffa5a5)
* add method to measure code coverage (5d40281ae5d7)
* add release plan template (d3c276b61465)
* replace with $_ _$ template with {% %} jinja-style (f4a3f41a178f)
* add method to determine the status of the last release plan (2c9787c43249)
* add method to determine code quality of current project (3bcab4c96a87)
* always generate conftest template (8800d680ece7)
* use new doc structure/template (b3b8ad290a68)
* rename generated command line package to `cli` (e0923ff1dee0)
* format generated source code before adding to git (6fa0142d1ac8)
* add setup.py to code formatter (2d1aa96c56b5)
* add current version to utila requirement (5ede3f558288)
* check that `Sphinx` is installed before generating docs (ef6e60e65a72)

### Fix

* do not run in virtual environment to run at baw --init (f02e053baddc)
* fix commit header (9e713e9714fa)
* reduce logging of git commit (efbcf05efc90)
* fix spelling error (2a385090710c)
* ensure that template engine gets correct key (667077fa83cd)
* enable testing with pytest (cd054172b5cd)
* fix required test resources (6854d2d68ae8)
* command is already logged in `log_result` (4994943e8934)
* escape ' to avoid syntax error in generated code (2b547129d1c5)
* log command in verbose mode (c73f7b25884b)
* do not format tests folder if not exists (3c4ef054841a)
* do not generate not renamed import (1d43697cad18)
* remove None output of test (03bac57bac60)

### Documentation

* extend interface documentation (aa33c1c351d0)
* Happy New Year! (e20371fe70df)
* extend interface documentation (7fb1926b2b01)
* extend interface documentation (9595638e1ce7)
* reformat with rst markup (8dc61d95fac1)
* move bugs to new location (2d809a48d019)

## v0.9.0

### Feature

* add live test reporting while running unit tests (5c9747712b82)
* add Dockerfile to run unit tests in (b46cd65c11eb)
* use all cores to run unit tests (ba820e5600a1)
* add yaml as know library (2c2b359eb4e6)
* extend linter white list (c465f1313e73)
* open browser after generating docs successfully (1e74742cf81c)
* extend linter plugins to improve code basis (d81754f5ca5a)
* parallelize formatter(yapf, isort) (fd9eea9c8411)
* extend forward slash with option to replace newlines (484ba8bd6364)
* add test=generate flag to generate test data (8aa61413f8a9)
* ensure that xpassed test will fail the test suite (e8343e85e573)
* deactivate logging time of running IDE (16c687159dab)
* add option to activate logging runtime of process (7241994ddbe9)
* update email address of automatic release generation (661acec13164)
* add test=nightly flag to mark very long running tests (6303c38369e1)
* remove conftest from gitignore (672128b201e8)
* add pytest parallel runner to reduce test endurance (2bfaf1b1497c)
* show file path which violates the assertion (0f0a5c66293e)
* extend vscode workspace template to ignore `external` folder (4f854cda350e)

### Fix

* remove --format test, there is a problem with multi processing (1bad42df69ed)
* require baw installation in virtual test (55270b4f3421)
* fix precondition that test can executed successfully (7589d014a3aa)
* add missing conftest template (85fe3a8a7475)
* add conftest after removing from generation long time ago (6a0a48aa1b1f)
* lint test directory only if it exists (f5b69f38ff54)
* support --ide command when test path does not exists (2ae558fb3995)
* add error message when given no --init project name (1c2770dca817)
* add path in front to avoid confusion by sys path (af0c300d90c8)
* increase clearance of logging format source and imports (e3838f929cdc)
* workaround for path which contain '\notes' for example (26b36e88cecf)
* fix cmdline parser template to new utila version (7f788a013fb5)
* add verbose parameter to reduce verbosity of logging (4a6d24d9339b)

### Documentation

* add backlog to store further development ideas (a24930e81e0b)

## v0.8.2

### Fix

* fix import error of cmdline (92dbb57705b0)

## v0.8.1

### Feature

* run publish after completed release (e87870f5ccbb)
* beautify non existing requirements error message (6a89da664302)
* add --notests flag to ignore tests (51300621e866)
* throw error if server is not reachable (0ebd52a86501)
* ignore that the fixture testdir is linted on pytest tests (c71714f1ebf9)
* add info about formatting to avoid confusion (1434b778fecf)
* only override conftest when file smaller than the new one (a509e9c877a5)
* run initial release without running tests (dc721015bb4c)
* use auto generated file (ec0286361ba4)
* ensure API call return status code (cb83cb4d4d8c)
* add --open command to open current folder in win explorer (06840bc82037)
* auto generate conftest file for pytest (edaa253a4400)
* ignore __main__ file and convert to unix line endings (e5b480af136a)
* open testcov report after successful test run (6c80cb4770e1)

### Fix

* catch None when baw is running without capturing stdout/err (9cce0b108757)
* workaround for overwinding error scope (a3b231d746ac)
* fix newlines in printing while creating new venv (ac671ed7a827)
* remove useless short commands (c31f0b4603c5)
* do not collect any head tag on empty repository (ada566b98cbf)
* __init__ to initial test project to avoid problems with test discovery (9af1dd2fb92e)
* fix error output for corrupted project.config (434902d316b0)

## v0.8.0

### Feature

* sync virtual and local package when running release (17ce37d804e0)
* avoid creating release on tagged commit (e1ef244b46bd)
* add option to sync requirements only (aff61133f818)
* support more verbose options (1c0649db718d)
* make formatter multi-project-able (9655a7ef7d8f)
* always use pytester plugin when running pytest (4fa10a241982)
* move cache folder and show progress in testnumber (773cecfd7af8)
* use multiple source locations from project config for linting (50889d3c480f)
* make test folder dependent on current time (3c3826b18e81)
* use pytester to shorten test code (bf1f2352059a)
* add new --testconfig flag to override test config file (4c4807340c0f)

### Fix

* don't patch the wheel when file does not exists. (90de85776b3a)
* fix spelling (c3fb7392b32b)
* do not remove newlines when use forward slash (ba6a19f38688)
* patching pip to support installing pdfminer.six, remove later (676abdb4b7f5)
* always show the result of the linter (ac232d1ebeea)
* let linter not fail when using in ide (421de9262d03)
* use return code to have a clear interface (b3e82387f19e)
* install new packages when upgrading to use them (39f4200c4997)
* fix templates path (87e7e6434ddd)

## v0.7.3

### Feature

* add --lint command to run python linter (7214e2916606)
* generate sort rule with baw --ide (e6c3be37e735)
* do not warn about conflicting dependencies in normal mode (83d4c77b80e4)
* generate workspace with baw (d5d0828c1d4d)

### Fix

* reduce shortcut commands to improve clarity (c6260a6a9cfc)
* rename template to avoid including in different tools (ae8c5e7e4c9e)
* fix isort configuration (9179c759662f)

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
