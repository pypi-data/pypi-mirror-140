""" A basic example usage of the Script class
>>> m = Main("")
>>> isinstance(m, Main)
True
"""

import logging
from lawnmowerlatte.util import Script

log = logging.getLogger()


class Main(Script):
    """main: A simple implementation of the Script class
    >>> isinstance(script, Main)
    True
    >>> isinstance(script, Script)
    True
    >>> issubclass(script.__class__, Script)
    True
    """

    def test(self, mock_test=False):
        """Run local tests and tests on other mods
        >>> script.test(True)
        Called doctest.testmod(
            <module 'lawnmowerlatte.__main__' from '.../lawnmowerlatte/__main__.py'>,
        ...
        Called doctest.testmod(
            <module 'lawnmowerlatte.util' from '.../lawnmowerlatte/util.py'>,
        ...
        Called doctest.testmod(
            <module 'lawnmowerlatte.logger' from '.../lawnmowerlatte/logger.py'>,
        ...
        """
        from lawnmowerlatte import logger, util

        super().test(mock_test)
        response = Script().test(mock_test)
        util.test_module(logger, mock_test=mock_test)


if __name__ == "__main__":
    script = Main()
    script.main()
