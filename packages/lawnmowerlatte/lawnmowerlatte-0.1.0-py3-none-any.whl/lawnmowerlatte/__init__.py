""" This module replaces the Pythonista3 builtin modules for calling shortcuts. This will work either in PyTo or Mac
>>> open_url = Mock("call_url")
>>> open_url("http://example.com")
Called call_url('http://example.com')

"""

from . import util
from . import logger

Script = util.Script

__all__ = ["Script"]
