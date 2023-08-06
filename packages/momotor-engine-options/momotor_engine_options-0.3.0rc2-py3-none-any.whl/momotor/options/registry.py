import collections
import dataclasses
import functools
import logging
import os
import pathlib
import textwrap
import typing
from string import Template

if typing.TYPE_CHECKING:
    from os import PathLike
    PathList = typing.Optional[typing.Iterable[typing.Union[str, PathLike]]]
    PathTuple = typing.Optional[typing.Tuple[typing.Union[str, PathLike], ...]]
    StrPathOrToolName = typing.Union[str, PathLike, "ToolName"]

__all__ = [
    'Tool', 'ToolName', 'SimpleVersion',
    'tool_registry_paths', 'match_tool', 'resolve_tool', 'registered_tools',
    'TOOL_REGISTRY_ENVNAME',
]


TOOL_REGISTRY_ENVNAME = 'TOOLREGISTRY'
DEFAULT_TOOL_REGISTRY_LOCATION = ['~/.toolregistry.d', '/etc/toolregistry.d']

logger = logging.getLogger(__name__)


@functools.total_ordering
@dataclasses.dataclass(frozen=True, init=False)
class SimpleVersion:
    """ Represents a simple version string (i.e., a string with dotted version-number parts)
    and makes it possible to order these.

    :py:const:`SimpleVersion.DEFAULT` is a special version constant which is always better than any other version number

    >>> _test = lambda x, y: (x < y, x == y, x > y)

    >>> _test(SimpleVersion('1'), SimpleVersion('2'))
    (True, False, False)

    >>> _test(SimpleVersion('1'), SimpleVersion('1.1'))
    (True, False, False)

    >>> _test(SimpleVersion('1.0'), SimpleVersion('1.1'))
    (True, False, False)

    >>> _test(SimpleVersion('1.0'), SimpleVersion('1.x'))
    (False, False, True)

    >>> _test(SimpleVersion('1.x'), SimpleVersion('1.x'))
    (False, True, False)

    >>> _test(SimpleVersion('1.0'), SimpleVersion('1.0'))
    (False, True, False)

    >>> _test(SimpleVersion('1.1'), SimpleVersion('1.0'))
    (False, False, True)

    >>> _test(SimpleVersion('1.1'), SimpleVersion('2'))
    (True, False, False)

    >>> _test(SimpleVersion('1.00'), SimpleVersion('1.0'))
    (False, True, False)

    >>> _test(SimpleVersion('1.09'), SimpleVersion('1.10'))
    (True, False, False)

    >>> _test(SimpleVersion(SimpleVersion.DEFAULT), SimpleVersion('1'))
    (False, False, True)

    >>> _test(SimpleVersion('1'), SimpleVersion(SimpleVersion.DEFAULT))
    (True, False, False)

    >>> _test(SimpleVersion(SimpleVersion.DEFAULT), SimpleVersion(SimpleVersion.DEFAULT))
    (False, True, False)

    """
    #: Constant indicating a default version
    DEFAULT: typing.ClassVar[str] = '_'

    #: The original value
    value: str

    _version: typing.Tuple[typing.Union[str, int]]

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError
        elif not value:
            raise ValueError

        object.__setattr__(self, 'value', value)
        object.__setattr__(self, '_version', None)

    @property
    def version(self) -> typing.Tuple[typing.Union[str, int]]:
        """ A tuple representing the :py:attr:`value` split on the dot character (``.``)
        and each part converted to :py:class:`int` if possible, and otherwise an :py:class:`str`.

        The special value :py:const:`~SimpleVersion.DEFAULT` is converted into an empty tuple.
        """
        def _convert(value):
            if value != self.DEFAULT:
                for part in value.split('.'):
                    try:
                        yield int(part)
                    except ValueError:
                        yield part

        if self._version is None:
            object.__setattr__(self, '_version', tuple(_convert(self.value)))

        return self._version

    def is_partial(self, other: "SimpleVersion") -> bool:
        """ Returns True if `self` is equal to or a partial version of `other`

        >>> SimpleVersion('1').is_partial(SimpleVersion('1'))
        True

        >>> SimpleVersion('1').is_partial(SimpleVersion('1.0'))
        True

        >>> SimpleVersion('1.0').is_partial(SimpleVersion('1'))
        False

        >>> SimpleVersion('2').is_partial(SimpleVersion('1.0'))
        False

        """
        version = self.version
        return other.version[:len(version)] == version

    def __eq__(self, other: "SimpleVersion") -> bool:
        return self.version == other.version

    def __lt__(self, other: "SimpleVersion") -> bool:
        # Default version (empty version tuple) is better than any explicit version
        if not self.version:
            return False
        elif not other.version:
            return True

        # Python throws a TypeError when attempting to do __lt__ between different types
        # (i.e., `self.version < other.version` will not work for all cases), so we check each element pair
        # manually
        for el1, el2 in zip(self.version, other.version):
            if el1 != el2:
                if type(el1) == type(el2):
                    return el1 < el2
                else:
                    return isinstance(el1, str)  # named versions are less than numeric versions

        return len(self.version) < len(other.version)

    def __hash__(self):
        return hash(self.version)

    def __str__(self):
        return self.value


