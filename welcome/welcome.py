import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.chat_formatting import pagify
import clashroyale
import brawlstats
import asyncio
import time
from random import choice

class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2536725)
        default_guild = {'roles': {'pres' : None, 'vp' : None, 'member' : None, 'bs' : None, 'guest' : None, 'leader' : None, 'family' : None,'remove': None}}
        self.config.register_guild(**default_guild)
        self.crconfig = Config.get_conf(None, identifier=2512325, cog_name="ClashRoyaleCog")
        self.bsconfig = Config.get_conf(None, identifier=5245652, cog_name="BrawlStarsCog")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 440960893916807188 and not member.bot:
            await self.do_setup(member)
        if member.guild.id == 593248015729295360 and not member.bot:
            await self.do_setup_LAFC(member)
        if member.guild.id == 654334199494606848 and not member.bot:
            await self.do_setup_LABSevent(member)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 593248015729295360 and not member.bot:
            welcomeCategory = discord.utils.get(member.guild.categories, id=602906519100719115)
            for ch in welcomeCategory.channels:
                if ch.topic == str(member.id):
                    await ch.delete(reason="User left.")
        if member.guild.id == 654334199494606848 and not member.bot:
            welcomeCategory = discord.utils.get(member.guild.categories, id=654334199993466880)
            for ch in welcomeCategory.channels:
                if ch.topic == str(member.id):
                    await ch.delete(reason="User left.")


    async def initialize(self):
        crapikey = await self.bot.get_shared_api_tokens("crapi")
        if crapikey["api_key"] is None:
            raise ValueError("The Clash Royale API key has not been set.")
        self.crapi = clashroyale.OfficialAPI(crapikey["api_key"], is_async=True)
        
        ofcbsapikey = await self.bot.get_shared_api_tokens("ofcbsapi")
        if ofcbsapikey["api_key"] is None:
            raise ValueError("The Official Brawl Stars API key has not been set.")
        self.ofcbsapi = brawlstats.Client(ofcbsapikey["api_key"], is_async=True)

    def get_bs_config(self):
        if self.bsconfig is None:
            self.bsconfig = Config.get_conf(None, identifier=5245652, cog_name="BrawlStarsCog")
        return self.bsconfig

    # @commands.command(hidden=True)
    # async def detect(self, ctx):
    #     try:
    #         att = ctx.message.attachments[0]
    #         if att.filename[-3:] == "png":
    #             name = "todetect.png"
    #         elif att.filename[-3:] == "jpg":
    #             name = "todetect.jpg"
    #         elif att.filename[-4:] == "jpeg":
    #             name = "todetect.jpeg"
    #         await att.save(name)
    #         text = pytesseract.image_to_data(Image.open(name))
    #         print(text)
    #     except IndexError:
    #         await ctx.send("No image.")

    async def do_setup(self, member):
        newcomer = member.guild.get_role(597767307397169173)
        await member.add_roles(newcomer)
        welcome = self.bot.get_channel(674348799673499671)
        welcomeEmbed = discord.Embed(colour=discord.Colour.blue())
        welcomeEmbed.set_image(url="https://i.imgur.com/wwhgP4f.png")
        text = f"Welcome to **LA** {member.mention}!\nMake sure to read <#713858515135103047> and <#713882338018459729> to familiarise yourself with the server.\nPlease type **/setup cr #your\\_cr\\_tag** or **/setup bs #your\\_bs\\_tag**,\nfor other games type **/setup other** to get verified and see rest of the server!"
        await welcome.send(embed=welcomeEmbed)
        await welcome.send(text)

    async def removeroleifpresent(self, member: discord.Member, *roles):
        msg = ""
        for role in roles:
            if role is None:
                continue
            if role in member.roles:
                await member.remove_roles(role)
                msg += f"Removed **{str(role)}**\n"
        return msg

    async def addroleifnotpresent(self, member: discord.Member, *roles):
        msg = ""
        for role in roles:
            if role is None:
                continue
            if role not in member.roles:
                await member.add_roles(role)
                msg += f"Added **{str(role)}**\n"
        return msg

    @commands.command()
    @commands.guild_only()
    async def newcomertest(self, ctx, tag, member: discord.Member):
        if ctx.author.id != 359131399132807178:
            return await ctx.send("Hands off.")

        await ctx.trigger_typing()

        labs = await self.config.guild(ctx.guid).family()
        guest = await self.config.guild(ctx.guild).guest()
        newcomer = await self.config.guild(ctx.guild).remove()
        brawlstars = await self.config.guild(ctx.guild).bs()
        vp = await self.config.guild(ctx.guild).vp()
        pres = await self.config.guild(ctx.guild).pres()

        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        msg = ""
        try:
            player = await self.ofcbsapi.get_player(tag)
            await self.config.user(member).tag.set(tag.replace("#", ""))
            cl_name = f"<:bsband:600741378497970177> {player.club.name}" if "name" in player.raw_data["club"] else "<:noclub:661285120287834122> No club"
            msg += f"**{player.name}** <:bstrophy:552558722770141204> {player.trophies} {cl_name}\n"
        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed=badEmbed("No player with this tag found!"))

        except brawlstats.errors.RequestError as e:
            return await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!****")

        nick = f"{player.name}"
        try:
            await member.edit(nick=nick[:31])
            msg += f"New nickname: **{nick[:31]}**\n"
        except discord.Forbidden:
            msg += f"I dont have permission to change nickname of this user!\n"
        except Exception as e:
            return await ctx.send(embed=discord.Embed(colour=discord.Colour.blue(), description=f"Something went wrong: {str(e)}"))

        player_in_club = "name" in player.raw_data["club"]
        guilds = await self.config.all_guilds()

        member_role_expected = None
        if player_in_club:
            server = guilds[ctx.guild.id]
            clubs = server["clubs"]
            for club in clubs:
                info = clubs[club]
                if player.club.tag.lower() == "#" + info["tag"]:
                    member_role_expected = info["role"]

        if not player_in_club:
            msg += await self.removeroleifpresent(member, newcomer)
            msg += await self.addroleifnotpresent(member, guest, brawlstars)

        if player_in_club and "LA " not in player.club.name:
            msg += await self.removeroleifpresent(member, newcomer)
            msg += await self.addroleifnotpresent(member, guest, brawlstars)

        if player_in_club and "LA " in player.club.name:
            if member_role_expected is None:
                msg += await self.removeroleifpresent(member, newcomer)
                msg += await self.addroleifnotpresent(member, guest, brawlstars)
                msg += f"Role for the club {player.club.name} not found.\n"
                return await ctx.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg))
            msg += await self.removeroleifpresent(member, newcomer)
            msg += await self.addroleifnotpresent(member, labs, brawlstars)
            msg += await self.addroleifnotpresent(member, member_role_expected)
            try:
                player_club = await self.ofcbsapi.get_club(player.club.tag)
                for mem in player_club.members:
                    if mem.tag == player.raw_data['tag']:
                        if mem.role.lower() == 'vicepresident':
                            msg += await self.addroleifnotpresent(member, vp)
                        elif mem.role.lower() == 'president':
                            msg += await self.addroleifnotpresent(member, pres)
                        break
            except brawlstats.errors.RequestError:
                msg += "<:offline:642094554019004416> Couldn't retrieve player's club role."
        if msg != "":
            await ctx.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg))

    @commands.command()
    @commands.guild_only()
    async def addroletest(self, ctx, keyword, role: discord.Role):
        if ctx.author.id != 359131399132807178:
            return await ctx.send("Hands off.")

        await self.config.user(member).roles.set_raw(keyword, value=role)

        return await ctx.send("Successful.")

    @commands.command()
    @commands.guild_only()
    async def setup(self, ctx, game, tag = "", member: discord.Member = None):
        if ctx.channel.id != 674348799673499671:
            return await ctx.send(embed=discord.Embed(description="This command can't be used in this channel.", colour=discord.Colour.red()))
        if member == None:
            member = ctx.author

        if not (game == "cr" or game == "bs" or game == "other"):
            return await ctx.send(embed=discord.Embed(description="That's not a valid option (`cr`, `bs` or `other`)!", colour=discord.Colour.red()))

        if (game == "cr" or game == "bs") and (tag == "" or len(tag) < 3):
            return await ctx.send(embed=discord.Embed(description="That doesn't look like a valid tag!", colour=discord.Colour.red()))

        globalChat = self.bot.get_channel(556425378764423179)
        newcomer = member.guild.get_role(597767307397169173)
        roleVerifiedMember = member.guild.get_role(597768235324145666)
        roleBSMember = member.guild.get_role(514642403278192652)
        roleCRMember = member.guild.get_role(475043204861788171)
        roleCR = member.guild.get_role(523444129221312522)
        roleBS = member.guild.get_role(523444501096824947)
        roleGuest = member.guild.get_role(472632693461614593)

        msg = ""
        if game.lower() == "bs":
            tag = tag.lower().replace('O', '0')
            if tag.startswith("#"):
                tag = tag.strip('#')
            try:
                player = await self.ofcbsapi.get_player(tag)
                nick = f"{player.name} | {player.club.name}" if "name" in player.raw_data["club"] else f"{player.name}"
                try:
                    await member.edit(nick=nick[:31])
                    msg += f"Nickname changed: {nick[:31]}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change nickname of this user. ({nick[:31]})\n"

                await self.get_bs_config().user(member).tag.set(tag)

                try:
                    await member.add_roles(roleVerifiedMember, roleBS)
                    msg += f"Assigned roles: {roleVerifiedMember.name}, {roleBS.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't add {roleVerifiedMember.name}, {roleBSMember.name}\n"

                try:
                    await member.remove_roles(newcomer)
                    msg += f"Removed roles: {newcomer.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't remove {newcomer.name}\n"

                if "name" in player.raw_data["club"] and "LA " in player.club.name:
                    try:
                        await member.add_roles(roleBSMember)
                        msg += f"Assigned roles: {roleBSMember.name}\n"
                    except discord.Forbidden:
                        msg += f":exclamation:Couldn't add {roleBSMember.name})\n"
                else:
                    try:
                        await member.add_roles(roleGuest)
                        msg += f"Assigned roles: {roleGuest.name}\n"
                    except discord.Forbidden:
                        msg += f":exclamation:Couldn't add {roleGuest.name})\n"
                await globalChat.send(f"<:LA:602901892141547540> {member.mention} welcome to LA Gaming!")
            except brawlstats.errors.NotFoundError as e:
                msg += "No player with this tag found, try again!"
            except brawlstats.errors.RequestError as e:
                msg += f"Brawl Stars API is offline, please try again later! ({str(e)})"
            except Exception as e:
                msg += f":exclamation:Error occured: {str(e)}\n"

        elif game.lower() == "cr":
            tag = tag.lower().replace('O', '0').replace(' ', '')
            if tag.startswith("#"):
                tag = tag.strip('#')
            try:
                player = await self.crapi.get_player("#" + tag)

                nick = f"{player.name} | {player.clan.name}" if player.clan is not None else f"{player.name}"
                try:
                    await member.edit(nick=nick[:31])
                    msg += f"Nickname changed: {nick[:31]}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change nickname of this user. ({nick[:31]})\n"

                await self.crconfig.user(member).tag.set(tag)

                try:
                    await member.add_roles(roleVerifiedMember, roleCR)
                    msg += f"Assigned roles: {roleVerifiedMember.name}, {roleCR}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't add {roleVerifiedMember.name}, {roleCR.name}\n"

                try:
                    await member.remove_roles(newcomer)
                    msg += f"Removed roles: {newcomer.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't add {newcomer.name}\n"

                la_clan = False
                if player.club is not None:
                    clans = await self.crconfig.guild(ctx.guild).clans()
                    for k in clans.keys():
                        if player.club.tag.replace("#", "") == clans[k]["tag"]:
                            la_clan = True

                if la_clan:
                    try:
                        await member.add_roles(roleCRMember)
                        msg += f"Assigned roles: {roleCRMember.name}\n"
                    except discord.Forbidden:
                        msg += f":exclamation:Couldn't add {roleCRMember.name})\n"
                else:
                    try:
                        await member.add_roles(roleGuest)
                        msg += f"Assigned roles: {roleGuest.name}\n"
                    except discord.Forbidden:
                        msg += f":exclamation:Couldn't add {roleGuest.name})\n"
                await globalChat.send(f"<:LA:602901892141547540> {member.mention} welcome to LA Gaming!")

            except clashroyale.NotFoundError as e:
                msg += "No player with this tag found, try again!"
            except clashroyale.RequestError as e:
                msg += f"Clash Royale API is offline, please try again later! ({str(e)})"
            except Exception as e:
                msg += f":exclamation:Error occured: {str(e)}\n"
        else:
            try:
                await member.add_roles(roleVerifiedMember)
                await member.add_roles(roleGuest)
                msg += f"Assigned roles: {roleVerifiedMember.name}, {roleGuest.name}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't change roles of this user. ({roleVerifiedMember.name}, {roleCRMember.name})\n"
            try:
                await member.remove_roles(newcomer)
                msg += f"Removed roles: {newcomer.name}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't remove roles of this user. ({newcomer.name})\n"
            await globalChat.send(f"<:LA:602901892141547540> {member.mention} welcome to LA Gaming!")
        
        await ctx.send(embed=discord.Embed(description=msg, color=discord.Colour.blue()))

    async def do_setup_LAFC(self, member):
        welcomingprocess = member.guild.get_role(673034397179445294)
        await member.add_roles(welcomingprocess)
        welcome = self.bot.get_channel(673026631362805770)
        sendTagEmbed = discord.Embed(title="Welcome to LA Fight Club!", description="To gain access to the rest of the server, send /setupLAFC and your Clash Royale tag in this channel.", colour=discord.Colour.blue())
        sendTagEmbed.set_image(url="https://i.imgur.com/Fc8uAWH.png")
        await welcome.send(member.mention)
        await welcome.send(embed=sendTagEmbed)
        
    @commands.guild_only()
    @commands.command(aliases=["setuplafc"])
    async def setupLAFC(self, ctx, tag, member: discord.Member = None):
        if ctx.channel.id != 673026631362805770:
            await ctx.send(embed=discord.Embed(description="This command can't be used in this channel.", colour=discord.Colour.red()))
            return
        globalChat = self.bot.get_channel(593248015729295362)
        if member == None:
            member = ctx.author
        welcomingprocess = member.guild.get_role(673034397179445294)
        msg = ""
        tag = tag.lower().replace('O', '0').replace(' ', '')
        if tag.startswith("#"):
            tag = tag.strip('#')
        try:
            player = await self.crapi.get_player("#" + tag)
            nick = f"{player.name} | {player.clan.name}" if player.clan is not None else f"{player.name}"
            try:
                await member.edit(nick=nick[:31])
                msg += f"Nickname changed: {nick[:31]}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't change nickname of this user. ({nick[:31]})\n"
            await self.crconfig.user(member).tag.set(tag)
            try:
                roleMember = member.guild.get_role(593299886167031809)
                await member.add_roles(roleMember)
                msg += f"Assigned roles: {roleMember.name}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't change roles of this user. ({roleMember.name})\n"
            trophyRole = None
            if player.trophies >= 8000:
                trophyRole = member.guild.get_role(600325526007054346)
            elif player.trophies >= 7000:
                trophyRole = member.guild.get_role(594960052604108811)
            elif player.trophies >= 6000:
                trophyRole = member.guild.get_role(594960023088660491)
            elif player.trophies >= 5000:
                trophyRole = member.guild.get_role(594959970181709828)
            elif player.trophies >= 4000:
                trophyRole = member.guild.get_role(594959895904649257)
            elif player.trophies >= 3000:
                trophyRole = member.guild.get_role(598396866299953165)
            if trophyRole is not None:
                try:
                    await member.add_roles(trophyRole)
                    msg += f"Assigned roles: {trophyRole.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change roles of this user. ({trophyRole.name})\n"
            if player.challengeMaxWins >= 20:
                try:
                    wins20Role = member.guild.get_role(593776990604230656)
                    await member.add_roles(wins20Role)
                    msg += f"Assigned roles: {wins20Role.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change roles of this user. ({wins20Role.name})\n"

        except clashroyale.NotFoundError as e:
            msg += "No player with this tag found, try again!\n"
        except ValueError as e:
            msg += f"**{str(e)}\nTry again or send a personal message to LA Modmail! ({str(e)})**\n"
        except clashroyale.RequestError as e:
            msg += f"Clash Royale API is offline, please try again later! ({str(e)})\n"
        except Exception as e:
            msg += f"**Something went wrong, please send a personal message to LA Modmail or try again! ({str(e)})**\n"
        await ctx.send(embed=discord.Embed(description=msg, colour=discord.Colour.blue()))

        await member.remove_roles(welcomingprocess)
        wlcm = ["Are you ready to fight?", "Do you have what it takes to become a champion?",
                "Ready to showcase your skill?", "Are you ready to prove yourself?"]
        await globalChat.send(
            f"<:lafclogo:603670041044582516> {member.mention} welcome to LA Fight Club! {choice(wlcm)}")

    async def do_setup_LABSevent(self, member):
        newcomer = member.guild.get_role(677272975938027540)
        await member.add_roles(newcomer)
        welcome = self.bot.get_channel(677272915779125269)
        sendTagEmbed = discord.Embed(title="Welcome to LA Events!", description="To gain access to the rest of the server, send /setupEvents and your Brawl Stars tag in this channel or «/setupEvents spectator» if you want to join as a spectator.", colour=discord.Colour.blue())
        sendTagEmbed.set_image(url="https://i.imgur.com/trjFkYP.png")
        await welcome.send(member.mention)
        await welcome.send(embed=sendTagEmbed)

    @commands.guild_only()
    @commands.command(aliases=["setupevents"])
    async def setupEvents(self, ctx, tag, member: discord.Member = None):
        if ctx.channel.id != 677272915779125269:
            await ctx.send(embed=discord.Embed(description="This command can't be used in this channel.", colour=discord.Colour.red()))
            return
        if member == None:
            member = ctx.author
        newcomer = member.guild.get_role(677272975938027540)
        msg = ""
        if tag != "spectator":
            selfroles = ctx.guild.get_channel(665566710492823554)
            guestselfroles = ctx.guild.get_channel(704890962421219339)
            tags = []
            guilds = await self.get_bs_config().all_guilds()
            events = guilds[654334199494606848]
            clubs = events["clubs"]
            for club in clubs:
                info = clubs[club]
                tagn = "#" + info["tag"]
                tags.append(tagn)

            tag = tag.lower().replace('O', '0')
            if tag.startswith("#"):
                tag = tag.strip('#')
            try:
                player = await self.ofcbsapi.get_player(tag)
                player_in_club = "name" in player.raw_data["club"]
                if player_in_club:
                    nick = f"{player.name} | {player.club.name}"
                elif not player_in_club:
                    nick = f"{player.name}"
                try:
                    await member.edit(nick=nick[:31])
                    msg += f"Nickname changed: {nick[:31]}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change nickname of this user. ({nick[:31]})\n"

                await self.get_bs_config().user(member).tag.set(tag)

                try:
                    LAMember = member.guild.get_role(654334569528688641)
                    guest = member.guild.get_role(701822453021802596)
                    if not player_in_club:
                        await member.add_roles(guest)
                        msg += f"Assigned roles: {guest.name}\n"
                        await guestselfroles.send(f"{member.mention}, take your regional roles to get pinged when a tourney is posted.", delete_after=10)
                    elif player_in_club and ("LA " in player.club.name or player.club.tag in tags):
                        await member.add_roles(LAMember)
                        msg += f"Assigned roles: {LAMember.name}\n"
                        await selfroles.send(f"{member.mention}, take your regional roles to get pinged when a tourney is posted.", delete_after=10)
                    else:
                        await member.add_roles(guest)
                        msg += f"Assigned roles: {guest.name}\n"
                        await guestselfroles.send(f"{member.mention}, take your regional roles to get pinged when a tourney is posted.",delete_after=10)
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't change roles of this user.\n"

                try:
                    await member.remove_roles(newcomer)
                    msg += f"Removed roles: {newcomer.name}\n"
                except discord.Forbidden:
                    msg += f":exclamation:Couldn't remove roles of this user. ({newcomer.name})\n"

                await member.remove_roles(newcomer)

            except brawlstats.errors.NotFoundError as e:
                await ctx.send("No player with this tag found, try again!")
                msg += f":exclamation:Error occured: {str(e)}\n"
            except brawlstats.errors.RequestError as e:
                await ctx.send(f"Brawl Stars API is offline, please try again later! ({str(e)})")
                msg += f":exclamation:Error occured: {str(e)}\n"
            except Exception as e:
                await ctx.send(f"**Something went wrong, please send a personal message to LA Modmail or try again!**")
                msg += f":exclamation:Error occured: {str(e)}\n"
        elif tag == "spectator":
            try:
                spectator = member.guild.get_role(671381405695082507)
                await member.add_roles(spectator)
                msg += f"Assigned roles: {spectator}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't change roles of this user.\n"
            try:
                await member.remove_roles(newcomer)
                msg += f"Removed roles: {newcomer.name}\n"
            except discord.Forbidden:
                msg += f":exclamation:Couldn't remove roles of this user. ({newcomer.name})\n"
        await ctx.send(embed=discord.Embed(description=msg, colour=discord.Colour.blue()))
