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
from logging import FileHandler, Formatter, getLogger
from os import makedirs, path
from sys import argv
from textwrap import dedent
from traceback import format_tb
from yaml import load_all, scanner


class Initiate(object):

    progname = __file__.rpartition('/')[2]
    loglevel = {'debug':10, 'info':20, 'warning':30, 'error':40, 'fatal':50}

    def __init__(self):

        self.Parser = Parsing()
        #self.Reading = Reading()
        #Concatenate() # Put all Parsing arguments and Reading parameters as the same variable, giving priority to parser
        self.Logger = Logging(self.Parser.args)

        sys.excepthook = self.Logger.ErrHandler

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
        
        parser = ArgumentParser(prog = 'python3 %s' % Initiate.progname, add_help = False, formatter_class = RawDescriptionHelpFormatter,
                                description = dedent('''\
                                    Pynix RHEL Framework !
                                    ----------------------
                                      RHEL framework for
                                      running daemons 
                                      and scripts.
                                    '''), epilog = dedent('''\
                                    Check the git repository at https://github.com/flippym/pynix,
                                    for more information about usage, documentation and bug report.'''))

        self.subparser = parser.add_subparsers(title='Positional', help='To see available options, use --help with each command', metavar='<command>')

        generate = {'bash-completion':
                        {'help':'Generate bash-completion for program', 'func':Generate.BashCompletion},
                    'program-yaml':
                        {'help':'Generate YAML template file for optional configurations', 'func':Generate.YamGenerate},
                   }

        self.Subparser('generate', {'generate':'Generate template files', 'bash-completion':'testmessage', 'program-yaml':'test'}, generate)
        #genparser = subparser.add_parser('generate', help='Generate template files', add_help=False)
        #gensub = genparser.add_subparsers(title='Positional', metavar='<subcommand>')
        #gensub.required = True

        #gensub.add_parser('bash-completion', help='Generate bash-completion for program', add_help=False)#.set_defaults(func=BashCompletion)
        #gensub.add_parser('program-yaml', help='Generate YAML template file for optional configurations', add_help=False).set_defaults(func=YamGenerate)
        #gensub.add_parser('log-yaml', help='Generate YAML template file for log configurations', add_help=False)
        #gensub.add_parser('rpm-spec', help='Generate SPEC template file for RPM building', add_help=False)
        #gensub.add_parser('systemd-unit', help='Generate UNIT template file for integration with systemd', add_help=False)
        #optional = genparser.add_argument_group('Optional')
        #optional.add_argument('-h', '--help', action = 'help', help = 'Show this help message')
        
        #daemonparser = subparser.add_parser('daemon', help='Daemon program management', add_help=False) # YAML
        #daemonsub = daemonparser.add_subparsers(title='Positional', metavar='subcommand')
        #daemonsub.required = True
        #daemonsub.add_parser('disable', help='Remove daemon from system startup')#.set_defaults(func=self.Reading)
        #daemonsub.add_parser('enable', help='Add daemon to system startup')
        #daemonsub.add_parser('reload', help='Reload daemon configurations')
        #daemonsub.add_parser('status', help='Check daemon running status')
        #daemonsub.add_parser('start', help='Initiate program as daemon')
        #daemonsub.add_parser('stop', help='Stop daemon program')
        #optional = daemonparser.add_argument_group('Optional')
        #optional.add_argument('-h', '--help', action = 'help', help = 'Show this help message')
        
        #scriptparser = subparser.add_parser('script', help='Script program execution', add_help=False)
        #scriptsub = scriptparser.add_subparsers(title='Positional', metavar='subcommand')
        #scriptsub.required = True
        #scriptsub.add_parser('run', help='Daemon program management', add_help=False)
        #optional = scriptparser.add_argument_group('Optional')
        #optional.add_argument('-h', '--help', action = 'help', help = 'Show this help message')

        self.Optional(parser)
        #self.Optional(daemonparser)

        self.args = parser.parse_args()

        if len(argv) == 1: # Returns the help message in case no arguments are provided
            parser.print_help()
            raise SystemExit

        #self.args.func()


    def Subparser(self, name, parsers):

        parser = self.subparser.add_parser(name, help=parsers[name]['help'], add_help=False)
        subparser = parser.add_subparsers(title='Positional', metavar='<subcommand>')
        subparser.required = True

        for each in parsers:
            positional = subparser.add_parser(each, help=parsers[each]['help'], add_help=False)
            positional.set_defaults(func=parsers[each]['func'])
            self.Optional(positional)

        self.Optional(parser)


    def Optional(self, parser):

        optional = parser.add_argument_group('Optional')
        optional.add_argument('-l', '--log', metavar = 'file', type = str, help = 'Log file path for event logging', required = False)
        optional.add_argument('-y', '--yaml', metavar = 'file', type = str, help = 'YAML file path for script configuration', required = False)
        optional.add_argument('-e', '--event', metavar = 'lvl', choices = Initiate.loglevel.keys(), help = 'Event log level: %s\n(default: info)' % ', '.join(Initiate.loglevel.keys()), required = False, default = 'info')
        optional.add_argument('-v', '--version', action = 'version', version = '%s %s' % (Initiate.progname, __version__), help = 'Show program version')
        optional.add_argument('-h', '--help', action = 'help', help = 'Show this help message')


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
        self.LogWrite('Uncaught exception\nTraceback (most recent call last):\n%s%s: %s' % (trace, error.__name__, value), 'debug')


class Generate(object):

    def YamGenerate():

        newyaml = path.realpath(__file__).replace('.py', '.yaml')

        if path.isfile(newyaml):
            LogWrite("The file %s already exists." % newyaml)
            raise SystemExit

        with open(newyaml, 'w') as openyaml: # Change log name and dir to name invoked in other script, not pynix
            openyaml.write(dedent('''\
                log:
                    path: /var/log/%s/%s
                    level: info
                other:
                    something:
                        - some other things
                    check: yes
                ''' % (Initiate.progname.split('.py')[0], Initiate.progname.replace('.py', '.log')))) # change % to format


    def BashCompletion():

        with open('/home/%s/.bashrc' % getpass.getuser(), 'w') as bashrc:

            bashrc.write('alias im-a-py=\'python3 %s\'\n\nfor file in /etc/bash_completion.d/* ; do\n    source "$file"\ndone' % __file__)

        if not os.path.isdir('/etc/bash_completion.d/'):
            os.makedirs('/etc/bash_completion.d/')

        with open('/etc/bash_completion.d/im-a-py', 'w') as imapy:
            imapy.write(dedent('''\
                _im-a-py()
                {
                    local cur prev opts
                    COMPREPLY=()
                    cur="${COMP_WORDS[COMP_CWORD]}"
                    prev="${COMP_WORDS[COMP_CWORD-1]}"
                    serv="install radio iptv database multi-equip"
                    pack="bash-completion"
                    opts="--help --verbose --version"
                    if [[ ${cur} == -* ]] ; then
                        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
                        return 0
                    elif [[ $prev == im-a-py ]] ; then
                        COMPREPLY=( $(compgen -W "${serv}" -- ${cur}) )
                        return 0
                    elif [[ ${prev} == "install" ]] ; then
                        COMPREPLY=( $(compgen -W "${pack}" -- ${cur}) )
                        return 0
                    fi
                }
                complete -F _im-a-py im-a-py
                '''))

Initiate()