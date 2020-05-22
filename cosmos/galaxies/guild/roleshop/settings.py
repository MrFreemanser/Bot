import discord
import typing

from .base import RoleShopBase

from discord.ext.commands import has_permissions


class RoleShopSettings(RoleShopBase):
    """A plugin to manage and setup Role Shop in server."""

    @RoleShopBase.command(name="датьзолото", aliases=["givepoint"])
    @has_permissions(administrator=True)
    async def give_points(self, ctx, points: int, *, member: discord.Member):
        """Generate and give points to specified member. You can also specify negative points to remove points."""
        if member.bot:
            return await ctx.send_line(f"{ctx.emotes.imortal_boost.d7} У наших помошников слишком узкие корманы, попробуй скинуть кому-то другому.")
        profile = await ctx.fetch_member_profile(member.id)
        profile.give_points(points)
        await ctx.send_line(f"{member.display_name} Получает {points}{ctx.emotes.web_emotion.g10} золотых ")

    @RoleShopBase.role_shop.command(name="создать")
    @has_permissions(manage_roles=True)
    async def create_role(self, ctx, points: int, *, role: typing.Union[discord.Role, str]):
        """Create a new or use specified role for the Role Shop."""
        if len(ctx.guild_profile.roleshop.roles) >= self.plugin.data.roleshop.max_roles:
            res = f"{ctx.emotes.web_emotion.xx}  Извини, но в магазине доступно всего {self.plugin.data.roleshop.max_roles} ролей"
            return await ctx.send_line(res)

        if isinstance(role, str):
            role = await ctx.guild.create_role(name=role, reason=f"Роль для магазина - создана. [{ctx.author}]")
        await ctx.guild_profile.roleshop.create_role(role.id, points)
        await ctx.send_line(f"{ctx.emotes.web_emotion.galka}  {role.name} Добавлен в магазин за {points}{ctx.emotes.web_emotion.g10} золотых.")

    @RoleShopBase.role_shop.command(name="удалить", aliases=["delete"])
    @has_permissions(manage_roles=True)
    async def delete_role(self, ctx, *, role: discord.Role = None):
        """Remove specified role from the Role Shop.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        description = "```css\nВыберите роль, которую хотите удалить из магазина.```"
        role = await self._get_role(ctx, role, ctx.guild_profile.roleshop.roles, "Меню удаления ролей", description)

        if await ctx.confirm(f"⚠   Вы уверены, что хоите удалить {role.name} из магазина ?"):
            # await role.delete(reason=f"Role deleted from role shop. [{ctx.author}]")
            await ctx.guild_profile.roleshop.remove_role(role.id)

            await ctx.send_line(f"{ctx.emotes.web_emotion.galka}    {role.name} была удалена из магазина.")

    @RoleShopBase.role_shop.group(name="изменить", aliases=["edit"])
    @has_permissions(manage_roles=True)
    async def modify_role(self, ctx):
        """Make changes to existing Role Shop role."""
        pass

    @modify_role.command(name="points", aliases=["стоимость"])
    async def modify_points(self, ctx, new_points: int, *, role: discord.Role = None):
        """Modify points required to redeem or purchase role.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        description = "```css\nDisplaying Role Shop roles. React with respective emote to modify that role.```"
        role = await self._get_role(ctx, role, ctx.guild_profile.roleshop.roles, "Изменение меню магазина", description)

        if await ctx.confirm(f"⚠    Вы действительно хотите изменить стоимсть с {role.name} на {new_points}?"):
            await ctx.guild_profile.roleshop.set_points(role.id, new_points)

            await ctx.send_line(f"{ctx.emotes.web_emotion.galka}   Стоимость {role.name} была изменена на {new_points}.")
