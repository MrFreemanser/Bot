import discord

from .base import RoleShopBase


class RoleShopPoints(RoleShopBase):
    """Implements Guild Points function which are bound to each server.
    Members can earn points in different servers by chatting normally in text channels where the bot can read their
    messages. They can also claim their daily points.

    These points can be redeemed to unlock various perks in the server set by the administrators like a role from
    Role Shop.

    """

    @RoleShopBase.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        profile = await self.bot.profile_cache.get_guild_profile(message.author.id, message.guild.id)
        if message.content == "Hello World!":
             profile.give_points(10)
        
        

    @RoleShopBase.group(name="баланс", invoke_without_command=True)
    async def points(self, ctx, *, member: discord.Member = None):
        """Displays Guild Points earned by you or specified member."""
        if member:
            adverb = f"{member.name}, у тебя в кармане"
        else:
            member = ctx.author
            adverb = f"{member.name}, у тебя в кармане"
        if member.bot:
            return await ctx.send_line(f"{ctx.emotes.imortal_boost.d10} Боты не могут получать золото")

        profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        await ctx.send_line(f"{ctx.emotes.web_emotion.g11}  {adverb} {profile.points}{ctx.emotes.web_emotion.g10} золотых монет.")

    @points.command(name="+")
    async def daily_points(self, ctx, *, member: discord.Member = None):
        """Lets you claim your daily золотых монет. Specify any member to let them have your daily золотых монет."""
        author_profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        target_name = "Вы"
        if (member and member.bot) or not member:
            target_profile = author_profile
        else:
            target_profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
            if target_profile is None:
                target_profile = author_profile
            else:
                target_name = member.display_name
        if not author_profile.can_take_daily_points:
            res = f"⏳    Вы можете получить ежедневные монеты снова через {author_profile.next_daily_points.humanize()}."
            return await ctx.send_line(res)

        daily_points = await author_profile.take_daily_points(target_profile)
        res = f"{ctx.emotes.web_emotion.b234}  {target_name} получили {daily_points}{ctx.emotes.web_emotion.g10} ежедневных монет."
        await ctx.send_line(res)

    @points.command(name="фыввв", aliases=["фывв", "ыфв"])
    async def transfer_points(self, ctx, points: int, *, member: discord.Member):
        """Transfer your points to specified member."""
        if member.bot:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.b235}  Зачем ты пытаешься это сделать ? Ну серьёзно ?")
        if points < 0:
            return await ctx.send_line(f"{ctx.emotes.web_emotion.b235}  Прости - но это уже слишком...")
        author_profile = await self.bot.profile_cache.get_guild_profile(ctx.author.id, ctx.guild.id)
        target_profile = await self.bot.profile_cache.get_guild_profile(member.id, ctx.guild.id)
        if author_profile.points < points:
            return await ctx.send_line(f"❌ Простите, но у вас недостатточно {ctx.emotes.web_emotion.g10} золотых монет.")
        author_profile.give_points(-points)
        target_profile.give_points(points)
        await ctx.send_line(f"{ctx.emotes.web_emotion.z23}    {ctx.author.name},ты поделился {points}{ctx.emotes.web_emotion.g10} c {member.display_name}.")
