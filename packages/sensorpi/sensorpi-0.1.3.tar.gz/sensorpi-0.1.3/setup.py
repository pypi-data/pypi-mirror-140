# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sensorpi', 'sensorpi.sensors']

package_data = \
{'': ['*']}

install_requires = \
['adafruit-circuitpython-bme280>=2.6,<3.0',
 'adafruit-circuitpython-bmp280>=3.2,<4.0',
 'adafruit-circuitpython-dht>=3.7.1,<4.0.0',
 'adafruit-circuitpython-tsl2591>=1.3.2,<2.0.0',
 'edn_format>=0.7,<0.8',
 'influxdb-client[ciso]>=1.25,<2.0',
 'numpy>=1.22,<2.0',
 'opencv-python-headless==4.5.5.62',
 'pandas>=1.4,<2.0',
 'picamera==1.13']

entry_points = \
{'console_scripts': ['run = sensorpi.__main__:main_with_prompt',
                     'sensorpi = sensorpi.__main__:main_with_prompt']}

setup_kwargs = {
    'name': 'sensorpi',
    'version': '0.1.3',
    'description': 'A Raspberry Pi tool to send multiple sensor data to an influxdb Database',
    'long_description': '* Introduction\nA program to read different sensor\'s data connected to for example a raspberry pi and send it to an influxdb. InfluxDB has to be already installed with a database. Install this on your own. (One way to easily install both grafana and influx is using the =install.sh= script found at https://github.com/Siytek/grafana-influx).\n\n* Installation\nIt might be needed to install the dependencies for =opencv-python-headless= first:\n\n#+begin_src shell eval no\nsudo apt install libaom0 libatlas3-base libavcodec58 libavformat58 libavutil56 libbluray2 libcairo2 libchromaprint1 libcodec2-0.8.1 libcroco3 libdatrie1 libdrm2 libfontconfig1 libgdk-pixbuf2.0-0 libgfortran5 libgme0 libgraphite2-3 libgsm1 libharfbuzz0b libjbig0 libmp3lame0 libmpg123-0 libogg0 libopenjp2-7 libopenmpt0 libopus0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpixman-1-0 librsvg2-2 libshine3 libsnappy1v5 libsoxr0 libspeex1 libssh-gcrypt-4 libswresample3 libswscale5 libthai0 libtheora0 libtiff5 libtwolame0 libva-drm2 libva-x11-2 libva2 libvdpau1 libvorbis0a libvorbisenc2 libvorbisfile3 libvpx5 libwavpack1 libwebp6 libwebpmux3 libx264-155 libx265-165 libxcb-render0 libxcb-shm0 libxfixes3 libxrender1 libxvidcore4 libzvbi0\n#+end_src\n\nInstall via pip:\n#+begin_src shell\npip install sensorpi\n#+end_src\n\nYou can download the repo from github by running\n#+begin_src shell :eval no\ngit clone https://github.com/weidtn/sensorpi.git\n#+end_src\n\nAnd then install with poetry:\n#+begin_src shell\npoetry install\n#+end_src\n\n* Configuration\nAll configuration is done in the config.edn file.\nIf you add a sensor here, it will automatically be read by the program and added to the measurement.\nInfluxDB data also has to be set up in here it defaults to a local installation on the same raspberry pi without any authentication. To use a remote InfluxDB, change the URL in the config file.\n\nThe configuration is written in edn. This works similar to a python dictionary. Keywords and values are separated by whitespace.\nYou have to provide the keywords =:influxdb= and =:sensors= with your data. An example config.edn would look like this:\n#+begin_src clojure :eval no\n;; This is just an example config.edn file, you have to manually change the data.\n{:influxdb {:url "http://localhost:8086"\n            :db "test1"}\n\n :sensors {:cam  ;; name of the sensor\n           {:type "camera" ;; type of the sensor. check supported types\n            :rotate true} ;; some further possible options depending on sensor\n           :ds18b20_1\n           {:type "ds18b20"}\n           :dht11_inside\n           {:type "dht11"\n            :pin 26}\n           "TSL2591 upside down" ;; the sensor names can also just be strings\n           {:type "tsl2591"}\n\n           :bme280\n           {:type "bme280"\n            :address 0x76\n            :protocol "i2c"}\n           :bmp280_0\n           {:type "bmp280"\n            :protocol "spi"\n            :pin "18"}\n           :bmp280_1\n           {:type "bmp280"\n            :protocol "spi"\n            :pin "12"}}}\n#+end_src\n* Usage:\nMake sure to have an InfluxDB v1.8 running and all the sensors connected. Then write a config.edn file with the needed data.\n\nThis will use the config file in the measurement1 folder and save to db as measurement1 every 30 seconds. Measurement and interval are optional and the program will automatically ask for them in the commandline. If no config is given, it will search for a config.edn file in sensorpi\'s folder.\n#+begin_src shell :eval no\nsensorpi -m measurement1 -i 30 -c ./measurement1/config.edn\n#+end_src\n\n* Supported sensors\nCurrently the following sensors are supported. Their implementations can be found in the sensorpi/sensors folder. Feel free to add your own sensors!\n\n- Camera (Integrating histogram)\n- DHT11\n- DS18B20\n- TSL2591\n- BMP280 (I2C, SPI)\n- BME280 (I2C, SPI)\n\nMultiple sensors should work if different addresses (I2C) or pins (SPI) are used.\n\n** Camera\ntype "camera"\n\nThe camera can be used as a sensor. The camera can save an image to a path and integrate the picture\'s histogram. This integral value is then saved to the database if the keyword =:hist= is true. The image can be rotated by 180° (not imporant for histogram). Example camera config:\n\nThe folder where the image should be saved to needs to exist already.\n#+begin_src clojure :eval no\n:sensors {:cam\n          {:type "camera"\n           :rotate true\n           :hist true                                ;; can also be false if you only need the image\n           :save                                     ;; if the :save keyword does not exist, only a histogram is calculated\n            {:path "/home/pi/measurement1/cam.png"   ;; saves image to the folder\n             :timestamp true}}}                      ;; Adds a timestamp to the image before ".png"\n#+end_src\n\nA nice trick is to save the image to =/usr/share/grafana/public/img/= so you can access it from a grafana text panel and little html/js (or maybe just symlink it): https://gist.github.com/weidtn/d1171a896483899b606ec9663925147f\n\n** BMP/BME 280\ntype "bme280" & "bmp280"\n\nYou have to specify a protocol for accessing the sensor and the address (I2C) or CS-Pin (SPI) in your config file:\n#+begin_src clojure :eval no\n:sensors {:bme280\n           {:type "bme280"\n            :protocol "i2c"\n            :address 0x76}\n           :bmp280_0\n           {:type "bmp280"\n            :protocol "spi"\n            :pin "18"}}\n#+end_src\n\n** TSL2591\ntype "tsl5281"\n\nThe TSL2591 sensor has no further options.\n\n** DHT11\ntype "dht11"\n\nYou have to provide the pin of the sensor like this:\n#+begin_src clojure :eval no\n:sensors {:dht11\n          {:type "dht11"\n            :pin 26}}\n#+end_src\n\n** DS18B20\ntype "ds18b20"\n\nThe DS18B20 sensor has no further options:\n#+begin_src clojure :eval no\n:sensors {:DS18B20\n           {:type "ds18b20"}}\n#+end_src\n',
    'author': 'Nikolai Weidt',
    'author_email': 'weidtn@gmail.com',
    'maintainer': 'Nikolai Weidt',
    'maintainer_email': 'weidtn@gmail.com',
    'url': 'https://github.com/weidtn/sensorpi/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
