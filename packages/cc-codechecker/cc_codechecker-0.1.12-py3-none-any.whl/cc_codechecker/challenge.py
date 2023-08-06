# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Challenge module.

A Challenge represent an use case for projects used to gain score points if
completed correctly. To complete correctly a Challenge any project must produce
expected outputs from starting inputs.
"""

# Standard Library
from typing import Any

# Codechecker
from cc_codechecker.configurable import Configurable
from cc_codechecker.project import Project


class Challenge(Configurable):
  """Define a step of the challenge.

  It can assign points to score the attempt.
  """
  name: str = ''
  argument: str = ''
  arguments: list = []
  result: str = ''
  results: list = []
  value: int = 0

  def __init__(self, **kwargs):
    """Creates a new Challenge object.

    A valid configuration can be:
      only name, without argument/s or result/s
      a pair argument-result
      a pair arguments-results

    An invalid configuration is:
      no name and any pair is given
      both argument and arguments are given
      both result and results are given

    A missing result/s configuration mean that you expect no results from that
    challenge.

    Args:
      name (str, optional):
        Define the name to give to the challenge.
        Used to define a challenge without inputs and outputs, only to prove
        that a user can create a compiling program :) .
      argument (str, optional):
        Define the file to load to test the project.
      arguments (list, optional):
        Define the arguments to give to the projects.
      result (str, optional):
        Define the file to check the project correctness.
      results (list, optional):
        Define the values to expect to check the project correctness.
      value (int, optional):
        Define the value of successfully completing the step.. Defaults to 1.
    """
    super().__init__(**kwargs)

    self.name = kwargs.get('name', '')
    self.argument = kwargs.get('argument', '')
    self.arguments = kwargs.get('arguments', '')
    self.result = kwargs.get('result', '')
    self.results = kwargs.get('results', '')
    self.value = kwargs.get('value', 0)
    first = not self.argument and not self.result and \
      not self.arguments and not self.results and self.name
    c_input = self.argument and self.arguments
    c_results = self.result and self.results
    if not first and (c_input or c_results):
      print('Invalid challenge configuration')
      raise ValueError(f'''Invalid challenge configuration. You must defined
        only one of the pair "argument-return [{ self.argument, self.result }]" or
        "arguments-returns [{ self.arguments, self.results }]"''')

    # Here the configuration is valid.
    if self._locals.verbose:
      print(f'Adding Challenge {self.name}')

  def __repr__(self) -> str:
    args: list[str] = []

    items = self.__dict__.items()
    valued = [(k,v) for k, v in items if _excluded(k, v)]
    for key, value in valued:
      args.append(f'{key}={value}')

    args_string = ','.join(args)

    return f'{self.__class__.__name__}({args_string})'

  def dump(self) -> dict[str, Any]:
    """Dump the challenge to a dictionary.

    Dump all challenge data to a dictionary for a better yaml handling.

    This method doesn't has to enforce the most simple version of project yaml
    that could be produced, since is more important keep the code simple as
    possible instead of data.

    Returns:
      dict[str]: dictionary dumped.
    """
    result = {}
    items = self.__dict__.items()
    valued = [(k,v) for k, v in items if _excluded(k, v)]
    for key, value in valued:
      if key != 'value' or value != 0:
        result[key] = value

    return result

  def run(self, ext_projects: list[Project]) -> int:
    """Execute the challenge with arguments.

    Args:
      ext_projects (list[Project]):
        List of external projects.
      context (Namespace):
        Application context from argparse.

    Results:
      int:
        score gained with this challenge.
    """

    if self._locals.verbose:
      message = f'Run Challenge {self.name}'
      if self.value:
        message = message + f' for {self.value} points'

      print(message)

    if self.argument:
      read_arguments(self.argument)

    contents = self.arguments if self.arguments else ''

    for project in ext_projects:
      proj_outs = project.run(contents)
      if not check_proj_outs(project, proj_outs):
        continue

      # Continue only with results.
      if self._locals.verbose:
        print(f'Check for {self.result} and {self.results}')
      if not self.result and not self.results:
        return self.value

      try:
        results: list | str = ''
        if self.result:
          with open(self.result, encoding='locale') as reader:
            results = reader.read().rstrip('\n')
        elif self.results:
          results = self.results

        with open('output.txt', encoding='locale') as out:
          outputs = out.read().rstrip('\n')
          print(f'Outputs: {outputs}')
      except OSError as ex:
        print(f'Exception in result {ex}')
        # Continue with next project.
        continue

      if self._locals.verbose:
        print(f'{outputs} == {results} => {outputs == results}')

      if str(outputs) == str(results):
        return self.value

    # No points collected at this point.
    return 0

def _excluded(key, value):
  excluded = ['_locals']
  return value and key not in excluded and not key.startswith('_')

def check_proj_outs(project: Project, outs: tuple[int, str]) -> bool:
  """Check for project run outputs.

  Add to this function code to handle exit status of projects. Could this be
  moved to runner object?

  Args:
    project (Project): Project to check.
    outs (tuple[int, str]): Outputs to check.

  Returns:
    bool: True if outs are ok, false otherwise.
  """
  if outs[0] == -1:
    print(f'Unknown {project.language} platform. Exit code {outs[0]}')
    # Continue with next project.
    return False

  if outs[0] > 0:
    print(f'Project {project.language} return with error {outs}')
    # Continue with next project.
    return False

  return True

def read_arguments(file_name: str):
  try:
    with open(file_name, encoding='locale') as i:
      contents = i.read()
      with open('input.txt', 'w', encoding='locale') as writer:
        writer.write(contents)
  except OSError as ex:
    print(f'Exception in input {ex}')
    raise ValueError(f'Missing a configuration file {ex}') from ex

def get_challenge(kwargs) -> Challenge | None:
  """Get a Challenge object from a string dictionary.

  Generate a new Challenge object from a string dictionary, useful to retrieve
  configuration from a YAML configuration file.

  Raises:
    ValueError: Raise when an error retrieving the Challenge occur.

  Returns:
    Challenge | None: Challenge retrieved or None if an error occurred.
  """
  try:
    return Challenge(**kwargs)
  except ValueError as v_er:
    raise ValueError(f'Failed to add challenge {kwargs}') from v_er
