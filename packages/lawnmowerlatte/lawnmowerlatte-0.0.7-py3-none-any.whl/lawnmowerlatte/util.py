""" 

"""

import os
import sys
import argparse
import inspect

from lawnmowerlatte.logger import log
from lawnmowerlatte.imports import minimock, mock, doctest


class Script:
    """util: Class containing portable command line"""

    default_level = log.config.default
    options = [
        {
            "args": ["--log"],
            "help": "enable logging to file",
            "action": "store_true",
        },
        {
            "args": ["--console", "-v"],
            "help": "show logging in console",
            "action": "store_true",
        },
        {
            "args": ["--debug", "-vv"],
            "help": "enable debug logging",
            "action": "store_true",
        },
        {
            "args": ["--debugv", "-vvv"],
            "help": "enable debugv logging",
            "action": "store_true",
        },
        {"args": ["--test"], "help": "run self tests", "action": "store_true"},
    ]
    default_errors = {
        "unknown-error": "The error key {key} is undefined.",
        "bad-args": "Arguments provided were invalid: {e}",
        "test-failure": "DocTest exectution failed due to test failure",
        "test-error": "DocTest exectution failed due to exception during execution",
    }
    app_errors = []
    testmode = False

    def __init__(self, argv=None):
        """
        >>> Script().argv == sys.argv[1:]
        True
        >>> Script("--debug").argv == ["--debug"]
        True
        >>> Script("--debug --log").argv == ["--debug", "--log"]
        True
        >>> Script(["--debug", "--log --debugv"]).argv
        ['--debug', '--log', '--debugv']
        """
        self.description = self.__doc__.splitlines()[0].strip()
        if ":" in self.description:
            self.name, self.description = self.description.split(":", 1)
            self.name = self.name.strip()
            self.description = self.description.strip()
        else:
            self.name = self.__class__.__name__

        if not isinstance(self, Script) and issubclass(type(self), Script):
            self.options.extend(super().options)

        log.critical(f"Creating object with args {argv=}")
        if argv is not None:
            if isinstance(argv, str):
                log.debug(
                    f"Creating {self.__class__.__name__} object using provided string {argv=}"
                )
                self.argv = argv.split(" ")
            elif isinstance(argv, list):
                log.debug(
                    f"Creating {self.__class__.__name__} object using provided list {argv=}"
                )
                self.argv = argv
            else:
                log.warning(
                    "Provided value for argv is neither a string nor list, continuing without args"
                )
                self.argv = []
        else:
            log.debug(
                f"Creating {self.__class__.__name__} object using {sys.argv[1:]=}"
            )
            self.argv = sys.argv[1:]

        # Remove empty strings
        self.argv = [arg for subarg in self.argv for arg in subarg.split(" ") if arg]

        self.__args = None
        self.__argparser = None
        self.__errors = None

    def main(self):
        """Stub main
        >>> sys.argv = "util.py --log".split()
        >>> script = Script("")
        >>> mock("script.help")
        >>> script.main()
        Called script.help()
        """
        log.config.update(self)

        if self.args.test:
            self.test()
            return

        self.fn()

    def fn(self):
        self.help()

    def help(self):
        """Show usage text
        # >>> script.argv
        >>> script.help()
        usage: ...
        ...
        options:
        ...
        arguments:
        ...
        error codes:
        ...
        """
        print(
            f"""\
{self.show_usage()}
{self.show_args()}

{self.show_errors()}
"""
        )

    @property
    def argparser(self):
        """Generate an arg parser object with all the args from the caller and the util module
        >>> script.argparser
        ArgumentParser(...
        >>> script.argparser.description == script.description
        True
        """
        if self.__argparser is not None:
            return self.__argparser

        self.__argparser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Merge class options with defaults
        self.options = list(
            {str(option): option for option in Script.options + self.options}.values()
        )

        # Add all arguments to the parser
        for option in self.options:
            option = option.copy()
            args = option.pop("args")
            kwargs = option
            self.__argparser.add_argument(*args, **kwargs)

        return self.__argparser

    @property
    def args(self):
        """Get the args, handle default args
        # >>> print(Script("--debug").show_args())
        >>> Script("--debug").args.debug
        True
        >>> Script("--debug").args.test
        False
        """
        if self.__args is not None:
            return self.__args

        try:
            self.__args = self.argparser.parse_args(self.argv)
        except Exception as ex:
            self.error("bad-args", e=ex)

        return self.__args

    def show_usage(self):
        return self.argparser.format_help()

    def show_args(self):
        """Display a list of all arguments parsed
        >>> print(Script("--log --debugv").show_args())
        arguments:
          log               True
          console           False
          debug             False
          debugv            True
          test              False
        """
        output = ["arguments:"]

        for arg, val in vars(self.args).items():
            output.append(f"  {arg:17} {val}")

        return "\n".join(output)

    def show_errors(self):
        """Render a table of error messages and exit codes
        >>> print(script.show_errors())
        error codes:
          127               The error key {key} is undefined.
        ...
        """
        output = ["error codes:"]

        for error, index in self.errors.values():
            output.append(f"  {index:<17} {error}")

        return "\n".join(output)

    @property
    def errors(self):
        """
        >>> script.errors["bad-args"]
        ('Arguments provided were invalid: {e}', 126)
        >>> script.errors["test-error"]
        ('DocTest exectution failed due to exception during execution', 124)
        """
        if self.__errors is not None:
            return self.__errors

        self.__errors = {}

        for key, error in self.default_errors.items():
            error_code = 127 - list(self.default_errors.keys()).index(key)
            self.__errors[key] = (error, error_code)

        for index, error in enumerate(self.app_errors):
            self.__errors[index + 1] = (error, index + 1)

        return self.__errors

    def error(self, key, **kwargs):
        """Format the error string, raise an exception or log the error and exit with the error code
        >>> script.error("not-a-real-error")
        Traceback (most recent call last):
        SystemExit: 127
        >>> script.error("unknown-error", key="missing-key")
        Traceback (most recent call last):
        ...
        TypeError: ...error() got multiple values for argument 'key'
        >>> script.error("test-failure")
        Traceback (most recent call last):
        SystemExit: 125
        >>> script.error("test-error")
        Traceback (most recent call last):
        SystemExit: 124
        """
        if key not in self.errors.keys():
            # If not defined, use catchall
            kwargs["key"] = key
            key = "unknown-error"

        string, code = self.errors[key]
        formatted_string = string.format(**kwargs)

        log.critical(f"Exit {code}: {formatted_string}")
        print(f"Exit {code}: {formatted_string}")

        exit(code)

    def test_globs(self):
        """Define test tools for Doctest
        >>> list(script.test_globs().keys())
        ['mock', 'minimock', 'script']
        """
        from lawnmowerlatte.imports import minimock, mock

        globs = {"mock": mock, "minimock": minimock, "script": type(self)("")}
        return globs

    def test(self, mock_test=False):
        """Run Doctests
        >>> script.test(mock_test=True)
        Called doctest.testmod(
            <module '...' from '.../util.py'>,
        ...
        """
        module = sys.modules[self.__class__.__module__]

        result = test_module(module, self.test_globs(), mock_test)

        if result is not None:
            self.error(result)


