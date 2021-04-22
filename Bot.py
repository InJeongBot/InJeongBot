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

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from urllib.parse import quote_plus

import os

import random

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('안녕'))
    print('Logging')
    print(bot.user.name)
    print('TOKEN =', TOKEN)
    print('Successly access')

def load_chrome_driver():
      
    options = webdriver.ChromeOptions()

    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    return webdriver.Chrome(executable_path=str(os.environ.get(r'C:\Users\tmvls\Desktop\디스코드 봇\chromedriver_win32\chromedriver.exe')), chrome_options=options)



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
            
        driver = load_chrome_driver()
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
async def n(ctx, *, keyword):
    driver = load_chrome_driver()
    driver.implicitly_wait(5)
    driver.get("https://search.naver.com/search.naver?where=image&sm=tab_jum&query="+ keyword)

    imgs = driver.find_elements_by_tag_name('img')
    
    links = []
    n = -1
    for img in imgs :
        if n > 4 :
            break
        link = str(img.get_attribute('src'))
        if 'http' in link :
            if 'logos' in link :
                continue
            else:
                links.append(link)
                n += 1
    print(links)
    if n > 0 :
        r = random.randint(0,n)
        embed = discord.Embed(title= keyword, color = 0x00ff00)
        embed.set_image(url = links[r])
    elif n == 0 :
        embed = discord.Embed(title= keyword, color = 0x00ff00)
        embed.set_image(url = links[0])
    else :
        embed = discord.Embed(title= '검색결과 없음', color = 0x00ff00)
    await ctx.send(embed=embed)


@bot.command()
async def g(ctx, *, keyword):
    driver = load_chrome_driver()
    driver.implicitly_wait(5)
    driver.get("https://www.google.co.kr/search?q="+ keyword +"&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjJ3uOx2JHwAhWMOpQKHQxdAI0Q_AUoAXoECAEQAw&biw=1920&bih=969")
    
    imgs = driver.find_elements_by_css_selector('.rg_i.Q4LuWd')
    
    links = []
    n = -1
    for img in imgs :
        if n > 4 :
            break
        link = str(img.get_attribute('src'))
        if 'http' in link :
            if 'logos' in link :
                continue
            else:
                links.append(link)
                n += 1
    print(links)
    if n > 0 :
        r = random.randint(0,n)
        embed = discord.Embed(title= keyword, color = 0x00ff00)
        embed.set_image(url = links[r])
    elif n == 0 :
        embed = discord.Embed(title= keyword, color = 0x00ff00)
        embed.set_image(url = links[0])
    else :
        embed = discord.Embed(title= '검색결과 없음', color = 0x00ff00)
    await ctx.send(embed=embed)


TOKEN = os.environ['BOT_TOKEN']
bot.run(TOKEN)
