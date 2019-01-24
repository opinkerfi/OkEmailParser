#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import time
import json
import socket
from mk_livestatus import Socket
from OpinKerfiAutoTask.OkAutoTask import OkAutoTask
from jinja2 import Environment, FileSystemLoader

debug = False

auto_task = OkAutoTask()

def parse_input_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("host_backend_address")
    parser.add_argument("host_backend_id")
    parser.add_argument("host_backend_name")
    parser.add_argument("host_name")
    parser.add_argument("host_address")
    parser.add_argument("ackowledged_by")
    args = parser.parse_args()
    return args

def get_template_environment():
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR),trim_blocks=True)

    return j2_env


def get_livestatus_connection(host_backend_address):
    """ Returns splitted host port data """
    backend = host_backend_address.split(':')
    backend_host = backend[0]
    backend_port = backend[1]
    return { 'backend_host': backend_host ,"backend_port": int(backend_port) }

def get_autotask_mapping(backend_id):
    """ Maps backend_id in thruk to autotask customer id and queue"""

    backends = [
        {'name': "manage.ruv.is",            'backend_id': "d07cd", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'nagios.ksgatt.is',         'backend_id': "9e0c6", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'hortense.skattur.is',      'backend_id': "1f017", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'admin.okhysing.is',        'backend_id': "0dc8e", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'netvik.is1net.net',        'backend_id': "dbc17", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'nagios.okhysing.is',       'backend_id': "20498", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'netvik.netrekstur.okh.is', 'backend_id': "82eea", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" },
        {'name': 'ver-monitor-01.okh.is',    'backend_id': "01d46", 'autotask_id': 34019, 'queue':"Hýsing og netrekstur" }
    ]

    backend_list  = [backend for backend in backends if backend['backend_id'] == backend_id]
    return backend_list[0]



def query_livestatus_host_status(input_hostname, livestatus_socket):

    query = livestatus_socket.hosts.columns(
        'name',
        'address',
        'plugin_output',
        'contacts'
    ).filter('name = ' + input_hostname )
    #).filter('name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    if debug:
        print(query)

    host_acknowledged = query.call()
    return host_acknowledged

def query_livestatus_host_services(input_hostname, livestatus_socket):

    query = livestatus_socket.services.columns(
        'host_name',
        'service_description',
        'state',
        'host_address',
        'plugin_output'
    ).filter('host_name = ' + input_hostname )
   # ).filter('host_name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    if debug:
        print(query)

    services_acknowledged = query.call()
    return services_acknowledged

def _write_to_livestatus(command_string, host_backend_address ):
    #livestatus_instance = livestatus_socket.Livestatus()
    #livestatus_instance.query("COMMAND %s" % command_string)

    socket_info = get_livestatus_connection(host_backend_address)
    #s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    #s.connect((socket_info['backend_host'], socket_info['backend_port']))

    command = "GET hosts\n"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((socket_info['backend_host'], socket_info['backend_port']))
            s.sendall(command.encode())
            data = s.recv(100000000).decode()

    # Write command to socket
    #s.send("GET hosts\n")

    # Important: Close sending direction. That way
    # the other side knows we are finished.
    #s.shutdown(socket.SHUT_WR)

    # Now read the answer
    #answer = s.recv(100000000)
    return data


def ack_host_through_livestatus(ticket, backend, livestatus_socket):
    """ Post Acknowlegdement to livestatus """

    acknowledge_host = livestatus_socket.do_command()

def ack_service_through_livestatus(livestatus_socket, ticket, host_name, acknowledged_by, host_service_statuses):
    """ ACK f. thjonustur """

    #ACKNOWLEDGE_SVC_PROBLEM;<host_name>;<service_description>;<sticky>;<notify>;<persistent>;<author>;<comment>
    #$nl->do(sprintf("COMMAND [%d] ACKNOWLEDGE_SVC_PROBLEM;%s;%s;1;1;1;%s;Email sent to Autotask", time(), $HOSTNAME,
    #                $service->{'service_description'}, $REMOTE_USER ));

    for host_service_status in host_service_statuses:
        timestamp = str(int(time.time()))
        command = "[" + timestamp +  "] ACKNOWLEDGE_SVC_PROBLEM;" + \
            host_name + ";" + host_service_status['description'] + \
        ";1;1;1;" + acknowledged_by + ";" + ticket
        print(command)

    _write_to_livestatus(command, livestatus_socket)


if __name__ == "__main__":
    args = parse_input_arguments()
    backend = get_autotask_mapping(args.host_backend_id)
    socket_info = get_livestatus_connection(args.host_backend_address)
    livestatus_socket = Socket((socket_info['backend_host'], socket_info['backend_port']))

    host_statuses = query_livestatus_host_status(args.host_name, livestatus_socket)
    host_service_statuses = query_livestatus_host_services(args.host_name, livestatus_socket)

    templates = get_template_environment()
    autotask = OkAutoTask()
    autotask_desciption = templates.get_template('autotaskTemplate.j2').render(args=args,
                                                               host_statuses=host_statuses,
                                                               host_service_statuses=host_service_statuses)

    ticket_link = "T1234567.123"
#    status = ack_service_through_livestatus(livestatus_socket, ticket_link, args.host_name, args.ackowledged_by, host_service_statuses)

    command_string = "test"
    status = _write_to_livestatus(command_string, args.host_backend_address )
    print(status)

#    ticket = autotask.create_ticket(
#        title = args.title,
#        description = args.description,
#        queue = backend['queue'],
#        accountID=backend['backend_id']
#    )

#nagios_link = "Beiðni: <a href=\"https://ww4.autotask.net/Mvc/ServiceDesk/TicketDetail.mvc?&ticketId=" + \
#    str(ticket.id) + "\">" + str(ticket.TicketNumber) + "</a>"
#print(nagios_link)
