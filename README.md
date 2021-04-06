# Linkproof-to-Alteon-Migration

## Table Of Contents ###
- [Description](#description )
- [How To Use](#how-to-use )
  * [Using Docker container](#using-docker-container)
  * [Running directly on a server](#running-directly-on-a-server)

## Description ##
The following script is used to migrate Linkproof Versions 6.12 or 6.13 configuration to Alteon configuration.
Supported Alteon versions are 31.0 and above (not tested on older versions)

## How To Use ##

### Using Docker container ###
Download all git content, Build and Run the container

For example :
```
# git clone https://github.com/Radware/Linkproof-to-Alteon-Migration.git
# cd Linkproof-to-Alteon-Migration
# docker build -t lp_mig . && docker run -dit -p 8080:3000 --name lp_mig --restart on-failure lp_mig
```
Then access the WebUI using the IP and port of the server (in this example port 8080)

### Running directly on a server ###
In order to use the script make sure you have installed python2.7
The script uses the following modules:
* click
* Flask
* itsdangerous
* Jinja2
* MarkupSafe
* py2-ipaddress
* uWSGI
* Werkzeug

Download all git content, install required modules and run flask instance<br>
For example : 
```
# git clone https://github.com/Radware/Linkproof-to-Alteon-Migration.git
# pip install -r requirements.txt
# FLASK_APP=browse.py
# python -m flask run --host=0.0.0.0 -p 3000
```
And access the WebUI using the IP and Flasks port  (in this example port 3000)
