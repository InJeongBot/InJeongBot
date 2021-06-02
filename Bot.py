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


command_prefix = '-'
bot = commands.Bot(command_prefix = command_prefix)
client = discord.Client()

administrator_id = [ 270403684389748736, 849320491034476574 ]

# 음악 목록
music_user = []
music_title = []
music_queue = []
music_now = []
music_thumbnail = []

music_var = [ music_user, music_title, music_queue, music_now, music_thumbnail ]
discord_server_id = []
discord_server_name = []
server_id = 0
music_var_num = 0

# Command /comfirm_server_id
@bot.command()
async def comfirm_server_id(ctx):
    global server_id
    global music_var_num
    if server_id != ctx.guild.id:
        while True:
            if ctx.guild.id in discord_server_id:
                server_id = ctx.guild.id
                for i in range(len(discord_server_id)):
                    if ctx.guild.id == discord_server_id[i]:
                        music_var_num = i
                        break
            else:
                discord_server_id.append(ctx.guild.id)
                discord_server_name.append(ctx.guild.name)
                continue
            break
        print(discord_server_name)
        print(discord_server_id)
        print(discord_server_name[music_var_num], discord_server_id[music_var_num])
        print(server_id)
        print(music_var_num)

# Event 디스코드 시작
@bot.event
async def on_ready():
    await bot.change_presence(status = discord.Status.online, activity = discord.Game('안녕'))
    print('Logging')
    print(bot.user.name)
    print('TOKEN =', TOKEN)
    print('Successly access')
