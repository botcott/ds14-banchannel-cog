import json
import logging
import os

from discord.ext import commands

with open(f"{os.path.dirname(__file__)}/config/config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

BAN_CHANNEL_ID = int(cfg["ban_channel_id"])
HIGH_REAPER_ROLE_ID = int(cfg["high_reaper_role_id"])
SKIP_ROLES = list(cfg["skip_roles"])
BAN_REASON = "Отправка сообщения в BAN CHANNEL"

logger = logging.getLogger(__name__)

class BanChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != BAN_CHANNEL_ID or message.author.bot:
            return
        
        guild = message.guild
        user = message.author
        high_reaper = guild.get_role(HIGH_REAPER_ROLE_ID)

        # Скип роли Главного Инженера
        for role_id in SKIP_ROLES:
            role = guild.get_role(role_id)
            if role and role in user.roles:
                return

        if not high_reaper:
            self.logger.error(f"Роль с ID {HIGH_REAPER_ROLE_ID} не найдена на сервере {guild.id}")
            return

        members = high_reaper.members

        try:
            # Бан
            await guild.ban(user, reason=BAN_REASON)
            self.logger.info(f"Пользователь {user} ({user.id}) забанен на сервере {guild.id} за сообщение в канале {BAN_CHANNEL_ID}")

            # Список ВЖ
            if members:
                if len(members) == 1:
                    mention_list = f"<@{members[0].id}>"
                else:
                    mention_list = ", ".join(f"<@{member.id}>" for member in members)
                appeal_text = f"Вы можете обжаловать данный бан у {mention_list}."
            else:
                appeal_text = "Для обжалования бана обратитесь к администрации сервера."

            # Отправка
            try:
                await user.send(
                    f"Вы были забанены на сервере **\"{guild.name}\"**.\n"
                    f"**Причина:** {BAN_REASON}\n"
                    f"{appeal_text}"
                )
                self.logger.info(f"ЛС отправлено пользователю {user} ({user.id}) о бане на сервере {guild.id}")
            except Exception as e:
                self.logger.error(f"Ошибка при отправке ЛС пользователю {user} ({user.id}): {e}")

        except Exception as e:
            self.logger.error(f"Ошибка при бане пользователя {user} ({user.id}): {e}")
