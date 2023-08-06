import unittest
from unittest.mock import *
from senka.plugin_manager import PluginManager
from pathlib import Path
import os

print('%s/plugin' % os.path.dirname(__file__))
class TestPluginManager(unittest.TestCase):
  def test_get_plugins(self):
    plugins = PluginManager.get_plugins('test_one', '%s/plugin' % os.path.dirname(__file__))
    assert len(plugins) == 1
    assert plugins[0].chain == 'test_one'

  def test_get_plugins_exception(self):
    with self.assertRaises(RuntimeError):
      plugins = PluginManager.get_plugins('test_none', '%s/no_plugin' % os.path.dirname(__file__))

if __name__ == '__main__':
  unittest.main()