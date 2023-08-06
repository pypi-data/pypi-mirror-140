import unittest
import pyteddy

class ModuleTestCase(unittest.TestCase):
    def test_get_template(self):
        pyteddy.get_template('default_package_template')
