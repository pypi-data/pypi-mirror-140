# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Projects module.

A Project represent a program that the user has to produce to complete
exercises for challenges.
"""

# Standard Library
import glob
import os
import subprocess
from typing import Any

# Codechecker
from cc_codechecker.configurable import Configurable
from cc_codechecker.context import Context
from cc_codechecker.runner import Runner
from cc_codechecker.runners.bash import Bash


def dotnet_installation(**kwargs): # pragma: no cover
  """Check the dotnet installation."""
  verbose = 'verbose' in kwargs and kwargs['verbose']
  args = ['dotnet --version']
  dotnet = subprocess.check_output(
    args,
    encoding='UTF-8',
    shell=True,
    stderr=subprocess.STDOUT,
  )
  if dotnet is False:
    if verbose:
      print(f'Dotnet version not correctly installed {dotnet}')

    return False

  if verbose:
    print(f'Dotnet version found: {dotnet}')

  return True

def dotnet_run(**kwargs) -> tuple[int, str]: # pragma: no cover
  """Run dotnet project."""
  verbose = 'verbose' in kwargs and kwargs['verbose']
  try:
    # Get *.csproj project file to run.
    folder_name = 'csharp'
    proj_name = 'csharp'
    proj = glob.glob(os.path.join(folder_name, f'{proj_name}.csproj'))
    if len(proj) != 1:
      return (-2, '')

    args = ['dotnet', 'run', '--project', proj[0]]
    program = subprocess.run(
      args,
      capture_output=True,
      check=False,
    )
    return (program.returncode, program.stdout.decode('utf-8'))
  except PermissionError as perm:
    if verbose:
      print(f'Permission error: {perm}')
    return (-1, '')

_known_languages = {
  'bash': Bash,
  'csharp': 'Csharp',
}

class Project(Configurable):
  """Define a Project."""

  language: str
  runner: Runner

  def __init__(
    self,
    language: str,
    **kwargs
  ) -> None:
    """Create a new Project instance.

    Creates a new Project instance checking that language given is in known
    languages array.

    Args:
      language (str): programming language supported

    Raises:
      ValueError: Thrown when invoking without a language
      ValueError: Thrown when giving a not known language
    """
    if not language:
      raise ValueError('Expected language for each project defined.')

    if not language in _known_languages:
      raise ValueError(f'Language {language} is not supported by codechecker')

    super().__init__()

    self.language = language
    if self.language == 'bash':
      self.runner = Bash()
    # Introduce more runners.
    # Introduce better runners.
    # Introduce runners better.

    self._locals = Context().options()
    if 'verbose' in kwargs:
      self._locals.verbose = kwargs.get('verbose', False)

    if self._locals.verbose:
      print(f'Adding Project {self.language}')

  def __repr__(self) -> str:
    """Represent the project with a string."""
    return f'{self.__class__.__name__}(language={self.language})'

  def dump(self) -> dict[str, Any]:
    """Dump the project to a dictionary.

    Dump all project data to a dictionary for a better yaml handling.

    This method doesn't has to enforce the most simple version of project yaml
    that could be produced, since is more important keep the code simple as
    possible instead of data.

    Returns:
      dict[str, Any]: dictionary dumped.
    """
    items = self.__dict__.items()
    valued = {k:v for k, v in items if self._excluded(k, v)}
    return valued

  def version(self) -> bool:
    """Check if required tools are installed in the current machine.

    Call the given runner for given project. If no specific runner is given,
    call the most generic one (feature not implemented yet).

    At the moment, no minimum version is required for projects. It needs a new
    field in yaml configuration file.

    Returns:
      bool: True if tools are installed, false otherwise.
    """
    return bool(self.runner.version())

  def run(self, contents) -> tuple[int, str]:
    """Execute the project with kwargs arguments.

    Call the given runner for given project. If no specific runner is given,
    call the most generic one (feature not implemented yet).

    Args:
      contents (list):
        List of contents to give to command.

    Returns:
      tuple[int, str]: exit code and message.
    """
    if self._locals.verbose:
      print(f'Run Project {self.language}')

    if not self.version():
      return (-1, 'Unknown version')

    return self.runner.run(contents)

  @classmethod
  def _excluded(cls, key: str, value) -> bool:
    excluded = ['runner']
    return super()._excluded(key, value) and key not in excluded

def get_project(kwargs) -> Project | None:
  """Get a Project object from a string dictionary.

  Generate a new Project object from a string dictionary, useful to retrieve
  configuration from a YAML configuration file.
  """
  try:
    return Project(**kwargs)
  except ValueError as v_er:
    raise ValueError(f'Failed to add {kwargs}') from v_er
