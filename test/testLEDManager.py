import unittest
import config_elephant
from config_elephant import *
import OPi.GPIO as gpio
import MultiColorLEDManager as led
import time


class TestLEDManager(unittest.TestCase):

    def test_start(self):
        
        mgr=led.MultiColorLEDManager('orange')
        
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            self.assert
            s.split(2)

if __name__ == '__main__':
    unittest.main()
