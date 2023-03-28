# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/Docstring_Generator.ipynb.

# %% auto 0
__all__ = ['SYSTEM_INSTRUCTION', 'FEW_SHOT_EXAMPLES', 'DEFAULT_MESSAGE_TEMPLATE', 'DOCSTRING_ERR', 'AUTO_GEN_PERFIX',
           'AUTO_GEN_BODY', 'AUTO_GEN_SUFFIX', 'AUTO_GEN_TXT', 'add_docstring_to_source']

# %% ../nbs/Docstring_Generator.ipynb 2
import time
import random
import ast
import textwrap
import os
import re
from typing import *
from pathlib import Path

import nbformat
import openai
import typer

from mypy_extensions import NamedArg

# %% ../nbs/Docstring_Generator.ipynb 4
def _visit_functions(
    tree: ast.AST,
    *,
    source: str,
    start_lineno: int = 1,
    end_lineno: int = -1,
    callback: Callable[
        [ast.AST, str, int, int, NamedArg(List[Tuple[int, int, int, int]], "retval")],
        Any,
    ],
    **kwargs: Any,
) -> None:
    """Walk the abstract syntax tree and call the callback function for every node found

    Args:
        tree: The python AST
        source: The source code
        start_lineno: The start line number
        end_lineno: The end line number
        callback: The callback function
        kwargs: The keyword arguments

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    if end_lineno == -1:
        end_lineno = len(source.split("\n"))

    if isinstance(tree, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef)):
        if ast.get_docstring(tree) is None:
            callback(tree, source, start_lineno, end_lineno, **kwargs)

    if hasattr(tree, "body"):
        for i, n in enumerate(tree.body):
            node_start_lineno = tree.body[i].lineno
            node_end_lineno = (
                tree.body[i + 1].lineno - 1 if i < (len(tree.body) - 1) else end_lineno
            )
            _visit_functions(
                n,
                source=source,
                start_lineno=node_start_lineno,
                end_lineno=node_end_lineno,
                callback=callback,
                **kwargs,
            )

# %% ../nbs/Docstring_Generator.ipynb 8
def _get_classes_and_functions(source: str) -> List[Tuple[int, int, int, int]]:
    """Get the classes and functions in a source file.

    Args:
        source: The source code of the file.
        recreate_auto_gen_docs: If set to True, the autogenerated docstrings from the previous runs will be replaced with the new one.


    Returns:
        A list of tuples of the form (start_lineno, end_lineno, start_col_offset, end_col_offset)

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    retval: List[Tuple[int, int, int, int]] = []
    tree = ast.parse(source)

    def callback(tree, source, start_lineno, end_lineno, *, retval):
        """Callback function for the ast.walk function.

        Args:
            tree: The tree to walk
            source: The source code
            start_lineno: The starting line number
            end_lineno: The ending line number

        Keyword Args:
            retval: The return value

        Returns:
            The return value

        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """
        retval.append(
            (start_lineno, tree.body[0].lineno - 1, end_lineno, tree.body[0].col_offset)
        )

    _visit_functions(
        tree,
        source=source,
        callback=callback,
        retval=retval,
    )

    return retval

