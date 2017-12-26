# rpi-20x4
Displaying information from Raspberry Pi to a i2c 20x4 LCD

Using a I2C TWI Serial 2004 20x4 LCD with a LCM1602 module shield.

20x4 interface functions from Matt Hawkins at https://www.raspberrypi-spy.co.uk/2015/05/using-an-i2c-enabled-lcd-screen-with-the-raspberry-pi/

## Screens
* Raspberry Pi CPU, RAM, temperature
* current weather, weather for next 3 days using OpenWeatherMap
* current commute times using Google Maps.

## Dependencies
     pip install googlemaps pyowm python-psutil

## Requirements
* OpenWeatherMap API key http://openweathermap.org/appid
* Google Maps API key https://developers.google.com/maps/documentation/directions/start
* Set LATLONG1 and LATLONG2 to lattitude and logitude of Directions start/finish