def test_module(module, test_globs=None, mock_test=False):
    """Run Doctests
    >>> test_module(sys.modules[script.__module__], mock_test=True)
    Called doctest.testmod(
        <module '...' from '.../util.py'>,
    ...
    """

    filename = os.path.basename(module.__file__)
    testmod = doctest.testmod

    if mock_test:
        doctest.testmod = minimock.Mock("doctest.testmod")
        log.alert(
            f"Simulating doctests of module {module} in file {filename} with mock"
        )
        log.debugv(f"{doctest.testmod=}")
    else:
        log.alert(f"Running doctests of module {module} in file {filename}")
        log.debugv(f"{doctest.testmod=}")

    try:
        log.critical(f"{module=}")
        doctest.testmod(
            module,
            raise_on_error=True,
            verbose=True,
            extraglobs=test_globs,
            optionflags=doctest.ELLIPSIS,
        )
    except doctest.DocTestFailure as e:
        log.critical(f"doctest failed: DocTestFailure")
        log.config.console = True
        log.config.level = "ERROR"
        try:
            e_path = f"{os.path.basename(e.test.filename)}:{(e.test.lineno + e.example.lineno + 1)}"
        except:
            e_path = "Unknown"

        e_str = f"""
=======================================
    DocTestFailure
        {e.test.name}
        {e_path}
=======================================
        
    Trying:
        {e.example.source}
    Expected:
        {e.example.want.strip() or "-----"}
        
    Got:
        {e.got}

=======================================
"""
        log.error(e_str)
        return "test-failure"
    except doctest.UnexpectedException as e:
        log.critical(f"doctest failed: UnexpectedException")
        log.config.console = True
        log.config.level = "ERROR"
        try:
            e_path1 = f"{os.path.basename(e.test.filename)}:{(e.test.lineno + e.example.lineno + 1)}"
        except:
            e_path1 = "Unknown"
        try:
            e_path2 = f"...{os.path.dirname(e.exc_info[2].tb_next.tb_next.tb_frame.f_code.co_filename)[-15:]}/{os.path.basename(e.exc_info[2].tb_next.tb_next.tb_frame.f_code.co_filename)}:{e.exc_info[2].tb_next.tb_next.tb_frame.f_lineno} in '{e.exc_info[2].tb_next.tb_next.tb_frame.f_code.co_name}'"
        except:
            e_path2 = "Unknown"
        e_str = f"""
=======================================
    UnexpectedException
        {e.test.name}
        {e_path1}
=======================================
        
    Trying:
        {e.example.source}
    Expected:
        {e.example.want.strip() or "-----"}
        
    Exception:
        {e.exc_info[0].__name__}: {e.exc_info[1]}
        {e_path2}

=======================================

"""
        log.exception(e_str)
        return "test-error"
    finally:
        doctest.testmod = testmod


def get_caller_module(level=None, ignore_direct_caller=True, ignore_self=True):
    """Return the module which called this function
    ignore_direct_caller    Starts at the caller of the caller
    ignore_self             Ignore all this of this module
    """
    ignore_modules = []

    if ignore_self:
        ignore_modules.append(sys.modules[__name__])

    frame = inspect.currentframe()

    from pprint import pprint

    # pprint(frame)
    # print(dir(frame))
    index = 0
    stack = []
    while frame.f_back is not None:
        # print(f"#{index} {frame=}")
        stack.append(frame)
        index += 1
        frame = frame.f_back

        if level is not None and level >= index:
            break

    for k, v in sys.modules.items():
        if v == k:
            return sys.modules[k]

    print(dir(frame))
    # help(frame)
    print({k: getattr(frame, k) for k in dir(frame)})
    # pprint(sys.modules)

    if __name__ == "__main__":
        module_obj = sys.modules[__name__]
    else:
        module_name = inspect.getmodulename(inspect.stack()[0][1])
        log.debug(f"Found root module '{module_name}'")
        module_obj = sys.modules[module_name]

        # print(f"{__name__=}")
        module_obj = sys.modules["__main__"]
        # print(f"{module_obj=}")
        pprint({k: getattr(module_obj, k) for k in dir(module_obj)})
    return module_obj


if __name__ == "__main__":
    script = Script()
    script.main()
