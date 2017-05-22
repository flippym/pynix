#
# Pynix Framework
# 

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1.0

import sys

try:
    from __main__ import __file__, __version__
except ImportError:
    pass

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from collections import OrderedDict
from getpass import getuser
from logging import FileHandler, Formatter, getLogger
from os import makedirs, path
from textwrap import dedent
from traceback import format_tb
from yaml import load_all, scanner # Trade YAML for ConfigParser


class Linux(object):

    progname = path.basename(__file__)
    loglevel = {'debug':10, 'info':20, 'warning':30, 'error':40, 'fatal':50}

    def __init__(self):

        #self._Parser = Parsing()
        #self.parse = self._Parser.Generate()

        #self.Reading = Reading()

        self.log = Logging(self._Parser.args.log, self._Parser.args.event)
        sys.excepthook = self.log.ErrHandler

        self._Parser.args.func(self.log)

        #if self.args.yaml:
        #    self.Reading()

    def Reading(self):

        try:
            with open(self.args.yaml, 'r') as openyaml:
                for section in load_all(openyaml):
                    for each in section:
                        if each == 'log':
                            self.args.log = section[each]['path']
                            self.args.event = section[each]['level']

                        elif each == 'other':
                            continue
                            # do something and create other sections

                        # elif each == 'some_section':
                            # do something

        except scanner.ScannerError as error:
            self.log("Syntax error in YAML file: {0}".format(error))
            raise SystemExit

        except IOError:
            self.log("No such file {0}".format(self.args.yaml))
            raise SystemExit

        except KeyError as error: # Escape other errors
            self.log("Warning, key {0} in '{1}' is not defined".format(error, each))


class Parsing(object): #Not fully functional, optional arguments are not parsed when before positional

    positional = []

    def __init__(self):
        
        parser = ArgumentParser(prog='python3 {}'.format(Linux.progname), add_help=False, 
            formatter_class=RawDescriptionHelpFormatter, description = dedent('''\
                 Pynix Framework
                -----------------
                  RHEL framework
                  for running
                  daemons and
                  scripts.
                '''), epilog = dedent('''\
                Check the git repository at https://github.com/flippym/pynix,
                for more information about usage, documentation and bug report.'''))

        self.subparser = parser.add_subparsers(title='Positional', help='To see available options, use --help with each command', 
            metavar='<command>')

        #self.func = parser.parse_args().func.__qualname__
        
        for sub in self.Generate():
            self.Subparser(sub)

        self.Optional(parser, True)
        self.args = parser.parse_args()

        if len(sys.argv) == 1: # Returns the help message in case no arguments are provided
            parser.print_help()
            raise SystemExit

    def Generate(self): # Subparsers are defined here with the following syntax
        
        generate = {'_name':'generate', '_help':'Generate program files',
                    'bash-completion':
                        {'help':'Generate bash-completion for program', 'func':Generate.BashCompletion},
                    'conf':
                        {'help':'Generate YAML template file for optional configurations', 'func':Generate.Conf},
                    'log':
                        {'help':'Generate YAML template file for log configurations', 'func':Generate.Log},
                    'spec':
                        {'help':'Generate SPEC template file for RPM building', 'func':Generate.Spec},
                    'unit':
                        {'help':'Generate UNIT template file for integration with systemd', 'func':Generate.Unit},
                   }

        daemon = {'_name':'daemon', '_help':'Daemon program management',
                    'disable':
                        {'help':'Remove daemon from system startup', 'func':Daemon.Disable},
                    'enable':
                        {'help':'Add daemon to system startup', 'func':Daemon.Enable},
                    'reload':
                        {'help':'Reload daemon configurations', 'func':Daemon.Reload},
                    'start':
                        {'help':'Initiate program as daemon', 'func':Daemon.Start},
                    'status':
                        {'help':'Check daemon running status', 'func':Daemon.Status},
                    'stop':
                        {'help':'Stop daemon program', 'func':Daemon.Stop},
                 }

        script = {'_name':'script', '_help':'Script program management',
                    'run':
                        {'help':'Initiate program as a script', 'func':Script.Run},
                 }

        for each in [generate, daemon, script]: # trade append for extend()
            self.positional.append(each)

        return self.positional

    def Subparser(self, parsers: dict) -> None:

        parser = self.subparser.add_parser(parsers['_name'], help=parsers['_help'], add_help=False)
        subparser = parser.add_subparsers(title='Positional', metavar='<subcommand>')
        subparser.required = True

        for each in sorted(parsers):
            if not each.startswith('_'):
                positional = subparser.add_parser(each, help=parsers[each]['help'], add_help=False)
                positional.set_defaults(func=parsers[each]['func'])
                self.Optional(positional, generate=parsers['_name'] == 'generate')

        self.Optional(parser)

    def Optional(self, parser: object, version=False, generate=False) -> None:

        loglevel = ', '.join(sorted(Linux.loglevel.keys(), key=Linux.loglevel.get))

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-c', '--conf', metavar='file', type=str, help='Configuration file path for parameters configuration')
        optional.add_argument('-e', '--event', metavar='lvl', choices=Linux.loglevel.keys(), default='info',
            help='Event log level: {}\n(default: info)'.format(loglevel))
        optional.add_argument('-l', '--log', metavar='file', type=str, help='Redirect all output to log file for event logging')

        if generate:
            optional.add_argument('-p', '--path', metavar='file', type=str, help='Specify path and file name for file generation')

        optional.add_argument('-h', '--help', action='help', help='Show this help message')

        if version:
            optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(Linux.progname, __version__),
                help='Show program version')


