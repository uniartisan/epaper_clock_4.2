import json
import os
import re
import sys
import time

import requests
from lxml import etree

output_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'weather.json')


def fail_exit(msg):
    with open(output_file, 'w') as out_file:
        json.dump({'error': msg}, out_file)
    sys.exit(1)


def write_tianqi():
    try:
        html = ''
        header = {
            "Host": 'www.tianqi.com',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59'
        }
        with open('location.json')as loc:
            loca = loc.readline()
            if len(loca) == 0:
                address = 'https://www.tianqi.com/xian/'
            else:
                address = 'https://www.tianqi.com/' + loca + '/'
        r = requests.get(address, timeout=10, headers=header)
        r.encoding = 'utf-8'
        html = r.text

        result = {field: None for field in '''city_name current_temp current_weather 
            current_wind current_humidity today_weather current_air 
            current_air_num today_uv tomorrow_weather tomorrow_temp_high
            tomorrow_temp_low tomorrow_wind'''.split()}
        tree = etree.HTML(html)
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[1]/h2')
        if rt:
            result['city_name'] = rt[0].text
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[3]/p/b')
        if rt:
            result['current_temp'] = rt[0].text.replace(u'℃', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[3]/span/b')
        if rt:
            result['current_weather'] = rt[0].text
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[4]/b[1]')
        if rt:
            result['current_humidity'] = rt[0].text.replace(
                u'%', '').replace(u'湿度：', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[4]/b[2]')
        if rt:
            result['current_wind'] = rt[0].text.replace(u'风向：', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[5]/h5')
        if rt:
            result['current_air'] = rt[0].text.replace(u'空气质量：', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[5]/h6')
        if rt:
            result['current_air_num'] = rt[0].text.replace(u'PM: ', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[3]/span/text()')
        if rt:
            result['today_weather'] = rt[0].replace(
                u' ~ ', '-').replace(u'℃', '')
        rt = tree.xpath('/html/body/div[5]/div/div[1]/dl/dd[4]/b[3]')
        if rt:
            result['today_uv'] = rt[0].text.replace(u'紫外线：', '')
        #print(result)

        # 获取第二天天气状态
        rt = tree.xpath('/html/body/div[5]/div/div[2]/div[2]/ul[2]/li[2]')
        if rt:
            result['tomorrow_weather'] = rt[0].text
        rt = tree.xpath(
            '/html/body/div[5]/div/div[2]/div[2]/div/ul/li[2]/span')
        if rt:
            result['tomorrow_temp_high'] = rt[0].text
        rt = tree.xpath('/html/body/div[5]/div/div[2]/div[2]/div/ul/li[2]/b')
        if rt:
            result['tomorrow_temp_low'] = rt[0].text
        rt = tree.xpath('/html/body/div[5]/div/div[2]/div[2]/ul[3]/li[2]')
        if rt:
            result['tomorrow_wind'] = rt[0].text

        keys_require = '''city_name current_temp current_weather 
            current_wind current_humidity today_weather current_air 
            current_air_num today_uv tomorrow_weather tomorrow_temp_high
            tomorrow_temp_low tomorrow_wind'''.split()

        for key in keys_require:
            if not result.get(key):
                fail_exit('can not get key %s' % key)

        result['update'] = int(time.time())
        with open(output_file, 'w') as out_file:
            json.dump(result, out_file, ensure_ascii=False, indent=4)
        return 1

    except Exception as e:
        print('qianti fail')
        return 0