'''
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')
'''

        

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
    embed.add_field(name = "명령어", value = "/join /leave /play (노래제목) /n (검색어) /g (검색어) \n/queuedel (숫자) /queue /queueclear \n/musicinfo /pause /resume /skip /stop \n/musicchannel /music_ch_video /music_ch_queue", inline = False)
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
        
        try:
            embed = discord.Embed(title = entireText, description = "")
            embed.set_image(url = thumbnail)
            await ctx.send(embed=embed)
        except:
            pass
        
        
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
async def musicchannel(ctx, chname, msg):
    global vc
    global music_msg

    category = discord.utils.get(ctx.guild.channels, id=int(msg))
    channel = await ctx.guild.create_text_channel(name = chname, topic = '#인정_Music')

    all_channels = ctx.guild.text_channels

    InJeongbot_music_ch_id = all_channels[len(all_channels) - 1].id
    
    InJeongbot_music_ch = bot.get_channel(InJeongbot_music_ch_id)
    
    await channel.edit(category = category)
    await channel.edit(position = 100)
    
    embed = discord.Embed(title='인정 Music', description='')
    embed.set_image(url = 'https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
                                   
    music_msg = await InJeongbot_music_ch.send('노래 목록 \n', embed=embed)

    music_reaction_list = ['✅','▶','⏸','⏹','⏭','']
    for n in music_reaction_list:
        await music_msg.add_reaction(n)


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

'''
# 봇 전용 음악 채널 버튼 만들기
@bot.command()
async def on_reaction_add(reaction,user):

    if (reaction.emoji == '✅'):
        try:
            global vc
            vc = await ctx.message.author.voice.channel.connect()
        except:
            try:
                await vc.move_to(ctx.message.author.voice.channel)
            except:
                pass


    if (reaction.emoji == '▶' ):
        try:
            vc.resume()
        except:
            pass

    if (reaction.emoji == '⏸'):
        try:
            vc.pause()
        except:
            pass

    if (reaction.emoji == '⏹'):
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

    if (reaction.emoji == '⏭'):
        if vc.is_playing():
            if len(music_user) >= 1:
                vc.stop()
'''
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
    
    imgs = driver.find_elements_by_tag_name('._image._listImage')
    
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



@bot.command()
async def delete_channel(ctx, channel_name):

   guild = ctx.message.guild
   existing_channel = discord.utils.get(guild.channels, name=channel_name)
   

   if existing_channel is not None:
      await existing_channel.delete()

   else:
      await ctx.send(f'"{channel_name}"이 존재하지 않아요')


# 추가 기능
@bot.command(pass_context = True)
async def dkssud(ctx, chname, msg):
    global vc

    category = discord.utils.get(ctx.guild.channels, id=int(msg))
    channel = await ctx.guild.create_text_channel(name = chname, topic = '#인정_Music')

    all_channels = ctx.guild.text_channels

    idd = all_channels[len(all_channels) - 1].id
    
    ch = bot.get_channel(idd)
    
    await channel.edit(category = category)
    await channel.edit(position = 100)
    
    embed = discord.Embed(title='인정 Music', description='')
    embed.set_image(url = 'https://i.ytimg.com/vi/1SLr62VBBjw/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCbXp098HNZl_SbZ5Io5GuHd6M4CA')
                                   
    dkssud = await ch.send('노래 목록 \n', embed=embed)

    await dkssud.add_reaction('✅')
    await dkssud.add_reaction('▶')
    await dkssud.add_reaction('⏸')
    await dkssud.add_reaction('⏹')
    await dkssud.add_reaction('⏭')


# 추가 기능
@bot.command(pass_context = True)
async def create_channel(ctx, chname, msg, topic_msg):

    category = discord.utils.get(ctx.guild.channels, id=int(msg))
    channel = await ctx.guild.create_text_channel(name = chname, topic = topic_msg)
    
    await channel.edit(category = category)
    await channel.edit(position = 100)

# 알람 기능
@bot.command(pass_context = True)
async def 알람(ctx, a_time, msg):
    await ctx.send(f"알람이 {a_time}초 후에 울립니다")
    t = time.time()
    while True:
        if time.time() >= t + int(a_time):
            await ctx.send(f"{ctx.message.author.mention} {msg}")
            break
        else:
            pass
        
# 추가 기능
@bot.command(pass_content = True)
async def 하이빅스비(ctx):
    await ctx.send(f"{ctx.message.author.mention} 네 주인님")


# ㅅㄹ ㄱ 매크로
# 헤로쿠용
thffod = ['<솔랭고파일>', '솔랭', 'thffod', 'ㅅㄹ', 'tf', 'ㅅㄺ', '솔ㄹ랭', 'thfffod', '소랭', 'thfod', '설랭', 'tjffod', '듀오', 'ebdh', 'ㄷㅇ', '아이언', 'dkdldjs', '브론즈', 'qmfhswm', 'bronze', 'iron', 'duo', 'solo', 'rank', 'srg', 'SRG', 'thffh', 'fodzm', 'ソロ', 'ランク', '솔 랭']
gkdl = ['<하이파일>', 'ㅎㅇ', 'gd', '하이', 'gkdl', 'ㅎ2', 'g2', 'hi', 'hello', '해위', '하위']



# 주식 기능
stock_commands = [ '등록 (@호출) (닉네임)', '주식정보', '내자산', '자산목록', '내주식', '주식목록', '매수 (주식이름) (갯수)', '매도 (주식이름) (갯수)', '돈보내기 (@호출) (긍맥)', '주식양도 (@호출) (주식이름) (갯수)', '대출 (금액)', '빚청산 (금액)', '내빚', '빚목록']
# parameter : i
stock_player_id = [] 
stock_player = [] 
money = []
start_price = 5000
stock_stocks = []
debt = []
# parameter : n
stock_name = [ '주식1', '주식2', '주식3', '주식4', '주식5', '주식6' ]
stock_price_p = [ 100, 100, 100, 100, 100, 100 ]
stock_price_c = [ 100, 100, 100, 100, 100, 100 ]

# 상장 폐지 (상폐)
delisting = 30
delisting_list = []


# 주식 상폐 여부 함수
def stock_delisting_check():
    global delisting_list
    delisting_list = []
    n = 0
    for price in stock_price_c:
        if price <= delisting:
            price = 100
            stock_price_c[n] = price
            stock_price_p[n] = price
            delisting_list.append(stock_name[n])
            for i in range(len(stock_player_id)):
                stock_stocks[i][stock_name[n]] = 0
        n += 1

# 주식 변동 함수
def stock_change():
    n = 0
    for price in stock_price_c:
        stock_price_p[n] = price
        n += 1

    n = 0
    for price in stock_price_p:
        if price > 100:
            pr = random.randint(price-100, price+100 + 1)
        else:
            pr = random.randint(0, price+100 + 1)
        stock_price_c[n] = pr
        n += 1

    print(stock_price_p)
    print(stock_price_c)

# 주식정보 함수
def stock_info():
    sn = ''
    for n in range(len(stock_name)):
        c1 = str(stock_price_c[n] - stock_price_p[n])
        if int(c1) >= 0:
            if len(c1) == 1:
                m1 = f'[ ▲    {c1} ]'
            elif len(c1) == 2:
                m1 = f'[ ▲   {c1} ]'
            elif len(c1) == 3:
                m1 = f'[ ▲  {c1} ]'
        else:
            if len(c1) == 2:
                m1 = f'[ ▼   {c1} ]'
            if len(c1) == 3:
                m1 = f'[ ▼  {c1} ]'
            if len(c1) == 4:
                m1 = f'[ ▼ {c1} ]'

        if stock_price_c[n] >= 1000:
            p1 = f'{stock_name[n]}:  {str(stock_price_c[n])}'
        elif stock_price_c[n] >= 100:
            p1 = f'{stock_name[n]}:   {str(stock_price_c[n])}'
        elif stock_price_c[n] >= 10:
            p1 = f'{stock_name[n]}:    {str(stock_price_c[n])}'
        else:
            p1 = f'{stock_name[n]}:     {str(stock_price_c[n])}'

        if n % 2 == 1:
            sn += f'\t\t{p1}\t{m1}\n'
        else: sn += f'{p1}\t{m1}'

    return sn


# 주식 초기화
def stock_clear():
    global stock_player_id, stock_player, money, stock_stocks, debt, stock_name,stock_price_p, stock_price_c
    stock_player_id = [] 
    stock_player = [] 
    money = []
    stock_stocks = []
    debt = []
    stock_name = [ '주식1', '주식2', '주식3', '주식4', '주식5', '주식6' ]
    stock_price_p = [ 100, 100, 100, 100, 100, 100 ]
    stock_price_c = [ 100, 100, 100, 100, 100, 100 ]

@bot.command()
async def 주식변동(ctx):
    if ctx.message.author.id in administrator_id:
        stock_change()
        stock_delisting_check()
        await ctx.send('```주가가 변동되었습니다.```')

@bot.command()
async def 관리자(ctx):
    if ctx.message.author.id in administrator_id:
        await ctx.send('관리자 확인')

@bot.command()
async def 주식정보(ctx):
    s = ''
    sn = stock_info()
    embed = discord.Embed(title = f"```========================\t인정주식\t========================\n\n{sn}```", description = "")
    embed.set_author(name = "   ㅇㅈ#6079", icon_url = 'https://cdn.discordapp.com/avatars/270403684389748736/621692a4dddbf42dd2b01df1301eebe6.png')
    await ctx.send(embed=embed)
    if len(delisting_list) != 0:
        for i in range(len(delisting_list)):
            if i != len(delisting_list) - 1:
                s += delisting_list[i] + '와(과) '
            else:
                s += delisting_list[i] + '이(가)'
        await ctx.send(f'```주가가 30 이하로 떨어져 {s} 상장 폐지 되었습니다.```')


@bot.command()
async def 주식초기화(ctx):
    if ctx.message.author.id in administrator_id:
        stock_clear()
        await ctx.send('```주식의 가격이 초기화 되었습니다.```')

@bot.command()
async def 내자산(ctx):  
    for n in range(len(stock_player_id)):
        if ctx.message.author.id == stock_player_id[n]:
            await ctx.send(f'```{stock_player[n]}님의 자산 : {money[n]}원```')
            break

@bot.command()
async def 자산목록(ctx):
    s = ''
    for n in range(len(stock_player_id)):
        s += f'{stock_player[n]} : {money[n]}원' + '\n'

    await ctx.send(f'```{s}```')

@bot.command()
async def 내주식(ctx):
    s = ''
    for i in range(len(stock_player_id)):
        if ctx.message.author.id == stock_player_id[i]:
            for n in range(len(stock_name)):
                if n == len(stock_name) - 1:
                    s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개'
                else:
                    s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개, ' 
            break

    await ctx.send(f'```{stock_player[i]}님의 주식 : {s}```')

@bot.command()
async def 주식목록(ctx):
    s = ''
    for i in range(len(stock_player_id)):
        s += f'{stock_player[i]} : '
        for n in range(len(stock_name)):
            if n == len(stock_name) - 1:
                s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개'
            else:
                s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개, ' 
        s += '\n'

    await ctx.send(f'```{s}```')

@bot.command()
async def 등록(ctx, member: discord.Member, msg):
    global start_price
    n = 0
    m = 0
    if member.id in stock_player_id:
        n = 1

    if msg in stock_player:
        m = 1

    if n + m >= 1:
        await ctx.send('```이미 등록되어 있습니다.```')
    elif n + m == 0:
        stock_player_id.append(member.id)
        stock_player.append(msg)
        money.append(start_price)
        debt.append(0)
        a = {}
        for n in range(len(stock_name)):
            a[stock_name[n]] = 0
        stock_stocks.append(a)
        await ctx.send(f'```{msg}님, 등록 되었습니다.```')

@bot.command()
async def 매수(ctx, msg, num):
    if int(num) > 0:
        for n in range(len(stock_name)):
            if msg == stock_name[n]:
                for i in range(len(stock_player_id)):
                    if ctx.message.author.id == stock_player_id[i]:
                        if money[i] - stock_price_c[n] >= 0:
                            if money[i] - stock_price_c[n] * int(num) < 0:
                                num = money[i] // stock_price_c[n]
    
                            stock_stocks[i][stock_name[n]] += int(num)
                            money[i] -= stock_price_c[n] * int(num)
                            await ctx.send(f'```{stock_player[i]}님이 {stock_name[n]}을(를) {stock_price_c[n] * int(num)}원({int(num)}개)에 매수 하였습니다.```')
                            break
                        else:
                            await ctx.send((f'```{stock_player[i]}님의 자산이 부족합니다.```'))
                    
    else:
        await ctx.send(f'```최소 1개 이상 적어주세요.```')

@bot.command()
async def 매도(ctx, msg, num):
    if int(num) > 0:
        for n in range(len(stock_name)):
            if msg == stock_name[n]:
                for i in range(len(stock_player_id)):
                    if ctx.message.author.id == stock_player_id[i]:
                        if stock_stocks[i][stock_name[n]] > 0:
                            if stock_stocks[i][stock_name[n]] - int(num) < 0:
                                num = stock_stocks[i][stock_name[n]]

                            stock_stocks[i][stock_name[n]] -= int(num)
                            money[i] += stock_price_c[n] * int(num)
                            await ctx.send(f'```{stock_player[i]}님이 {stock_name[n]}을(를) {stock_price_c[n] * int(num)}원({int(num)}개)에 매도 하였습니다.```')
                            break
                        else:
                            await ctx.send(f'```현재 {stock_player[i]}님은 {stock_name[n]}을(를) {stock_stocks[i][stock_name[n]]}개 가지고 있습니다.```')

    else:
        await ctx.send(f'```최소 1개 이상 적어주세요.```')

@bot.command()
async def 돈보내기(ctx, member: discord.Member, won):
    if int(won) > 0:
        for n in range(len(stock_player_id)):
            if member.id == stock_player_id[n]:
                for i in range(len(stock_player_id)):
                    if ctx.message.author.id == stock_player_id[i]:
                        if money[i] - int(won) >= 0:
                            money[n] += int(won)
                            money[i] -= int(won)
                            await ctx.send(f'```{stock_player[i]}님이 {stock_player[n]}님에게 {int(won)}원을 보내주었습니다.```')
                            break
                        else:
                            await ctx.send(f'```{stock_player[i]}님의 자산이 부족합니다.```')
                            break
    else:
        await ctx.send(f'```최소 1원 이상 적어주세요.```')

@bot.command()
async def 주식양도(ctx, member: discord.Member, msg, num):
    if int(num) > 0:
        for n in range(len(stock_player_id)):
            if member.id == stock_player_id[n]:
                for i in range(len(stock_player_id)):
                    if ctx.message.author.id == stock_player_id[i]:
                        for r in range(len(stock_name)):
                            if msg == stock_name[r]:
                                if stock_stocks[i][stock_name[r]] - int(num) >= 0:
                                    stock_stocks[i][stock_name[r]] -= int(num)
                                    stock_stocks[n][stock_name[r]] += int(num)
                                    await ctx.send(f'```{stock_player[i]}님이 {stock_player[n]}님에게 {stock_name[r]}을(를) {int(num)}개 양도해 주었습니다.```')
                                    break
                                else:
                                    await ctx.send(f'```현재 {stock_player[i]}님은 {stock_name[r]}을(를) {stock_stocks[i][stock_name[r]]}개 가지고 있습니다.```')
                                    break
    else:
        await ctx.send(f'```최소 1개 이상 적어주세요.```')

@bot.command()
async def 대출(ctx, won):
    if int(won) > 0:
        for i in range(len(stock_player_id)):
            if ctx.message.author.id == stock_player_id[i]:
                money[i] += int(won)
                debt[i] += int(won)
                await ctx.send(f'```{stock_player[i]}님이 {int(won)}원을 대출 받았습니다.```')
                break
    else:
        await ctx.send(f'```최소 1원 이상 적어주세요.```')

@bot.command()
async def 빚청산(ctx, won):
    if int(won) > 0:
        for i in range(len(stock_player_id)):
            if ctx.message.author.id == stock_player_id[i]:
                if debt[i] > 0:
                    if debt[i] - int(won) >= 0:
                        money[i] -= int(won)
                        debt[i] -= int(won)
                        await ctx.send(f'```{stock_player[i]}님이 빚 {debt[i]+int(won)}원 중 {int(won)}원을 갚았습니다.```')
                        break
                    else:
                        await ctx.send(f'```{stock_player[i]}님의 대출 현황은 {debt[i]}원 입니다.```')
                else:
                    await ctx.send(f'```{stock_player[i]}님의 대출 현황은 {debt[i]}원 입니다.```')
    else:
        await ctx.send(f'```최소 1원 이상 적어주세요.```')

@bot.command()
async def 내빚(ctx):
    for i in range(len(stock_player_id)):
        if ctx.message.author.id == stock_player_id[i]:
            await ctx.send(f'```{stock_player[i]}님의 빚 : {debt[i]}원```')
            break

@bot.command()
async def 빚목록(ctx):
    s = '빚 목록\n'
    for i in range(len(stock_player_id)):
        s += f'{stock_player[i]} : {debt[i]}원' + '\n'
    await ctx.send(f'```{s}```')

# 봇 전용 주식 채널 만들기
@bot.command(pass_context = True)
async def stockchannel(ctx, chname, msg):
    category = discord.utils.get(ctx.guild.channels, id=int(msg))
    channel = await ctx.guild.create_text_channel(name = chname, topic = '#인정주식')
    
    await channel.edit(category = category)
    await channel.edit(position = 100)


@bot.event
async def on_message(msg):
    global server_id
    await comfirm_server_id(msg)

    topic = msg.channel.topic

    if msg.author.id == 834693850538180618:
        return None

    if msg.content[:1] == command_prefix:
        await bot.process_commands(msg)

    else:
        if server_id == 768734914949939210:
            r = random.randint(0,1)
            o = False
            # 마법의 소라고동
            if '?' in msg.content:
                if '834693850538180618' in msg.content:
                    if r == 1:
                        await msg.channel.send('그 래.')
                        o = True
                    else:
                        await msg.channel.send('안 돼.')
                        o = True
                        
            if o == False:
                # 솔랭 하이 매크로
                if msg.content == '270403684389748736':
                    await msg.channel.send('ㄴ')

                for i in thffod:
                    if i in msg.content:
                        await msg.channel.send('ㄴ')
                        break
                for j in gkdl:
                    if j in msg.content:
                        await msg.channel.send('ㅂㅇ')
                        break
 
    if topic != None and '#인정_Music' in topic:
        await play(bot, msg=msg.content)
        await msg.delete()
        
        try:
            embed_music = discord.Embed(title='인정 Music \n' + music_now[0], description='')
            embed_music.set_image(url=music_thumbnail[0])
            await music_msg.edit(embed=embed_music)
                
        except:
            pass


    # 주식 기능
    elif topic is not None and '#인정주식' in topic:

        await msg.delete()
        if msg.content == '도움말':
            s = ''
            for i in stock_commands:
                s += i + '\n'
            await msg.channel.send(f'```{s}```')

        elif msg.content == '내자산':
            for n in range(len(stock_player_id)):
                if msg.author.id == stock_player_id[n]:
                    await msg.channel.send(f'```{stock_player[n]}님의 자산 : {money[n]}원```')
                    break

        elif msg.content == '자산목록':
            s = ''
            for n in range(len(stock_player_id)):
                s += f'{stock_player[n]} : {money[n]}원' + '\n'
            await msg.channel.send(f'```{s}```')

        elif msg.content == '주식초기화':
            if msg.author.id == administrator_id:
                stock_clear()
                await msg.channel.send('```주식의 가격이 초기화 되었습니다.```')

        elif msg.content == '주식정보':
            s = ''
            sn = stock_info()
            embed = discord.Embed(title = f"```========================\t인정주식\t========================\n\n{sn}```", description = "")
            embed.set_author(name = "   ㅇㅈ#6079", icon_url = 'https://cdn.discordapp.com/avatars/270403684389748736/621692a4dddbf42dd2b01df1301eebe6.png')
            await msg.channel.send(embed=embed)
            if len(delisting_list) != 0:
                for i in range(len(delisting_list)):
                    if i != len(delisting_list) - 1:
                        s += delisting_list[i] + '와(과) '
                    else:
                        s += delisting_list[i] + '이(가)'
                await msg.channel.send(f'```주가가 30이하로 떨어져 {s} 상장 폐지 되었습니다.```')

        elif msg.content == '주식변동':
            for admin_id in administrator_id:
                if msg.author.id == admin_id:
                    stock_change()
                    stock_delisting_check()
                    await msg.channel.send('```주가가 변동되었습니다.```')

        elif msg.content == '내주식':
            s = ''
            for i in range(len(stock_player_id)):
                if msg.author.id == stock_player_id[i]:
                    for n in range(len(stock_name)):
                        if n == len(stock_name) - 1:
                            s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개'
                        else:
                            s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개, ' 
                    break

            await msg.channel.send(f'```{stock_player[i]}님의 주식 : {s}```')
        
        elif msg.content == '주식목록':
            s = ''
            for i in range(len(stock_player_id)):
                s += f'{stock_player[i]} : '
                for n in range(len(stock_name)):
                    if n == len(stock_name) - 1:
                        s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개'
                    else:
                        s += f'{stock_name[n]} {stock_stocks[i][stock_name[n]]}개, ' 
                s += '\n'

            await msg.channel.send(f'```{s}```')

        elif msg.content == '내빚':
            for i in range(len(stock_player_id)):
                if msg.author.id == stock_player_id[i]:
                    await msg.channel.send(f'```{stock_player[i]}님의 빚 : {debt[i]}```')
                    break

        elif msg.content == '빚목록':
            s = '빚 목록\n'
            for i in range(len(stock_player_id)):
                s += f'{stock_player[i]} : {debt[i]}' + '\n'
            await msg.channel.send(f'```{s}```')




TOKEN = os.environ['BOT_TOKEN']
bot.run(TOKEN)
