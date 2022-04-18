
from nr.util.terminal.colors import StyleManager


def test_style_manager():
  manager = StyleManager()
  manager.add_style('u', 'cyan', attrs='underline,italic')
  assert repr(manager.format('Hello <u>World!</u>')) == repr('Hello \x1b[36;4;3mWorld!\x1b[0m')
  assert repr(manager.format('Hello <bg=blue;attr=underline>World!</bg>')) == repr('Hello \x1b[44;4mWorld!\x1b[0m')
  assert manager.format('Hello <u>World!</u>', repl=lambda _, c: c) == 'Hello World!'
