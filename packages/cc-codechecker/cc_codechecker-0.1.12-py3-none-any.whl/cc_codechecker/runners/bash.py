# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Bash runner.

Give definitions for runner for Bash projects.
"""
# Standard Library
import subprocess

# Codechecker
from cc_codechecker.runner import Runner

NOT_EXECUTABLE_ERROR = 126


class Bash(Runner):
  """Bash runner.

  Support for bash projects.
  """

  def position(self) -> str:
    """Get the bash executable position.

    :return: path to the bash executable.
    :rtype: str
    """
    args = ['command -v bash']
    bash_pos = subprocess.check_output(
      args,
      encoding='locale',
      shell=True,
      stderr=subprocess.STDOUT,
    )
    if self._locals.verbose:
      print(f'Bash position {bash_pos}')

    return bash_pos

  def version(self) -> str:
    """Get the bash executable version.

    Run a check on current system for an installed bash. If bash is not
    installed, Projects targetting this platform could not be executed.
    Using the POSIX standard command *command* make us more cross-platform.
    Look at this page for more info:
    https://pubs.opengroup.org/onlinepubs/9699919799/utilities/command.html.

    :return: version of the bash executable.
    :rtype: str.
    """
    bash_path = self._check_position()
    args = ['echo $BASH_VERSION']
    bash_ver = subprocess.check_output(
      args,
      encoding='locale',
      executable=bash_path,
      shell=True,
      stderr=subprocess.STDOUT,
    )
    if self._locals.verbose:
      print(f'Bash version {bash_ver}')

    return bash_ver.rstrip('\n')

  def run(self, *args, **kwargs) -> tuple[int, str]:
    """Run the bash executable for the project.

    Run the project in the bash folder. I don't know if it is shell injection
    prune.

    :param args: arguments are passed to bash execution.
    :param kwargs: extra arguments are passed to bash execution.
    :return: exit code and message from bash project execution.
    :rtype: tuple[int, str].
    """
    bash_path = self._check_position()

    program_file_name = './bash/program.sh'
    cmd: list[str] = []
    bash_run = subprocess.run(
      cmd,
      capture_output=True,
      check=False,
      encoding='locale',
      executable=bash_path,
      shell=True, # Is this shell injection prune?
    )

    run_verbose = kwargs['verbose'] \
      if 'verbose' in kwargs \
      else self._locals.verbose
    if run_verbose:
      print(f'Bash run {bash_run}')

    if bash_run.returncode is NOT_EXECUTABLE_ERROR and not bash_run.stdout:
      bash_run.stdout = f'{program_file_name} is not executable'

    return (bash_run.returncode, bash_run.stdout)

  def _check_position(self) -> str:
    """Find bash executable.

    Raise a Value Error if executable is not found.

    :return: bash executable path.
    :rtype: str.
    :raises ValueError: if bash is not installed.
    """
    bash_path = self.position().rstrip('\n')
    if not bash_path:
      raise ValueError('Bash executable not installed')

    return bash_path
