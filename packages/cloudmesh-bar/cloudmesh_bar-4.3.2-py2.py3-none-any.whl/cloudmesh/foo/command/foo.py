from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters

class FooCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_foo(self, args, arguments):
        """
        ::

          Usage:
                foo -f FILE
                foo FILE
                foo list

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

        """
        VERBOSE(arguments)
