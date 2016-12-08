#!/usr/bin/python

import time
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

import paho.mqtt.client as mqtt

class juleljus(object):
	def __init__(self, leds=50):
		self.leds = leds
		self.spi = SPI.SpiDev(0, 0)
		self.pixels = Adafruit_WS2801.WS2801Pixels(self.leds,spi=self.spi )

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
		print("white in red")
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

	def dispatch(self, pattern, delay=0.2):
		method = getattr(self, pattern)
		#method(delay)	
		method()

light = juleljus()
#light.running_red(delay=0.05)

#time.sleep(2)

#light.clear()

#pixels.clear()
#pixels.show()
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("juleljus/#")


def on_message(client, userdata, msg):
	print("nu")
	print(userdata)
	print(msg.payload)
	light.dispatch(pattern=msg.payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.128.7")

#client.subscribe("juleljus/#")

client.loop_forever()
