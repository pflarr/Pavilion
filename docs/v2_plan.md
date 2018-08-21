# Pavilion Version 2.0

We're taking a hard look at Pavilion as it is: what works, what doesn't, what we would like to add
to it. We'll use that to design a set of changes to improve Pavilion's usability, stability, and
extensibility. 

#### Re-design Philosophy
 
 - Should be suitable for postDST, automated, and acceptance testing. 
 - Tests should be trackable, start to finish.
 - Test status should always be known, even from other machines.
 - Building tests should be separated from running a test.
  - The test configs should support building most tests via configuration alone.
 - Test builds should be cached and reused.
 - Output should be easy to parse.
 - Tests should be able to inherit configuration from other tests in the same suite.
 - Users should rarely, if ever, have to actually look in a test run's result directory to find out
   what is going on.
 - Backwards compatibility will be broken.
 - The last vestiges of gazebo should go away (including all perl).
 
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
