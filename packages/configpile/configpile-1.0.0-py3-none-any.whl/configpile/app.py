from __future__ import annotations

import argparse
import os
import shutil
import sys
import textwrap
from cmath import exp
from collections import OrderedDict
from configparser import ConfigParser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    FrozenSet,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
)
from typing import OrderedDict as OrderedDictT
from typing import Sequence, Tuple, Type, TypeVar

import class_doc

from . import sources, types
from .arg import Arg, Expander, Param
from .config import Config
from .errors import Err
from .util import dict_from_multiple_keys, filter_ordered_dict_by_value_type

A = TypeVar("A", bound="App")
T = TypeVar("T", covariant=True)


@dataclass(frozen=True)
class Args:
    """
    Describes the arguments present in an app
    """

    #: All arguments present in the app
    #:
    #: Those are indexed by the field name
    all: Mapping[str, Arg]

    #: All parameters present in the app, for which a value is recovered
    #:
    #: Those are indexed by the field name
    params: Mapping[str, Param]  # type: ignore[type-arg]

    #: All command line flags that expand into a (key, value) pair of strings
    cl_expanders: Mapping[str, Expander]

    #: All command line arguments that are followed by a value
    cl_params: Mapping[str, Param]  # type: ignore[type-arg]

    #: The positional arguments
    cl_positional: Optional[Param]  # type: ignore[type-arg]

    #: Map of all config file keys
    cf_params: Mapping[str, Param]  # type: ignore[type-arg]

    #: Map of all supported env. variables
    env_params: Mapping[str, Param]  # type: ignore[type-arg]

    @staticmethod
    def populated_base_args(cls: Type[A]) -> OrderedDictT[str, Arg]:
        """
        Returns an ordered dictionary of configuration arguments

        In the returned dictionary, the :class:`.Arg` instances are updated with their
        field name and help string.

        Args:
            cls: App class type

        Returns:
            Argument dictionary
        """
        docs: Mapping[str, Sequence[str]] = class_doc.extract_docs_from_cls_obj(cls)

        def get_help(name: str) -> str:
            seq = docs.get(name, [])
            return textwrap.dedent("\n".join(seq))

        elements: List[Tuple[str, Arg]] = [
            (
                name,
                arg.updated(name=name, help=get_help(name), env_prefix=cls.env_prefix_),
            )
            for parent_including_itself in cls.__mro__
            for (name, arg) in parent_including_itself.__dict__.items()
            if isinstance(arg, Arg) and not name.endswith("_")
        ]
        return OrderedDict(elements)

    @staticmethod
    def from_app_class(cls: Type[A]) -> Args:
        """
        Returns a :class:`.Args` instance populated with updated arguments

        Args:
            cls: The :class:`.App` subclass to investigate

        Returns:
            An object holding the arguments/flags sorted by type
        """
        all: OrderedDictT[str, Arg] = Args.populated_base_args(cls)
        fields: OrderedDictT[str, Param] = filter_ordered_dict_by_value_type(Param, all)  # type: ignore[type-arg]

        cl_all: Mapping[str, Arg] = dict_from_multiple_keys(
            [(arg.all_flags(), arg) for arg in all.values()]
        )
        cl_expanders: Mapping[str, Expander] = {
            k: v for (k, v) in cl_all.items() if isinstance(v, Expander)
        }
        cl_flag_args: Mapping[str, Param] = {k: v for (k, v) in cl_all.items() if isinstance(v, Param)}  # type: ignore[type-arg]
        cl_pos_args: Sequence[Param] = [a for a in fields.values() if a.positional.is_positional()]  # type: ignore[type-arg]
        if len(cl_pos_args) == 0:
            cl_positional = None
        elif len(cl_pos_args) == 1:
            cl_positional = cl_pos_args[0]
        else:
            raise ValueError("At most one positional argument can be given")
        cf_keys: Mapping[str, Param] = dict_from_multiple_keys(  # type: ignore[type-arg]
            [(arg.all_config_key_names(), arg) for arg in fields.values()]
        )
        env_vars: Mapping[str, Param] = dict_from_multiple_keys(  # type: ignore[type-arg]
            [(arg.all_env_var_names(), arg) for arg in fields.values()]
        )
        assert not any(
            map(lambda a: a.positional.should_be_last(), cl_pos_args[:-1])
        ), "Only the last positional argument may take a variable number of values"
        return Args(
            all=all,
            params=fields,
            cl_expanders=cl_expanders,
            cl_params=cl_flag_args,
            cl_positional=cl_positional,
            cf_params=cf_keys,
            env_params=env_vars,
        )


