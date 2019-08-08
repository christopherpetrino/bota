import discord
import sys
from bota.constant import MAX_COMMAND_WORD_LENGTH
from bota.private_constant import DISCORD_TOKEN, DISCORD_CLIENT_ID, ADMIN_ID
from bota.applications.top_games import get_top_games
from bota.web_scrap.scrap import get_current_trend, get_counter_hero, get_good_against, get_reddit
from bota.web_scrap.scrap import get_skill_build, get_item_build, get_profile, save_id, get_protracker_hero
from bota.web_scrap.twitch_process import get_dota2_top_stream
from bota.web_scrap.TI.group_stage import get_group_stage
from bota.log_process import save_command_logs, get_command_log_tail
from discord.utils import find
from bota import constant


client = discord.Client()
GUILDS = []

# This weird spacing is to pretty text in discord
commands_list = {'!top_game'        : 'Shows top 9 Live Games        eg: **`!top game`**',
                 '!counter HeroName': 'Shows Heroes which counter the given hero name        eg: **`!counter am`**',
                 '!good HeroName'   : 'Opposite of !counter command. Good against.        eg: **`!good axe`**',
                 '!skill': 'Shows most popular & win rate talent/skill build        eg:**`!skill meepo`**',
                 '!item HeroName'   : 'Shows current meta item build by Top Rank Players        eg: **`!item kotl`**',
                 '!profile  steamID': 'Shows your profile stats given steamID        eg: **`!profile 116585378`**',
                 '!save Alias steamID': 'Saves your steamID under Alias name, and call by Alias name.\n'
                                       '        \
                                       First **--->** **`!save midone 116585378`**  Then **--->** **`!profile midone`**',
                 '!trend'           : 'Shows current heroes trend        eg: `!trend`',
                 '!twitch language' : '**`!twitch`** shows top 8 twitch stream,   eg2: **`!twitch en`** just shows top english streams',
                 '!protrack HeroName': 'Shows hero played recently by Pros, plus shows `GOOD`  and  `BAD` heroes against it.  eg:**`!protrack slark`**',
                 '!reddit'          : 'Gets a reddit post from   **/r/DotA2**. Options: `new`, `controversial`, `top`, `rising`, `random`, `hot`:\n'
                                      '                       eg 1:   **`!reddit`**             : Gets a random post from  /r/DotA2/\n'
                                      '                       eg 2:   **`!reddit hot`**   : Gets Top 3 hot post from  /r/DotA2/\n'
                                      '                       eg 3:   **`!reddit new`**   : Gets Top 3 new post from    /r/DotA2/',
                 '!update'     : 'Shows any new   `Updates`   and   `BOT support`'
                 }


UPDATE_BLOCK = '```cs\n"UPDATE": Added Language option in twitch "!twitch en" "!twitch ru"```'
NOTE = "**NOTE**: Can use short Hero Names, !counter anti mage ---as---> !counter am"
DOTA2_LOGO_URL = 'https://seeklogo.com/images/D/dota-2-logo-A8CAC9B4C9-seeklogo.com.png'

LAST_UPDATE = "**UPDATES:**\n" \
              "1. Added Language option in twitch    `!twitch en`    date: `07-Aug-2019`\n"\
              "2. Added new command    `!protrack HeroName`    date: `06-Aug-2019`\n" \
              "3. Added Notable hero in    `!top game`    date: `05-Aug-2019`\n" \
              "For more info and support please join: https://discord.gg/a7QYPWd"


def embed_txt_message(content, add_header=False, header=constant.DEFAULT_EMBED_HEADER, color=discord.Color.blue()):
    embed_msg = discord.Embed(description=content, color=color)
    if add_header:
        embed_msg.set_author(name=header['name'], icon_url=header['icon_url'], url=header['url'])
    return embed_msg


def get_help():
    help_string = []
    head = "```css\nBelow are the commands to use DOTA BOT: 😋```"
    post_head = UPDATE_BLOCK
    head = head + post_head
    help_string.append(head)
    body = []
    for key, value in commands_list.items():
        command = '**' + key + '**'
        command_help = value
        full = command + '\t:\t' + command_help
        body.append(full + '\n')
    help_string = help_string + body
    help_string = "\n".join(help_string)
    return help_string


