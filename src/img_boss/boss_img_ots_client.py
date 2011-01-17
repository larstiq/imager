#!/usr/bin/python
#~ Copyright (C) 2011 Nokia Corporation and/or its subsidiary(-ies).
#~ Contact: Islam Amer <islam.amer@nokia.com>
#~ This program is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.

#~ This program is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.

#~ You should have received a copy of the GNU General Public License
#~ along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Depends on:  ruote-amqp-pyclient, json
# http://download.opensuse.org/repositories/Maemo:/MeeGo-Infra/

import RuoteAMQP
try:
     import simplejson as json
except ImportError:
     import json
import sys
import os
import io
from uuid import uuid1
from optparse import OptionParser
import ConfigParser

defaultconf = """[boss]
amqp_host = 127.0.0.1:5672
amqp_user = boss
amqp_pwd = boss
amqp_vhost = boss

ots_server_url = http://OTS_URL_HERE
default_device_group = OTS_DEVICE_GROUP
default_sw_product = SOFTWARE_PRODUCT
"""


# Image URL, Device Group, Software Product, Email Address

def submit(ks, arch, imgtype, device, sw_product, email): 
    # Specify a minimal OTS process definition
    
    process = """
            Ruote.process_definition :name => 'build_and_test' do
              sequence do
                build_ks 
                _if :test => '${f:status} != SUCCESS' do
                    notify :template => 'kickstart_failed', :subject => '[BOSS] Kickstart validation failed'
                    cancel_process
                end
                build_image
                _if :test => '${f:status} != SUCCESS' do
                    notify :template => 'image_failed', :subject => '[BOSS] Image %s creation failed'
                    cancel_process
                end
                notify :template => 'image_created', :subject => '[BOSS] Image %s creation succeeded'
                test_image
              end
            end
          """ % ( ks , ks)
    fields= {
      "prefix": "custom",
      "name": "%s" % ks,
      "release": "daily-custom",
      "status": "SUCCESS",
      "arch": arch,
      "type": imgtype,
      "kickstart" : open(ks).read(),
	    "server" : config.get('boss', 'ots_server_url'), 
	    "devicegroup" : 'devicegroup:' + device,
	    "product" : sw_product,
	    "email" : [email],
            }
    print "Launching image build and test run ... "
    launcher = RuoteAMQP.Launcher(amqp_host=amqp_host, amqp_user=amqp_user,
                              amqp_pass=amqp_pass, amqp_vhost=amqp_vhost)

    launcher.launch(process, fields)
        

if __name__ == '__main__':
    import sys
    
    usage="usage: %prog -e|--email <author@email> KSURL"
    description = """
%prog Sends a image to OBS for testing. 
"""
    parser = OptionParser(usage=usage, description=description)

    parser.add_option("-t", "--type", dest="imgtype", action="store", 
                      help="Image type")
    parser.add_option("-a", "--arch", dest="arch", action="store", 
                      help="Image arch")
    parser.add_option("-e", "--email", dest="email", action="store", 
                      help="Author email")
    parser.add_option("-d", "--device", dest="device", action="store", 
                      help="OTS Device Group")
    parser.add_option("-c", "--conf", dest="conf", action="store", 
                      help="alternate configuration file")
    parser.add_option("-H", "--host", dest="amqp_host", action="store", 
                      help="BOSS AMQP host")
    parser.add_option("-u", "--user", dest="amqp_user", action="store", 
                      help="BOSS AMQP user")
    parser.add_option("-p", "--pass", dest="amqp_pwd", action="store", 
                      help="BOSS AMQP password")
    parser.add_option("-v", "--vhost", dest="amqp_vhost", action="store", 
                      help="BOSS AMQP vhost")
    (options, args) = parser.parse_args()

    if not options.email:
        print "Email is currently the only feedback mechanism. Define email with --email."
        exit()

    if len(args) != 1:
       print usage
       exit()

    ks = args[0]

    if options.amqp_host and options.amqp_user and options.amqp_pwd and options.amqp_vhost:
        if options.conf:
            print "Don't specify both config file and connection settings at the same time!"
            sys.exit(1)
        amqp_host = options.amqp_host
        amqp_user = options.amqp_user
        amqp_pass = options.amqp_pwd
        amqp_vhost = options.amqp_vhost
    else:
        try:
            conf = open(options.conf)
        except:
            # Fallback
            print "Using default configuration.."
            conf = io.BytesIO(defaultconf)
        
        config = ConfigParser.ConfigParser()
        config.readfp(conf)
        conf.close
        
        amqp_host = config.get('boss', 'amqp_host')
        amqp_user = config.get('boss', 'amqp_user')
        amqp_pass = config.get('boss', 'amqp_pwd')
        amqp_vhost = config.get('boss', 'amqp_vhost')

        if not options.device:
	    options.device = config.get('boss', 'default_device_group')

	product = config.get('boss', 'default_sw_product')

	submit(ks, options.arch, options.imgtype, options.device, product, options.email)
