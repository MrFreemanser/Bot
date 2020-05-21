import discord
from discord.ext.commands import CommandError

from .._models import GuildBaseCog


class NotRoleShopRoleError(CommandError):

    def __init__(self, role):
        self.role = role


class RoleShopBase(GuildBaseCog):
    """Base cog for Role Shop plugin."""

    async def _get_role(self, ctx, role, roles, title, description: str = str()) -> discord.Role:
        # roles = roles or ctx.guild_profile.roleshop.roles
        if role:
            if not ctx.guild_profile.roleshop.has_role(role.id):
                raise NotRoleShopRoleError(role)
            return role
        menu = ctx.get_field_menu(roles, self._paginator_parser)
        menu.embed.description = description
        menu.embed.set_author(name=title, icon_url=ctx.author.avatar_url)
        response = await menu.wait_for_response()
        return ctx.guild.get_role(response.entry.id)

    @staticmethod
    async def _paginator_parser(ctx, roleshop_role, _):
        role = ctx.guild.get_role(roleshop_role.id)
        points = roleshop_role.points
        return role.name, f"`Цена:` **{points}**  {ctx.emotes.web_emotion.g10}\n`Роль:` {role.mention}"

    @GuildBaseCog.group(name="купить", aliases=["магазин"], invoke_without_command=True)
    async def role_shop(self, ctx):
        """Displays all of the roles which can be purchased from role shop."""
        if not ctx.guild_profile.roleshop:
            return await ctx.send_line(f"{ctx.emotes.imortal_boost.g8} На данный момент в магазине пусто.")
        paginator = ctx.get_field_paginator(ctx.guild_profile.roleshop.roles, entry_parser=self._paginator_parser)
        paginator.embed.description = "```css\n Добро пожаловать в лавку !" \
                                    "```"
        paginator.embed.set_author(name="Магазин ролей", icon_url=ctx.author.avatar_url)
        await paginator.paginate()

    
    @role_shop.error
    async def role_shop_error(self, ctx, error):    # TODO: Override Command with custom dispatch_error method.
        if isinstance(error, NotRoleShopRoleError):
            await ctx.send_line(f"❌   Роль  {error.role.name} отсутствует в магазине.")
