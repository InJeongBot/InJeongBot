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


bot = commands.Bot(command_prefix = '=')
client = discord.Client()

# 음악 목록
music_user = []
music_title = []
music_queue = []
music_now = []
music_thumbnail = []


# Event 디스코드 시작
@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Game('안녕'))
    print('Logging')
    print(bot.user.name)
    print('TOKEN =', TOKEN)
    print('Successly access')

    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

        

# f_music_title 함수
def f_music_title(msg):
    global music
    global Text
    
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    driver = load_chrome_driver()
    driver.get("https://www.youtube.com/results?search_query="+msg)
    source = driver.page_source
    bs = bs4.BeautifulSoup(source, 'lxml')
    entire = bs.find_all('a', {'id': 'video-title'})
    entireNum = entire[0]
    music = entireNum.text.strip()
    
    music_title.append(music)
    music_now.append(music)
    test1 = entireNum.get('href')
    url = 'https://www.youtube.com'+test1

    #썸네일
    test1_video_number = test1[9:]
    test1_thumbnail = 'http://img.youtube.com/vi/'+ test1_video_number +'/0.jpg'
    music_thumbnail.append(test1_thumbnail)
    
    with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
    URL = info['formats'][0]['url']

    driver.quit()
    
    return music, URL

# music_play 함수
def music_play(ctx):
    global vc
    
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    URL = music_queue[0]
    del music_user[0]
    del music_title[0]
    del music_queue[0]
    del music_thumbnail[0]
    
    vc = get(bot.voice_clients, guild = ctx.guild)
    
    if not vc.is_playing():
        vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx)) 

# music_play_next 함수
def music_play_next(ctx):
    if len(music_now) - len(music_user) >= 2:
        for i in range(len(music_now) - len(music_user) - 1):
            del music_now[0]
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    if len(music_user) >= 1:
        if not vc.is_playing():
            del music_now[0]
            URL = music_queue[0]
            del music_user[0]
            del music_title[0]
            del music_queue[0]
            del music_thumbnail[0]
            
            vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx))

    else:
        if not vc.is_playing():
            try:
                ex = len(music_now) - len(music_user)
                del music_user[:]
                del music_title[:]
                del music_queue[:]
                del music_thumbnail[:]
                while True:
                    try:
                        del music_now[ex]
                    except:
                        break
            except:
                pass
            


# 구글 드라이버 세팅 함수
def load_chrome_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)


# Command /도움말
@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title = "인정봇", description = "")
    embed.set_author(name = "ㅇㅈ#6079", icon_url = 'https://cdn.discordapp.com/avatars/270403684389748736/621692a4dddbf42dd2b01df1301eebe6.png')
    embed.add_field(name = "사용 설명서", value = "- 인정-music 채널 가서  ✅ 누른 다음 제목만 적으세요 \n- 딜레이 심하니까 될때까지 기다렸다가 입력하세요 \n- ( 오류날 시 @ㅇㅈ#6079 ) \n- 다른 채널이나 채널 안들어가 있어도 노래 틀 수 있어요", inline = False)
    embed.add_field(name = "이모지 사용법", value = "- (=join) (=resume) (=pause) (=stop) (=skip) \n- 이모지 한번 누르면 취소했다가 다시 눌러야 작동함", inline = False)
    embed.add_field(name = "Command", value = "/join /leave /play (노래제목) /n (검색어) /g (검색어) \n/queuedel (숫자) /queue /queueclear \n/musicinfo /pause /resume /skip /stop \n/musicchannel /music_ch_video /music_ch_queue", inline = False)
    await ctx.send(embed=embed)


# Command /join
@bot.command()
async def join(ctx):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            await ctx.send("채널에 입장해 주세요")

   
# Command /leave
@bot.command()
async def leave(ctx):
    try:
        client.loop.create_task(vc.disconnect())
    except:
        await ctx.send("인정봇이 음성 채널에 들어가 있지 않네요")



# Command /play 노래제목
@bot.command()
async def play(ctx, *, msg):
    try:
        global vc
        vc = await ctx.message.author.voice.channel.connect()
    except:
        try:
            await vc.move_to(ctx.message.author.voice.channel)
        except:
            pass
    
    if not vc.is_playing():

        options = webdriver.ChromeOptions()
        options.add_argument("headless")
            
        global entireText
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        
        driver = load_chrome_driver()
        driver.get("https://www.youtube.com/results?search_query="+msg)
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

        driver.quit()

        music_now.insert(0, entireText)
        music_thumbnail.insert(0, thumbnail)
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        
        
        #embed = discord.Embed(title = entireText, description = "")
        #embed.set_image(url = thumbnail)
        #await ctx.send(embed=embed)
        
        
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: music_play_next(ctx))

    else:
        music_user.append(msg)
        result, URLTEST = f_music_title(msg)
        music_queue.append(URLTEST)


