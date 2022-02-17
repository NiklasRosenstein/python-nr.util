
import importlib
from pathlib import Path

import nr.util
from nr.util.fs import recurse_directory


def test_import_all_modules():
  directory = Path(nr.util.__file__).parent
  for path in recurse_directory(directory):
    if path.suffix != '.py': continue
    file = path
    path = path.with_suffix('')
    if path.name == '__init__':
      path = path.parent
    module = 'nr.util.' + '.'.join(path.relative_to(directory).parts)
    assert importlib.import_module(module.rstrip('.')).__file__ == str(file)
