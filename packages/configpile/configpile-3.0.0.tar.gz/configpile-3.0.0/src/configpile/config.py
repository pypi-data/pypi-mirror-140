from __future__ import annotations

import abc
import argparse
import os
import shutil
import sys
import textwrap
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

import class_doc
from typing_extensions import Annotated, get_args, get_origin, get_type_hints

from . import arg, types
from .arg import Arg, Cmd, Expander, Param, Positional
from .collector import Instance
from .errors import ArgErr, Err, ManyErr, Result, collect
from .sources import CommandLine, EnvironmentVariables, IniSection, IniSectionSource, Source
from .util import filter_types_single

C = TypeVar("C", bound="Config")


@dataclass(frozen=True)
class ConfigProcessor(Generic[C]):
    """
    Process command-line arguments

    """

    cs: ConfigStructure[C]
    cwd: Path
    args: Sequence[str]
    env: Mapping[str, str]

    def command_line(self) -> Result[CommandLine]:
        """
        Constructs a command line source

        Returns:
            A source or an error
        """
        exp_flags = {flag: cmd.inserts() for (flag, cmd) in self.cs.cl_expanders.items()}
        val_flags = frozenset(self.cs.cl_flag_params.keys())
        return CommandLine.make(self.args, exp_flags, val_flags)

    def environment_variables(self) -> Result[EnvironmentVariables]:
        """
        Constructs a source from environment variables

        Returns:
            A source or an error
        """
        return EnvironmentVariables(self.env)

    def process(self) -> Result[C]:
        """
        Runs the processing

        Returns:
            A parsed configuration or an error
        """
        cs = self.cs
        config_sources: Result[Tuple[CommandLine, EnvironmentVariables]] = collect(
            self.command_line(), self.environment_variables()
        )
        if isinstance(config_sources, Err):
            return config_sources
        cl, env = config_sources
        ini_from_env: Result[Sequence[Instance[Sequence[Path]]]] = env[cs.ini_files]
        if isinstance(ini_from_env, Err):
            return ini_from_env
        ini_from_cl: Result[Sequence[Instance[Sequence[Path]]]] = cl[cs.ini_files]
        if isinstance(ini_from_cl, Err):
            return ini_from_cl
        sources: List[Source] = [env]
        ini_instances: Sequence[Path] = [
            ins for instances in [*ini_from_env, *ini_from_cl] for ins in instances.value
        ]
        for fn in ini_instances:
            sections_res = IniSectionSource.from_file(
                self.cwd / fn, cs.ini_sections, cs.ini_params
            )
            if isinstance(sections_res, Err):
                return sections_res
            sources.extend(sections_res)
        sources.append(cl)
        values: List[Tuple[str, Any]] = []
        errs: List[Err] = []
        for name, arg in cs.params.items():
            res = Source.collect(sources, arg)
            if isinstance(res, Err):
                errs.append(ArgErr(arg, res))
            else:
                values.append((name, res))
        if errs:
            return ManyErr(errs)
        else:
            return cs.config(**dict(values))


