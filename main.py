import os
from discord.ext import commands

if __name__ == '__main__':
    client = commands.Bot(command_prefix="+")
    client.remove_command('help')


    @client.command()
    @commands.has_permissions(administrator=True)
    async def load(ctx, extension):
        client.load_extension(f"cogs.{extension}")

    @client.command()
    @commands.has_permissions(administrator=True)
    async def unload(ctx, extension):
        client.unload_extension(f"cogs.{extension}")

    @client.command()
    @commands.has_permissions(administrator=True)
    async def reset(ctx, extension):
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension(f'cogs.{filename[:-3]}')

    client.run('YOUR_TOKEN_HERE')