# %% ../nbs/Docstring_Generator.ipynb 10
def _get_code_from_source(source: str, start_line_no: int, end_line_no: int) -> str:
    """Get code from source

    Args:
        source: The source code of the file.
        start_line_no: Start line number
        end_line_no: End line number

    Returns:
        The extracted code

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    source_lines = source.split("\n")
    extracted_lines = source_lines[start_line_no - 1 : end_line_no]
    return "\n".join(extracted_lines)

# %% ../nbs/Docstring_Generator.ipynb 12
# Reference: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb


def _retry_with_exponential_backoff(
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 10,
    max_wait: float = 60,
    errors: tuple = (
        openai.error.RateLimitError,
        openai.error.ServiceUnavailableError,
        openai.error.APIError,
    ),
) -> Callable:
    """Retry a function with exponential backoff."""

    def decorator(func):
        """Decorator to retry a function if it fails.

        Args:
            func: The function to be decorated
            max_retries: The maximum number of retries
            initial_delay: The initial delay
            exponential_base: The exponential base
            max_wait: The maximum wait
            jitter: The jitter

        Returns:
            The decorated function

        Raises:
            Exception: If the maximum number of retries is exceeded

        !!! note

            The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
        """

        def _wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay

            while True:
                try:
                    return func(*args, **kwargs)

                except errors as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        )
                    delay = min(
                        delay
                        * exponential_base
                        * (1 + jitter * random.random()),  # nosec
                        max_wait,
                    )
                    typer.secho(
                        f"Note: OpenAI's API rate limit reached. Command will automatically retry in {int(delay)} seconds. For more information visit: https://help.openai.com/en/articles/5955598-is-api-usage-subject-to-any-rate-limits",
                        fg=typer.colors.BLUE,
                    )
                    time.sleep(delay)

                except Exception as e:
                    raise e

        return _wrapper

    return decorator


@_retry_with_exponential_backoff()
def _completions_with_backoff(*args, **kwargs):
    return openai.ChatCompletion.create(*args, **kwargs)

# %% ../nbs/Docstring_Generator.ipynb 13
SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": "Write a comprehensive Google-styled docstring, including a brief one-line summary for the code given by the user.",
}

# %% ../nbs/Docstring_Generator.ipynb 14
FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": """
def add_strings(s1: Optional[str] = None, s2: Optional[str] = None) -> str:
    if s1 is None or s2 is None:
        raise ValueError(Both s1 and s2 must be provided and must be of type string")
    return s1 + s2
        """,
    },
    {
        "role": "assistant",
        "content": """Add two strings

Args:
    s1: First string
    s2: Second string
    
Returns:
    The added string
    
Raises:
    ValueError: If s1 or s2 is None
""",
    },
    {
        "role": "user",
        "content": """
class Person:
    def __init__(self, name, surname, age):
        self.name = name
        self.surname = surname
        self.age = age

    def info(self, additional=""):
        print('My name is :' + self.name + additional)
""",
    },
    {
        "role": "assistant",
        "content": """A class to represent a person.

Attributes:
    name : first name of the person
    surname : family name of the person
    age : age of the person
""",
    },
]

# %% ../nbs/Docstring_Generator.ipynb 15
DEFAULT_MESSAGE_TEMPLATE = [SYSTEM_INSTRUCTION] + FEW_SHOT_EXAMPLES

# %% ../nbs/Docstring_Generator.ipynb 21
def _get_best_docstring(docstrings: List[str]) -> Optional[str]:
    """Get the best docstring from a list of docstrings.

    Args:
        docstrings: List of docstrings

    Returns:
        The best docstring

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    docstrings = [d for d in docstrings if "Args:" in d or "Attributes:" in d]
    docstrings = [d for d in docstrings if "~~~~" not in d]
    return docstrings[0] if len(docstrings) > 0 else None

# %% ../nbs/Docstring_Generator.ipynb 24
DOCSTRING_ERR = """!!! note
    
    Failed to generate docs
"""


def _generate_docstring_using_chat_gpt(
    code: str, message_template: str, **kwargs: Union[int, float, str, List[str]]
) -> str:
    """Generate a docstring using chat GPT model.

    Args:
        code: The code for which to generate a docstring.
        message_template: The message template to instruct the model.
        **kwargs: The keyword arguments.

    Returns:
        The generated docstring.

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    messages = message_template + [{"role": "user", "content": code}]
    response = _completions_with_backoff(messages=messages, **kwargs)
    choices = [choice["message"]["content"] for choice in response["choices"]]

    best_docstring = _get_best_docstring(choices)
    retval = best_docstring if best_docstring is not None else DOCSTRING_ERR
    return retval

# %% ../nbs/Docstring_Generator.ipynb 26
AUTO_GEN_PERFIX = """
!!! note

"""
AUTO_GEN_BODY = "The above docstring is autogenerated by docstring-gen library"
AUTO_GEN_SUFFIX = "(https://docstring-gen.airt.ai)"

AUTO_GEN_TXT = AUTO_GEN_PERFIX + " " * 4 + AUTO_GEN_BODY + " " + AUTO_GEN_SUFFIX

# %% ../nbs/Docstring_Generator.ipynb 28
def _add_auto_gen_txt(docstring: str) -> str:
    """Add the autogenerated by docstring-gen library text to the end of a docstring

    Args:
        docstring: The docstring to which the text will be added

    Returns:
        The docstring with the added text

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    return docstring + AUTO_GEN_TXT + "\n"

# %% ../nbs/Docstring_Generator.ipynb 30
def _fix_docstring_indent(
    docstring: str, col_offset: int, *, include_auto_gen_txt: bool
) -> str:
    """Fix the indentation of a docstring.

    Args:
        docstring: The docstring to fix.
        col_offset: The column offset to use.
        include_auto_gen_txt: If True, include the auto-generated text in the docstring.

    Returns:
        The fixed docstring.

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    lines = docstring.split("\n")
    rest = textwrap.dedent("\n".join(lines[1:]))
    retval = lines[0] + "\n" + rest

    if include_auto_gen_txt:
        retval = _add_auto_gen_txt(retval)

    retval = '"""' + retval + '"""'
    retval = textwrap.indent(retval, prefix=" " * col_offset)
    return retval

# %% ../nbs/Docstring_Generator.ipynb 34
def _inject_docstring_to_source(
    source: str,
    indented_docstrings: List[str],
    linenos: List[Tuple[int, int, int, int]],
) -> str:
    """Injects docstrings into source code

    Args:
        source: The source code
        indented_docstrings: The docstrings to be injected
        linenos: The line numbers where the docstrings should be injected

    Returns:
        The source code with the injected docstrings

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    source_lines = source.split("\n")
    line_offset = 0
    for docstring, (_, docstring_line_no, _, _) in zip(indented_docstrings, linenos):
        docstring_lines = docstring.split("\n")
        source_lines = (
            source_lines[: docstring_line_no + line_offset]
            + docstring_lines
            + source_lines[docstring_line_no + line_offset :]
        )
        line_offset += len(docstring_lines)

    return "\n".join(source_lines)

# %% ../nbs/Docstring_Generator.ipynb 36
def _remove_auto_generated_docstring(source: str) -> str:
    """Remove the autogenerated docstrings from the source code.

    Args:
        source: The source code

    Returns:
        The source code without the auto generated docstring

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    placeholder = "{DOCSTRING_PLACEHOLDER}"
    retval = re.sub(
        f'"""((?!""").)*?({AUTO_GEN_BODY}).*?"""', placeholder, source, flags=re.DOTALL
    )
    retval = "\n".join([l for l in retval.split("\n") if l.strip() != placeholder])
    return retval

# %% ../nbs/Docstring_Generator.ipynb 38
def _check_and_add_docstrings_to_source(
    source: str,
    include_auto_gen_txt: bool,
    recreate_auto_gen_docs: bool,
    **kwargs: Union[int, float, str, List[str]],
) -> str:
    """Check and add docstrings to classes and functions that don't have one.

    Args:
        source: Source code
        include_auto_gen_txt: Include auto gen text
        recreate_auto_gen_docs: If set to True, the autogenerated docstrings from the previous runs will be replaced with the new one.
        kwargs: Keyword arguments

    Returns:
        The source code with docstrings

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    if recreate_auto_gen_docs:
        source = _remove_auto_generated_docstring(source)

    linenos = _get_classes_and_functions(source)
    if len(linenos) != 0:
        classes_and_functions = [
            _get_code_from_source(source, start_line_no, end_line_no)
            for start_line_no, docstring_line_no, end_line_no, node_offset in linenos
        ]

        docstrings = [
            _generate_docstring_using_chat_gpt(i, DEFAULT_MESSAGE_TEMPLATE, **kwargs)
            for i in classes_and_functions
        ]
        offsets = [node_offset for i, _, _, node_offset in linenos]

        indented_docstrings = [
            _fix_docstring_indent(
                docstring, offset, include_auto_gen_txt=include_auto_gen_txt
            )
            for docstring, offset in zip(docstrings, offsets)
        ]
        source = _inject_docstring_to_source(source, indented_docstrings, linenos)

    return source

# %% ../nbs/Docstring_Generator.ipynb 41
def _get_files(p: Path) -> List[Path]:
    """Get Jupyter notebooks and Python files path in the directory.

    Args:
        p: Path to the directory

    Returns:
        A list of paths to the files in the directory

    Raises:
        ValueError: If the directory does not contain any Python files or notebooks

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    exts = [".ipynb", ".py"]
    files = [
        f
        for f in p.rglob("*")
        if f.suffix in exts
        and not any(p.startswith(".") for p in f.parts)
        and not f.name.startswith("_")
    ]

    if len(files) == 0:
        raise ValueError(
            f"The directory {p.resolve()} does not contain any Python files or notebooks"
        )

    return files

# %% ../nbs/Docstring_Generator.ipynb 44
def _add_docstring_to_nb(
    file: Path,
    include_auto_gen_txt: bool,
    recreate_auto_gen_docs: bool,
    version: int = 4,
    **kwargs: Union[int, float, str, List[str]],
) -> None:
    """Add docstrings to a Jupyter notebook.

    Args:
        file (Path): Path to the notebook file.
        include_auto_gen_txt (bool): If True, include a text indicating that the docstring was auto-generated.
        recreate_auto_gen_docs (bool): If True, recreate the docstrings even if they already exist.
        version (int): The version of the notebook.
        **kwargs: Additional arguments to be passed to the function that generates the docstrings.

    Returns:
        None

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    file_modified = False
    _f = nbformat.read(file, as_version=version)

    for cell in _f.cells:
        if cell.cell_type == "code":
            original_src = cell["source"]
            try:
                updated_src = _check_and_add_docstrings_to_source(
                    original_src, include_auto_gen_txt, recreate_auto_gen_docs, **kwargs
                )
                if not file_modified:
                    file_modified = original_src != updated_src
                cell["source"] = updated_src
            except SyntaxError as e:
                typer.secho(
                    f"WARNING: Unable to parse the below cell contents in {file} due to: {e}. Skipping the cell for docstring generation.",
                    fg=typer.colors.YELLOW,
                )
                typer.echo(original_src)
                cell["source"] = original_src

    nbformat.write(_f, file)

    if file_modified or recreate_auto_gen_docs:
        typer.secho(f"Successfully added docstrings to {file}", fg=typer.colors.CYAN)


def _add_docstring_to_py(
    file: Path,
    include_auto_gen_txt: bool,
    recreate_auto_gen_docs: bool,
    **kwargs: Union[int, float, str, List[str]],
) -> None:
    """Add docstrings to a python file.

    Args:
        file: The path to the python file.
        include_auto_gen_txt: Whether to include a text indicating that the docstring is auto-generated.
        recreate_auto_gen_docs: Whether to recreate the docstrings even if they already exist.
        kwargs: Additional keyword arguments.

    Returns:
        None

    Raises:
        ValueError: If file is not a path to a python file.

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    try:
        file_modified = False
        with file.open("r") as f:
            source = f.read()
        original_src = source
        updated_src = _check_and_add_docstrings_to_source(
            source, include_auto_gen_txt, recreate_auto_gen_docs, **kwargs
        )

        with file.open("w") as f:
            f.write(updated_src)

        if not file_modified:
            file_modified = original_src != updated_src

        if file_modified or recreate_auto_gen_docs:
            typer.secho(
                f"Successfully added docstrings to {file}", fg=typer.colors.CYAN
            )

    except SyntaxError as e:
        typer.secho(
            f"WARNING: Unable to parse the {file} due to: {e}. Skipping the file for docstring generation.",
            fg=typer.colors.YELLOW,
        )


def add_docstring_to_source(
    path: Union[str, Path],
    include_auto_gen_txt: bool = True,
    recreate_auto_gen_docs: bool = False,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.2,
    max_tokens: int = 250,
    top_p: float = 1.0,
    n: int = 3,
) -> None:
    """Reads a Jupyter notebook or Python file, or a directory containing these files, and adds docstrings to classes and methods that do not have them.

    Args:
        path: The path to the Jupyter notebook or Python file, or a directory containing these files.
        include_auto_gen_txt: If set to True, a note indicating that the docstring was autogenerated by docstring-gen library will be added to the end.
        recreate_auto_gen_docs: If set to True, the autogenerated docstrings from the previous runs will be replaced with the new one.
        model: The name of the Codex model that will be used to generate docstrings.
        temperature: Setting the temperature close to zero produces better results, whereas higher temperatures produce more complex, and sometimes irrelevant docstrings.
        max_tokens: The maximum number of tokens to be used when generating a docstring for a function or class. Please note that a higher number will deplete your token quota faster.
        top_p: You can also specify a top-P value from 0-1 to achieve similar results to changing the temperature. According to the Open AI documentation, it is generally recommended to change either this or the temperature but not both.
        n: The number of docstrings to be generated for each function or class, with the best one being added to the source code. Please note that a higher number will deplete your token quota faster.

    Returns:
        None

    !!! note

        The above docstring is autogenerated by docstring-gen library (https://docstring-gen.airt.ai)
    """
    path = Path(path)
    files = _get_files(path) if path.is_dir() else [path]
    frequency_penalty = 0.0
    presence_penalty = 0.0
    stop = ["#", '"""']

    for file in files:
        if file.suffix == ".ipynb":
            _add_docstring_to_nb(
                file=file,
                include_auto_gen_txt=include_auto_gen_txt,
                recreate_auto_gen_docs=recreate_auto_gen_docs,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                n=n,
            )
        else:
            _add_docstring_to_py(
                file=file,
                include_auto_gen_txt=include_auto_gen_txt,
                recreate_auto_gen_docs=recreate_auto_gen_docs,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                n=n,
            )
