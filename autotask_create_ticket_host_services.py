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

def get_autotask_mapping(name):
    """ Maps backend_id in thruk to autotask customer id and queue"""

    backends = [
        {
            'name': "manage.ruv.is",
            'backend_id': "d07cd",
            'autotask_id': 667,
            'queue': "Tölvupóstur"
        },{
            'name': 'nagios.ksgatt.is',
            'backend_id': "9e0c6",
            'autotask_id': 4475,
            'queue': "Tölvupóstur"
        },{
            'name': 'hortense.skattur.is',
            'backend_id': "1f017",
            'autotask_id': 385,
            'queue': "Tölvupóstur"
        },{
            'name': 'admin.okhysing.is',
            'backend_id': "0dc8e",
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        },{
            'name': 'netvik.is1net.net',
            'backend_id': "dbc17",
            'autotask_id': 3128,
            'queue': "Tölvupóstur"
        },{
            'name': 'nagios.okhysing.is',
            'backend_id': "20498",
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        },{
            'name': 'netvik.netrekstur.okh.is',
            'backend_id': "82eea",
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        },{
            'name': 'ver-monitor-01.okh.is',
            'backend_id': "01d46",
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        }
    ]

    backend_list = [
        backend for backend in backends if backend['name'] == name]
    return backend_list[0]


def get_autotask_domain_to_customer_mapping(hostname):
    domains = [
        {
            'name': 'matis.local',
            'autotask_id': 996,
            'queue': "Tölvupóstur"
        }, {
            'name': 'landmotun.local',
            'autotask_id': 4527,
            'queue': "Tölvupóstur"
        }, {
            'name': 'okh.is',
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        }, {
            'name': 'okhysing.is',
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        }, {
            'name': 'ok.is',
            'autotask_id': 0,
            'queue': "Tölvupóstur"
        }, {
            'name': 'ksgatt.is',
            'autotask_id': 4475,
            'queue': "Tölvupóstur"
        }, {
            'name': 'ks.is',
            'autotask_id': 4475,
            'queue': "Tölvupóstur"
        }, {
            'name': 'lifland.is',
            'autotask_id': 3463,
            'queue': "Tölvupóstur"
        }, {
            'name': 'vogar.is',
            'autotask_id': 3339,
            'queue': "Tölvupóstur"
        }, {
            'name': 'gjtravel.is',
            'autotask_id': 7789,
            'queue': "Tölvupóstur"
        }, {
            'name': 'askja.is',
            'autotask_id': 4535,
            'queue': "Tölvupóstur"
        }, {
            'name': 'askja.local',
            'autotask_id': 4535,
            'queue': "Tölvupóstur"
        }, {
            'name': 'mainmanager.internal',
            'autotask_id': 676,
            'queue': "Tölvupóstur"
        }
    ]

    # Lookup domain from domains dictinoary and return autotask_id for matching item
    domain_result = [
        domain for domain in domains if domain['name'] in hostname.lower()]
    if domain_result:
        return domain_result[0]
    else:
        return {
            'name': 'okhysing.is',
            'autotask_id': 34019,
            'queue': "Tölvupóstur"
        }  # Opin Kerfi Hysing

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
    backend = get_autotask_mapping(args.host_backend_name)
    socket_info = get_livestatus_connection(args.host_backend_address)
    livestatus_action = LiveStatusAction(args.host_backend_address)

    # Create live status socket from input data
    livestatus_socket = Socket((
        socket_info['backend_host'],
        socket_info['backend_port']
    ))

    # Query for non acknowlegded host issues
    host_statuses = query_livestatus_host_status(
        args.host_name,
        livestatus_socket
    )

    # Query for non acknowlegded service issues
    host_service_statuses = query_livestatus_host_services(
        args.host_name,
        livestatus_socket
    )

    # Generate autotask description text from template
    autotask_rendered_description = templates.get_template('autotaskTemplate.j2').render(
        args=args,
        host_statuses=host_statuses,
        host_service_statuses=host_service_statuses
    )

    # Create ticket if there are host_statues or host_service_statuses
    if len(host_statuses) >= 1 or len(host_service_statuses) >= 1:
        customer = get_autotask_domain_to_customer_mapping(args.host_name)
        ticket = autotask.create_ticket(
            title = "Nagios eftirlit - " + args.host_name ,
            description = autotask_rendered_description,
            queue = customer['queue'],
            accountID = customer['autotask_id']
        )

        # Generate comment from template
        comment = templates.get_template('thrukcommentTemplate.j2').render(ticket=ticket)

    # If there are host statuses we acknowledge and add comment
    if len(host_statuses) >= 1 :
        livestatus_action.ack_host(args.host_name, args.acknowledged_by ,comment)

    # If there are service statuses we acknowledge and add comment
    if len(host_service_statuses)  >= 1 :
        livestatus_action.ack_services(host_service_statuses,args.acknowledged_by,comment)
