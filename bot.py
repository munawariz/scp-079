from discord.ext import commands
from discord import Intents, Message
from dotenv import load_dotenv
from cogwatch import watch
import os
import re

class SCP079(commands.Bot):
    def __init__(self, prefix: str, intents: str):
        self.prefix = prefix
        super().__init__(command_prefix=prefix, intents=intents)

    @watch(path='extensions', preload=True)
    async def on_ready(self):
        print('Bot ready.')

    async def on_message(self, message: Message):
        if message.author.bot:
            return

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