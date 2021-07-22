
echo off

python -m unittest test_common test_format

rem Command-Line Interface
rem The unittest module can be used from the command line to run tests from modules, classes or even individual test methods:

rem python -m unittest test_module1 test_module2
rem python -m unittest test_module.TestClass
rem python -m unittest test_module.TestClass.test_method
rem You can pass in a list with any combination of module names, and fully qualified class or method names.

rem Test modules can be specified by file path as well:

rem python -m unittest tests/test_something.py
rem This allows you to use the shell filename completion to specify the test module. The file specified must still be importable as a module. The path is converted to a module name by removing the ‘.py’ and converting path separators into ‘.’. If you want to execute a test file that isn’t importable as a module you should execute the file directly instead.

rem You can run tests with more detail (higher verbosity) by passing in the -v flag:

rem python -m unittest -v test_module
rem When executed without arguments Test Discovery is started:

rem python -m unittest
rem For a list of all the command-line options:

rem python -m unittest -h
rem Changed in version 3.2: In earlier versions it was only possible to run individual test methods and not modules or classes.

rem Command-line options
rem unittest supports these command-line options:

rem -b, --buffer
rem The standard output and standard error streams are buffered during the test run. Output during a passing test is discarded. Output is echoed normally on test fail or error and is added to the failure messages.

rem -c, --catch
rem Control-C during the test run waits for the current test to end and then reports all the results so far. A second Control-C raises the normal KeyboardInterrupt exception.

rem See Signal Handling for the functions that provide this functionality.

rem -f, --failfast
rem Stop the test run on the first error or failure.

rem -k
rem Only run test methods and classes that match the pattern or substring. This option may be used multiple times, in which case all test cases that match of the given patterns are included.

rem Patterns that contain a wildcard character (*) are matched against the test name using fnmatch.fnmatchcase(); otherwise simple case-sensitive substring matching is used.

rem Patterns are matched against the fully qualified test method name as imported by the test loader.

rem For example, -k foo matches foo_tests.SomeTest.test_something, bar_tests.SomeTest.test_foo, but not bar_tests.FooTest.test_something.

rem --locals
rem Show local variables in tracebacks.

rem New in version 3.2: The command-line options -b, -c and -f were added.

rem New in version 3.5: The command-line option --locals.

rem New in version 3.7: The command-line option -k.

rem The command line can also be used for test discovery, for running all of the tests in a project or just a subset.

