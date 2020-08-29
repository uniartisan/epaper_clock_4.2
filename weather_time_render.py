# coding: utf-8

from PIL import Image, ImageDraw, ImageFont
from lib import epd4in2bc
import datetime
import json
import os
import sys
import time
import requests
from cpu_temperature import *
from tianqi import *
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


def isConnected():
    try:
        html = requests.get("https://www.baidu.com", timeout=5)
    except:
        return False
    return True


def kill_if_exit():
    info = []
    r = os.popen(
        'ps -ef | grep "weather_time_render.py" | grep -v grep | awk \'{print $2}\'')
    info = r.readlines()
    pid = 0
    if len(info) >= 2:
        for i in range(0, len(info)-1):
            pid = info[i]
            os.system('sudo kill %s' % (pid))
        print('kill suceess')

    if pid != 0:
        return 1
    else:
        return 0


def get_all_data():
    success = False
    while(success == False):
        success = write_cpu()
        success = write_tianqi()
    time.sleep(5)


def weather_retry():
    write_tianqi()
    print('fail to get weather data, waiting for 80 secs')
    time.sleep(80)


def check_midnight():
    hour = datetime.datetime.now().hour
    if 1 <= hour < 6:
        return 1
    else:
        return 0


try:
    # 午夜不刷新
    if check_midnight():
        sys.exit('Midnight:Skip')

    if kill_if_exit():
        time.sleep(60)
    get_all_data()

    epd = epd4in2bc.EPD()
    epd.init()

    # 定义字体
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font26 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 26)
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
    font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
    font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
    font54 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 54)

    HBlackimage = Image.new('1', (epd.width, epd.height), 255)
    HRYimage = Image.new('1', (epd.width, epd.height), 255)
    drawblack = ImageDraw.Draw(HBlackimage)
    drawyellow = ImageDraw.Draw(HRYimage)

    hour_flag = 0
    date_flag = 0
    net_work_flag = 0
    weather_flag = 0
    time_now = datetime.datetime.now()
    date_string = time_now.strftime('%Y-%m-%d')
    week_string = [u'星期一', u'星期二', u'星期三', u'星期四',
                   u'星期五', u'星期六', u'星期日'][time_now.isoweekday() - 1]
    
    # 午夜页面
    if time_now == 0:
        drawblack.text((98, 90), '(*/ω＼*)', font=font54, fill=0)
        drawyellow.text((110, 170), 'SLEEPING TIME', font=font26, fill=0)
        message=date_string+' '+week_string
        message = ' '*14+message
        drawblack.text((0, 250), message, font=font26, fill=0)
        epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
        epd.sleep()
        sys.exit('Midnight:Flash')

    # 绘制边框线，输出日期信息
    for i in range(32, 34):
        drawblack.line((0, i, 400, i), fill=0)
    for i in range(269, 271):
        drawblack.line((0, i, 400, i), fill=0)
    drawblack.text((10, 0), date_string, font=font26, fill=0)
    drawblack.text((150, 0), week_string, font=font26, fill=0)

    hour_now = datetime.datetime.now().hour
    hour_mes = ' AM'

    # hour_flag 23~6点为1
    if hour_now < 6:
        hour_mes += '   凌晨'
        hour_flag = 1
    elif hour_now >= 12:
        hour_mes = ' PM'
        if hour_now >= 23:
            hour_mes += '   深夜'
            hour_flag = 1
        hour_now -= 12

    if hour_flag == 0:      # 非深夜
        drawblack.text((240, 0), str(hour_now) +
                       hour_mes, font=font26, fill=0)
    else:
        drawyellow.text((240, 0), str(hour_now) +
                        hour_mes, font=font26, fill=0)
    hour_now = datetime.datetime.now().hour     # 重新赋值为24小时制
    # hour_now =23

    if hour_flag == 0:
        # cpu 工作状况
        cpu_data_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'raspi_temp.json')
        cpu_data = {}
        with open(cpu_data_file, 'r')as f:
            cpu_data = json.load(f)
        cpu_tem = cpu_data['cpu_temp']
        ram_per = cpu_data['mem_per']
        # CPU 温度异常
        if float(cpu_tem) <= 50:
            drawblack.text((5, 275), 'CPU 温度：'+str(cpu_tem) +
                           ' 摄氏度', font=font18, fill=0)
        else:
            drawyellow.text((5, 275), 'CPU 温度：'+str(cpu_tem) +
                            ' 摄氏度', font=font18, fill=0)
        drawblack.text((215, 275), 'RAM 使用率：'+str(ram_per) +
                       ' %', font=font18, fill=0)
    else:   # 深夜
        if datetime.datetime.now().hour < 6:
            if datetime.datetime.now().hour == 1:
                drawyellow.text((20, 275), '这是一个彩蛋~还不睡！！', font=font18, fill=0)
            elif datetime.datetime.now().hour == 0:
                drawblack.text((20, 275), '咋还没有睡觉~', font=font18, fill=0)
            else:
                drawblack.text((20, 275), '让我康康是哪个小孩子还没睡觉~',
                               font=font18, fill=0)
        else:
            drawblack.text((20, 275), '劳累了一天，该睡觉了哦~', font=font18, fill=0)
        drawyellow.text((280, 272), ':P', font=font24, fill=0)

    # 检测网络情况
    while net_work_flag == 0:
        net_work_flag = isConnected()
        if net_work_flag == 0:
            drawyellow.text((20, 50), 'ERROR:',
                            font=font48, fill=net_work_flag)
            drawyellow.text((50, 110), '好像失去了网络连接…',
                            font=font26, fill=net_work_flag)
            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            time.sleep(180)

    # 读取天气信息
    while weather_flag == 0:
        weather_data_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'weather.json')
        wdata = {}
        with open(weather_data_file, 'r') as in_file:
            wdata = json.load(in_file)
        if 'error' in wdata:
            drawyellow.text((20, 50), 'ERROR:', font=font48, fill=weather_flag)
            drawyellow.text((50, 110), '无法加载天气数据!',
                            font=font26, fill=weather_flag)
            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            weather_retry()
        elif int(time.time()) - wdata['update'] > 5 * 60:
            drawyellow.text((20, 50), 'ERROR:', font=font48, fill=weather_flag)
            drawyellow.text((50, 110), '天气数据过期!',
                            font=font26, fill=weather_flag)
            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            weather_retry()
        else:
            weather_flag = 1

    for i in range(50, 150):
        drawyellow.line((0, i, 400, i), fill=1)

    # 处理天气数据
    city_name = wdata['city_name']
    today_weather = wdata['today_weather']
    current_temp = wdata['current_temp']
    current_weather = wdata['current_weather']
    current_wind = wdata['current_wind']
    current_humidity = wdata['current_humidity']
    current_air = wdata['current_air']
    current_air_num = wdata['current_air_num']
    today_uv = wdata['today_uv']
    tomorrow_weather = wdata['tomorrow_weather']
    tomorrow_temp_high = wdata['tomorrow_temp_high']
    tomorrow_temp_low = wdata['tomorrow_temp_low']
    tomorrow_wind = wdata['tomorrow_wind']
    if 22 <= hour_now < 24:
        cw = tomorrow_weather
    else:
        cw = current_weather

    bmp_name = {u'晴': 'WQING.BMP', u'阴': 'WYIN.BMP', u'多云': 'WDYZQ.BMP',
                u'雷阵雨': 'WLZYU.BMP', u'小雨': 'WXYU.BMP', u'中雨': 'WXYU.BMP'}.get(cw, None)
    if not bmp_name:
        if u'雨' in cw and u'雷' not in cw:
            bmp_name = 'WYU.BMP'
        elif u'雪' in cw:
            bmp_name = 'WXUE.BMP'
        elif u'雹' in cw:
            bmp_name = 'WBBAO.BMP'
        elif u'雾' in cw or u'霾' in cw:
            bmp_name = 'WWU.BMP'
        elif u'云' in cw:
            bmp_name = 'WDYZQ.BMP'
        elif u'雷' in cw:
            bmp_name = 'WLZYU.BMP'

    blackimage1 = Image.new('1', (epd.width, epd.height), 255)
    yellowimage1 = Image.new('1', (epd.width, epd.height), 255)
    newimage = Image.open(os.path.join(picdir, bmp_name))
    if bmp_name == 'WQING.BMP' or bmp_name == 'WDYZQ.BMP' or bmp_name == 'WYIN.BMP':
        HBlackimage.paste(newimage, (25, 52))
        bad_weather = 0
    else:
        HRYimage.paste(newimage, (25, 46))
        bad_weather = 1

    # 输出主要天气信息
    if 22 <= hour_now < 24:
        drawblack.text((190, 50), '明日：', font=font16, fill=0)
        # 不同的明日天气不同显示
        wether_lenth = len(tomorrow_weather)
        if wether_lenth == 1:
            message_x =255;message_y=55;fonts=font48
        elif wether_lenth == 2:
            message_x =252;message_y=55;fonts=font48
        elif wether_lenth <= 4:
            message_x =238;message_y=63;fonts=font36
        else:
            message_x =232;message_y=75;fonts=font30

        if bad_weather:
            drawyellow.text((message_x, message_y), str(
                tomorrow_weather), font=fonts, fill=0)
        else:
            drawblack.text((message_x, message_y), str(
                tomorrow_weather), font=fonts, fill=0)

        drawblack.text((220, 120), '最低气温：' +
                       str(tomorrow_temp_low) + ' 度', font=font18, fill=0)
        drawblack.text((220, 150), '最高气温：' +
                       str(tomorrow_temp_high) + ' 度', font=font18, fill=0)
        drawblack.text((220, 180), '明日将会是 ' +
                       str(tomorrow_wind), font=font18, fill=0)

        if int(tomorrow_temp_high)-int(tomorrow_temp_low) >= 12:
            if u'雨' in tomorrow_weather:
                message = '明日有异常天气，且温差较大'
            else:
                message = '明日的温差有些大，要注意穿衣哦~'
        else:
            if int(tomorrow_temp_high) >= 32:
                message = '不妙，明天好像有点热欸'
            if int(tomorrow_temp_low) <= 15:
                message = '明天好像有点冷'
            elif int(tomorrow_temp_low) <= 5 or u'雪' in tomorrow_weather:
                message = '明天的天气有些恶劣呢'
            elif u'雨' in tomorrow_weather:
                message = '明天有可能下雨，要注意呢'
            else:
                message = '明天天气大概率还不错哦！'
        message = ' '*4*int((23-len(message))/2)+message
        drawblack.text((0, 212), str(message), font=font18, fill=0)

    else:
        drawblack.text((190, 50), str(city_name)+'：', font=font16, fill=0)
        if 10 < float(current_temp) < 30:
            drawblack.text((250, 55), str(current_temp) +
                           '度', font=font48, fill=0)
        else:
            drawyellow.text((250, 55), str(current_temp) +
                            '度', font=font48, fill=0)
        drawblack.text((220, 120), '今日气温 ' +
                       str(today_weather) + ' 度', font=font18, fill=0)
        drawblack.text((220, 150), str(current_weather) +
                       ' ' + str(current_wind), font=font18, fill=0)
        drawblack.text((220, 180), '相对湿度 ' +
                       str(current_humidity) + '%', font=font18, fill=0)

        # 空气指数
        drawblack.text((80, 212), 'PM指数:' +
                       str(current_air), font=font18, fill=0)
        if current_air != '优' and current_air != '良':
            drawyellow.rectangle((66, 216, 74, 228), fill=0)

        # 紫外线强度
        drawblack.text((236, 212), 'UV强度:' +
                       str(today_uv), font=font18, fill=0)
        if u'强' in str(today_uv):
            drawyellow.rectangle((222, 216, 230, 228), fill=0)

    # 一言 或 纪念日
     # date_check = time_now.strftime('%m-%d')
    # if date_check == '01-01':
    #     date_year = int(time_now.strftime('%Y'))
    #     age = str(date_year-2020)
    #     hitokoto = age+ 'xxx'
    # elif date_check == '06-16':
    #     date_year = int(time_now.strftime('%Y'))
    #     age = str(date_year-2019)
    #     hitokoto = 'xxx'
    # else:

    url = 'https://v1.hitokoto.cn/?max_length=22&json'
    response = requests.get(url=url)
    content = response.content
    result = json.loads(content)
    hitokoto = str(result['hitokoto'])

    # 居中效果
    hitokoto = ' '*4*int((23-len(hitokoto))/2)+hitokoto
    drawblack.text((0, 240), str(hitokoto), font=font18, fill=0)

    # 显示并休眠
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    epd.sleep()

except IOError as e:
    print('IO error!!!')

except KeyboardInterrupt:
    epd.sleep()
    exit()