@functools.total_ordering
@dataclasses.dataclass(frozen=True, init=False)
class ToolName:
    """ Represents a tool name as a tuple of :py:class:`SimpleVersion` objects

    Instantiated from a tool file name (either a :py:class:`str`, :py:class:`pathlib.PurePath`, or another
    :py:class:`ToolName`), it splits all the parts of the tool name and represents each part as a
    :py:class:`SimpleVersion`, and allows these names to be compared and ordered.

    >>> ToolName('test/1.0') < ToolName('test/2.0')
    True

    >>> ToolName('test').is_partial(ToolName('test/1.0'))
    True

    >>> ToolName('test/1').is_partial(ToolName('test/1.0'))
    True

    >>> ToolName('test/1.0').is_partial(ToolName('test/1.0'))
    True

    >>> ToolName('test/1.0').is_partial(ToolName('test'))
    False

    """

    #: Constant for the separator between name elements
    SEPARATOR: typing.ClassVar[str] = '/'

    #: Constant for the default file name
    DEFAULT_FILENAME: typing.ClassVar[str] = '_default'

    #: The tool name
    name: str

    _versions: typing.Tuple[SimpleVersion, ...] = None

    def __init__(self, name: "StrPathOrToolName"):
        if isinstance(name, str):
            versions = None

        elif isinstance(name, ToolName):
            name, versions = name.name, name._versions

        elif isinstance(name, pathlib.PurePath):
            if name.is_absolute():
                raise ValueError

            name, versions = self.SEPARATOR.join(
                SimpleVersion.DEFAULT if part == self.DEFAULT_FILENAME else part
                for part in name.parts
            ), None

        else:
            raise TypeError

        object.__setattr__(self, 'name', name)
        object.__setattr__(self, '_versions', versions)

    @classmethod
    def factory(cls, name: "StrPathOrToolName") -> "ToolName":
        """ Helper factory to create a :py:class:`ToolName` from a :py:class:`str`, :py:class:`pathlib.PurePath`
        or another :py:class:`ToolName`.

        If `name` is a :py:class:`ToolName`, returns `name` unmodified, otherwise instantiates
        a new :py:class:`ToolName` object for the given name.
        """
        if isinstance(name, cls):
            return name
        else:
            return cls(name)

    @property
    def versions(self) -> typing.Tuple[SimpleVersion, ...]:
        """ A tuple representing the :py:attr:`name` split on the :py:const:`~ToolName.SEPARATOR`
        and each part converted to a :py:class:`SimpleVersion`.
        """
        if self._versions is None:
            versions = tuple(
                SimpleVersion(part)
                for part in self.name.split(self.SEPARATOR)
            )
            object.__setattr__(self, '_versions', versions)

        return self._versions

    def is_partial(self, other: "StrPathOrToolName") -> bool:
        """ Checks if all elements of :py:attr:`self.versions` are the same or a partial version of
        :py:attr:`other.versions`.
        """
        for left, right in zip(self.versions, ToolName.factory(other).versions):
            if not left.is_partial(right):
                return False

        return len(self.versions) <= len(other.versions)

    def __eq__(self, other: "StrPathOrToolName") -> bool:
        return self.versions == ToolName.factory(other).versions

    def __lt__(self, other: "StrPathOrToolName") -> bool:
        return self.versions < ToolName.factory(other).versions

    def __hash__(self):
        return hash(self.versions)

    def __str__(self):
        return self.name