class Logging(object): #Consider loading from yaml file

    def __init__(self, logpath, level):

        self.level = level

        if logpath:
            try:
                self.logger = getLogger(__name__)
                handler = FileHandler(logpath)
                formatter = Formatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%d %b %Y %H:%M:%S')
                level = Linux.loglevel[level]

                handler.setLevel(level)
                handler.setFormatter(formatter)

                self.logger.setLevel(level)
                self.logger.addHandler(handler)

            except IOError:
                print("Permission denied to create log file in specified path")
                raise SystemExit

            except NameError as e:
                print("Unable to log to file {0}, {1}".format(logpath, e))
                raise SystemExit

        else:
            self.logger = None

    def __call__(self, string, level = 'info'):
        
        if self.logger:
            self.logger.log(Linux.loglevel[level], string)

        elif Linux.loglevel[level] >= Linux.loglevel[self.level]: # Restrict ouput based on event level
            print(string)

    def ErrHandler(self, error, value, trace):

        trace = ''.join(format_tb(trace))

        self('Uncaught exception: {0}\nTraceback (most recent call last):\n{1}{0}: {2}'.format(error.__name__, trace,
            value), 'error')
        

class Generate(object):

    def BashCompletion(logger):

        logger("Generating new bash completion file")
        parsers, subparsers = OrderedDict(), set()

        for parser in Parsing.Generate(None): # Structures the dictionary into a more malleable format
            parsers[parser['_name']] = [k for k,v in parser.items() if not k.startswith('_')] # Get from Parsing().parser, instead Parsing.Generate() 

        for name in parsers.keys(): # Dynamic bash completion subparser syntax
            variables = ' '.join(sorted(parsers[name]))
            subparsers.add('{0}="{1}"'.format(name, variables))

        with open('/etc/bash_completion.d/{}'.format(path.splitext(Linux.progname)[0]), 'w') as openbash:
            openbash.write(dedent('''\
                _{0}()
                {{
                    local cur prev opts
                    COMPREPLY=()
                    cur="${{COMP_WORDS[COMP_CWORD]}}"
                    prev="${{COMP_WORDS[COMP_CWORD-1]}}"
                    serv="{1}"
                    {2}
                    opts="--help --verbose --version"
                    if [[ ${{cur}} == -* ]] ; then
                        COMPREPLY=( $(compgen -W "${{opts}}" -- ${{cur}}) )
                        return 0
                    elif [[ $prev == {0} ]] ; then
                        COMPREPLY=( $(compgen -W "${{serv}}" -- ${{cur}}) )
                        return 0
                    else
                        for each in $serv ; do
                            if [[ ${{prev}} == $each ]] ; then
                                COMPREPLY=( $(compgen -W "${{!each}}" -- ${{cur}}) )
                                return 0
                            fi
                        done
                    fi
                }}
                complete -F _{0} {0}''').format(Linux.progname, ' '.join(parsers.keys()), '\n    '.join(subparsers)))

    def Conf(logger):

        logger("Generating new template configuration file")
        newyaml = path.realpath(__file__).replace('.py', '.yaml')

        if path.isfile(newyaml):
            logger("The file {} already exists".format(newyaml), 'error')
            raise SystemExit

        with open(newyaml, 'w') as openyaml: #Change log name and dir to name invoked in other script, not pynix
            openyaml.write(dedent('''\
                log:
                    path: /var/log/{0}/{1}
                    level: info
                other:
                    something:
                        - some other things
                    check: yes
                ''').format(path.splitext(Linux.progname)[0], Linux.progname.replace('.py', '.log')))

    def Log(logger):

        logger("Generating new template log configuration file")

    def Spec(logger):

        logger("Generating new template spec file")

    def Unit(logger):

        logger("Generating new template unit file")


class Daemon(object):

    def Disable(logger):

        logger("Disabling running daemon")

    def Enable(logger):

        logger("Enabling running daemon")

    def Reload(logger):

        logger("Reloading running daemon")

    def Start(logger):

        logger("Starting daemon")

    def Status(logger):

        pass

    def Stop(logger):

        logger("Stoping running daemon")


class Script(object):

    def Run(logger):

        logger("Starting script")
