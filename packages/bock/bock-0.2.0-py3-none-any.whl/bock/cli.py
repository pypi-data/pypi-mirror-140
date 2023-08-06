import os
import click

# commands to be loaded for click
# according to: https://click.palletsprojects.com/en/8.0.x/commands/#nested-handling-and-contexts

class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        commands = []
        commands_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))
        for filename in os.listdir(commands_folder):
            if filename.endswith(".py") and filename != '__init__.py':
                commands.append(filename.replace(".py", ""))

        commands.sort()
        return commands

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"bock.commands.{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli



@click.command(cls=ComplexCLI)
def cli():
    """Welcome to Bock! An all-in-one cli utility tool for GAMS development!"""
    pass