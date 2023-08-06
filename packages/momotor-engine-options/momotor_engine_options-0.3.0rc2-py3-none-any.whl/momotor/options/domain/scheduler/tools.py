from typing_extensions import TypeAlias

import typing
from textwrap import dedent

from momotor.bundles import RecipeBundle, ConfigBundle
from momotor.options.domain.tools import ToolOptionDefinition, TOOLS_DOMAIN
from momotor.options.option import OptionDefinition, OptionNameDomain
from momotor.options.parser.placeholders import replace_placeholders
from momotor.options.providers import Providers
from momotor.options.registry import ToolName
from momotor.options.split import multi_split
from momotor.options.task_id import StepTaskId
from ._domain import DOMAIN

TOOLS_OPTION_NAME = OptionNameDomain('tools', DOMAIN)
tools_option = OptionDefinition(
    name=TOOLS_OPTION_NAME,
    type='str',
    doc=dedent(f"""\
        List of tools required for the step. Can only be provided by <step> nodes.
        
        Multiple tools can be provided by using multiple {TOOLS_OPTION_NAME} options, or using a single
        {TOOLS_OPTION_NAME} option with multiple tool names. Multiple tool names on a single option should 
        be space or comma separated.
        
        The list of tools should only contain tool names. Any detailed version requirements should
        be listed in the special `{TOOLS_DOMAIN}` domain  
    """),
    multiple=True,
    location='step',
)

ToolRequirements: TypeAlias = typing.Mapping[str, typing.Sequence[ToolName]]


def get_scheduler_tools_option(recipe: RecipeBundle, config: typing.Optional[ConfigBundle], step_id: str) \
        -> ToolRequirements:
    """ Get the tool requirements by parsing the :py:ref:`{TOOLS_OPTION_NAME} option` for a single step

    This gets the value of the :py:ref:`{TOOLS_OPTION_NAME} option` for the step, and subsequently gets the
    specific tool version requirements (if any) from the options in the
    :py:ref:`{TOOLS_DOMAIN} domain <{TOOLS_DOMAIN} domain>`.

    A step requiring tools must define the :py:ref:`{TOOLS_OPTION_NAME} option` in the recipe. The tool version options
    are defined in the :py:ref:`{TOOLS_DOMAIN} domain <{TOOLS_DOMAIN} domain>` in the normal
    locations: *config*, *recipe*, *step*.

    Example of a step defining some tool requirements:

    .. code-block:: xml

      <recipe ...>
        ...
        <step ...>
          ...
          <options domain="{TOOLS_OPTION_NAME.domain}">
            <option name="{TOOLS_OPTION_NAME.name}" value="anaconda3" />
          </options>
          <options domain="{TOOLS_DOMAIN}">
            <option name="anaconda3" value="anaconda3/_/momotor anaconda3" />
          </options>
          ...
        </step>
        ...
      </recipe>

    This indicates to the scheduler that this step requires the `anaconda3` tool. It also indicates
    to both the scheduler and to the checklet that will execute this step that the `anaconda3/_/momotor` version
    is preferred, but if not available any `anaconda3` will do.

    For the format of the tool version requirements, see :py:ref:`tool registry`.
    """
    requirement_providers = Providers(
        recipe=recipe,
        task_id=StepTaskId(step_id, None)
    )

    version_providers = Providers(
        recipe=recipe,
        config=config,
        task_id=StepTaskId(step_id, None)
    )

    tools = {}
    for tool_req in tools_option.resolve(requirement_providers, False):
        tool_req = replace_placeholders(tool_req, requirement_providers)
        for name in multi_split(tool_req, ','):
            if name not in tools:
                tools[name] = tuple(
                    ToolOptionDefinition(name=name).resolve(version_providers)
                )

    return tools


get_scheduler_tools_option.__doc__ = get_scheduler_tools_option.__doc__.format(
    TOOLS_OPTION_NAME=TOOLS_OPTION_NAME,
    TOOLS_DOMAIN=TOOLS_DOMAIN,
)
