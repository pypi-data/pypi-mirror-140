from unittest import TestCase
from MickeNet.PyGPGlib import PyGpgLib
import pathlib as pl


class TestCaseBase(TestCase):
    def assertIsFile(self, path):
        if not pl.Path(path).resolve().is_file():
            raise AssertionError("File does not exist: %s" % str(path))


class TestPyGpgLib(TestCaseBase):

    def test_verify_content(self):
        path = 'C:\\Users\\mickael.eriksson\\Downloads\\p20220223-155151_noenvelope_trav.xml'
        pygpglib = PyGpgLib('C:\\Users\mickael.eriksson\\AppData\\Roaming\gnupg',
                            'C:\\Program Files (x86)\\GnuPG\\bin\\gpg.exe')
        ps = pygpglib.verify_content(path, 'T3a4ever@', 'C:\\Users\\mickael.eriksson\\', 'xml')
        path = pl.Path(ps)
        self.assertIsFile(path)

    def test_sign_content(self):
        path = 'C:\\Users\\mickael.eriksson\\Downloads\\p20220223-155151_noenvelope_trav.xml'
        pygpglib = PyGpgLib('C:\\Users\mickael.eriksson\\AppData\\Roaming\gnupg',
                            'C:\\Program Files (x86)\\GnuPG\\bin\\gpg.exe')
        ps = pygpglib.sign_content(path, 'T3a4ever@', 'C:\\Users\\mickael.eriksson\\', 'gpg')
        path = pl.Path(ps)
        self.assertIsFile(path)
