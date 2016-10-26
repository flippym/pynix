#!/usr/bin/env python3

__author__ = "Frederico Martins"
__email__ = "fredericomartins@outlook.com"
__license__ = "GPLv3"
__version__ = 1.0

import sys

from argparse import ArgumentParser, SUPPRESS, RawDescriptionHelpFormatter
from logging import DEBUG, ERROR, FATAL, FileHandler, Formatter, getLogger, INFO, WARNING
from os import makedirs, path
from textwrap import dedent
from traceback import format_tb
from yaml import load_all, scanner


class Initiate(object):

    progname = __file__.rpartition('/')[2] # To remove a replace with the other script __file__
    loglevel = ['debug', 'info', 'warning', 'error', 'fatal'] # To replace with logging.getloglevels()

    def __init__(self):#, progname):

        self.Parsing() # keep only class Parsing in this file, with function __init__ instead of function Parsing. Put all others in another file for import | Lib project

        if self.args.yaml:
            self.Reading()

        if self.args.log:
            self.Logging()

        if self.args.generate_yaml: # template generate conf-yaml/log-yaml/bash-completion, positional
            YamGenerate()

        # Create positional daemon/script


    def Parsing(self):
                
        parser = ArgumentParser(prog = 'python3 %s' % self.progname, add_help = False, formatter_class = RawDescriptionHelpFormatter,
                                description = dedent('''\
                                    This is a script template!
                                    --------------------------
                                        Enter description
                                        here.
                                    '''), epilog = 'Script Template Epilog')

        parser.add_argument('-l', '--log', metavar = 'file', type = str, help = 'Log file path for event logging', required = False)
        parser.add_argument('-y', '--yaml', metavar = 'file', type = str, help = 'YAML file path for script configuration', required = False)
        parser.add_argument('-e', '--event', metavar = 'lv', choices = self.loglevel, help = 'Event log level: %s\n(default: info)' % ', '.join(self.loglevel), required = False, default = 'info')
        parser.add_argument('-g', '--generate-yaml', action = 'store_true', help = 'Generate YAML template file in the script current directory')
        parser.add_argument('-v', '--version', action = 'version', version = '%s %s' % (self.progname, __version__), help = 'Show program version')
        parser.add_argument('-h', '--help', action = 'help', help = 'Show this help message')

        parser.add_argument('generate', help = '--help, for subcommands available', nargs = '?') # Divide in 1 command, with costum help message
        parser.add_argument('daemon', help = '--help, for subcommands available', nargs = '?')
        parser.add_argument('script', help = '--help, for subcommands available', nargs = '?')

        self.args = parser.parse_args()


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


    def Logging(self): # Consider loading from yaml file

        global logger

        DirCreate(path.realpath(self.args.log).rpartition('/')[0]) # path.realpath to prevent error when the full path ain't specified
        sys.excepthook = ErrHandler # For removal, place in main script

        logger = getLogger(__name__)

        try:
            handler = FileHandler(self.args.log)
            formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            if self.args.event:
                level = eval(self.args.event.upper())
                logger.setLevel(level)
                handler.setLevel(level)

            else:
                logger.setLevel(INFO)
                handler.setLevel(INFO)
        
        except (ValueError, NameError):
            LogWrite("Unknown log level in YAML file")
            raise SystemExit

        except IOError:
            LogWrite("Permission denied to create log file in specified path")
            raise SystemExit

        handler.setFormatter(formatter)
        logger.addHandler(handler)


def DirCreate(directory):

    if not path.exists(directory):
        makedirs(directory)


def LogWrite(string, level = 'info'):

    if 'logger' in globals() and level in Initiate.loglevel:
        getattr(logger, level)(string)

    else: # elif level == something: # So when the -e argument takes some level, it will only print that level. Ex: -e warning, it will only print LogWrite('string', 'warning') and above levels
        print(string)


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


def ErrHandler(error, value, trace):

    trace = ''.join(format_tb(trace))

    LogWrite('Uncaught exception: %s' % (error.__name__), 'error') # Keep in mind this description methodology, info, warning, error, fatal -short; debug -long
    LogWrite('Uncaught exception\nTraceback (most recent call last):\n%s%s: %s' % (trace, error.__name__, value), 'debug')


Initiate()

LogWrite('Starting script execution')
# ... Code goes here
LogWrite('Script execution ended')