@functools.total_ordering
@dataclasses.dataclass(frozen=True)
class Tool:
    """ Data class representing the contents of a tool registry file.
    """

    #: Canonical name of the tool after resolving soft links
    name: ToolName

    #: Environment variables for the tool as indicated by the tool file
    environment: typing.Mapping[str, str]

    #: Path to the tool as indicated by the tool file
    path: pathlib.Path

    # Cached `path.exists`
    _exists_cache: bool = dataclasses.field(init=False, hash=False, default=None)

    @classmethod
    def from_file_factory(cls, registry_path: pathlib.Path, tool_file_path: pathlib.PurePath) -> "Tool":
        """ Read a tool definition file and return a populated :py:class:`Tool` dataclass.

        :param registry_path: path to the registry
        :param tool_file_path: path to the tool file, relative to `registry_path`
        :return: the tool
        """
        path = registry_path / tool_file_path
        tool_name = ToolName(tool_file_path)

        lines = path.read_text().splitlines()

        tool_path = None
        while not tool_path:
            try:
                tool_path = _unquote(lines.pop(-1).strip())
            except IndexError:
                break

        environment = collections.ChainMap({}, os.environ)
        for lineno, env_line in enumerate(lines):
            key, sep, value = env_line.partition('=')
            if sep:
                # noinspection PyBroadException
                try:
                    environment[key.strip()] = Template(
                        _unquote(value.strip())
                    ).safe_substitute(
                        environment
                    ) or None
                except Exception:
                    pass
                else:
                    continue

            logger.warning(f'invalid environment definition ignored ({path!s}:{lineno + 1}) {env_line!r}')

        tool_path = pathlib.Path(
            Template(tool_path).safe_substitute(environment)
        ).expanduser().resolve()

        # if logger.isEnabledFor(logging.DEBUG):
        #     logger.debug(f'tool {tool_name!r} resolved to {tool_path!s} (using {path!s})')
        #     for key, value in environment.items():
        #         logger.debug(f'tool {tool_name!r} environment {key}={value}')

        return cls(tool_name, environment.maps[0], tool_path)

    def exists(self) -> bool:
        """ Shortcut for :py:func:`.path.exists`. Result is cached.

        :return: `True` if the tool exists.
        """
        exists = self._exists_cache
        if exists is None:
            exists = self.path.exists()
            object.__setattr__(self, '_exists_cache', exists)

        return exists

    def __eq__(self, other: "Tool") -> bool:
        return self.exists() == other.exists() and self.name == other.name

    def __lt__(self, other: "Tool") -> bool:
        self_exists, other_exists = self.exists(), other.exists()
        if self_exists == other_exists:
            return self.name < other.name
        else:
            return other_exists

    def __hash__(self):
        return hash((self.exists(), self.name))


