# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Configuration module.

A configuration represent the complete definition of the current coding
challenge.
"""

# Standard Library
from typing import Any

import yaml  # type: ignore

# Codechecker
from cc_codechecker.challenge import Challenge, get_challenge
from cc_codechecker.context import Context
from cc_codechecker.project import Project, get_project

DEFAULT_OUTPUT = 'output.txt'
FILE_NAME = '.codechecker.yml'

class Configuration():
  """Define a complete configuration for code checker.

  Raises:
    ValueError: thrown if no challenges are given
    ValueError: thrown if no projects are given
  """

  challenges: list[Challenge]
  output: str = DEFAULT_OUTPUT
  projects: list[Project]

  def __init__(
    self,
    challenges: list[Challenge],
    projects: list[Project],
    output: str = DEFAULT_OUTPUT,
    **kwargs
  ) -> None:
    """Create a new Configuration object."""
    if not challenges or len(challenges) < 1:
      raise ValueError('Expected at least one challenge')
    if not projects or len(projects) < 1:
      raise ValueError('Expected at least one project')

    super().__init__()

    self.challenges = challenges
    self.output = output
    self.projects = projects

    self._locals = Context().options()
    if verbose := kwargs.get('verbose', None):
      self._locals.verbose = verbose

    if self._locals.verbose:
      print('Adding Configuration')

  def __repr__(self) -> str:
    """Represent the configuration object with a string."""
    args: list[str] = []
    if hasattr(self, 'challenges') and self.challenges:
      c_string = ','.join(str(c) for c in self.challenges)
      args.append(f'challenges=[{c_string}]')
    if hasattr(self, 'output') and self.output != DEFAULT_OUTPUT:
      args.append(f'output:{self.output}')
    if self.projects:
      p_string = ','.join(str(p) for p in self.projects)
      args.append(f'projects=[{p_string}]')
    args_string = ','.join(args)
    return f'{self.__class__.__name__}({args_string})'

  def dump(self) -> dict[str, Any]:
    """Dump the configuration to a dictionary.

    Dump all configuration data to a dictionary for a better yaml handling.

    Returns:
      dict[str, Any]: dictionary dumped.
    """
    result: dict = {}
    challenges = [k.dump() for k in self.challenges]
    projects = [k.dump() for k in self.projects]
    result['challenges'] = challenges
    result['projects'] = projects

    items = self.__dict__.items()
    valued = [(k,v) for k, v in items if _excluded(k, v)]
    for key, value in valued:
      if key != 'output' or value != 'output.txt':
        result[key] = value

    return result

  def run(self):
    """Run the configuration.

    Args:
      context (Namespace):
        Application context from argparse.
    """
    score: int = 0
    for challenge in self.challenges:
      points = challenge.run(self.projects)
      score = score + points
      if self._locals.verbose:
        print(f'Gained {points} points, now {score}')

    try:
      with open('score.txt', 'w', encoding='locale') as score_writer:
        score_writer.write(str(score))
    except OSError as ex:
      print(f'Exception in writing scores: {ex}')

def _excluded(key, value):
  excluded = ['challenges', 'projects']
  return value and key not in excluded and not key.startswith('_')

def set_configuration(configuration: Configuration):
  """Set the configuration to yaml.

  Write the .codechecker.yml file in the root directory to save the current
  configuration.

  Args:
    configuration (Configuration):
      Configuration object to save.
  """
  try:
    with open(FILE_NAME, 'w', encoding='locale') as file:
      file.write(yaml.dump(configuration.dump()))
    return True
  except yaml.YAMLError as exc:
    print(f'Error in configuration file: {exc}')
    return False

def get_configuration(
  dic: dict[str, Any] | None
) -> Configuration | None:
  """Get the configuration from yaml.

  Read the codechecker.yml file in the root directory and read it to get the
  actual configuration provided. If something given in dic, convert it.

  Args:
    dic (dict[str, Any], optional):
      Dictionary of a yaml object. If left None, configuration will be read
      from ``.codechecker.yml`` file inside root dir.
      Defaults to None.

  Returns:
    Optional[Configuration]:
      The Configuration object produced. None if dictionary or file input is
      invalid.
  """
  raw_configuration: dict[str, Any] = {}
  if dic is not None:
    raw_configuration = dic

  if 'projects' not in raw_configuration:
    raise ValueError('Necessary at least one project')
  if 'challenges' not in raw_configuration:
    raise ValueError('Necessary at least one challenge')

  try:
    raw_projects: dict = raw_configuration.get('projects', {})
    projects = load_projects(raw_projects)

    raw_challenges = raw_configuration.get('challenges', {})
    challenges = load_challenges(raw_challenges)

    conf = Configuration(
      challenges=challenges,
      projects=projects,
      )
    return conf
  except yaml.YAMLError as exc:
    print(f'Error in configuration file: {exc}')
    return None

def load_projects(raw_projects: Any | dict) -> list[Project]:
  """Load projects from raw dictionary.

  Args:
    raw_projects (Any | dict): raw projects collection.

  Returns:
    list[Project]: Projects list.
  """
  projects: list[Project] = []
  if isinstance(raw_projects, str):
    proj = get_project({'language': raw_projects})
    if proj is not None:
      projects.append(proj)
  else:
    for raw_proj in raw_projects:
      if isinstance(raw_proj, str):
        proj = get_project({'language': raw_proj})
      else:
        proj = get_project(raw_proj)

      if proj is not None:
        projects.append(proj)

  return projects

def load_challenges(raw_challenges: Any | dict) -> list[Challenge]:
  """Load challenges from raw challenge dictionary.

  Args:
    raw_challenges (Any | dict): raw challenge collection.

  Returns:
    list[Challenge]: Challenge list.
  """
  challenges: list[Challenge] = []
  if isinstance(raw_challenges, str):
    challenge = get_challenge({'name': raw_challenges})
    if challenge is not None:
      challenges.append(challenge)
  else:
    for raw_challenge in raw_challenges:
      if isinstance(raw_challenge, str):
        challenge = get_challenge({'name': raw_challenge})
      else:
        challenge = get_challenge(raw_challenge)

      if challenge is not None:
        challenges.append(challenge)

  return challenges
