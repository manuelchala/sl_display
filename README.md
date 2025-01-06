# SL Display - Raspberry Pi Pico with Ink Screen Display
This repository include all the files required to display departures from Stockholm's public tranport system.

This project utilizes a Raspberry Pi Pico microcontroller and an ink screen display to showcase dynamic content. The project integrates code and libraries provided by both the manufacturer of the display and Raspberry Pi.

# Requirements

- Raspberry Pi Pico

- Pico-ePaper-3.7 ink screen display compatible with Raspberry Pi Pico

- Micro-USB cable

- Thonny micropython or similar development environment


# Usage

1. Connect the ink screen display to the Raspberry Pico according to the manufacturer's instructions.

2. Power on the Raspberry Pi and the display will initialize.

3. Copy all the scripts into the Raspberry Pi.

4. Modify the credentials file with SSID and password for internet connection.

5. Update the Site ID of interest. Search the ID of the station in SL's system by looking in [Trafiklab](https://www.trafiklab.se/api/trafiklab-apis/sl/transport/).

6. Connect the device to a power outlet and let the device run as needed.


# Contributing

Feel free to contribute to this project by submitting issues. Any suggestions for improvements or additional features are welcome.

# License

This project is licensed under the MIT License.
