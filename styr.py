#!/usr/bin/python

# MIT License
#
# Copyright (c) 2017 Jimmy Hedman
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

import paho.mqtt.client as mqtt

import json

import os

import ssl

MQTT_SERVER = os.getenv('MQTT_SERVER','test.mosquitto.com')
MQTT_USERNAME = os.getenv('MQTT_USERNAME','')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD','')

class juleljus(object):
    def __init__(self, leds=50):
        self.leds = leds
        self.spi = SPI.SpiDev(0, 0)
        self.pixels = Adafruit_WS2801.WS2801Pixels(self.leds, spi=self.spi)

    def clear(self):
        self.pixels.clear()
        self.pixels.show()

    def pattern_running_red(self, delay=0.2):
        print("red")
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(led, 255, 0, 0)
            self.pixels.show()
            time.sleep(delay)

    def pattern_running_white(self, delay=0.05):
        print("white")
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(led, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)

    def pattern_red_in_white(self, delay=0.2):
        self.pixels.clear()
        for led in range(self.leds / 2):
            self.pixels.set_pixel_rgb(led*2, 255, 0, 0)
            self.pixels.set_pixel_rgb(led*2+1, 255, 255, 255)
        self.pixels.show()

    def pattern_running_white_blue(self, delay=0.2):
        for led in range(self.leds-1):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(led, 32, 32, 255)
            self.pixels.set_pixel_rgb(led+1, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)
        self.pixels.clear()
        self.pixels.show()

    def pattern_rainbow(self, delay=0.2):
        self.pixels.clear()
        for led in range(self.leds):
            self.pixels.set_pixel_hsv(led, (led*1.0)/self.leds, 1, 1)
        self.pixels.show()

    def pattern_red_white_bounce(self, delay=0.02):
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(led, 255, 0, 0)
            self.pixels.set_pixel_rgb(self.leds - led - 1, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(self.leds - led - 1, 255, 0, 0)
            self.pixels.set_pixel_rgb(led, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(led, 255, 0, 0)
            self.pixels.set_pixel_rgb(self.leds - led - 1, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)
        for led in range(self.leds):
            self.pixels.clear()
            self.pixels.set_pixel_rgb(self.leds - led - 1, 255, 0, 0)
            self.pixels.set_pixel_rgb(led, 255, 255, 255)
            self.pixels.show()
            time.sleep(delay)

    def dispatch(self, pattern, delay=0.2):
        method = getattr(self, "pattern_"+pattern, self.pattern_red_in_white)
        method()

    def patterns(self):
        return [pattern[8:] for pattern in dir(self) if pattern.startswith("pattern_")]


light = juleljus()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("juleljus/#")


def on_message(client, userdata, msg):
    if (msg.topic == "juleljus/patterns"):
        print(light.patterns())
        client.publish("juleljus/return", json.dumps(light.patterns()))
    if (msg.topic == "juleljus/run"):
        print(userdata)
        print(msg.topic)
        print(msg.payload)
        light.dispatch(pattern=json.loads(msg.payload))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.tls_set(tls_version=ssl.PROTOCOL_TLSv1_2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

client.connect(MQTT_SERVER, 8883)

client.loop_forever()
