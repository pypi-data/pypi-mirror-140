# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Abstract class for yaml objects.
"""
# Standard Library
from typing import Any

# Codechecker
from cc_codechecker.context import Context


class Configurable:
  """Abstract class for yaml objects.

  This class expose two methods for two different presentation modes useful for
  an yaml object: dump generate dictionaries and repr generate a string. At the
  moment is not possible to generate the yaml file properly using only the
  representation method, since we have to main both presentations.
  """
  def __init__(self, **kwargs) -> None:
    """Create a new configurable yaml object."""
    self._locals = Context().options()

    # Check if verbose override is needed.
    verbose = kwargs.get('verbose', None)
    if verbose:
      self._locals.verbose = verbose

  def dump(self) -> dict[str, Any]:
    """Dump the configurable object to a dictionary."""
    return dict(self.valued_items())

  @classmethod
  def _excluded(cls, key: str, value) -> bool:
    return bool(key) and bool(value) and not key.startswith('_')

  def valued_items(self) -> list[tuple[str, Any]]:
    """Gets valued items in the object.

    Useful when you want to represent the object without default values. Child
    objects need to inherit _excluded method to hide private fields useless for
    end user or for yaml configuration.

    Returns:
      list[tuple[str, Any]]: items not
    """

    items = self.__dict__.items()
    return [(k,v) for k, v in items if self._excluded(k, v)]

  def __repr__(self) -> str:
    res = [f'{k}={v}' for k, v in self.valued_items()]
    args_string = ','.join(res)
    return f'{self.__class__.__name__}({args_string})'
