#!/usr/bin/env python

import argparse
import os
import time
import json
import sys
from mk_livestatus import Socket
#from CheckMK import SingleSiteConnection
from CheckMK.LiveStatus import *
#import CheckMK
from OpinKerfiAutoTask.OkAutoTask import OkAutoTask
from jinja2 import Environment, FileSystemLoader

def parse_input_arguments():
    """ Parses the input arguments of this script """
    parser = argparse.ArgumentParser()
    parser.add_argument("host_backend_address")
    parser.add_argument("host_backend_id")
    parser.add_argument("host_backend_name")
    parser.add_argument("host_name")
    parser.add_argument("host_address")
    parser.add_argument("acknowledged_by")
    args = parser.parse_args()
    return args


def get_template_environment():
    """ Sets up where to look for jinja templates """
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

    return j2_env


def get_livestatus_connection(host_backend_address):
    """ Returns splitted host port data """
    backend = host_backend_address.split(':')
    backend_host = backend[0]
    backend_port = backend[1]
    return {'backend_host': backend_host, "backend_port": int(backend_port)}

def get_states_mapping(state):
    """ TODO: map numeric stats to warning, critical """
    pass

def get_autotask_mapping(backend_id):
    """ Maps backend_id in thruk to autotask customer id and queue"""

    backends = [
        {
            'name': "manage.ruv.is",
            'backend_id': "d07cd",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'nagios.ksgatt.is',
            'backend_id': "9e0c6",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'hortense.skattur.is',
            'backend_id': "1f017",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'admin.okhysing.is',
            'backend_id': "0dc8e",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'netvik.is1net.net',
            'backend_id': "dbc17",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'nagios.okhysing.is',
            'backend_id': "20498",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'netvik.netrekstur.okh.is',
            'backend_id': "82eea",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        },{
            'name': 'ver-monitor-01.okh.is',
            'backend_id': "01d46",
            'autotask_id': 34019,
            'queue': "Hýsing og netrekstur"
        }
    ]

    backend_list = [
        backend for backend in backends if backend['backend_id'] == backend_id]
    return backend_list[0]


def query_livestatus_host_status(input_hostname, livestatus_socket):

    query = livestatus_socket.hosts.columns(
        'name',
        'address',
        'plugin_output',
        'contacts'
    ).filter('name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    host_acknowledged = query.call()
    return host_acknowledged


def query_livestatus_host_services(input_hostname, livestatus_socket):

    query = livestatus_socket.services.columns(
        'host_name',
        'service_description',
        'state',
        'host_address',
        'plugin_output'
    ).filter('host_name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    services_acknowledged = query.call()
    return services_acknowledged


class LiveStatusAction:

    def __init__(self, host_backend_url):
        self.livestatus_socket = 'tcp:' + host_backend_url

    def command(self, command):
        """ Post a command over single connection. """
        command = "[%s] %s" % (int(time.time()), command)
        # Create the connection
        #conn = lstatus.SingleSiteConnection(self.livestatus_socket)
        conn = SingleSiteConnection(self.livestatus_socket)
        # Run the command the connection
        # TODO: remove results since the command does not return value.
        results = conn.command(command)
        # Return the results
        return results

    def ack_host(self, host_name, acknowledged_by, message):
        """ Helper Function: Acknowledge a host problem with a comment.
        This should be able to to pickup the user name from the session.
        """
        cmd = "ACKNOWLEDGE_HOST_PROBLEM;%(host_name)s;1;1;1;%(acknowledged_by)s;%(message)s\n" % locals()
        self.command( cmd )

    def ack_hosts(self, host_list, acknowledged_by,  message):
        """ Helper Function: Acknowledge a list of host problems with a comment.
        This should be able to pickup the user name from the session in a
        later version. """
        cmd_t = "ACKNOWLEDGE_HOST_PROBLEM;%(host_name)s;1;1;1;%(acknowledged_by)s;%(message)s\n"
        for host_name in host_list:
            self.command( cmd_t % locals() )

    def ack_service(self, service, acknowledged_by, message):
        """ Helper Function: Acknowledge a service problem with a comment. """
        self.command( "ACKNOWLEDGE_SVC_PROBLEM;%(service)s;1;1;1;%(acknowledged_by)s;%(message)s\n" % locals() )

    def ack_services(self, service_list, acknowledged_by, message):
        """ Helper Function: Acknowledge a list service problems with a comment. """
        for service in service_list:
            self.command(
                "ACKNOWLEDGE_SVC_PROBLEM;" + \
                service['host_name'] + ";" + \
                service['description'] + ";" + \
                "1;1;1;" + \
                acknowledged_by + ";" + \
                message + "\n"
            )

if __name__ == "__main__":
    args = parse_input_arguments()
    templates = get_template_environment()
    autotask = OkAutoTask()
    backend = get_autotask_mapping(args.host_backend_id)
    socket_info = get_livestatus_connection(args.host_backend_address)
    livestatus_action = LiveStatusAction(args.host_backend_address)

    livestatus_socket = Socket((
        socket_info['backend_host'],
        socket_info['backend_port']
    ))

    host_statuses = query_livestatus_host_status(
        args.host_name,
        livestatus_socket
    )

    host_service_statuses = query_livestatus_host_services(
        args.host_name,
        livestatus_socket
    )

    autotask_rendered_description = templates.get_template('autotaskTemplate.j2').render(
        args=args,
        host_statuses=host_statuses,
        host_service_statuses=host_service_statuses
    )

    ticket_link = "Sent via Autotask api - ticket creation failed."
    if len(host_statuses) >= 1 or len(host_service_statuses) >= 1:
        ticket = autotask.create_ticket(
            title = "Nagios Eftirlit - " + args.host_name ,
            description = autotask_rendered_description,
            queue=backend['queue'],
            accountID=backend['autotask_id']
        )

        ticket_link = "Beiðni: https://ww4.autotask.net/Mvc/ServiceDesk/TicketDetail.mvc?&ticketId=" + \
        str(ticket.id) + " - " + str(ticket.TicketNumber)

    if len(host_statuses) >= 1 :
        livestatus_action.ack_host(args.host_name, args.acknowledged_by ,ticket_link)

    if len(host_service_statuses)  >= 1 :
        livestatus_action.ack_services(host_service_statuses,args.acknowledged_by,ticket_link)
