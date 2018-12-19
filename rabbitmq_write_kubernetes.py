#!/usr/bin/python3

#
# Relies on vault sidecar to provide dynamic credentials
# renewal of credentials is transparent to application
# Using periodic token
#

import requests
import pika
from os import environ
#from rabbitmq_helpers_kubernetes import *
from time import sleep
import json

rabbitmq_host = environ['RABBIT_HOST']
dynamic_secret_path = '/usr/share/secrets/dynamic-secret'

if __name__ == '__main__':
    with open(dynamic_secret_path, 'r') as dynamic_secret:
        secrets = json.load(dynamic_secret)

    un = secrets['username']
    pw = secrets['password']

    count = 0

    while 1:
        credentials = pika.PlainCredentials(un, pw)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, credentials=credentials, port='5672', virtual_host='/'))

        channel = connection.channel()

        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='', routing_key='hello', body='Message number %d' % count)

        print(" [x] Sent %d'" % count)
        connection.close()
        count += 1
        sleep(300)
