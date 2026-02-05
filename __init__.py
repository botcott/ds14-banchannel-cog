from .banchannel_cog import BanChannelCog

def setup(bot):
    bot.add_cog(BanChannelCog(bot))