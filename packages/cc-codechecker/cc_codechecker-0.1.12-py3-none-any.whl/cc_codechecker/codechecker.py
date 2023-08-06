# SPDX-FileCopyrightText: 2022 Daniele Tentoni <daniele.tentoni.1996@gmail.com
#
# SPDX-License-Identifier: MIT

"""Codechecker top-level functions.

Functions written in this file has to be considered our **public api**.
Any change to this file as to be considered a breaking change if it require
any update to other users.
"""

# Standard Library
import argparse
import os
import sys
from argparse import Namespace
from importlib.metadata import version
from textwrap import dedent

import yaml

# Codechecker
from cc_codechecker.challenge import Challenge
from cc_codechecker.configuration import (
  FILE_NAME,
  Configuration,
  get_configuration,
  set_configuration,
)
from cc_codechecker.context import Context
from cc_codechecker.project import Project


def check(options: Namespace) -> int: # pragma: no cover
  """Check the current configuration.

  Try to load the current configuration to check possible errors.

  Args:
    options (Namespace):
      Application context from argparse.

  Returns:
    int: Exit code.
  """
  context = Context(options)
  raw_configuration = _read_conf_from_file()
  configuration = get_configuration(raw_configuration)
  if context.options().verbose:
    print(f'Retrieved configuration: {configuration}')

  return os.EX_OK

def init(options: Namespace) -> int: # pragma: no cover
  """Initialize a new challenge.

  Initialize a new challenge by create the configuration file in the root
  directory where the toll was executed.

  Args:
    options (Namespace):
      Application context from argparse.

  Returns:
    int: Exit code.
  """
  context = Context(options)
  if context.options().verbose:
    print('Initializing a new challenge')

  hidden = os.path.isfile('.codechecker.yml')
  overwrite = context.options().overwrite_yml
  if not overwrite and hidden:
    print('You already have a codechecker project installed')
    return os.EX_CANTCREAT

  # This is the minimal valid configuration.
  conf = Configuration(
    [Challenge(name='base')],
    [Project('bash')],
  )
  set_configuration(conf)
  if context.options().verbose:
    print('Initialization completed')

  if not os.path.isfile('README.md'):
    try:
      with open('README.md', 'w', encoding='locale') as writer:
        writer.write('# Coding Challenge')
    except OSError as os_error:
      print(f'Error during README generation {os_error}')
      return os.EX_CANTCREAT

  return os.EX_OK

def _read_conf_from_file() -> dict:
  try:
    with open(FILE_NAME, encoding='locale') as file:
      return yaml.full_load(file)
  except OSError as os_error:
    print(f'Problem opening the configuration file: {os_error}')
    raise ValueError('Fail to retrieve configuration file') from os_error
  except Exception as ex:
    print(f'Unknown exception while reading configuration due to {ex}')
    raise Exception from ex

def run(options: Namespace) -> int: # pragma: no cover
  """Run the coding challenge.

  Run the coding challenge, executing all challenges for all projects and
  writing a result. Return 0 if all is ok, otherwise try to return the most
  semantic error code from the context.

  Args:
    options (Namespace):
      Application context from argparse.

  Returns:
    int: Exit code.
  """
  context = Context(options)
  raw_configuration = _read_conf_from_file()
  configuration = get_configuration(raw_configuration)
  if configuration is None:
    if context.options().verbose:
      print('Configuration file is empty, no work to do')
    return os.EX_CONFIG

  if not isinstance(configuration, Configuration):
    if context.options().verbose:
      c = configuration.__class__
      print(f'''Configuration not well formed, found {c} instead of
            cc_codechecker.configuration.Configuration''')

    return os.EX_CONFIG

  configuration.run()
  return os.EX_OK

def parse_args(args) -> Namespace: # pragma: no cover
  """Parse args.

  Args:
      args (dict): arguments to parse.

  Returns:
      Namespace: options parsed.
  """
  parser = argparse.ArgumentParser(
    description=dedent('''\
      ╭━━━╮    ╭╮   ╭━━━┳╮       ╭╮
      ┃╭━╮┃    ┃┃   ┃╭━╮┃┃       ┃┃
      ┃┃ ╰╋━━┳━╯┣━━╮┃┃ ╰┫╰━┳━━┳━━┫┃╭┳━━┳━╮
      ┃┃ ╭┫╭╮┃╭╮┃┃━┫┃┃ ╭┫╭╮┃┃━┫╭━┫╰╯┫┃━┫╭╯
      ┃╰━╯┃╰╯┃╰╯┃┃━┫┃╰━╯┃┃┃┃┃━┫╰━┫╭╮┫┃━┫┃
      ╰━━━┻━━┻━━┻━━╯╰━━━┻╯╰┻━━┻━━┻╯╰┻━━┻╯

      Manage coding challenges
      '''),
    formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='''run the program in verbose version, making easy following the
    program flow''')
  parser.add_argument(
    '--version',
    action='store_true',
    help='show program version number'
  )
  subparsers = parser.add_subparsers(
    title='subcommands',
    description='valid subcommands',
    help='additional help',
  )
  config_parser = subparsers.add_parser(
    'config',
    description='run a check of the challenge configuration',
    help='help you to config codechecker',
    )
  config_parser.set_defaults(func=check)
  config_parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='print the configuration read to screen',
  )
  init_parser = subparsers.add_parser(
    'init',
    description='''init a new challenge in the current directory. This command
    doesn\'t have any effect if ran in a folder with already a challenge
    configured. If you want to overwrite current configuration, see
    --overwrite-* options.''',
    help='help you create a new challenge',
  )
  init_parser.set_defaults(func=init)
  init_parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='print initialization steps to screen'
  )
  init_parser.add_argument(
    '-o',
    '--overwrite-yml',
    action='store_true',
    help='overwrite current yaml configuration file.',
  )
  run_parser = subparsers.add_parser(
    'run',
    description='run the challenge',
    help='run the coding challenge',
  )
  run_parser.set_defaults(func=run)
  run_parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='print run steps to screen',
  )
  return parser.parse_args(args)

def main(): # pragma: no cover
  """Execute the program."""
  parser = parse_args(sys.argv[1:])
  try:
    if parser.version:
      __version__ = version('cc-codechecker')
      print(__version__)
      sys.exit(os.EX_OK)

    sys.exit(parser.func(parser))
  except AttributeError as aex:
    if parser.verbose:
      if not hasattr(parser, 'func'):
        print('''You had run an unknown command. Ask for help running
              `cc_codechecker -h`''')
      else:
        print(f'Attribute exception {aex.with_traceback(None)}')

    sys.exit(os.EX_NOINPUT)
