# coding: utf-8

import json
import os
import time

import Adafruit_DHT

# Set sensor type : Options are DHT11,DHT22 or AM2302
sensor = Adafruit_DHT.DHT11

# Set GPIO sensor is connected to
gpio = 4

# Use read_retry method. This will retry up to 15 times to
# get a sensor reading (waiting 2 seconds between each retry).
humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)

result = {'temp': int(temperature), 'humidity': int(
    humidity), 'update': int(time.time())}
data_file = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'home_air.json')
with open(data_file, 'w') as out_file:
    json.dump(result, out_file)
