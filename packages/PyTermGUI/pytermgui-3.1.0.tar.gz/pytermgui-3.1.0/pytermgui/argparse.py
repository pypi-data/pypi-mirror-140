from argparse import ArgumentParser as _Argparser

from .ansi_interface import terminal
from .widgets import Container, Splitter, Label


class ArgumentParser(_Argparser):
    def print_help(self, file=None) -> None:
        root = Container("[245 italic]> " + self.description, width=terminal.width)

        body = Container(relative_width=0.7)
        options = Container(relative_width=0.3)
        descriptions = Container(relative_width=0.6)

        for action in self._actions:
            line = ""
            for item in action.option_strings:
                if len(line) > 0:
                    line += "[/fg], "

                line += "[72]" + item

            # body += Splitter(Label(f"{line:<20}", parent_align=0), Label(action.help))
            # body += Splitter("", "")

            options += Label(f"{line:<20}", parent_align=0)
            descriptions += Label(action.help)

        root += Splitter(options, descriptions)

        for line in root.get_lines():
            print(line)
