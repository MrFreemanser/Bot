from discord.ext.commands import DefaultHelpCommand


class CosmosHelp(DefaultHelpCommand):

    async def send_bot_help(self, mapping):

        configs = self.context.bot.configs
        arrow = self.context.bot.emotes.misc.next

        embed = self.context.embeds.primary()
        embed.set_thumbnail(url=configs.info.brand_icon)
        embed.set_author(
            name="Команды", icon_url=self.context.bot.user.avatar_url, url=configs.info.homepage)
        embed.set_footer(text="| IMMORTAL BOOST", icon_url=configs.info.brand_logo)
        embed.description = f"Check the [documentation]({configs.info.homepage}) for full reference of all " \
                            f"plugins and commands. Feel free to [join our community](" \
                            f"{configs.info.community}) for help with anything."
        embed.add_field(name=f"Торговая лавка", value=f" `!!магазин` - Магазин ролей \n"
                                                 f" `!!купить роль` - Купить роль\n"
                                                 f" `!!магазин надеть` - Применить купленную роль\n"
                                                 f" `!!магазин снять` - Снять купленную роль\n")
        embed.add_field(name="Валюта сервера", value=f"`!!баланс` - Показывает кошелёк\n"
                                            # f"- [Home Page]({self.BASE_URL})\n"
                                            f"`!!баланс +` - Получить ежедневные монеты\n"
                                            f"`!!баланс + @member`  - Поделиться ежедневными монетами с пользователем\n"
                                            # f"- [Community]({self.COMMUNITY_INVITE})\n"
                                            # f"- [Documentation]({self.BASE_URL}galaxy-reference/)\n")
                        )
        embed.add_field(name="Support Us", value=f" Patreon)\n"
                                                 f" PayPal)\n"
                                                 f" Voten")                

        destination = self.get_destination()
        await destination.send(embed=embed)
