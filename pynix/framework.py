# Pynix Framework

__author__ = "Frederico Martins"
__license__ = "GPLv3"
__version__ = 1.0

import sys

from collections import OrderedDict
from getpass import getuser
from logging import FileHandler, Formatter, getLogger
from os import makedirs, path
from sys import exit
from textwrap import dedent
from traceback import format_tb

from pynix import exceptions


program = path.basename(__file__)
translate = OrderedDict([('debug', 10), ('info', 20), ('warning', 30), ('error', 40), ('fatal', 50)])


class Linux(object):

    def __init__(self, log=None, level='info'):

        try:
            self.log = Logging(log, translate[level])
        except KeyError as error:
            raise exceptions.InvalidLogLevel(error, ', '.join(translate.keys())) from None
        else:
            sys.excepthook = self.ErrorHandler

    def ErrorHandler(self, error, value, trace):

        trace = ''.join(format_tb(trace))

        self.log('Uncaught exception: {0}\nTraceback (most recent call last):\n{1}{0}: {2}'.format(error.__name__, trace,
            value), 'error')


class Logging(object):

    def __init__(self, log, level):

        self.level = level

        if log:
            self.logger = getLogger(__name__)
            try:
                handler = FileHandler(log)
            except IOError:
                raise exceptions.PermissionDenied(log) from None
            except NameError as error:
                print("Unable to log to file {0}, {1}".format(log, error))
            else:
                handler.setLevel(self.level)
                handler.setFormatter(Formatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s', 
                    datefmt='%d %b %Y %H:%M:%S'))
                self.logger.setLevel(self.level)
                self.logger.addHandler(handler)

    def __call__(self, string, level='info'):

        if translate[level] >= self.level: # Restrict ouput based on event level
            if self.logger:
                self.logger.log(translate[level], string)
            else:
                print(string)


class Generate(object):

    def BashCompletion(logger):

        logger("Generating new bash completion file")
        parsers, subparsers = OrderedDict(), set()

        for parser in Parsing.Generate(None): # Structures the dictionary into a more malleable format
            parsers[parser['_name']] = [k for k,v in parser.items() if not k.startswith('_')] # Get from Parsing().parser, instead Parsing.Generate() 

        for name in parsers.keys(): # Dynamic bash completion subparser syntax
            variables = ' '.join(sorted(parsers[name]))
            subparsers.add('{0}="{1}"'.format(name, variables))

        with open('/etc/bash_completion.d/{}'.format(path.splitext(program)[0]), 'w') as openbash:
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
                complete -F _{0} {0}''').format(program, ' '.join(parsers.keys()), '\n    '.join(subparsers)))

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
                ''').format(path.splitext(program)[0], program.replace('.py', '.log')))

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
