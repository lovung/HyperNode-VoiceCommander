#!/usr/bin/env python
import pika
import ssl

ssl_options=dict(
        ssl_version=ssl.PROTOCOL_TLSv1_2,
        ca_certs="./cacert.pem",
        keyfile="./key.pem",
        certfile="./cert.pem",
        cert_reqs=ssl.CERT_REQUIRED)
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

class hyperAMQPClient(object):
    def __init__(self, host='vulong1602.ddns.net',
                 port=5671,
                 ssl_options = ssl_options):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,
                                            port=port,
                                            heartbeat_interval = 0,
                                            ssl = True,
                                            ssl_options = ssl_options))
        self.channel = self.connection.channel()
    def declareTopic(topic):
        self.channel.queue_declare(queue=topic)

    def topicGenerator(mac_address, model, task, method):
        if len(mac_address) != 12:
            return -1
        if len(topic) != 4:
            return -1
        if len(task) <= 0:
            return -1
        if method != 'pub' and method != 'sub':
            return -1
        key = 0
        for c in mac_address:
            c_int = int(c, 16)
            key += c_int
        key *= int(mac_address[10],16)
        key += int(mac_address[11],16)
        print("key = %x" % key)
        if len(key) == 1:
            strKey = mac_address[8] + mac_address[9] + "00" + hex(key)[2:]
        else if len(key) == 2:
            strKey = mac_address[8] + mac_address[9] + "0" + hex(key)[2:]
        else if len(key) == 3:
            strKey = mac_address[8] + mac_address[9] + hex(key)[2:]

        return strKey + '.' + topic + '.' + task + '.' + method


    def publishMessage(routing_key, message):
        self.channel.basic_publish(exchange='',
                      routing_key=routing_key,
                      body=message)

    def startSubcribe(received_callback = callback, topic):
        self.channel.basic_consume(callback,
                              queue=topic,
                              no_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def closeConnection():
        self.connection.close()
