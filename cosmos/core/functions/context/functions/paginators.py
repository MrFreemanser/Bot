import asyncio
import discord

from discord.ext import commands


EmptyEmbed = discord.Embed.Empty


class NoEntriesError(commands.CommandError):

    pass


class BasePaginator(object):

    @staticmethod
    async def _default_entry_parser(ctx, entry, _):
        return entry

    def __init__(self, ctx, entries, per_page=12, timeout=90, show_author=False, inline=True, is_menu=False, **kwargs):
        self.ctx = ctx
        self.loop = self.ctx.bot.loop
        self.emotes = self.ctx.bot.emotes
        self.entries = entries
        if not self.entries:
            raise NoEntriesError
        self.per_page = per_page
        self.max_pages = self.__count_pages()
        self.embed = self.ctx.bot.theme.embeds.primary()
        self.is_paginating = len(self.entries) > self.per_page
        self.on_function_page = False
        self.timeout = timeout
        self.show_author = show_author
        self.inline = inline
        self.is_menu = is_menu
        self.show_entry_count = kwargs.get("show_entry_count", False)
        self.show_controllers = kwargs.get("show_controllers", True)
        self.show_return = kwargs.get("show_return", True)
        self.entry_parser = kwargs.get("entry_parser") or self._default_entry_parser
        self.reaction_bullets = []
        self.controllers = [
            (self.emotes.web_es.backward, self.first_page),
            (self.emotes.web_es.prev, self.previous_page),
            (self.emotes.web_es.close, self.close),
            (self.emotes.web_es.next, self.next_page),
            (self.emotes.web_es.forward, self.last_page),
        ]
        self.default_functions = [
            (self.emotes.misc.return_, self.show_current_page),
        ]
        self.functions = []
        self.current_page = 1
        self.message = None
        self.match = None

    def __count_pages(self):
        pages, left = divmod(len(self.entries), self.per_page)
        if left:
            pages += 1
        return pages

    async def set_controllers(self, **kwargs):
        if self.is_menu:
            for reaction in self.reaction_bullets:
                await self.message.add_reaction(reaction)
        if self.show_controllers and self.is_paginating:
            for reaction, _ in self.controllers:
                if self.max_pages == 2 and reaction in [self.emotes.misc.backward, self.emotes.misc.forward]:
                    continue
                if not kwargs.get(reaction.name, True):
                    continue
                await self.message.add_reaction(reaction)
        for reaction, _ in self.functions:
            await self.message.add_reaction(reaction)

    def get_page(self, page):
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, first=False, **kwargs):
        self.current_page = page
        entries = self.get_page(page)
        para = []

        if self.is_menu:
            for _, entry in enumerate(entries, 1 + (page - 1) * self.per_page):
                string = await entry.get_string()
                bullet = entry.emote
                self.reaction_bullets.append(bullet)
                para.append(f"{bullet} {string}")
        else:
            for index, entry in enumerate(entries, 1 + (page - 1) * self.per_page):
                text = await self.entry_parser(self.ctx, entry, self.entries)
                if self.show_entry_count:
                    prefix = f"{index}. {text}"
                else:
                    prefix = text
                para.append(prefix)

        if self.max_pages > 1:
            if self.show_entry_count:
                text = f"Displaying {page} of {self.max_pages} pages and {len(entries)} entries."
            else:
                text = f"Displaying {page} of {self.max_pages} pages."
            self.embed.set_footer(text=text)

        if self.show_author:
            self.embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.avatar_url)

        if not first:
            self.embed.description = "\n".join(para)
            return await self.message.edit(embed=self.embed)

        para.append(str())

        self.embed.description = "\n".join(para)
        self.message = await self.ctx.send(embed=self.embed)

        await self.set_controllers(**kwargs)

    async def check_show_page(self, page):
        if page != 0 and page <= self.max_pages:
            await self.show_page(page)

    async def first_page(self):
        await self.show_page(1)

    async def last_page(self):
        await self.show_page(self.max_pages)

    async def next_page(self):
        await self.check_show_page(self.current_page + 1)

    async def previous_page(self):
        await self.check_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.is_paginating:
            await self.show_page(self.current_page)

    async def close(self):
        await self._clean("Это меню было закрыто")
        self.is_paginating = False

    def add_function(self, emote, function):
        self.functions.append((emote, function))

    async def _clean(self, message: str = None, icon_url: str = None):
        message = message or "Это меню было закрыто из-за неактивности"
        icon_url = icon_url or self.ctx.bot.theme.images.cancel
        self.embed.set_footer(text=message, icon_url=icon_url)
        await self.message.edit(embed=self.embed)
        try:
            await self.message.clear_reactions()
        except discord.Forbidden:
            pass

    def check_reaction(self, reaction, user):
        if user is None or user.id != self.ctx.author.id:
            return False
        if reaction.message.id != self.message.id:
            return False

        for emote, function in self.controllers + self.default_functions + self.functions:
            if reaction.emoji == emote:
                self.match = function
                if (emote, function) in self.functions:
                    self.embed.set_footer()
                    if self.show_return:
                        self.loop.create_task(self.message.add_reaction(self.emotes.misc.return_))
                    self.on_function_page = True
                else:
                    if self.on_function_page:
                        self.loop.create_task(self.message.remove_reaction(self.emotes.misc.return_, self.ctx.me))
                        self.on_function_page = False
                return True

        if reaction.emoji in self.reaction_bullets and self.is_menu:
            return True

        return False

    async def paginate(self, **kwargs):
        first_page = self.show_page(1, first=True, **kwargs)
        if not self.is_paginating:
            await first_page
        else:
            self.loop.create_task(first_page)

        while self.is_paginating:
            try:
                r, user = await self.ctx.bot.wait_for("reaction_add", check=self.check_reaction, timeout=self.timeout)
            except asyncio.TimeoutError:
                self.is_paginating = False
                try:
                    await self._clean()
                except discord.Forbidden:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(r, user)
            except discord.Forbidden:
                pass
            except discord.NotFound:
                self.ctx.bot.eh.sentry.capture_exception()

            await self.match()


class FieldPaginator(BasePaginator):

    @staticmethod
    async def _default_entry_parser(ctx, entry, entries):
        try:
            return entry[0], entry[1]
        except TypeError:
            return entry, entries[entry]

    async def show_page(self, page, first=False, **kwargs):
        self.current_page = page
        entries = self.get_page(page)
        self.embed.clear_fields()

        if self.is_menu:
            for entry in entries:
                bullet = entry.emote
                key, value = await entry.get_string()
                key = f"{bullet}   {key}"
                self.reaction_bullets.append(bullet)
                self.embed.add_field(name=key, value=value, inline=self.inline)
        else:
            for entry in entries:
                key, value = await self.entry_parser(self.ctx, entry, self.entries)
                self.embed.add_field(name=key, value=value, inline=self.inline)

        if self.max_pages > 1:
            if self.show_entry_count:
                text = f"Displaying {page} of {self.max_pages} pages and {len(entries)} entries."
            else:
                text = f"Displaying {page} of {self.max_pages} pages."
            self.embed.set_footer(text=text)

        if self.show_author:
            self.embed.set_author(name=self.ctx.author.name, icon_url=self.ctx.author.avatar_url)

        if not first:
            return await self.message.edit(embed=self.embed)

        self.message = await self.ctx.send(embed=self.embed)

        await self.set_controllers(**kwargs)