def _unquote(value: str) -> str:
    """

    >>> _unquote('')
    ''

    >>> _unquote('no quotes')
    'no quotes'

    >>> _unquote('  unquoted space is stripped  ')
    'unquoted space is stripped'

    >>> _unquote('"quoted"')
    'quoted'

    >>> _unquote("'quoted'")
    'quoted'

    >>> _unquote('"  quoted keeps all space  "')
    '  quoted keeps all space  '

    >>> _unquote('  "leading and trailing space is ignored"  ')
    'leading and trailing space is ignored'

    >>> _unquote('"quoted" with trailing')
    'quoted'

    >>> _unquote(r'"quoted \\"with escape\\""')
    'quoted "with escape"'

    >>> _unquote('"unbalanced')
    '"unbalanced'

    :param value:
    :return:
    """
    # If value starts with a quote, find the matching end-quote and ignore everything after that,
    # ignoring backslash-escaped quotes
    idx, vl = 0, len(value)
    while idx < vl and value[idx] in ' \t':
        idx += 1

    if idx < vl:
        q = value[idx]
        if q in '"\'':
            c, lc, qv = '', '', ''
            idx += 1
            while idx < vl:
                qv += c
                lc, c = c, value[idx]
                if c == q:
                    if lc != '\\':
                        return qv

                    qv = qv[:-1]

                idx += 1

    return value.strip()


