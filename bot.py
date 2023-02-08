from discord.ext import commands
from discord import app_commands, Intents, Interaction, Message
from dotenv import load_dotenv
from cogwatch import watch
from typing import Union
import os
import re

class SCP079(commands.Bot):
    def __init__(self, prefix: str, intents: str):
        self.prefix = prefix
        
        super().__init__(command_prefix=prefix, intents=intents)

    @property
    def DEBUG_GUILDS(self):
        guilds = []
        for guild_id in os.environ.get('DEBUG_GUILDS').split(','):
            guilds.append(self.get_guild(int(guild_id)))
        return guilds
    
    @property
    def LOG_CHANNELS(self): 
        channels = []
        for channel_id in os.environ.get('LOG_CHANNELS').split(','):
            channels.append(self.get_channel(int(channel_id)))
        return channels

    async def setup_hook(self):
        """
        Slash command should be preloaded earlier because syncing needs to happen before on_ready.
        Sync only with debug guild when stage is debug, reduce discord rate limit.
        """
        for filename in os.listdir('./extensions/slashes'):
            if filename.endswith('.py'):
                try: await self.load_extension(f'extensions.slashes.{filename[:-3]}')
                except Exception as e: print(e)

        if os.environ.get('STAGE').lower() == 'debug':
            for guild in self.DEBUG_GUILDS:
                await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        print('Slash command synced.')

    @watch(path='extensions', preload=True)
    async def on_ready(self):
        print('Bot ready.')

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        
        """
        Custom logic handler when you want to process prefixless trigger,
        change the message content to desired command. The rest will be executed like the usual flow
        """
        shopee_match = re.search("(https:\/\/|http:\/\/|\/\/)?shopee\.co\.id\/[a-zA-Z0-9-_]+-i\.[0-9]+\.[0-9]+(\?[a-zA-Z0-9-_]+(=[a-zA-Z0-9-_]+)?(&[a-zA-Z0-9-_]+(=[a-zA-Z0-9-_]+)?)*)?", message.content)
        if shopee_match:
            message.content = f'{self.prefix}shopee_product {shopee_match.group(0)}'
        
        tokopedia_match = re.search("(https:\/\/|http:\/\/|\/\/)?(www\.)?tokopedia\.com\/[a-zA-Z0-9-_]+\/[a-zA-Z0-9-_]+(\?[a-zA-Z0-9-_]+(=[a-zA-Z0-9-_]+)?(&[a-zA-Z0-9-_]+(=[a-zA-Z0-9-_]+)?)*)?", message.content)
        if tokopedia_match:
            message.content = f'{self.prefix}tokopedia_product {tokopedia_match.group(0)}'
        
        await self.process_commands(message)

    async def on_command_completion(self, ctx: commands.Context):
        await ctx.invoke(self.get_command('send_log_to_channel'))

    async def on_command_error(self, ctx: commands.Context, exception: commands.errors.CommandError):
        await ctx.invoke(self.get_command('send_log_to_channel'), exception)
    
    async def on_app_command_completion(self, interaction: Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]):
        ctx = await commands.Context.from_interaction(interaction)
        ctx.current_argument = [f"{option['name']}:{option['value']}" for option in interaction.data['options']]
        await ctx.invoke(self.get_command('send_log_to_channel'))
    
    async def on_app_command_error(self, interaction: Interaction, exception: app_commands.AppCommandError):
        ctx = await commands.Context.from_interaction(interaction)
        ctx.current_argument = [f"{option['name']}:{option['value']}" for option in interaction.data['options']]
        await ctx.invoke(self.get_command('send_log_to_channel'), exception)

def start_bot():
    load_dotenv()

    intents = Intents.default()
    intents.message_content = True
    intents.members = True
    intents.presences = True

    scp = SCP079(prefix='!', intents=intents)
    scp.run(token=os.environ.get('TOKEN'))

if __name__ == '__main__':
    start_bot()