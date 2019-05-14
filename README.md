# Linkproof-to-Alteon-Migration

## Table Of Contents ###
- [Description](#description )
- [How To Use](#how-to-use )
  * [Using Docker container](#using-docker-container)
  * [Running derectly on a server](#running-derectly-on-a-server)

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
# docker build -t lp_mig . && docker run -dit -p 8080:3011 --name lp_mig --restart on-failure lp_mig
```
Then access the WebUI using the IP and port of the server (in this example port 8080)

### Running derectly on a server ###
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

Run flask instance <br>
For example : 
```
# python -m flask run --host=0.0.0.0 -p 3000
```
And access the WebUI using the IP and port of the container (in this example port 3000)
