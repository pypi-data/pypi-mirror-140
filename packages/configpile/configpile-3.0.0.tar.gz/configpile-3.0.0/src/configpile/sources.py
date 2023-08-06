from __future__ import annotations

import abc
import configparser
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Generic, Iterable, List, Literal, Mapping, Sequence, Tuple, TypeVar

from .arg import Param, Positional
from .collector import Instance
from .errors import ArgErr, Err, GenErr, ManyErr, Result, collect_seq

T = TypeVar("T")  #: Item type


class Source(abc.ABC):
    """
    Describes a source of argument name/value pairs
    """

    @abstractmethod
    def get_strings(self, param: Param[T]) -> Result[Sequence[str]]:
        """
        Returns a sequence of string values corresponding to the given parameter

        Args:
            param: Parameter to collect the strings for

        Returns:
            A sequence of strings or an error
        """
        pass

    def __getitem__(self, param: Param[T]) -> Result[Sequence[Instance[T]]]:
        """
        Returns instances of all parsed values corresponding to the given parameter

        Args:
            param: Parameter to collect the instance for

        Returns:
            A sequence of instances or an error
        """
        res = self.get_strings(param)
        if isinstance(res, Err):
            return res
        else:
            return collect_seq([Instance.parse(s, param.param_type, source=self) for s in res])

    @staticmethod
    def collect_instances(
        sources: Sequence[Source], param: Param[T]
    ) -> Result[Sequence[Instance[T]]]:
        """
        Parses all instances of a parameter in a sequence of sources

        Args:
            sources: Sequence of sources to get the strings from
            param: Param to parse

        Returns:
            A sequence of instances or an error
        """
        ok: List[Instance[T]] = []
        errs: List[Err] = []
        for source in sources:
            res = source[param]
            if isinstance(res, ManyErr):
                errs.extend(res.errs)
            elif isinstance(res, Err):
                errs.append(res)
            else:
                ok.extend(res)
        if errs:
            return ManyErr(errs)
        else:
            return ok

    @staticmethod
    def collect(sources: Sequence[Source], param: Param[T]) -> Result[T]:
        """
        Parses and collect the value of a parameter from a sequence of sources

        Args:
            sources: Sequence of sources to get the strings from
            param: Parameter to parse and collect

        Returns:
            The collected value or an error
        """
        instances = Source.collect_instances(sources, param)
        if isinstance(instances, Err):
            return instances
        return param.collector.collect(instances)


@dataclass(frozen=True)
class EnvironmentVariables(Source):
    """
    Source coming from environment variables
    """

    env: Mapping[str, str]

    def get_strings(self, arg: Param[T]) -> Result[Sequence[str]]:
        if isinstance(arg.env_var_name, str) and arg.env_var_name in self.env:
            return [self.env[arg.env_var_name]]
        else:
            return []


@dataclass(frozen=True)
class IniSection:
    """
    Describes a section of an INI file to include in the current configuration
    """

    name: str  #: Section name
    strict: bool  #: Whether all the keys must correspond to parsed arguments


@dataclass(frozen=True)
class IniSectionSource(Source):
    """
    Source coming from the section of an INI file
    """

    filename: Path
    section_name: str
    elements: Mapping[str, str]

    def get_strings(self, arg: Param[T]) -> Result[Sequence[str]]:
        if isinstance(arg.config_key_name, str) and arg.config_key_name in self.elements:
            return [self.elements[arg.config_key_name]]
        else:
            return []

    @staticmethod
    def from_file(
        ini_file: Path, sections: Sequence[IniSection], valid_keys: Iterable[str]
    ) -> Result[Sequence[IniSectionSource]]:
        config = configparser.ConfigParser()
        try:
            with open(ini_file, "r") as f:
                config.read_file(f)
        except FileNotFoundError as e:
            return GenErr(f"File {ini_file} not found")
        res: List[IniSectionSource] = []
        for s in sections:  # loop through sections, later section values override earlier ones
            elements: Dict[str, str] = {}
            if s.name in config.sections():
                data: configparser.SectionProxy = config[s.name]
                if s.strict:
                    # we're strict, so we list all keys present in the section and match them
                    for k in data.keys():
                        if k not in valid_keys:
                            return GenErr(f"Invalid key {k} in section {s.name} of {ini_file}")
                        elements[k] = data[k]  # insert value
                else:
                    # we're not strict, so we only extract the valid keys
                    for k in valid_keys:
                        if k in data:
                            elements[k] = data[k]
            if elements:
                res.append(IniSectionSource(ini_file, s.name, elements))
        return res


@dataclass(frozen=True)
class CommandLine(Source):
    """
    Source describing command line arguments
    """

    pairs: Sequence[Tuple[str, str]]  #: Key/value argument pairs
    positional: Sequence[str]  #: Remaining positional values
    commands: Sequence[str]  #: Remaining commands

    def get_strings(self, arg: Param[T]) -> Result[Sequence[str]]:
        from_pairs: List[str] = [value for (key, value) in self.pairs if key in arg.all_flags()]
        from_pos: List[str] = []
        if arg.positional != Positional.FORBIDDEN:
            if arg.positional == Positional.ONCE and len(self.positional) != 1:
                return GenErr("One positional argument must be provided")
            if arg.positional == Positional.ONE_OR_MORE and len(self.positional) == 0:
                return GenErr("At least one positional argument must be provided")
            from_pos = list(self.positional)
        return [*from_pos, *from_pairs]

    @staticmethod
    def make(
        args: Sequence[str],
        expanding_flags: Mapping[str, Tuple[str, str]],
        flags_followed_by_value: Iterable[str],
        command_flags: Iterable[str] = [],
    ) -> Result[CommandLine]:
        """
        Returns processed command line arguments

        Args:
            args: Raw command line arguments
            expanding_flags: Flags that expand to a key/value pair
            flags_followed_by_value: Flags that are followed by a value

        Returns:
            The processed command line
        """
        pairs: List[Tuple[str, str]] = []
        commands: List[str] = []
        rest: List[str] = []
        i = 0
        while i < len(args):
            k = args[i]
            if k in expanding_flags:
                kv = expanding_flags[k]
                pairs.append(kv)
            elif k in flags_followed_by_value:
                i += 1
                if i >= len(args):
                    return GenErr("Unexpected end of command line")
                else:
                    v = args[i]
                    pairs.append((k, v))
            elif k in command_flags:
                commands.append(k)
            else:
                rest.append(k)
            i += 1
        return CommandLine(pairs=pairs, positional=rest, commands=commands)
