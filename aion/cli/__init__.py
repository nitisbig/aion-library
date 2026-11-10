"""`aion` command line. Each file in aion/cli/commands/ defines one click command
named `cli`; it is discovered automatically and imported only when invoked.

    uv run aion --help
    uv run aion doctor
"""

from __future__ import annotations

import importlib
import pkgutil

import click

from aion.cli import commands as _commands_pkg

def _names() -> list[str]:
    return sorted(m.name.replace("_", "-") for m in pkgutil.iter_modules(_commands_pkg.__path__)
                  if not m.name.startswith("_"))


class _LazyGroup(click.Group):
    def list_commands(self, ctx):
        return _names()

    def get_command(self, ctx, name):
        if name not in _names():
            return None
        mod = importlib.import_module(f"aion.cli.commands.{name.replace('-', '_')}")
        return mod.cli


@click.group(cls=_LazyGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="aion", prog_name="aion")
def main():
    """aion: animation engine for math explainer videos.

    Start with `aion doctor`, then `aion new <slug>`. Agents: read AGENTS.md
    and use `aion catalog <query>` instead of reading source.
    """


if __name__ == "__main__":
    main()