# Command /queuedel (숫자)
@bot.command()
async def queuedel(ctx, *, number):
    try:
        ex = len(music_now) - len(music_user)
        del music_user[int(number) - 1]
        del music_title[int(number) - 1]
        del music_queue[int(number)-1]
        del music_now[int(number)-1+ex]
        del music_thumbnail[int(number)-1+ex]
            
        await ctx.send("대기열이 정상적으로 삭제되었습니다")
    except:
        if len(list) == 0:
            await ctx.send("대기열에 노래가 없네요")
            
        elif len(list) < int(number):
            await ctx.send("목록의 개수는 " + str(len(list)) + "이에요")
            
        else:
            await ctx.send("숫자를 입력해주세요!")

# Command /queue
@bot.command()
async def queue(ctx):
    if len(music_title) == 0:
        await ctx.send("노래를 등록해주세요")
    else:
        global Text
        Text = ""
        for i in range(len(music_title)):
            Text = Text + "\n" + str(i + 1) + ". " + str(music_title[i])
            
        await ctx.send(embed = discord.Embed(title = "노래목록", description = Text.strip()))


# Command /queueclear
@bot.command()
async def queueclear(ctx):
    try:
        ex = len(music_now) - len(music_user)
        del music_user[:]
        del music_title[:]
        del music_queue[:]
        del music_thumbnail[:]
        while True:
            try:
                del music_now[ex]
            except:
                break
        await ctx.send("목록이 초기화 되었습니다")
    except:
        await ctx.send("노래를 등록해주세요")


# Command /목록재생
@bot.command()
async def 목록재생(ctx):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    if len(user) == 0:
        await ctx.send("노래를 등록해주세요")
    else:
        if len(music_now) - len(music_user) >= 1:
            for i in range(len(music_now) - len(music_user)):
                del music_now[0]
        if not vc.is_playing():
            music_play(ctx)
        else:
            await ctx.send("노래가 이미 재생되고 있어요!")

            
# Command /musicinfo
@bot.command()
async def musicinfo(ctx):
    if not vc.is_playing():
        await ctx.send("노래를 재생하고 있지 않네요")
    else:
        await ctx.send("현재 " + music_now[0] + "을(를) 재생하고 있습니다")


# Command /pause
@bot.command()
async def pause(ctx):
    try:
        vc.pause()
    except:
        await ctx.send("노래를 재생하고 있지 않네요")


# Command /resume
@bot.command()
async def resume(ctx):
    try:
        vc.resume()
    except:
         await ctx.send("노래를 재생하고 있지 않네요")

# Command /skip
@bot.command()
async def skip(ctx):
    if vc.is_playing():
        if len(music_user) >= 1:
            vc.stop()

        else:
            await ctx.send("스킵할 노래가 없네요")
    else:
        await ctx.send("노래를 재생하고 있지 않네요")

# Command /stop
@bot.command()
async def stop(ctx):
    if vc.is_playing():
        vc.stop()
    else:
        await ctx.send("노래를 재생하고 있지 않네요")
    try:
        ex = len(music_now) - len(music_user)
        del music_user[:]
        del music_title[:]
        del music_queue[:]
        del music_thumbnail[:]
        while True:
            try:
                del music_now[ex]
            except:
                break
    except:
        pass
        
    try:
        client.loop.create_task(vc.disconnect())
    except:
        pass


