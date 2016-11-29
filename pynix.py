#!/usr/bin/env python3

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
from sys import argv
from textwrap import dedent
from traceback import format_tb
from yaml import load_all, scanner


class Initiate(object):

    progname = path.basename(__file__)
    loglevel = {'debug':10, 'info':20, 'warning':30, 'error':40, 'fatal':50}

    def __init__(self):

        self.Parser = Parsing()
        #self.Reading = Reading()
        #Concatenate() # Put all Parsing arguments and Reading parameters as the same variable, giving priority to parser
        #self.Logger = Logging(self.Parser.args)

        #sys.excepthook = self.Logger.ErrHandler

        #if self.args.yaml:
        #    self.Reading()

        #if self.args.log:
        #    self.logger = self.Logging()


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
            LogWrite("Syntax error in YAML file: %s" % error)
            raise SystemExit

        except IOError:
            LogWrite("No such file %s" % self.args.yaml)
            raise SystemExit

        except KeyError as error: # Escape other errors
            LogWrite("Warning, key %s in '%s' not defined" % (error, each))


class Parsing(object):

    def __init__(self):
        
        parser = ArgumentParser(prog='python3 {}'.format(Initiate.progname), add_help=False, 
                                formatter_class=RawDescriptionHelpFormatter, description = dedent('''\
                                    Pynix RHEL Framework !
                                    ----------------------
                                      RHEL framework for
                                      running daemons 
                                      and scripts.
                                    '''), epilog = dedent('''\
                                    Check the git repository at https://github.com/flippym/pynix,
                                    for more information about usage, documentation and bug report.'''))

        self.subparser = parser.add_subparsers(title='Positional', help='To see available options, use --help with each command', 
                                               metavar='<command>')
        
        for sub in self.Generate():
            self.Subparser(sub)

        self.Optional(parser, True)
        self.args = parser.parse_args()

        if len(argv) == 1: # Returns the help message in case no arguments are provided
            parser.print_help()
            raise SystemExit

        self.args.func()


    def Generate(self): # Subparsers are defined here with the following syntax
        
        generate = {'_name':'generate', '_help':'Generate template files',
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

        return generate, daemon, script


    def Subparser(self, parsers: dict) -> None:

        parser = self.subparser.add_parser(parsers['_name'], help=parsers['_help'], add_help=False)
        subparser = parser.add_subparsers(title='Positional', metavar='<subcommand>')
        subparser.required = True

        del parsers['_name'], parsers['_help']

        for each in sorted(parsers):
            positional = subparser.add_parser(each, help=parsers[each]['help'], add_help=False)
            positional.set_defaults(func=parsers[each]['func'])
            self.Optional(positional)

        self.Optional(parser)


    def Optional(self, parser: object, version=False) -> None:

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-c', '--conf', metavar='file', type=str, help='Configuration file path for parameters configuration', required=False)
        optional.add_argument('-e', '--event', metavar='lvl', choices=Initiate.loglevel.keys(), help='Event log level: {}\n(default: info)'.format(', '.join(Initiate.loglevel.keys())), required=False, default='info')
        optional.add_argument('-l', '--log', metavar='file', type=str, help='Redirect all output to log file for event logging', required=False)
        optional.add_argument('-h', '--help', action='help', help='Show this help message')

        if version:
            optional.add_argument('-v', '--version', action='version', version='{0} {1}'.format(Initiate.progname, __version__), help='Show program version')

        #if parser.getname() == 'generate':
        #    optional.add_argument('-p', '--path', metavar='file', type=str, help='Specify path and file name for file generation')


class Logging(object): # Consider loading from yaml file

    def __init__(self, args):

        #path.realpath(args.log).rpartition('/')[0] # path.realpath to prevent error when the full path ain't specified

        self.logger = getLogger(__name__)

        try:
            handler = FileHandler(args.log)
            formatter = Formatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s', datefmt='%d %b %Y %H:%M:%S')

            if args.event:
                level = Initiate.loglevel[args.event]
                self.logger.setLevel(level)
                handler.setLevel(level)

            else:
                self.logger.setLevel(Initiate.loglevel['info'])
                handler.setLevel(Initiate.loglevel['info'])
        
        except (ValueError, NameError):
            LogWrite("Unknown log level in YAML file")
            raise SystemExit

        except IOError:
            LogWrite("Permission denied to create log file in specified path")
            raise SystemExit

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    def LogWrite(self, string, level = 'info'):

        if self.logger:
            self.logger.log(Initiate.loglevel[level], string)

        else: #level == args.event: # When the event level is set, it will only print above levels
            print(string)


    def ErrHandler(self, error, value, trace):

        trace = ''.join(format_tb(trace))

        self.LogWrite('Uncaught exception: %s' % (error.__name__), 'error') # Keep in mind this description methodology, info, warning, error, fatal -short; debug -long
        self.LogWrite('Uncaught exception\nTraceback (most recent call last):\n{0}{1}: {2}'.format(trace, error.__name__, value), 'debug')


class Generate(object):

    def BashCompletion():

        parsers, subparsers = OrderedDict(), set()

        for parser in Parsing.Generate(None): # Structures the dictionary into a more malleable format
            parsers[parser['_name']] = [k for k,v in parser.items() if not k.startswith('_')]

        for name in parsers.keys(): # Dynamic bash completion subparser syntax
            variables = ' '.join(sorted(parsers[name]))
            subparsers.add('{0}="{1}"'.format(name, variables))

        with open('/etc/bash_completion.d/{}'.format(path.splitext(Initiate.progname)[0]), 'w') as openbash:
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
                complete -F _{0} {0}''').format(Initiate.progname, ' '.join(parsers.keys()), '\n    '.join(subparsers)))


    def Conf():

        newyaml = path.realpath(__file__).replace('.py', '.yaml')

        if path.isfile(newyaml):
            LogWrite("The file {} already exists.".format(newyaml))
            raise SystemExit

        with open(newyaml, 'w') as openyaml: # Change log name and dir to name invoked in other script, not pynix
            openyaml.write(dedent('''\
                log:
                    path: /var/log/{0}/{1}
                    level: info
                other:
                    something:
                        - some other things
                    check: yes
                ''').format(path.splitext(Initiate.progname), Initiate.progname.replace('.py', '.log')))


    def Log():

        pass


    def Spec():

        pass


    def Unit():

        pass


class Daemon(object):

    def Disable():

        pass


    def Enable():

        pass


    def Reload():

        pass


    def Start():

        pass


    def Status():

        pass


    def Stop():

        pass


class Script(object):

    def Run():

        pass