class App:
    """
    A base class for the configuration of Python scripts
    """

    #: Configuration file paths
    #:
    #: The paths are absolute or relative to the current working directory, and
    #: point to existing INI files containing configuration settings
    ini_files: Param[Sequence[Path]] = Param.append(types.path.separated_by(","))

    # TODO help: Optional[HelpCmd] = HelpCmd(short_flag_name="-h")  #: Show a help message and exit

    #: Names of sections to parse in configuration files, with unknown keys ignored
    ini_relaxed_sections_: Sequence[str] = ["Common", "COMMON", "common"]

    #: Names of additional sections to parse in configuration files, unknown keys error
    ini_strict_sections_: Sequence[str] = []

    @classmethod
    def ini_sections_(cls) -> Sequence[sources.IniSection]:
        """
        Returns a sequence of INI file sections to parse

        By default, this parses first the relaxed sections and then the strict ones.

        This method can be overridden.
        """
        relaxed = [sources.IniSection(name, False) for name in cls.ini_relaxed_sections_]
        strict = [sources.IniSection(name, True) for name in cls.ini_strict_sections_]
        return relaxed + strict

    prog_: Optional[str] = None  #: Program name
    description_: Optional[str] = None  #: Text to display before the argument help
    env_prefix_: Optional[str] = None  #: Uppercase prefix of environment variables

    args_: Args  #: Arguments

    @classmethod
    def app_(cls: Type[A]) -> A:
        """
        Creates an instance with updated fields

        This class method should be called on subclasses of :class:`.App`.

        Returns:
            An instance of App
        """
        res = cls()
        assert (
            not cls.ini_files.positional.is_positional()
        ), "Configuration files cannot be given as positional arguments"
        if res.prog_ is None:
            res.prog_ = sys.argv[0]
        if res.description_ is None:
            res.description_ = cls.__doc__
        res.args_ = Args.from_app_class(cls)
        for name, arg in res.args_.all.items():
            res.__setattr__(name, arg)
        return res

    def parse_(
        self,
        cwd: Path = Path.cwd(),
        args: Sequence[str] = sys.argv[1:],
        env: Mapping[str, str] = os.environ,
    ) -> Config:
        """
        Parses multiple information sources into a configuration and display help on error

        Default values are taken from the current working directory, the script command line
        arguments, and the current environment variables.

        Args:
            cwd: Directory used as a base for the configuration file relative paths
            args: Command line arguments
            env: Environment variables

        Returns:
            A parsed configuration
        """
        res = Config.make(self, cwd, args, env)
        if isinstance(res, Err):
            try:
                from rich.console import Console
                from rich.markdown import Markdown

                console = Console()
                md = Markdown("\n".join(res.markdown()))
                console.print(md)
            except:
                sz = shutil.get_terminal_size()
                t = res.markdown()
                print(textwrap.fill("\n".join(t), width=sz.columns))
            self.argument_parser_().print_help()
            sys.exit(1)
        return res

    def argument_parser_(self) -> argparse.ArgumentParser:
        """
        Returns an :class:`argparse.ArgumentParser` for documentation purposes
        """
        p = argparse.ArgumentParser(prog=self.prog_, description=self.description_)
        for arg in self.args_.cl_params.values():
            p.add_argument(
                *arg.all_flags(),
                **arg.argparse_argument_kwargs(),
            )
        return p
