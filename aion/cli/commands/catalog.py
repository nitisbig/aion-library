"""aion catalog: search the API (signatures + one-line docs) without reading source."""

from __future__ import annotations

import json

import click


@click.command()
@click.argument("query", required=False)
@click.option("--full", is_flag=True, help="Include docstring examples.")
@click.option("--json", "as_json", is_flag=True)
def cli(query, full, as_json):
    """Print matching exports: name(signature)  # summary  [module]."""
    from aion import catalog

    es = catalog.search(query)
    if as_json:
        click.echo(json.dumps(catalog.as_json(es), indent=1))
    else:
        click.echo(catalog.render_lines(es, full) or f"no match for {query!r}")
