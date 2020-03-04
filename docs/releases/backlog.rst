.. _backlog:

backlog
=======

* **---rp** to create release plan with current project status

    * linter result
    * code coverage
    * amount of tests plus failing tests

* do not strip long pytest logs

* define user configuration file in ~/.baw

* make pip check asynchronus to improve upgrade step

* fix: baw --plan=close: if there is a closed plan 1.9 and further closed
  plans: 1.10, 1.11, 1.12 and a open plan 1.13, --plan=close closes 1.9
  again.

* baw --testconfig use append to support additive entrees

* check pip completion to use this as baw/tool completion