async def broadcast_message(msg):
    global GUILDS
    for guild in GUILDS:
        await guild.text_channels[0].send(msg)


@client.event  # event decorator/wrapper
async def on_ready():
    global GUILDS
    GUILDS = client.guilds
    await client.change_presence(activity=discord.Game(name="Dota2 | type '!help'"))
    print(f"Logged in as {client.user}")


@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(f'Hello **{format(guild.name)}**✌✌!\n'
                           f'Type   `!help` or `!command`   to get list of commands to use.')


@client.event
async def on_message(message):
    is_command_called = True
    command_called = ""
    message_string = message.content
    message_string = message_string.lower().strip()
    message_word_length = len(message_string.split())
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")

    if client.user == message.author:
        is_command_called = False
        # Ignore all message passed by the our bot
        pass

    elif message.author.bot:
        # Ignore if message is from another Bot
        is_command_called = False
        pass
    
    elif '!help' == message_string or '--help' == message_string or '!command' in message_string:
        command_called = "!help"
        help_string = get_help()
        # await message.channel.send(help_string)
        embed_msg = embed_txt_message(help_string, add_header=True)
        embed_msg.set_footer(text=NOTE, icon_url=DOTA2_LOGO_URL)
        await  message.channel.send(embed=embed_msg)

    elif ('!top_game' in message_string or '!top game' in message_string) and \
         message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!top_game"
        image_path = get_top_games()
        await message.channel.send(f"Getting Top Live Spectacting Games, Source: Dota2API, Dota2ProTracker")
        await message.channel.send('Top Games: ', file=discord.File(f'{image_path}'))

    elif '!profile' in message_string.split()[0]:
        command_called = "!profile"
        flag, id, mode, result, medal_url = get_profile(message_string)
        result_embed = embed_txt_message(result)
        result_embed.set_author(name=f"**Profile: {id}**", url=f'https://www.dotabuff.com/players/{id}',
                                icon_url=constant.DEFAULT_EMBED_HEADER['icon_url'])
        result_embed.set_thumbnail(url=medal_url)
        if not flag:
            if mode == 1:
                await message.channel.send(f'Could not find any profile under: **{id}**')
            else:
                await message.channel.send(f'Could not find any Alias name : **{id}**')
        else:
            await message.channel.send(embed=result_embed)

    elif '!save' in message_string.split()[0]:
        command_called = "!save"
        user_name, id, flag, status = save_id(message_string)
        if flag:
            await message.channel.send(f'**{id}** saved under the alias: {user_name}')
        else:
            await message.channel.send(f'**Failed to save, reason: {status}')

    elif "!trend" in message_string and message_word_length < (MAX_COMMAND_WORD_LENGTH - 2):
        command_called = "!trend"
        image_path = get_current_trend()
        await message.channel.send(f"Getting this week Heroes Trend, Source: DotaBuff")
        embed_msg = discord.Embed(description='Current Trend: ')
        await message.channel.send(embed=embed_msg, file=discord.File(image_path))

    elif ("!counter" in message_string or "!bad" in message_string) and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!counter"
        found, hero_name, image_path = get_counter_hero(message_string)
        if not found:
            if hero_name != '':
                await message.channel.send(f"Do you mean  **{hero_name}**, Try again with correct name")
            else:
                await message.channel.send(f"Could not find hero, Please make sure the hero name is correct")
        else:
            await message.channel.send(f'**{hero_name.upper()}** is bad against, Source: DotaBuff ', file=discord.File(image_path))

    elif "!good" in message_string and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!good"
        found, hero_name, image_path = get_good_against(message_string)
        if not found:
            if hero_name != '':
                await message.channel.send(f"Do you mean  **{hero_name}**, Try again with correct name")
            else:
                await message.channel.send(f"Could not find hero, Please make sure the hero name is correct")
        else:
            await message.channel.send(f'**{hero_name.upper()}** is good against, Source: DotaBuff ', file=discord.File(image_path))

    elif ("!skill" in message_string or "!talent" in message_string) \
            and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!skill"
        found, hero_name, image_path = await get_skill_build(message_string)
        if not found:
            if hero_name != '':
                await message.channel.send(f"Do you mean  **{hero_name}**, Try again with correct name")
            else:
                await message.channel.send(f"Could not find hero, Please make sure the hero name is correct")
        else:
            await message.channel.send(f'**{hero_name.upper()}** most popular Skill/Talent build: , Source: DotaBuff', file=discord.File(image_path))

    elif "!item" in message_string and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!item"
        found, hero_name, image_path = get_item_build(message_string)
        if not found:
            if hero_name != '':
                await message.channel.send(f"Do you mean  **{hero_name}**, Try again with correct name")
            else:
                await message.channel.send(f"Could not find hero, Please make sure the hero name is correct")
        else:
            await message.channel.send(f'**{hero_name.upper()}** recent Item build by **Top Rank Players**:, Source: DotaBuff', file=discord.File(image_path))

    elif "!twitch" in message_string and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!twitch"
        language = None if len(message_string.split()) <= 1 else message_string.split()[1]
        result = get_dota2_top_stream(language)
        embed_msg = embed_txt_message(result)
        await message.channel.send(embed=embed_msg)

    elif "!reddit" in message_string and message_word_length < MAX_COMMAND_WORD_LENGTH:
        result_list, mode = get_reddit(message_string)
        command_called = f"!reddit {mode}"
        await message.channel.send(f"**REDDIT**  SortBy: **{mode.upper()}**, Source: Reddit")
        for result in result_list:
            await message.channel.send(f'{result}')

    elif "!protrack" in message_string and message_word_length < MAX_COMMAND_WORD_LENGTH:
        command_called = "!protrack"
        found, hero_name, result_string, icon_path = get_protracker_hero(message_string)
        if not found:
            if hero_name != '':
                await message.channel.send(f"Do you mean  **{hero_name}**, Try again with correct name")
            else:
                await message.channel.send(f"Could not find hero, Please make sure the hero name is correct")
        else:
            embed_msg = embed_txt_message(result_string)
            embed_msg.set_author(name=f'**{hero_name.upper()}** Dota2ProTracker:', url='http://www.dota2protracker.com/',
                                 icon_url=f'https://raw.githubusercontent.com/bendangnuksung/bota/master/bota/data/character_icons_big/{hero_name}.png')
            embed_msg.set_thumbnail(url=f'https://raw.githubusercontent.com/bendangnuksung/bota/master/bota/data/character_icons_big/{hero_name}.png')
            await message.channel.send(embed=embed_msg)
            # await message.channel.send(f'ProTracker Record from last **7** days,    Source:   **Dota2 ProTracker**\n'
            #                            f'{result_string}', file=discord.File(icon_path))

    elif "!ti group" in message_string:
        # Release it as soon the TI starts
        command_called = '!ti group'
        result_string = get_group_stage()
        await message.channel.send('`TI9 GROUP STAGE`\n' + result_string)

    elif "!update" in message_string and message_word_length < 2:
        await message.channel.send(LAST_UPDATE)

    # Admin privilege
    elif "!get_user" in message_string and str(message.author) == ADMIN_ID:
        command_called = "!get_user"
        await message.channel.send(f'Steam Users ID:', file=discord.File(constant.STEAM_USER_FILE_PATH))

    elif "!exit" in message_string and str(message.author) == ADMIN_ID:
        message_split = message_string.split()
        if len(message_split) > 1:
            client_id = message_split[1]
            if str(client_id) == str(DISCORD_CLIENT_ID):
                await message.channel.send(f'Exiting client: {client_id}')
                sys.exit(0)

    elif "!broadcast" in message_string and str(message.author) == ADMIN_ID:
        message_split = message_string.split()
        if len(message_split) > 1:
            client_id = message_split[1]
            if str(client_id) == str(DISCORD_CLIENT_ID):
                message = " ".join(message_split[2:])
                await broadcast_message(message)

    elif "!tail" in message_string and str(message.author) == ADMIN_ID:
        is_command_called = False
        n = 5
        try:
            n = int(message_string.split()[1])
        except Exception:
            pass
        tail_log = get_command_log_tail(n)
        await message.channel.send(tail_log)

    # Message user
    elif f"{DISCORD_CLIENT_ID}" in message_string:
        await message.channel.send(f"Hello {message.author.name}"
                                   f" Please type    `!help`  or `!command`  for more options")

    else:
        is_command_called = False

    if is_command_called:
        save_command_logs(message, command_called)


client.run(DISCORD_TOKEN)
