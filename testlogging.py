import unittest
import logging
from utils import Logging
from unittest import mock 
from unittest.mock import MagicMock

class tester(Logging):
    def noop(self):
        return


class TestLogging(unittest.TestCase):
   
    @mock.patch('logging.debug')
    def testDebug(self, debug_mock):
        mytest = tester(name='testing', file='testing.log', level=logging.INFO)
        mytest.debuglog("debug log message")
        debug_mock.assert_called_once()



if __name__ == "__main__":
	unittest.main()	
