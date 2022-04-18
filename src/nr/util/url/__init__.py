
""" Tools for URL handling. """

from __future__ import annotations

import dataclasses
import urllib.parse


@dataclasses.dataclass
class Url:
  """ Helper to represent the components of a URL, including first class support for username, password, host and port. """

  scheme: str = ''
  hostname: str = ''
  path: str = ''
  params: str = ''
  query: str = ''
  fragment: str = ''

  username: str | None = None
  password: str | None = None
  port: int | None = None

  def __str__(self) -> str:
    return urllib.parse.urlunparse((self.scheme, self.netloc, self.path, self.params, self.query, self.fragment))

  @property
  def netloc(self) -> str:
    parts = []
    if self.username or self.password:
      parts.append(f'{urllib.parse.quote(self.username or "")}:{urllib.parse.quote(self.password or "")}@')
    parts.append(self.hostname)
    if self.port:
      parts.append(f':{self.port}')
    return ''.join(parts)

  @staticmethod
  def of(url: str) -> Url:
    """ Parses the *url* string into its parts.

    Raises:
      ValueError: If an invalid URL is passed (for example if the port number cannot be parsed to an integer).
    """
    parsed = urllib.parse.urlparse(url)
    return Url(
      scheme=parsed.scheme,
      hostname=parsed.hostname or '',
      path=parsed.path,
      params=parsed.params,
      query=parsed.query,
      fragment=parsed.fragment,
      username=parsed.username,
      password=parsed.password,
      port=parsed.port,
    )
