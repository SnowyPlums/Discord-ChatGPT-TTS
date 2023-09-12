import functools
import typing

from dotenv import load_dotenv
import os

import chatGPTSpeech

import speech_recognition as sr

import discord
from discord.ext import commands

#-Load .env content---------------------------------------

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = int(os.getenv('SERVER_ID'))
TEXT_CHANNEL = int(os.getenv('TEXT_CHANNEL'))

#-Discord bot config--------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=";", intents=intents)

class BotInfo:
    def __init__(self, vc = any, flag = False):
        self._vc = vc
        self._flag = flag

    def get_vc(self):
        return self._vc
    
    def set_vc(self, x):
        self._vc = x

    def get_flag(self):
        return self._flag
    
    def set_flag(self, x):
        self._flag = x

botInfo = BotInfo()

#-Speech recognizer---------------------------------------

recognizer = sr.Recognizer()

#---------------------------------------------------------
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(SERVER))
    print('bot ready')

@bot.tree.command(name = "start", guild=discord.Object(SERVER))
async def start(ctx: discord.Interaction):
    if ctx.channel_id == TEXT_CHANNEL:
        vc = ctx.user.voice

        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice == None:
            vc = await vc.channel.connect()
            botInfo.set_vc(vc)

        await ctx.response.send_message('I will now start to listen')
        await run_askGPT(askGPT)

@bot.tree.command(name = "stop", guild=discord.Object(SERVER))
async def stop(ctx: discord.Interaction):
    chatGPTSpeech.stopCode()
    await ctx.response.send_message('I will now stop running')
    await exit()

@bot.tree.command(name = "purge-context", guild=discord.Object(SERVER))
async def purgeContext(ctx: discord.Interaction):
    chatGPTSpeech.purgeContext()
    await ctx.response.send_message('Context is now purged')

@bot.tree.command(name = "create-summary", guild=discord.Object(SERVER))
async def createSummary(ctx: discord.Interaction):
    chatGPTSpeech.createSummary()
    await ctx.response.send_message('A summary of the current context was created')



async def run_askGPT(askGPT: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(askGPT, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)

def askGPT():
    channel = bot.get_channel(TEXT_CHANNEL)
    with sr.Microphone(device_index=3) as source:
        print("Passively listening for 'Cortana'...")

        while True:
            try:
                audio_chunk = recognizer.listen(source, timeout=4)
            except sr.WaitTimeoutError:
                continue  # No speech detected in the timeframe

            try:
                stt = recognizer.recognize_google(audio_chunk)

                if "cortana" in stt.lower():
                    tts = stt.lower().split('cortana ')[-1]

                    print(f"Keyword 'Cortana' detected: {tts}")

                    chatGPTSpeech.sendPrompt(tts)

                    botInfo.set_flag(True)

                    if botInfo.get_flag():
                        botInfo.get_vc().play(discord.FFmpegPCMAudio('output.wav'))
                        botInfo.set_flag(False)
                    

            except sr.UnknownValueError:
                print("Google could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")


bot.run(TOKEN)