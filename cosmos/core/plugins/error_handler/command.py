from ...functions.context.functions.paginators import NoEntriesError

import sys
import discord
import traceback
import asyncio

from ...functions import Cog
from cosmos import exceptions
from discord.ext import commands
from sentry_sdk import configure_scope


class CommandErrorHandler(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @staticmethod
    async def __send_response(ctx, emote_url, content):
        return await ctx.send_line(content, emote_url, color=discord.Color(0xFF1744))

    @Cog.listener()
    async def on_command_error(self, ctx, error):

        images = self.bot.theme.images

        if isinstance(error, discord.Forbidden):
            pass

        elif isinstance(error, exceptions.GuildNotPrime):
            # Tried to use prime function in non-prime guild.
            await ctx.send_line(
                "Что бы получить расширенные возможности - посетите эту страницу.",
                icon_url=images.privacy, author_url=self.bot.configs.info.patreon)

        elif isinstance(error, exceptions.DisabledFunctionError):
            await self.__send_response(ctx, images.unavailable, "Эта функция была отключена в данном канале.")

        elif isinstance(error, commands.BotMissingPermissions):
            await self.__send_response(
                ctx, images.mandenied,
                f"У меня отсутствуют  необходимые права {error.missing_perms[0].replace('_', ' ').title()} для исполнения этой команды.")

        elif isinstance(error, commands.MissingPermissions):
            await self.__send_response(
                ctx, images.denied,
                f"Вам не хватает разрений разрешений {error.missing_perms[0].replace('_', ' ').title()} для использования этой команды")

        elif isinstance(error, commands.CheckFailure):
            await self.__send_response(ctx, images.denied, "Вы не можете использовать эту команду")

        elif isinstance(error, commands.UserInputError):
            await self.__send_response(ctx, images.error, "Не могу распознать команду. Попробуйте ещё раз")

        elif isinstance(error, NoEntriesError):
            await ctx.message.add_reaction(self.bot.emotes.misc.nill)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.message.add_reaction(self.bot.emotes.misc.clock)

        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, asyncio.TimeoutError):
            pass
        else:
            with configure_scope() as scope:
                scope.user = {
                    "username": str(ctx.author), "id": ctx.author.id,
                    "guild": ctx.guild.name, "guild_id": ctx.guild.id,
                    "command": ctx.command.name, "args": ctx.args, "kwargs": ctx.kwargs,
                }
            self.bot.eh.sentry.capture_exception(error)
            self.bot.log.debug(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