@dataclass(frozen=True)
class ConfigStructure(Generic[C]):
    config: Type[C]

    prog: str  #: Program name
    description: Optional[str]  #: Text to display before the argument help
    env_prefix: Optional[str]  #: Prefix of environment variables

    ini_files: Param[Sequence[Path]]  #: Parameter describing INI files to parse

    ini_sections: Sequence[IniSection]  #: Sequence of INI sections to parse

    #: All parameters indexed by destination field
    params: Mapping[str, Param[Any]]

    #: Command-line commands that are not expanders
    cl_non_expander_cmds: Mapping[str, Cmd]

    #: Command-line commands that are expanders
    cl_expanders: Mapping[str, Expander]

    #: Parameters triggered by command-line flags, indexed by their flags
    cl_flag_params: Mapping[str, Param[Any]]

    #: Positional command-line parameters
    cl_positional: Optional[Param[Any]]

    #: Parameters present in configuration files, indexed by their key
    ini_params: Mapping[str, Param[Any]]

    #: Parameters present in environment variables, indexed by variable name
    env_params: Mapping[str, Param[Any]]

    @staticmethod
    def from_config(cls: Type[C]) -> ConfigStructure[C]:

        # fill program name from script invocation
        prog = cls.prog_
        if prog is None:
            prog = sys.argv[0]
        # fill description from class docstring
        description: Optional[str] = cls.description_
        if description is None:
            description = cls.__doc__
        env_prefix = cls.env_prefix_
        ini_sections: Sequence[IniSection] = cls.ini_sections_()

        args: List[Arg] = []
        params: Dict[str, Param[Any]] = {}
        cl_non_expander_cmds: Dict[str, Cmd] = {}
        cl_expanders: Dict[str, Expander] = {}
        cl_flag_params: Dict[str, Param[Any]] = {}
        cl_positional: Optional[Param[Any]] = None
        ini_files: Optional[Param[Sequence[Path]]] = None
        ini_params: Dict[str, Param[Any]] = {}
        env_params: Dict[str, Param[Any]] = {}

        docs: Mapping[str, Sequence[str]] = class_doc.extract_docs_from_cls_obj(cls)

        def format_docstring(seq: Sequence[str]) -> str:
            return textwrap.dedent("\n".join(seq))

        th = get_type_hints(cls, include_extras=True)
        for name, typ in th.items():
            arg: Optional[Arg] = None
            if get_origin(typ) is ClassVar:
                a = getattr(cls, name)
                if isinstance(a, Arg):
                    assert isinstance(a, Cmd), "Only commands (Cmd) can be class attributes"
                    arg = a
            if get_origin(typ) is Annotated:
                param = filter_types_single(Param, get_args(typ))
                if param is not None:
                    arg = param
            if arg is not None:
                help = format_docstring(docs.get(name, []))
                arg = arg.updated(name, help, cls.env_prefix_)
                args.append(arg)
                if name == "ini_files":
                    assert isinstance(arg, Param)
                    ini_files = arg

        for arg in args:
            if isinstance(arg, Param):
                assert arg.name is not None
                params[arg.name] = arg
                if arg.positional != Positional.FORBIDDEN:
                    assert cl_positional is None, "Only one positional argument is allowed"
                    cl_positional = arg
                for flag in arg.all_flags():
                    cl_flag_params[flag] = arg
                for key in arg.all_config_key_names():
                    ini_params[key] = arg
                for name in arg.all_env_var_names():
                    env_params[name] = arg
            elif isinstance(arg, Cmd):
                for flag in arg.all_flags():
                    if isinstance(arg, Expander):
                        cl_expanders[flag] = arg
                    else:
                        cl_non_expander_cmds[flag] = arg
            else:
                raise ValueError(f"Not implemented, type: {type(arg)}")

        assert ini_files is not None

        return ConfigStructure(
            cls,
            prog=prog,
            description=description,
            env_prefix=env_prefix,
            ini_files=ini_files,
            ini_sections=ini_sections,
            params=params,
            cl_non_expander_cmds=cl_non_expander_cmds,
            cl_expanders=cl_expanders,
            cl_flag_params=cl_flag_params,
            cl_positional=cl_positional,
            ini_params=ini_params,
            env_params=env_params,
        )

    def get_argument_parser(self) -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(prog=self.prog, description=self.description)
        for param in self.params.values():
            p.add_argument(*param.all_flags(), **param.argparse_argument_kwargs())
        return p


@dataclass(frozen=True)
class Config(abc.ABC):
    """
    Base class for dataclasses holding configuration data
    """

    #: Configuration file paths
    #:
    #: The paths are absolute or relative to the current working directory, and
    #: point to existing INI files containing configuration settings
    ini_files: Annotated[Sequence[Path], arg.append(types.path.separated_by(","))]

    #: Names of sections to parse in configuration files, with unknown keys ignored
    ini_relaxed_sections_: ClassVar[Sequence[str]] = ["Common", "COMMON", "common"]

    #: Names of additional sections to parse in configuration files, unknown keys error
    ini_strict_sections_: ClassVar[Sequence[str]] = []

    @classmethod
    def ini_sections_(cls) -> Sequence[IniSection]:
        """
        Returns a sequence of INI file sections to parse

        By default, this parses first the relaxed sections and then the strict ones.

        This method can be overridden.
        """
        relaxed = [IniSection(name, False) for name in cls.ini_relaxed_sections_]
        strict = [IniSection(name, True) for name in cls.ini_strict_sections_]
        return relaxed + strict

    prog_: ClassVar[Optional[str]] = None  #: Program name
    description_: ClassVar[Optional[str]] = None  #: Text to display before the argument help
    env_prefix_: ClassVar[Optional[str]] = None  #: Prefix for environment variables

    @classmethod
    def config_structure_(cls: Type[C]) -> ConfigStructure[C]:
        return ConfigStructure.from_config(cls)

    @classmethod
    def parse_command_line_(
        cls: Type[C],
        cwd: Path = Path.cwd(),
        args: Sequence[str] = sys.argv[1:],
        env: Mapping[str, str] = os.environ,
    ) -> Result[C]:
        """
        Parses multiple information sources, returns a configuration or an error

        Default values are taken from the current working directory, the script command line
        arguments, and the current environment variables.

        Args:
            cwd: Directory used as a base for the configuration file relative paths
            args: Command line arguments
            env: Environment variables

        Returns:
            A parsed configuration or an error
        """
        cs = cls.config_structure_()
        cp = ConfigProcessor(cs, cwd, args, env)
        return cp.process()

    @classmethod
    def from_command_line_(
        cls: Type[C],
        cwd: Path = Path.cwd(),
        args: Sequence[str] = sys.argv[1:],
        env: Mapping[str, str] = os.environ,
    ) -> C:
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
        res = cls.parse_command_line_(cwd, args, env)
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
            cls.get_argument_parser_().print_help()
            sys.exit(1)
        return res

    @classmethod
    def get_argument_parser_(cls: Type[C]) -> argparse.ArgumentParser:
        """
        Returns an :class:`argparse.ArgumentParser` for documentation purposes
        """
        return cls.config_structure_().get_argument_parser()
