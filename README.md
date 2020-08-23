# epaper_clock
**一个树莓派墨水屏台历**
## 硬件准备
* 树莓派
* 微雪4.2寸三色墨水屏
* DHT11/22可选

## 已经实现功能
* 爬取天气信息，可自定义城市 、 区
* 显示一言或者纪念日信息
* 黄色显示异常状态，如：高温、CPU异常、PM异常、UV异常等

### 待实现功能
* 异常状况自动初始化墨水屏
* 检测或自动更新功能
* 通过U盘自动更新WIFI信息 :)

## 使用方法
1. 安装 waveshare 官方所需依赖

2. 安装程序所需依赖
```bash
sudo apt install python3-pip
sudo pip3 install requests lxml
sudo apt install git build-essential python3-dev
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 ./setup.py install
```
3. 运行程序
```bash
git clone https://github.com/uniartisan/epaper_clock_4.2.git
cd epaper_clock_4.2
```
在location.json文件并填入城市信息
```bash
python3 weather_time_render.py
```

4. 根据需求设置cron、开机自启动start脚本

## 成品预览
![the clock](https://raw.githubusercontent.com/uniartisan/epaper_clock_4.2/master/pic/preview.jpg)

