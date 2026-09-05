# Changelog
### Version 1.0.0

#### New features

* [feat(GWE, PRT)](https://github.com/MODFLOW-ORG/modflowapi/commit/655ec0e5728fc44d1ba9a86cc8a9f805b32397c8): Updates for GWE and PRT support. Committed by jlarsen on 2024-07-24.
* [feat(GWE, PRT)](https://github.com/MODFLOW-ORG/modflowapi/commit/5193948b41ab2f894d412b35a3caf64edab4c908): Updates for GWE and PRT support. Committed by Joshua Larsen on 2024-08-21.
* [feat(advanced package support)](https://github.com/MODFLOW-ORG/modflowapi/commit/aafe9d0a336d09ff5783493106a01fe6de622959): Refactoring for advanced package support. Committed by Joshua Larsen on 2025-04-11.

#### Bug fixes

* [fix(model_names, X)](https://github.com/MODFLOW-ORG/modflowapi/commit/7aa43cad364fab1b5557df05aec662dc694d3b7c): Updates to ApiSimulation and ApiModel. Committed by Joshua Larsen on 2025-04-30.
* [fix](https://github.com/MODFLOW-ORG/modflowapi/commit/1d112bb0ed3b71ee829b4dbc31f09461de2eb857): Skip interface model and connection variables (#95). Committed by wpbonelli on 2026-06-19.
* [fix(apisimulation.py)](https://github.com/MODFLOW-ORG/modflowapi/commit/b547a5677601809ed24a447d55ffdae8403bd800): Fix exchange-related bugs (#99). Committed by wpbonelli on 2026-07-04.
* [fix(runner.py)](https://github.com/MODFLOW-ORG/modflowapi/commit/73dd08712688c3586e3051f1012819c0907cbb0b): Cap picard iterations with ats (#102). Committed by wpbonelli on 2026-07-11.

#### Refactoring

* [refactor](https://github.com/MODFLOW-ORG/modflowapi/commit/1aea1c9d4e8e0020472f831892b313d8f67e6c33): Support python3.12, pin numpy<2, add status classifier (#43). Committed by wpbonelli on 2024-02-08.
* [refactor(ci)](https://github.com/MODFLOW-ORG/modflowapi/commit/94aae77f189d62f9145af72792b6ce95c317dd3d): Update flopy classes prior to building mf6-examples. Committed by jlarsen on 2024-08-21.
* [refactor](https://github.com/MODFLOW-ORG/modflowapi/commit/6f5ff7653a5f353a87a0578731714dd0f2d5dd3d): Generalize exchange detection (#100). Committed by wpbonelli on 2026-07-04.
* [refactor](https://github.com/MODFLOW-ORG/modflowapi/commit/2796799a3b8017fb0686a583cb3cfc3fef314818): Miscellaneous (#101). Committed by wpbonelli on 2026-07-04.

### Version 0.2.0

#### Refactoring

* [refactor(rhs, hcof)](https://github.com/MODFLOW-ORG/modflowapi/commit/c0f681c5b7525388ead4df8c6363c1b4514d6de6): Updates to allow setting values when rhs and hcof have not yet had pointers set.. Committed by Joshua Larsen on 2023-04-28.
* [refactor(Quickstart.ipynb)](https://github.com/MODFLOW-ORG/modflowapi/commit/3b6675aa687f5af01813abfdb143c7ddd4343646): Fix error in callback_function. Committed by Joshua Larsen on 2023-07-17.
* [refactor(rhs, hcof)](https://github.com/MODFLOW-ORG/modflowapi/commit/ce4e50286d66da51c6b05f0de29c7c646344f6ce): Allow setting rhs and hcof when pointers have not been previously set. Committed by Joshua Larsen on 2023-07-17.
* [refactor](https://github.com/MODFLOW-ORG/modflowapi/commit/e693282611d5863bafeece362230a4aadd02311f): Update libmf6 path handling (#27). Committed by w-bonelli on 2023-08-03.
* [refactor(_ptr_to_recarray)](https://github.com/MODFLOW-ORG/modflowapi/commit/5a631592f2da57bf1564c263e9602c46e5a5a50c): Slice pointers prior to setting data to recarray. Committed by Joshua Larsen on 2023-08-08.
* [refactor(_ptr_to_recarray)](https://github.com/MODFLOW-ORG/modflowapi/commit/959fe31abda263a52d01262af7dc4c2a878eadb5): Slice pointers prior to setting data to recarray. Committed by Joshua Larsen on 2023-08-08.
* [refactor(extensions)](https://github.com/MODFLOW-ORG/modflowapi/commit/c97339d06e7386055e486f6354825ec15cea4638): Add support for IDM changes. Committed by Joshua Larsen on 2023-12-21.
* [refactor(extensions)](https://github.com/MODFLOW-ORG/modflowapi/commit/de0aff9c21d5d925235f306fd2b3d148c3281efa): Add support for IDM changes. Committed by Joshua Larsen on 2023-12-21.

### Version 0.1.0

* Fix typo in README (https://github.com/MODFLOW-ORG/modflowapi/pull/4)
* modflowapi interface (https://github.com/MODFLOW-ORG/modflowapi/pull/8)
* update package: manual variable address assembly updated to use xmipy get_variable_addr()
* update additional manual variable address assembly statements
* Refactor code and added functionality:
* add stress_period_start, stress_period_end Callbacks
* fix ApiModel __repr__
* added Exchanges, TDIS, ATS, and SLN support
* added ScalarInput and ScalarPackage support
* update autotests
* added parallel testing support through pytest-xdist
* updated markers and split the extensions tests from the mf6 examples tests
* added a test for ATS
* update setup.cfg
* update ci.yml
* update(ListInput): add auxvar to stress_period_data when auxiliary variables are used
* Allow None to be passed to stress_period_data.values to disable stresses for a package
* updates: ApiModel, ApiSimulation, run_simulation
* added a `totim` property on `ApiSimulation` and `ApiModel`
* added docstrings to ApiModel property methods
* updated termination message in run_simulation
* added a finalize callback to Callbacks and run_simulation
* add support for AUXNAME_CST
* add(Head Monitor Example): Add a head monitor example application
* ApiModel: adjust X based on nodetouser
* ApiPackage: enforce lower cased variable names in get_advanced_var
* ArrayPointer: trap for arrays that are not adjusted by reduced node numbers (ex. idomain)
* update setup.cfg
* try reformatting the xmipy installation instructions
* fix(get value): fixed error handling when modflowapi fails to get a pointer to a value from the API (https://github.com/MODFLOW-ORG/modflowapi/pull/9)
Co-authored-by: scottrp <45947939+scottrp@users.noreply.github.com>
* update(rhs, hcof, AdvancedInput): bug fixes for setting variable values for advanced inputs
* update rhs and hcof to copy values to pointer instead of overwriting the pointer
* add a check for AdvancedInput variables that do not have pointer support in xmipy
* update setting routine for AdvancedInput
* refactor(EOL): change CRLF to LF line endings for source files (https://github.com/MODFLOW-ORG/modflowapi/pull/12)
* Use pyproject.toml for project metadata, add citation info (https://github.com/MODFLOW-ORG/modflowapi/pull/11)
* add(test_rhs_hcof_advanced): add additional test  (https://github.com/MODFLOW-ORG/modflowapi/pull/13)
* added test for getting and setting rhs, hcof, and advanced variable values
* update project to use unix line separators
* use np.testing.assert_allclose() instead of AssertionError
* Add missing RIV support to modflowapi (https://github.com/MODFLOW-ORG/modflowapi/pull/16)
* add(test_rhs_hcof_advanced): add additional test
* added test for getting and setting rhs, hcof, and advanced variable values
* update project to use unix line separators
* use np.testing.assert_allclose() instead of AssertionError
* Add missing riv package to modflowapi

### Version 0.0.1

Initial release.