# 봇 전용 음악 채널 만들기
@bot.command(pass_context = True)
async def musicchannel(ctx):
    global vc
    global music_msg

    category = discord.utils.get(ctx.guild.channels, id=832545338002767920)
    channel = await ctx.guild.create_text_channel(name = "music천둥", topic = '#인정_Music')

    all_channels = ctx.guild.text_channels

    InJeongbot_music_ch_id = all_channels[len(all_channels) - 1].id
    
    InJeongbot_music_ch = bot.get_channel(InJeongbot_music_ch_id)
    
    await channel.edit(category = category)
    await channel.edit(position = 100)
    
    embed = discord.Embed(title='인정 Music', description='')
    embed.set_image(url = 'https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
                                   
    music_msg = await InJeongbot_music_ch.send('노래 목록 \n', embed=embed)
    
    while True:
        try:
            embed_music = discord.Embed(title='인정 Music \n' + music_now[0], description='')
            embed_music.set_image(url=music_thumbnail[0])
            await music_msg.edit(embed=embed_music)
                
        except:
            if not vc.is_playing():
                embed_music_f = discord.Embed(title='인정 Music', description='')
                embed_music_f.set_image(url='https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
                await music_msg.edit(embed=embed_music_f)

# 봇 전용 음악 채널 버튼 만들기
@bot.command(pass_context = True)
async def music_ch_video(ctx):
    await music_msg.add_reaction('✅')
    await music_msg.add_reaction('▶')
    await music_msg.add_reaction('⏸')
    await music_msg.add_reaction('⏹')
    await music_msg.add_reaction('⏭')
    
    while True:
        try:
            def check(reaction, user):
                return str(reaction) in ['✅','▶', '⏸', '⏹', '⏭'] and user == ctx.author and reaction.message.id == music_msg.id

            reaction, user = await bot.wait_for('reaction_add', check=check)

            if (str(reaction) == '✅'):
                try:
                    global vc
                    vc = await ctx.message.author.voice.channel.connect()
                except:
                    try:
                        await vc.move_to(ctx.message.author.voice.channel)
                    except:
                        pass
                    
            
            if (str(reaction) == '▶' ):
                try:
                    vc.resume()
                except:
                    pass

            if (str(reaction) == '⏸'):
                try:
                    vc.pause()
                except:
                    pass

            if (str(reaction) == '⏹'):
                if vc.is_playing():
                    try:
                        vc.stop()
                    except:
                        pass
                    try:
                        ex = len(music_now) - len(music_user)
                        del music_user[:]
                        del music_title[:]
                        del music_queue[:]
                        del music_thumbnail[:]
                        while True:
                            try:
                                del music_now[ex]
                            except:
                                break
                    except:
                        pass
                try:
                    client.loop.create_task(vc.disconnect())
                except:
                    pass
                    
            if (str(reaction) == '⏭'):
                if vc.is_playing():
                    if len(music_user) >= 1:
                        vc.stop()
        except:
            pass

# 봇 전용 음악 채널 노래 목록 만들기
@bot.command(pass_context = True)
async def music_ch_queue(ctx):
    while True:
        try:
            text = []
            for i in range(len(music_title)):
                text.append('' + "\n" + str(i + 1) + ". " + str(music_title[i]))
            text.reverse()
            Text = ''
            for i in range(len(text)):
                Text = Text + str(text[i])
            await music_msg.edit(content = '노래 목록 \n' + Text.strip())
        except:
            pass
            
    
# Command /n (내용)
@bot.command()
async def n(ctx, *, keyword):

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    driver = load_chrome_driver()
    driver.implicitly_wait(5)
    driver.get("https://search.naver.com/search.naver?where=image&sm=tab_jum&query="+ keyword)
    driver.maximize_window()
    
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
    
    driver.quit()
    
    if n > 0 :
        r = random.randint(0,n)
        embed = discord.Embed(title= keyword)
        embed.set_image(url = links[r])
    elif n == 0 :
        embed = discord.Embed(title= keyword)
        embed.set_image(url = links[0])
    else :
        embed = discord.Embed(title= '검색결과 없음')
    await ctx.send(embed=embed)


# Command /g (내용)
@bot.command()
async def g(ctx, *, keyword):

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    
    driver = load_chrome_driver()
    driver.implicitly_wait(5)
    driver.get("https://www.google.co.kr/search?q="+ keyword +"&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjJ3uOx2JHwAhWMOpQKHQxdAI0Q_AUoAXoECAEQAw&biw=1920&bih=969")
    driver.maximize_window()

    imgs = driver.find_elements_by_css_selector('img')
    
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

    driver.quit()
    
    if n > 0 :
        r = random.randint(0,n)
        embed = discord.Embed(title= keyword)
        embed.set_image(url = links[r])
    elif n == 0 :
        embed = discord.Embed(title= keyword)
        embed.set_image(url = links[0])
    else :
        embed = discord.Embed(title= '검색결과 없음')
    await ctx.send(embed=embed)

# 봇 음악 전용 채널
@bot.event
async def on_message(msg):
    if msg.author.bot :
        return None
    topic = msg.channel.topic
    if topic != None and '#인정_Music' in topic:
        await play(bot, msg=msg.content)
        await msg.delete()
        
        try:
            embed_music = discord.Embed(title='인정 Music \n' + music_now[0], description='')
            embed_music.set_image(url=music_thumbnail[0])
            await music_msg.edit(embed=embed_music)
                
        except:
            pass
    else:
        await bot.process_commands(msg)


@bot.command()
async def delete_channel(ctx, channel_name):

   guild = ctx.message.guild
   existing_channel = discord.utils.get(guild.channels, name=channel_name)
   

   if existing_channel is not None:
      await existing_channel.delete()

   else:
      await ctx.send(f'"{channel_name}"이 존재하지 않아요')

@bot.command()
async def musicset(ctx):
    await musicchannel(ctx)
    await music_ch_video(ctx)
    await music_ch_queue(ctx)


    
TOKEN = os.environ['BOT_TOKEN']
bot.run(TOKEN)