def need_posix(f):
    """ Decorator that will throw an assertion error if the current system is not a Posix system
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        assert os.name == 'posix', 'Tool registry only supported on Posix systems'
        return f(*args, **kwargs)

    doc = wrapper.__doc__
    if doc:
        doc = textwrap.dedent(doc) + '\n\n'
    else:
        doc = ''

    wrapper.__doc__ = doc + '*Only available on Posix systems, does not work on Windows*'
    return wrapper


def tool_registry_paths(paths: "PathList" = None, include_default_paths: bool = True) -> typing.Iterable[pathlib.Path]:
    """ Collect the tool registry paths
    """
    paths = list(paths) if paths is not None else list()

    if include_default_paths:
        tool_registry: str = os.environ.get(TOOL_REGISTRY_ENVNAME)
        if tool_registry:
            paths.extend(tool_registry.split(':'))
        elif tool_registry is None:
            paths.extend(DEFAULT_TOOL_REGISTRY_LOCATION)

    logger.debug(f'tool registry locations: {", ".join(str(p) for p in paths)}')

    for path in paths:
        if isinstance(path, str):
            path = path.strip()

        path = pathlib.Path(path).expanduser().absolute()
        if path.exists():
            yield path
        else:
            logger.debug(f'tool registry path does not exist: {path!s}')


def _is_candidate(path: pathlib.Path):
    name = path.name
    return not (name.startswith('.') or name.endswith('~'))


@functools.lru_cache(maxsize=1)
def _registered_tools(
        paths: "PathTuple" = None, *,
        include_default_paths: bool = True,
        include_missing: bool = False,
) -> typing.Dict[ToolName, Tool]:
    """ Implementation of :py:func:`registered_tools`
    """
    logger.debug(f'reading tool registries')

    tools: typing.Dict[ToolName, Tool] = {}
    for registry_path in tool_registry_paths(paths, include_default_paths):
        logger.debug(f'reading tool registry {registry_path!s}')
        for tool_file_path in registry_path.rglob('*'):
            if not tool_file_path.is_file() or not _is_candidate(tool_file_path):
                continue

            alias_file_name = tool_file_path.relative_to(registry_path)
            try:
                tool_file_name = tool_file_path.resolve(True).relative_to(registry_path)
            except FileNotFoundError:
                logger.warning(f'unable to resolve symlink {alias_file_name!s} in registry {registry_path!s}')
                continue

            tool_name = ToolName(tool_file_name)
            if tool_name not in tools:
                try:
                    tool = Tool.from_file_factory(registry_path, tool_file_name)
                except Exception as e:
                    logger.warning(f'unable to read {tool_file_name!s} in registry {registry_path!s}: {e} ')
                    continue

                if not tool.exists() and not include_missing:
                    logger.warning(f'ignoring tool {tool_file_name!s} in registry {registry_path!s}: tool not found')
                    continue

                assert tool_name == tool.name
                tools[tool.name] = tool

            alias_name = ToolName(alias_file_name)
            if alias_name not in tools:
                tools[alias_name] = tools[tool_name]

    return tools


@need_posix
def registered_tools(
        paths: "PathList" = None, *,
        include_default_paths: bool = True,
        include_missing: bool = False,
) -> typing.Dict[ToolName, Tool]:
    """
    Return a mapping with all locally installed tools.

    If `include_default_paths` is True (default), this reads the tool registry from `.toolregistry.d` in
    the current user's home directory and `/etc/toolregistry.d`. If `paths` is provided, registry will be read from
    all paths in the path list as well.

    :param paths: paths to read the tool registry from. prepended to the default paths
    :param include_default_paths: include the default paths
    :param include_missing: include tools that are registered but the executable does not actually exist
    :return: a mapping from tool name to tool dataclass
    """

    return _registered_tools(
        tuple(paths) if paths is not None else None,
        include_default_paths=include_default_paths,
        include_missing=include_missing,
    )


def match_tool(name: "StrPathOrToolName", tools: typing.Iterable["StrPathOrToolName"]) \
        -> typing.Optional["StrPathOrToolName"]:
    """
    Match tool `name` with :py:const:`~SimpleVersion.DEFAULT` placeholders
    and (partial) version numbers to a tool name in the `tools` container.

    Returns the most specific matched name from `tools`, or None if no match could be made.

    :param name: Name of the tool to match
    :param tools: An iterable of tool names to match `name` against
    :return: The matched name from `tools`, or `None`

    Does **not** access the local registry.
    """
    name, best_name, best_candidate = ToolName.factory(name), None, None
    for cname in tools:
        candidate = ToolName.factory(cname)
        if name.is_partial(candidate) and (best_candidate is None or candidate > best_candidate):
            best_name, best_candidate = cname, candidate

    return best_name


@need_posix
def resolve_tool(name: "StrPathOrToolName", *, paths: "PathList" = None, include_default_paths: bool = True) -> Tool:
    """
    Resolve a tool `name` to a :py:class:`Tool` dataclass.

    If `include_default_paths` is True (default), this reads the tool registry from `.toolregistry.d` in
    the current user's home directory and `/etc/toolregistry.d`. If `paths` is provided, registry will be read from
    all paths in the path list as well.

    :param name: Name of the tool to resolve
    :param paths: paths to read the tool registry from. prepended to the default paths
    :param include_default_paths: include the default paths
    :return: The tool info object.
    :raises FileNotFoundError: if the name could not be resolved
    """
    name = ToolName.factory(name)
    registry = registered_tools(
        paths,
        include_default_paths=include_default_paths,
        include_missing=False,
    )

    if name in registry:
        logger.debug(f'tool {name} found in registry')
        return registry[name]

    matched_name = match_tool(name, registry.keys())
    if matched_name:
        logger.debug(f'tool {name} found in registry (as {matched_name})')
        return registry[matched_name]

    logger.warning(f'tool {name} not found in registry')
    raise FileNotFoundError


def _print_registry():
    print("Registered tools:")
    print('-----------------')

    tools = registered_tools(include_missing=True)
    for alias_name, tool in sorted(tools.items()):
        print(f'{alias_name} => {tool.path}')

    print()


def _print_tool(tool_name: str):
    tool_info = resolve_tool(tool_name)

    print('name:')
    print(f'  {tool_info.name}')

    print('path:')
    print(f'  {tool_info.path}')

    if tool_info.environment:
        print('environment:')
        for env_name, env_value in sorted(tool_info.environment.items()):
            print(f'  {env_name}={env_value}')

    print()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        _print_tool(sys.argv[1])
    else:
        _print_registry()
