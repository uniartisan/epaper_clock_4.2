# coding: utf-8

from PIL import Image, ImageDraw, ImageFont
from lib import epd4in2bc
import datetime
import json
import os
import sys
import time
import requests

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


def isConnected():
    try:
        html = requests.get("https://www.baidu.com", timeout=2)
    except:
        return False
    return True


try:

    epd = epd4in2bc.EPD()
    epd.init()
    # epd.Clear()
    # time.sleep(1)

    # Drawing on the image
    font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font48 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
    clock_x = 40
    clock_y = 40
    temp_x = 0
    hour_flag = 0
    date_flag = 0
    net_work_flag = 0
    time_now = datetime.datetime.now()
    time_string = time_now.strftime('%H:%M')
    date_string = time_now.strftime('%Y-%m-%d')
    week_string = [u'星期一', u'星期二', u'星期三', u'星期四',
                   u'星期五', u'星期六', u'星期日'][time_now.isoweekday() - 1]
    if time_string[0] == '0':
        epd.Clear()
        time_string = time_string[1:]
        temp_x += 40

    for c in time_string:
        bmp_name = 'NUM{}.BMP'.format('S' if c == ':' else c)
        temp_x += 70 if c == ':' else 100

    HBlackimage = Image.new('1', (epd.width, epd.height), 255)
    HRYimage = Image.new('1', (epd.width, epd.height), 255)
    drawblack = ImageDraw.Draw(HBlackimage)
    drawyellow = ImageDraw.Draw(HRYimage)
    drawry = ImageDraw.Draw(HRYimage)
    drawblack.text((10, 0), date_string, font=font24, fill=0)
    drawblack.text((150, 0), week_string, font=font24, fill=0)
    hour_now = datetime.datetime.now().hour
    hour_mes = ' AM'
    if (hour_now) < 6:
        hour_mes += '   凌晨'
        hour_flag = 1
    elif(hour_now) >= 12:
        hour_mes = ' PM'
        if(hour_now) >= 23:
            hour_mes += '   深夜'
            hour_flag = 1
        hour_now -= 12

    if hour_flag == 0:
        drawblack.text((240, 0), str(hour_now) +
                       hour_mes, font=font24, fill=0)
        epd.Clear()
    else:
        drawyellow.text((240, 0), str(hour_now) +
                        hour_mes, font=font24, fill=0)

    # 绘制边框线
    for i in range(29, 31):
        drawblack.line((0, i, 400, i), fill=0)
    for i in range(269, 271):
        drawblack.line((0, i, 400, i), fill=0)

    if hour_flag == 0:
        # cpu 工作状况
        cpu_data_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'raspi_temp.json')
        cpu_data = {}
        with open(cpu_data_file, 'r')as f:
            cpu_data = json.load(f)
        cpu_tem = cpu_data['cpu_temp']
        ram_per = cpu_data['mem_per']
        if float(cpu_tem) <= 50:
            drawblack.text((5, 275), 'CPU 温度：'+str(cpu_tem) +
                           ' 摄氏度', font=font18, fill=0)
        else:
            drawyellow.text((5, 275), 'CPU 温度：'+str(cpu_tem) +
                            ' 摄氏度', font=font18, fill=0)
        drawblack.text((215, 275), 'RAM 使用率：'+str(ram_per) +
                       ' %', font=font18, fill=0)
    else:
        if datetime.datetime.now().hour < 6:
            if datetime.datetime.now().hour == 1:
                drawyellow.text((20, 275), '这是一个彩蛋~还不睡！！', font=font18, fill=0)
            elif datetime.datetime.now().hour == 0:
                drawblack.text((20, 275), '我好爱你 (*/ω＼*)', font=font18, fill=0)
            else:
                drawblack.text((20, 275), '让我康康是哪个小孩子还没睡觉~',
                               font=font18, fill=0)
        else:
            drawblack.text((20, 275), '劳累了一天，该睡觉了哦~', font=font18, fill=0)
        drawyellow.text((280, 272), ':P', font=font24, fill=0)

    weather_data_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'weather.json')
    wdata = {}

    # 检测网络情况
    while net_work_flag == 0:
        net_work_flag = isConnected()
        if net_work_flag == 0:
            drawyellow.text((20, 50), 'ERROR:', font=font48, fill=0)
            drawyellow.text((50, 110), '好像失去了网络连接…', font=font24, fill=0)
            epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
            time.sleep(180)
        else:
            drawyellow.text((20, 50), 'ERROR:', font=font48, fill=1)
            drawyellow.text((50, 110), '好像失去了网络连接…', font=font24, fill=1)
    with open(weather_data_file, 'r') as in_file:
        wdata = json.load(in_file)
    if 'error' in wdata:
        drawyellow.text((20, 50), 'ERROR:', font=font48, fill=0)
        drawyellow.text((50, 110), '无法加载天气数据!', font=font24, fill=0)
    else:
        if int(time.time()) - wdata['update'] > 2 * 3600:
            drawyellow.text((20, 50), 'ERROR:', font=font48, fill=0)
            drawyellow.text((50, 110), '天气数据过期!', font=font24, fill=0)
        else:
            cw = wdata['current_weather']
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
                HBlackimage.paste(newimage, (25, 55))
            else:
                HRYimage.paste(newimage, (25, 55))

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
            drawblack.text((190, 50), str(city_name)+'：', font=font16, fill=0)
            if 10 < float(current_temp) < 35:
                drawblack.text((250, 60), str(current_temp) +
                               '度', font=font48, fill=0)
            else:
                drawyellow.text((250, 60), str(current_temp) +
                                '度', font=font48, fill=0)
            drawblack.text((220, 125), '今日气温 ' +
                           str(today_weather) + ' 度', font=font18, fill=0)
            drawblack.text((220, 155), str(current_weather) +
                           ' ' + str(current_wind), font=font18, fill=0)
            drawblack.text((220, 185), '相对湿度 ' +
                           str(current_humidity) + '%', font=font18, fill=0)

            # 空气指数
            if current_air == '优' or current_air == '良':
                drawblack.text((80, 215), 'PM指数:' +
                               str(current_air), font=font16, fill=0)
            else:
                drawyellow.text((80, 215), 'PM指数:' +
                                str(current_air), font=font16, fill=0)

            # 紫外线强度
            if u'强' in str(today_uv):
                drawyellow.text((230, 215), 'UV强度:' +
                                str(today_uv), font=font16, fill=0)
            else:
                drawblack.text((230, 215), 'UV强度:' +
                               str(today_uv), font=font16, fill=0)

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

    url = 'https://v1.hitokoto.cn/?max_length=23&json'
    response = requests.get(url=url)
    content = response.content
    result = json.loads(content)
    hitokoto = str(result['hitokoto'])

    # 居中效果
    hitokoto = ' '*4*int((22-len(hitokoto))/2)+hitokoto
    drawblack.text((0, 240), str(hitokoto), font=font18, fill=0)

    # 显示并休眠
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    epd.sleep()

except IOError as e:
    print('IO error!!!')

except KeyboardInterrupt:
    epd.sleep()
    exit()
