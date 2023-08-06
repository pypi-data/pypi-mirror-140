# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""
Abstract Runner Module.

Runner helps you to write plugins for cc_codechecker, providing facilities to
check requirements on current machine about installed softwares and running
projects.

Anyone can write any runner by extending this module and implementing all
necessaries methods. This makes cc_codechecker extensible as pleasure.

If you need to declare other methods than currently defined, prepend their
names with an _ (underscore).

Submit any new plugin requests to daniele.tentoni.1996@gmail.com.

Unit testing
------------

When updating this class, add unit tests to ``test_base_runner.py``.
Usually, when you add another method that raise a NotImplementedException in
his abstract form, add a new argument to ``test_position_raise_exception``
method parametrization.
"""

# Codechecker
from cc_codechecker.configurable import Configurable


class Runner(Configurable):
  """Abstract base class for projects execution.

  Extends this class to make custom runners.
  """

  def position(self) -> str:
    """Get the executable position.

    :return: path to the runner executable.
    :rtype: str.
    :raises NotImplementedError: if method is not inherited.
    """
    raise NotImplementedError

  def version(self) -> str:
    """Get the executable version.

    :return: version of the runner executable.
    :rtype: str.
    :raises NotImplementedError: if method is not inherited.
    """
    raise NotImplementedError

  def run(self, *args, **kwargs) -> tuple[int, str]:
    """Run the executable for the project.

    :param args: arguments are passed to runtime execution.
    :param kwargs: extra arguments are passed to runtime execution.
    :return: exit code and message from runtime execution.
    :rtype: tuple[int, str].
    :raises NotImplementError: if method is not inherited.
    """
    raise NotImplementedError
