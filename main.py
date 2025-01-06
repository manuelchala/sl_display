# -----------------------------------------------------------------------------
# Author               :   Manuel Chala
# Github               :   https://github.com/manuelchala/sl_display
#
# This project uses code and libraries provided by the manufacturer of the ink display and by Raspberry Pi.
# Portions of this script are derived from or based on example code and documentation provided by these sources.
# Full credit for those sections goes to their respective authors and organizations.
# Any modifications or extensions to the original code are my own work.
# -----------------------------------------------------------------------------

import network
import time
import urequests
from machine import Pin
import ujson as json
import gc
import utime

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connect or fail
    wait = 10
    while wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        wait -= 1
        print('Waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('WiFi connection failed')
    else:
        print('Connected')
        print('IP:', wlan.ifconfig()[0])

def get_next_trains(site_id):
    url_2 = f"https://transport.integration.sl.se/v1/sites/{site_id}/departures"
    r_2 = None
    
    try:
        r_2 = urequests.get(url_2)
        if r_2.status_code == 200:
            data_2 = r_2.json()
            departures = data_2.get('departures', [])
            output_string = ""
            train_count = 0
            
            for departure in departures:
                line = departure.get('line', {})
                transport_mode = line.get('transport_mode')
                line_id = line.get('id')
                destination = departure.get('destination', '')
                display = departure.get('display', '')

                if transport_mode == "TRAIN":
                    output_string += f"    {line_id} {destination} -> {display}\n"
                    train_count += 1
                    if train_count == 4:
                        break
            
            del data_2, departures, line  # Free memory after processing
            gc.collect()

            return output_string if train_count > 0 else "No trains :("
        else:
            print("Error in the request. Status code:", r_2.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        if r_2:
            r_2.close()

def get_next_buses(site_id):
    url_2 = f"https://transport.integration.sl.se/v1/sites/{site_id}/departures"
    r_2 = None
    
    try:
        r_2 = urequests.get(url_2)
        if r_2.status_code == 200:
            data_2 = r_2.json()
            departures = data_2.get('departures', [])  # Limit to the first 4 departures
            output_string = "  Bus 179"
            bus_count = 0
            
            for departure in departures:
                line = departure.get('line', {})
                transport_mode = line.get('transport_mode')
                line_id = line.get('id')
                display = departure.get('display', '')

                if transport_mode == "BUS" and line_id == 179:
                    output_string += f" -> {display}"
                    bus_count += 1
                    if bus_count == 4:
                        break
            
            del data_2, departures, line  # Free memory after processing
            gc.collect()

            return output_string if bus_count > 0 else "No buses :("
        else:
            print("Error in the request. Status code:", r_2.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        if r_2:
            r_2.close()

def get_current_datetime():
    url = "https://script.googleusercontent.com/macros/echo?user_content_key=j6_xC2duTv5WNpVXDHbRCIBDI6T3k1WkPU5IK0l8Jgm-DYq86yE-WOQmQfCyOgJJOkYzKKVZHgC2UOBBl5R98jmcf-Rv0bt3m5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnJ9GRkcRevgjTvo8Dc32iw_BLJPcPfRdVKhJT5HNzQuXEeN3QFwl2n0M6ZmO-h7C6bwVq0tbM60-YSRgvERRRx9L72oj6rycKTFdWLHMlS_T&lib=MwxUjRcLr2qLlnVOLh12wSNkqcO1Ikdrk"
    response = urequests.get(url)
    
    try:
        if response.status_code == 200:
            data = response.json()
            
            # Construct the datetime string
            datetime_value = f"{data['dayofweekName']}, {data['day']} {data['monthName']} {data['year']}-{data['hours']:02}:{data['minutes']:02}:{data['seconds']:02}"
            
            del data  # Free memory after processing
            gc.collect()
            return datetime_value
        else:
            return None
    finally:
        response.close()

def get_weather_data():
    url = "https://api.open-meteo.com/v1/forecast?latitude=59.430510140079825&longitude=17.951579335376234&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = urequests.get(url)

    try:
        if response.status_code == 200:
            data = response.json()
            current_temperature = str(data['current']['temperature_2m'])
            current_wind_speed = str(data['current']['wind_speed_10m'])
            del data  # Free memory after processing
            gc.collect()
            return current_temperature, current_wind_speed
        else:
            return None, None
    finally:
        response.close()

from epd_3in7 import EPD_3in7
from centerwriter import CenterWriter
import font30
import credentials

if __name__ == '__main__':

    # Initialize Wi-Fi connection
    connect_to_wifi(credentials.ssid, credentials.password)

    # Initialize EPD and CenterWriter
    epd = EPD_3in7()
    cw = CenterWriter(epd, font30)  
         
    epd.fill(0xff)  # Clear the display

    while True:
        try:
            gc.collect()  # Trigger garbage collection at the start

            result_train = get_next_trains(credentials.siteid)
            result_buses = get_next_buses(credentials.siteid)

            if result_train is None:
                result_train = "No train data available"
            if result_buses is None:
                result_buses = "No bus data available"

            # Limit train data to the first four lines
            lines = result_train.split('\n')[:4]
            result_train_limited = '\n'.join(lines)

            # Get formatted datetime
            formatted_datetime = get_current_datetime()
            if formatted_datetime is None:
                formatted_datetime = "Time not available"

            epd.fill(0xff)  # Clear the display

            # Set vertical spacing and write text on e-paper display
            cw.set_vertical_spacing(0)
            cw.write_lines([
                f"SL DEPARTURES",
                f"{formatted_datetime}",
                #f"Temp: {temperature}°C - Wind: {wind_speed} km/h",
                "------------------------------------------------------------",
                result_train_limited,
                "", "", "",
                "------------------------------------------------------------",
                result_buses
            ])

            epd.show()  # Show content on e-paper display
            
            gc.collect()  # Trigger garbage collection before sleeping

            time.sleep(60)  # Sleep for 1 minute
        except Exception as e:
            print("An error occurred:", e)
            gc.collect()  # Handle exceptions and trigger garbage collection
