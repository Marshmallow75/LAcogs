import discord
import httpx
from redbot.core import commands, Config


class ClashOfClansCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=42136942)
        default_user = {"tag": None}
        self.config.register_user(**default_user)
        default_guild = {"clans": {}}
        self.config.register_guild(**default_guild)
        self.baseurl = "https://api.clashofclans.com/v1/"

    async def initialize(self):
        cockey = await self.bot.get_shared_api_tokens("cocapi")
        token = cockey["api_key"]
        if token is None:
            raise ValueError("CoC API key has not been set.")
        self.headers = {
            "authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

    def apirequest(self, url: str):
        url = self.baseurl + url
        response = httpx.get(url=url, headers=self.headers, timeout=20)
        return response.json()
    
        @commands.command()
    async def find_member(self, ctx, member: discord.Member):
        for u in self.config.all_users():
            if discord.utils.escape_markdown(u.display_name.lower()) == discord.utils.escape_markdown(member.display_name.lower()):
                await ctx.send(self.config.user(u).tag())
        await ctx.send("No matches were found.")
    
    @commands.command()
    async def get(self, ctx, tag: str):
        """Takes in the clan's tag and returns clan info"""

        tag = "clans/%23" + tag.replace("#", "")
        clan_json = self.apirequest(tag)
        
        try:
            if clan_json['clanLevel'] < 5:
                donation_upgrade = 0
            elif clan_json['clanLevel'] < 10:
                donation_upgrade = 1
            else:
                donation_upgrade = 2
        except:
            return await ctx.send(clan_json)
        
        await ctx.send("All went good.")

    @commands.command()
    async def getclantest(self, ctx, tag: str):
        tag = "clans/%23" + tag.replace("#", "")

        try:
            clan_json = self.apirequest(tag)
        except Exception as e:
            return await ctx.send(e)
        
        class General(commands.Cog):
   #Description of what this file does 
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="get_clan", aliases=["getclan", "clan"])
    async def get_clan(self, ctx, clan_tag):
        """Gets clan information from API and displays it for user"""
        # This line uses a utility in the coc.py library to correct clan tags (case, missing #, etc.)
        clan_tag = coc.utils.correct_tag(clan_tag)

        clan = await self.bot.coc.get_clan(clan_tag)
        content = f"The clan name for {clan_tag} is {clan.name}.\n"
        content += f"{clan.name} currently has {clan.member_count} members.\n\n"

        war = await self.bot.coc.get_current_war(clan_tag)
        if war:
            content += f"Current war state is {war.state}\n"
            if war.state != "notInWar":
                content += f"Opponent: {war.opponent}"

        await ctx.send(content)

def setup(bot):
    bot.add_cog(General(bot))

        await ctx.send(clan_json['name'])
