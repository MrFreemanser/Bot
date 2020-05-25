import discord

from .points import RoleShopPoints
from .settings import RoleShopSettings

from .._models.exceptions import *


class RoleShop(RoleShopPoints, RoleShopSettings):
    """Implements Role Shop functionality in server.

    Members can redeem or purchase roles which has been put on Role Shop by server administrators using their
    золотых монет. Once the role is redeemed it stays in their inventory. They can also easily equip or un-equip
    any of the roles they have redeemed previously.

    """

    INESCAPABLE = False

    @RoleShopSettings.role_shop.command(name="purchased", inescapable=False)
    async def purchased_roles(self, ctx, *, member: discord.Member = None):
        """Displays your all of the roles purchased from Role Shop or of specified member."""
        member = member or ctx.author
        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        paginator = ctx.get_field_paginator(profile.roleshop.roles, entry_parser=self._paginator_parser)
        paginator.embed.set_author(name="Purchased Roles - Role Shop", icon_url=ctx.author.avatar_url)
        paginator.embed.description = "```css\nDisplaying roles you have purchased from Role Shop.```"
        await paginator.paginate()

    @RoleShopSettings.role_shop.command(name="роль", aliases=["purchase"], inescapable=False)
    async def buy_role(self, ctx, *, role: discord.Role = None):
        """Redeem or purchase specified role from Role Shop using your earned золотых монет.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        await ctx.message.delete(delay=5)
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in ctx.guild_profile.roleshop.roles if role not in profile.roleshop.roles]
        # TODO: Maybe only include roles which can be purchased by that member because of less points.
        description = "```\nДобро пожаловать в цветную лавку ! " \
                      "\nДля покупки ролей - активируйте соответствующую ей emoji```"
        role = await self._get_role(ctx, role, roles, "Покупка ролей", description)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role in profile.roleshop.roles:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    Ты уже купил  {role.name}",delete_after=5)
        msg = await ctx.send_line(f"⚠    Ты уверен, что хочешь купить {role.name}?",delete_after=10)
        if await ctx.confirm(msg):
            await ctx.guild_profile.roleshop.buy_role(profile, role.id)
            await ctx.send_line(f"{ctx.emotes.web_emotion.galka}  Роль {role.name} приобретена. У тебя осталось {profile.points}{ctx.emotes.web_emotion.g10} золотых монет.", delete_after=5)
            msg=await ctx.confirm(f"{ctx.emotes.imortal_boost.g8}    Активировать роль {role.name} сейчас?",delete_after=5)
        if await ctx.confirm(msg):
            msg=await ctx.author.add_roles(role, reason="Роль приобретена.")
        await msg.delete(delay=5) 


    @buy_role.error
    async def buy_error(self, ctx, error):
        if isinstance(error, NotEnoughPointsError):
            return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}  Очень жаль, но у вас недостаточно {ctx.emotes.web_emotion.g10}", delete_after=5)

<<<<<<< HEAD
    #@RoleShopSettings.role_shop.command(name="sell", inescapable=False)
    #async def sell_role(self, ctx, *, role: discord.Role = None):
    #     """Sell your already purchased role back to Role Shop giving you Guild Points worth value of same role."""
    #     # TODO: Let Guild Administrators decide if members can sell role.
    #    profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
    #     role = await self._get_role(ctx, role, profile.roleshop.roles)
    #     _role = ctx.guild_profile.roleshop.roles.get(role.id)
    #    if _role not in profile.roleshop.roles:
    #         return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    You haven't purchased {role.name} yet.")
    #     if await ctx.confirm(f"⚠    Are you sure to sell {role.name}?"):
    #         await ctx.guild_profile.roleshop.sell_role(profile, role.id)
    #         await ctx.author.remove_roles(role)
    #         await ctx.send_line(f"{ctx.emotes.web_emotion.galka}    You sold {role.name} earning {_role.points} золотых монет.")
=======
    @RoleShopSettings.role_shop.command(name="sell", inescapable=False)
    async def sell_role(self, ctx, *, role: discord.Role = None):
         """Sell your already purchased role back to Role Shop giving you Guild Points worth value of same role."""
         # TODO: Let Guild Administrators decide if members can sell role.
         profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
         role = await self._get_role(ctx, role, profile.roleshop.roles)
         _role = ctx.guild_profile.roleshop.roles.get(role.id)
         if _role not in profile.roleshop.roles:
             return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    You haven't purchased {role.name} yet.")
         if await ctx.confirm(f"⚠    Are you sure to sell {role.name}?"):
             await ctx.guild_profile.roleshop.sell_role(profile, role.id)
             await ctx.author.remove_roles(role)
             await ctx.send_line(f"{ctx.emotes.web_emotion.galka}    You sold {role.name} earning {_role.points} золотых монет.")
>>>>>>> fix_bug

    @RoleShopSettings.role_shop.group(name="equip", aliases=["надеть"], invoke_without_command=True, inescapable=False)
    async def equip_role(self, ctx, *, role: discord.Role = None):
        """Equip specified role which you have purchased from the Role Shop.
        It displays an interactive reaction based menu to choose your desired role if it's not specified.

        """
        await ctx.message.delete(delay=5)
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) not in ctx.author.roles]
        description ="```\nДля применения роли - нажмите на реакцию" \
                "\n```"
        role = await self._get_role(ctx, role, roles, "Меню магазина - Инвентарь", description)
        _role = ctx.guild_profile.roleshop.roles.get(role.id)
        if _role not in profile.roleshop.roles:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    Вы ещё не купили {role.name}.", delete_after=5)
        if role in ctx.author.roles:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    Вы уже применили {role.name}.", delete_after=5)
        msg=await ctx.author.add_roles(role, reason="Роль применена из магазина.")
        msg=await ctx.send_line(f"{ctx.emotes.web_emotion.galka}   Роль {role.name} применена.")
        await msg.delete(delay=5)

    @equip_role.command(name="все")
    async def equip_all_roles(self, ctx):
        """Equip all of the roles you have purchased from Role Shop."""
        await ctx.message.delete(delay=5)
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            msg=await ctx.author.add_roles(role, reason="Роль применена из магазина.")
        msg=await ctx.send_line("✅    Применены все купленные роли")
        await msg.delete(delay=5)

    @RoleShopSettings.role_shop.group(name="снять", invoke_without_command=True, inescapable=False)
    async def unequip_role(self, ctx, *, role: discord.Role = None):
        """Un-equip specified Role Shop role which you have already equipped."""
        await ctx.message.delete(delay=5)
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        roles = [role for role in profile.roleshop.roles if ctx.guild.get_role(role.id) in ctx.author.roles]
        description = "```\nСписок приобритённых ролей"
        role = await self._get_role(ctx, role, roles, "Меню магазина - Инвентарь", description)
        if role not in ctx.author.roles:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.xx}    Вы уже сняли роль {role.name}.")
        msg=await ctx.author.remove_roles(role)
        msg=await ctx.send_line(f"{ctx.emotes.web_emotion.galka}  Роль {role.name} снята.")
        await msg.delete(delay=5)

    @unequip_role.command(name="all")
    async def unequip_all_roles(self, ctx):
        """Un-equip all of the roles belonging to Role Shop which you have equipped."""
        await ctx.message.delete(delay=5)
        if not await ctx.confirm():
            return
        profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        for _role in profile.roleshop.roles:
            role = ctx.guild.get_role(_role.id)
            await ctx.author.remove_roles(role, reason="Role un-equipped from role shop.", delete_after=5)
        await ctx.send_line("✅    Вы применили все доступные вам роли.", delete_after=5)
