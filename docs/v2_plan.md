# Pavilion Version 2.0

We're taking a hard look at Pavilion as it is: what works, what doesn't, what we would like to add
to it. We'll use that to design a set of changes to improve Pavilion's usability, stability, and
extensibility. 

#### Re-design Requirements
 
 - Should be suitable for postDST, automated, and acceptance testing. 
 - Tests should be trackable, start to finish.
 - Test status should always be known, even from other machines.
 - Anything the user needs from the results directory should be accessible from the pav command
   line.
 - Building tests should be separated from running a test.
  - The test configs should support building most tests via configuration alone.
  - Tests that are builds would still be built within the test run.
  - Test builds should be cached and reused.
 - Pavilion output should be easy to parse programatically.
 - Test configurations should be easy to organize with little repetition.
 - Test configuration should be flexible enough to remove the need for 'runit' scripts in
   most cases.
 - The last vestiges of gazebo should go away (including all perl).

**Backwards compatibility will be broken.**
 
## Test Builds

The test build process is as follows:

 1. Determine the build hash
 2. Copy/extract/checkout the code into the build cache directory, named for the hash.
 3. Generate a build script from the config. 
 4. Run the build script. 

Builds should be automatically done for tests without a cached build. Since these steps can run as
part of a test, each step should update the test status.

### Source origin

We should use a plugable system for source origins, initially supporting:

 - Tar Files
 - git repositories
 - Directories

### Config based building
To build (most) tests via configurations alone, we need a few things:

 1. Support for build environment descriptions
    - Which modules to load
    - What environment variables to set
 2. Plugins that 'wrap' modules with additional code. IE, set MPICC env 
    according to os/compiler/mpi, module swapping instead of loading on cray, etc.

### Caching builds
To cache a build we need to understand what makes builds different from each other. These
differences can include:

 - Code differences (tar hash, git commit hash, recursive directory hash)
 - modules loaded
 - Environment variables
 - host 

These can be incorporated into a unique hash to identify each build, much like Spack does. Each
cached build should also be 'touched' each time it used, giving us a way to determine which builds
are no longer useful.

#### pav build
```
pav build [-r] <test_suite[.sub_test]>...

Build the given test/s. 

 -r Force a rebuild of cached versions of the given test/s.
```

## Running Tests
 
 1. Build, if a cached build isn't available.
 2. Copy as softlinks ( cp -as ) the cached directory to working space
   - Saves considerable space
   - Original cached version won't get overwritten.
 3. Write a job script.
 4. Run job script according to scheduler.
 5. Parse/grep output, get final status.
 6. Finalize results
  - Copy logs, result files to results directory. 
 7. Delete working space.
 8. Write Final Status.

### Run IDs

 - Assigned to each test run. 
 - Generated sequentially via a lockfile across systems.
 - Run ID files will be symlinks to the results directories.
 - Organized into runs/running and runs/finished directories.
 - Give users a handle to reference test runs for pav commands.

#### Series IDs
 
 - Series are groups of tests being run together. 
 - They will exist as a series/running/\<series ID\> directory containing runID softlinks.
 - Also generated sequentially via a lockfile.

### Tracking Progress
A status file (results/run.status) in each results directory will track the progress of the test. It will be written to before and after each step, confirming that the step started and completed (or failed). These writes will be appends, and will each consist of a single line of the format:
```
<step #> <ts> <step_name> <status> [user msg]
```

In most cases these updates will be quite easy, as the steps are controlled directly by Pavilion
itself. However, once the run is started and Pavilion exits, tracking status becomes more difficult.
To handle this, the test run process will be split into two parts. In the first, steps 1-3 of the
run process will occur in the instance of paraview started by the user. This will get the test ready
to go, the results directory created, and the run will be trackable. Then for each test run a
separate, detached pavilion process will be started to follow that run to completion. It will
continue updating the status through each step and monitor the status of the scheduler task (or
process PID).

## Configuration

We will be keeping most of the current config syntax, while making improvements in a few key areas.

### Separation of Host, Mode, and Test

This has already been implemented, and will remain in 2.0.

Rather than a directory per host, there is now a general Pavilion config directory with
subdirectories with configs for *hosts*, *modes*, and *tests*. The *host* configs describe the
specific limits of a given host to use for tests run on that host, much like the old
`default_test_config.yaml` files. *Mode* configs are an optional layer of configuration that allow
for easy specification of the different ways in which you might run a test on a host. For example,
the `postDST` mode sets the slurm reservation and qos to `PreventMaint` and `hpctest` respectively.
Finally, the *test configs* describe, in a host agnostic manner, how to run the test. 

This setup allows us to maintain a single configuration file for each test and host, greatly
simplifying the process of running and setting up tests.

Currently *host* and *mode* configs use dummy values for required keys, and set up a dummy test that
gets applied globally. In 2.0, *host* and *mode* config files will contain the test config at the
top level of the file, and no keys will be required. 

### Test Configs

    - Drop the **name** required key, instead using the key value for the test as the name.
    - **test src** should also be optional, as some test may simply run shell commands.
    - **test_args** will be lists instead of strings, for readability.
 
#### Test iterations

Pavilion currently supports giving config items as a list when a string is expected, and then
producing a version of that test for each combination of list items. This functionality will remain
in 2.0. 

#### Test inheritance

Tests should also be able to inherit from each other. This would add a **inherits\_from** key to
test configs. Config items in the child test would override those in the parent. Only single
inheritance would be allowed. 

#### Substitution 

All fields in the config can contain python style format escapes. IE `{key}` or `key[subkey]`.
Pavilion will provide a dict of values as keys for these escapes, such has *host* and *os*, the test
config itself, and dynamically determined parameters from scheduler plugins. If the builtin python
format systax is used (which it probably will be), it limits the depth of test configs to two (which
they already are).

#### Other Config Changes

 - Pavilion currently supports placing a list of tests to run in configuration files. This
   functionality will be moved to a command line option.
 - Argument strings (the **run:test_args** key) will be replaced with a list of string arguments.

