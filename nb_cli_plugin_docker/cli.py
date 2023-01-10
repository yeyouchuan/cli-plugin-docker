from pathlib import Path
from typing import List, cast

import click
from noneprompt import Choice, ListPrompt, CancelledError
from nb_cli.cli import CLI_DEFAULT_STYLE, ClickAliasedGroup, run_sync, run_async

from .handler import generate_config_file


@click.group(cls=ClickAliasedGroup, invoke_without_command=True)
@click.pass_context
@run_async
async def docker(ctx: click.Context):
    """Manage Bot Deployment with Docker."""
    if ctx.invoked_subcommand is not None:
        return

    command = cast(ClickAliasedGroup, ctx.command)

    # auto discover sub commands and scripts
    choices: List[Choice[click.Command]] = []
    for sub_cmd_name in await run_sync(command.list_commands)(ctx):
        if sub_cmd := await run_sync(command.get_command)(ctx, sub_cmd_name):
            choices.append(
                Choice(
                    sub_cmd.help or f"Run subcommand {sub_cmd.name}",
                    sub_cmd,
                )
            )

    try:
        result = await ListPrompt(
            "What do you want to do?", choices=choices
        ).prompt_async(style=CLI_DEFAULT_STYLE)
    except CancelledError:
        ctx.exit()

    sub_cmd = result.data
    await run_sync(ctx.invoke)(sub_cmd)


@docker.command()
@click.option("-d", "--cwd", default=".", help="The working directory.")
@run_async
async def generate(cwd: str):
    """Generate Dockerfile and docker-compose.yml."""
    await generate_config_file(cwd=Path(cwd))
