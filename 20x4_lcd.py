#/usr/bin/python3

import googlemaps

#  Raspberry Pi Temperatures:
from subprocess import PIPE, Popen
import psutil  # pip python-psutil
from datetime import datetime

# Weather
import pyowm  # pip install pyowm

MAPS_API = 'GOOGLE_MAPS_API_KEY'
SLEEP_TIME = 5  # display each screen for X seconds
UPDATE_TIME = 15  # update data every X minutes
OWM_API = 'OWM_API_KEY'

OWM_LOCATION_ID = 'OWM_LOCATION_ID'

LATLONG1 = '44.778726, -67.202684'  # starting point for directions
LATLONG2 = '32.644601, -117.053074'  # ending point for directions

# LCD display
#!/usr/bin/python3
# --------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  py
#  LCD test script using I2C backpack.
#  Supports 16x2 and 20x4 screens.
#
# Author : Matt Hawkins
# Date   : 20/09/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------
import smbus
import time

# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 20  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line

LCD_BACKLIGHT = 0x08  # On
# LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
# bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1


def lcd_init():
    # Initialise display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = the data
    # mode = 1 for data
    #        0 for command

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)


def lcd_toggle_enable(bits):
    # Toggle enable
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)


def lcd_string(message, line):
    # Send string to display

    message = message.ljust(LCD_WIDTH, " ")

    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

lcd_init()


def getweather():
    try:
        owm = pyowm.OWM(OWM_API)  # You MUST provide a valid API key

        location = OWM_LOCATION_ID
        forecast_out = []

        observation = owm.weather_at_id(location)
        w = observation.get_weather()
        current_temp = str(int(w.get_temperature('fahrenheit')['temp']))
        current_status = str(w.get_status())

        # today_weather = w.get_temperature('fahrenheit')  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}
        #today_day = datetime.date.today().strftime('%a')
        # forecast_out.append({'day':today_day,'high':today_weather['temp'],'low':today_weather['temp_min'],'status':w.get_status()})
        # Daily weather forecast just for the next 4 days at _location_
        forecast = owm.daily_forecast_at_id(location, limit=4).get_forecast().get_weathers()
        for weather in forecast:
            forecast_day = weather.get_reference_time('date').strftime('%a')
            forecast_out.append({'day':forecast_day,'high':weather.get_temperature('fahrenheit')['max'],'low':weather.get_temperature('fahrenheit')['min'],'status':weather.get_status()})

        # display formatting
        output_list = ['Currently:' + current_temp+'F.'+current_status]

        for i in forecast_out:
            output_list.append(i['day']+'.'+str(int(i['high']))+'F-'+str(int(i['low']))+'F.'+i['status'])

        # for i in forecast_out:
        #     output_list.append(i['day']+'.'+str(int(i['high']))+'F-'+str(int(i['low']))+'F.'+i['status'])
    except:
        output_list = ['no weather', ' ', ' ', ' ']
    return output_list


def rpidata():
    try:
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        decoded = output.decode('utf-8')
        cpu_temperature = float(decoded[decoded.index('=') + 1:decoded.rindex("'")])

        cpu_usage = psutil.cpu_percent()

        # ram_total = ram.total / 2 ** 20  # MiB.
        # ram_used = ram.used / 2 ** 20
        # ram_free = ram.free / 2 ** 20
        ram_percent_used = psutil.virtual_memory().percent
        update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        output_list = [
            update,
            'CPU='+str(cpu_usage)+'% used, '+str(int(cpu_temperature))+'C',
            'RAM='+str(ram_percent_used)+'% used',
            '....................']
    except:
        output_list = ['no rpidata',' ', ' ', ' ']
    return output_list

def maps():

    try:
        gmaps = googlemaps.Client(key=MAPS_API)
        direct1 = gmaps.directions(LATLONG1,
                                         LATLONG2,
                                         departure_time=datetime.datetime.now())
        commute1 = direct1[0]['legs'][0]['duration_in_traffic']['text']
        commute1_route = direct1[0]['summary']


        output_list = [
            'Travel Times:',
            'Commute 1:     '+commute1 + ',' + commute1_route,
            '.....'
            '.....']
    except:
        output_list = ['no maps', ' ', ' ', ' ']
    return output_list

def display(output_list):
    # lcd_string(message, line_address, style):

    # Send string to display
    # style=1 Left justified
    # style=2 Centred
    # style=3 Right justified
    # overlength = [False, False, False, False]
    # for i in output_list:
    #     if len(i)>20:
    #         diff = 20-len(i)
    #         i = i+diff*'.'

    lcd_string(output_list[0],LCD_LINE_1)
    lcd_string(output_list[1],LCD_LINE_2)
    lcd_string(output_list[2],LCD_LINE_3)
    lcd_string(output_list[3],LCD_LINE_4)
    return

def load_data():
    rpidata_out = rpidata()
    weather_out = getweather()
    maps_out = maps()
    return [rpidata_out, weather_out, maps_out]

def main():
    while True:
        data = load_data()
        for i in range(int(UPDATE_TIME/SLEEP_TIME*60/len(data))):
            for j in data:
                display(j)
                time.sleep(SLEEP_TIME)




try:
    main()


except KeyboardInterrupt:
    pass
finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    time.sleep(5)
    lcd_string(" ",LCD_LINE_1)
