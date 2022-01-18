
""" ASGI/WSGI application launchers. """

import abc
import base64
import pickle
import os

from .._app import App


class AWSGILauncher(abc.ABC):
  """
  Interface for AWSGI/WSGI application launchers.
  """

  @abc.abstractmethod
  def launch(self, entrypoint: str, factory: bool) -> None: ...


try:
  from databind.core.annotations import union  # type: ignore[import]
except ImportError:
  pass
else:
  union(
    union.Subtypes.chain(
      union.Subtypes.dynamic({
        'uvicorn': lambda: __import__(__name__ + '.uvicorn', fromlist=['UvicornLauncher']).UvicornLauncher,
      }),
      union.Subtypes.entrypoint('nr.util.awsgi.launcher'),
    ),
    style=union.Style.flat
  )(AWSGILauncher)


def launch(launcher: AWSGILauncher, app: str | App, factory: bool = False) -> None:
  """
  Launches the application using the specified ASGI/WSGI launcher. If an #App instance is specified, it will be
  pickled in this process and unpickled in subprocesses to avoid limitations of finding an application just by
  an entrypoint.
  """

  if not isinstance(app, str):
    if not isinstance(app, App):
      raise RuntimeError(f'expected str|App, got {type(app).__name__}')

    os.environ['_NR_UTILS_AWSGI_PICKLED_APP'] = base64.b64encode(pickle.dumps(app)).decode('ascii')
    app = __name__ + ':_pickled_app'
    factory = True

  launcher.launch(app, factory)


def _pickled_app():
  """ Internal. Loader for a pickled app. """

  app: App = pickle.loads(base64.b64decode(os.environ.pop('_NR_UTILS_AWSGI_PICKLED_APP').encode('ascii')))
  app.initialize()

  if app.asgi_app:
    return app.asgi_app
  elif app.wsgi_app:
    return app.wsgi_app
  else:
    raise RuntimeError(f'{type(app).__name__} does not provide an asgi_app or wsgi_app')