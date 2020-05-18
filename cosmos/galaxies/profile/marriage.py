import asyncio
import discord

from .. import Cog


class Marriage(Cog):
    """A Fun plugin which brings members closer than before."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache

    @Cog.group(name="propose", aliases=["proposal", "proposals", "marry", "accept"], invoke_without_command=True)
    async def propose_user(self, ctx, *, user: discord.Member):
        """Lets you propose them. Luckily, if they have already prosed you, it proceeds for marriage."""
        if user.bot or user.id == ctx.author.id:
            res = f"😶    You are really weird. But I understand your feelings {ctx.author.name}."
            return await ctx.send_line(res)
        target_profile = await self.cache.get_profile(user.id)
        author_profile = await self.cache.get_profile(ctx.author.id)
        if author_profile.spouse_id == user.id and target_profile.spouse_id == ctx.author.id:
            res = f"🎉    Congratulations! You guys got married again."
            return await ctx.send_line(res)
        if target_profile.spouse:
            res = f"💔    ... sorry to inform you but uh {user.name} is already married."
            return await ctx.send_line(res)
        if author_profile.spouse:
            res = f"😒    By any chance do you still remember {author_profile.spouse.name}?"
            return await ctx.send_line(res)
        if author_profile.proposed:
            res = f"You've already proposed to {author_profile.proposed.name}. You need to cancel your proposal first."
            return await ctx.send_line(res)

        def check_kiss(msg):
            if msg.author.id in [ctx.author.id, user.id] and "kiss" in msg.content.lower() and msg.mentions:
                if msg.mentions[0].id in [ctx.author.id, user.id]:
                    return True
            return False

        if target_profile.proposed and target_profile.proposed.id == ctx.author.id:
            content = f"{ctx.author.mention} {user.mention}"
            res = f"💕    in honor of ur entrance into wedlock, you may now kiss!"
            await ctx.send(content, embed=ctx.embed_line(res))
            author_kiss = False
            target_kiss = False
            while not (author_kiss and target_kiss):
                try:
                    _message = await self.bot.wait_for("message", check=check_kiss)
                    await _message.add_reaction("💟")
                    if _message.mentions[0].id == user.id:
                        author_kiss = True
                    elif _message.mentions[0].id == ctx.author.id:
                        target_kiss = True
                except asyncio.TimeoutError:
                    res = "🕛    Time is up. Thought you can always give it another shot."
                    return await ctx.send_line(res)
            await target_profile.marry(author_profile)
            content = f"{ctx.author.mention} {user.mention}"
            res = f"🎉    {ctx.author.name} and {user.name} have made themselves one in matrimony. Omedetou!"
            return await ctx.send(content, embed=ctx.embed_line(res))

        if target_profile.proposer:
            res = f"😔    Someone has already proposed to {user.name}. They should decline them first right?"
            return await ctx.send_line(res)

        await target_profile.propose(author_profile)
        try:
            res = f"💖    {ctx.author.name} has proposed you."
            await user.send(embed=ctx.embed_line(res))
        except discord.Forbidden:
            pass
        res = f"💖    You have proposed to {user.name}!"
        await ctx.send_line(res)

    @propose_user.command(name="decline", aliases=["reject"])
    async def decline_proposal(self, ctx):
        """Declines proposal if you had any."""
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.proposer:
            res = f"{ctx.author.name}, you do not have any pending proposals."
            return await ctx.send_line(res, ctx.author.avatar_url)
        target_profile = await self.cache.get_profile(author_profile.proposer_id)
        await author_profile.decline_proposal(target_profile)
        try:
            res = f"💔    {ctx.author.name} отклонил ваше предложение."
            await target_profile.user.send(embed=ctx.embed_line(res))
        except discord.Forbidden:
            pass
        res = f"You have declined the proposal of {target_profile.user.name}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @propose_user.command(name="cancel", aliases=["revoke", "pull"])
    async def cancel_proposal(self, ctx):
        """Cancels your proposal you made to someone."""
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.proposed:
            res = f"{ctx.author.name}, у тебя в кармане not sent any proposals yet."
            return await ctx.send_line(res, ctx.author.avatar_url)
        target_profile = await self.cache.get_profile(author_profile.proposed_id)
        await author_profile.cancel_proposal(target_profile)
        try:
            res = f"💔    {ctx.author.name} has pulled back their proposal from you."
            await target_profile.user.send(embed=ctx.embed_line(res))
        except discord.Forbidden:
            pass
        res = f"You have cancelled your proposal sent to {target_profile.user.name}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @Cog.command(name="divorce")
    async def divorce_user(self, ctx):
        """Lets you divorce if you're already married to someone."""
        author_profile = await self.cache.get_profile(ctx.author.id)
        if not author_profile.spouse:
            res = "You are not married yet to divorce."
            return await ctx.send_line(res, ctx.author.avatar_url)
        target_profile = await self.cache.get_profile(author_profile.spouse.id)
        await author_profile.divorce(target_profile)
        try:
            res = f"💔    {ctx.author.name} has divorced you."
            await target_profile.user.send(embed=ctx.embed_line(res))
        except discord.Forbidden:
            pass
        res = f"You have divorced {target_profile.user.name}."
        await ctx.send_line(res, ctx.author.avatar_url)
