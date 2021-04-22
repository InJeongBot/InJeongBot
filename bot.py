import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time
import asyncio
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import os

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('안녕'))
    bot.user.name = '인정'
    print('Logging')
    print(bot.user.name)
    print('TOKEN =', TOKEN)
    print('Successly access')

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    await bot.process_commands(msg)

@bot.command()
async def join(ctx):
    global vc
    vc = await ctx.message.author.voice.channel.connect()
    

@bot.command()
async def play(ctx, *, msg):
    if not vc.is_playing():
        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
        chromedriver_dir = r"C:\Users\tmvls\Desktop\디스코드 봇\chromedriver_win32\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chromedriver_dir)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = bs4.BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        entireText = entireNum.text.strip()
        musicurl = entireNum.get('href')
        url = 'https://www.youtube.com'+musicurl
        video_number = musicurl[9:]
        image_type = '0'
        thumbnail = 'http://img.youtube.com/vi/'+ video_number +'/'+ image_type +'.jpg'
        
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        embed = discord.Embed(title= "노래 재생", description = entireText, color = 0x00ff00)
        embed.set_image(url = thumbnail)
        await ctx.send(embed=embed)
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    else:
        await ctx.send("이미 노래가 재생 중 입니다.")
    print('musicurl =', musicurl)

@bot.command()
async def 게임의신(ctx):
    embed = discord.Embed(title='게임의 신', description='키무라')
    embed.set_image(url="https://cdn.discordapp.com/attachments/754206116380016683/834487987555401758/2ff903bb2d0e9650.jpg")
    await ctx.channel.send(embed=embed)

access_token = os.environ["BOT_TOKEN"]
TOKEN = 'access_token'
bot.run(TOKEN)
