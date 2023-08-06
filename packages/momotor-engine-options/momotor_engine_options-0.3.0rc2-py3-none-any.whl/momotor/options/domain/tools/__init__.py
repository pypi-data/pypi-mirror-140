from dataclasses import dataclass

import logging
import typing

from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.providers import Providers
from momotor.options.registry import ToolName, Tool, resolve_tool
from momotor.options.types import SubDomainDefinitionType

from ._domain import DOMAIN as TOOLS_DOMAIN
from ...split import multi_split

if typing.TYPE_CHECKING:
    from os import PathLike
    PathList = typing.Optional[typing.Iterable[typing.Union[str, PathLike]]]


__all__ = ['ToolOptionDefinition', 'ToolOptionName', 'TOOLS_DOMAIN']


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolOptionName(OptionNameDomain):
    domain: str = TOOLS_DOMAIN


TOOLS_OPTION_LOCATION = 'config', 'step', 'recipe'


@dataclass(frozen=True)
class ToolOptionDefinition(OptionDefinition):
    """ A specialization of :py:class:`~momotor.options.option.OptionDefinition` for tool dependency definitions.

    Provides appropriate defaults for :py:attr:`domain`, :py:attr:`default` and :pt:attr:`location` fields:
    * the default for :py:attr:`domain` is ``{TOOLS_DOMAIN}``
    * the default for :py:attr:`default` is the option name, i.e. if no option for the given name is in any bundle,
      the default version as defined in the registry will be used.
    * the default for :py:attr:`location` is ``config, step, recipe`` and cannot be changed.

    Other differences compared to :py:class:`~momotor.options.option.OptionDefinition`:

    * a single option value can be a space or comma separated list of version requirements to indicate alternative
      version preferences of a single tool (in order of most to least preferred),
    * :py:attr:`multiple` must be `False` (setting it to `True` will throw a :py:class:`ValueError`),
    * :py:meth:`resolve` returns an iterable of :py:class:`~momotor.options.registry.ToolName` objects,
    * additional method :py:meth:`resolve_tool` resolves the tool using the tool registry, it resolves to a single tool,
      matching the most preferred tool available.
    * auto-generates suitable :py:attr:`doc` if none is provided

    """
    type = 'str'

    def __post_init__(self):
        if isinstance(self.name, OptionNameDomain):
            name, domain = self.name.name, self.name.domain
        else:
            name, domain = self.name, self.domain

        if ToolName.SEPARATOR in name:
            raise ValueError(f'ToolOptionDefinition.name cannot contain {ToolName.SEPARATOR}')

        if domain is None:
            object.__setattr__(self, 'domain', TOOLS_DOMAIN)

        if self.default is self.NO_DEFAULT:
            object.__setattr__(self, 'default', name)

        super().__post_init__()

        if self.location is None or self.location == TOOLS_OPTION_LOCATION:
            object.__setattr__(self, 'location', TOOLS_OPTION_LOCATION)
        else:
            raise ValueError(f"ToolOptionDefinition.location cannot be changed {self.location!r}")

        if self.multiple:
            raise ValueError("ToolOptionDefinition.multiple must be False")

        if not self.doc:
            object.__setattr__(
                self, 'doc',
                f"{name} version to use. "
                f"See the :py:ref:`tool registry` documentation for details. "
                f"Default: '{self.default}'"
            )

    def resolve(
            self,
            providers: Providers,
            subdomains: typing.Union[SubDomainDefinitionType, bool] = None
    ) -> typing.Iterable[ToolName]:
        result = super().resolve(providers, subdomains)
        if result is None:
            raise FileNotFoundError

        for name in multi_split(result, ','):
            yield ToolName(name)

    def resolve_tool(
            self,
            providers: Providers,
            subdomains: typing.Union[SubDomainDefinitionType, bool] = None, *,
            paths: "PathList" = None,
            include_default_paths: bool = True
    ) -> typing.Optional[Tool]:
        """ Resolve a tool option into a single :py:class:`~momotor.options.registry.Tool` using the tool registry.
        If multiple options are provided, the first existing tool will be returned. If none of the
        requested tools exist, raises :py:class:`FileNotFoundError`

        `providers` and `subdomain` arguments are the same as for :py:meth:`resolve`, and
        `paths` and `include_default_paths` arguments are the same as for
        :py:meth:`momotor.options.registry.resolve_tool`

        """
        logger.debug(f'resolving "{self.name}" tool')

        for name in self.resolve(providers, subdomains):
            try:
                return resolve_tool(
                    name, paths=paths, include_default_paths=include_default_paths
                )
            except FileNotFoundError:
                pass

        logger.warning(f'unable to resolve "{self.name}" tool')
        raise FileNotFoundError


ToolOptionDefinition.__doc__ = ToolOptionDefinition.__doc__.format(TOOLS_DOMAIN=TOOLS_DOMAIN)
