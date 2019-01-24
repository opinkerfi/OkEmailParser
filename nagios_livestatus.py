#!/usr/bin/env python

from mk_livestatus import Socket
import json

debug = 0

input_hostname = 'BHS-DVR-02.net.bhs.is'

backend = "localhost:6557"
backend = backend.split(':')
print(backend)
backend_host = backend[0]
backend_port = backend[1]
print("Backend host : " + backend_host)
print("Backend port : " + backend_port)


livestatus_socket = Socket(('localhost', 6557))
#livestatus_socket = Socket('/var/spool/nagios/cmd/livestatus')

def query_host_status(input_hostname):

    query = livestatus_socket.hosts.columns(
        'name',
        'address',
        'plugin_output',
        'contacts'
    ).filter('name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    if debug:
        print(query)

    host_acknowledged = query.call()
    print(host_acknowledged)

def query_host_services(input_hostname):

    query = livestatus_socket.services.columns(
        'host_name',
        'service_description',
        'state',
        'host_address',
        'plugin_output'
    #).filter('host_name = ' + input_hostname )
    ).filter('host_name = ' + input_hostname ).filter('state != 0').filter('acknowledged != 1')

    if debug:
        print(query)

    services_acknowledged = query.call()
    print(services_acknowledged)





#my $hosts = $nl->selectall_arrayref("GET hosts\nColumns: name address plugin_output contacts\nFilter: name = $HOSTNAME\nFilter: state != 0\nFilter: acknowledged != 1", { Slice => {} });
#my $services = $nl->selectall_arrayref("GET services\nColumns: host_name service_description state host_address plugin_output\nFilter: host_name = $HOSTNAME\nFilter: state != 0\nFilter: acknowledged != 1", { Slice => {} });


status = query_host_status(input_hostname)
print(status)

status = query_host_services(input_hostname)
print(status)
