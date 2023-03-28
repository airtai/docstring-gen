# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/CLI.ipynb.

# %% auto 0
__all__ = ['gen']

# %% ../nbs/CLI.ipynb 2
from typing import *
from pathlib import Path
import importlib

import typer

from .docstring_generator import add_docstring_to_source

# %% ../nbs/CLI.ipynb 5
_app = typer.Typer()


@_app.command(
    help="This command reads a Jupyter notebook or Python file, or a directory containing these files, and adds docstrings to classes and methods that do not have them.",
)
def gen(
    path: str = typer.Argument(
        ".",
        help="The path to the Jupyter notebook or Python file, or a directory containing these files",
    ),
    include_auto_gen_txt: bool = typer.Option(
        True,
        help="If set to True, a note indicating that the docstring was autogenerated by docstring-gen library will be added to the end.",
    ),
    recreate_auto_gen_docs: bool = typer.Option(
        False,
        "--force-recreate-auto-generated",
        "-f",
        help="If set to True, the autogenerated docstrings from the previous runs will be replaced with the new one.",
    ),
    model: str = typer.Option(
        "gpt-3.5-turbo",
        help="The name of the GPT model that will be used to generate docstrings.",
    ),
    temperature: float = typer.Option(
        0.2,
        help="Setting the temperature close to zero produces better results, whereas higher temperatures produce more complex, and sometimes irrelevant docstrings.",
        min=0.0,
        max=2.0,
    ),
    max_tokens: int = typer.Option(
        250,
        help="The maximum number of tokens to be used when generating a docstring for a function or class. Please note that a higher number will deplete your token quota faster.",
    ),
    top_p: float = typer.Option(
        1.0,
        help="You can also specify a top-P value from 0-1 to achieve similar results to changing the temperature. According to the Open AI documentation, it is generally recommended to change either this or the temperature but not both.",
        min=0.0,
        max=1.0,
    ),
    n: int = typer.Option(
        3,
        help="The number of docstrings to be generated for each function or class, with the best one being added to the source code. Please note that a higher number will deplete your token quota faster.",
    ),
) -> None:
    try:
        add_docstring_to_source(
            path=path,
            include_auto_gen_txt=include_auto_gen_txt,
            recreate_auto_gen_docs=recreate_auto_gen_docs,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            n=n,
        )
    except Exception as e:
        typer.secho(e, err=True, fg=typer.colors.RED)
        raise typer.Exit(1)
