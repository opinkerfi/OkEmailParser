#!/usr/bin/perl -w
#
use strict;
use warnings;
use lib "/usr/share/thruk/lib";
use Monitoring::Livestatus;
use Data::Dumper;
use MIME::Lite;
use JSON;
use feature qw/ say /;
$Data::Dumper::Sortkeys = 1;

#usage:
#perl autotask_create_ticket_host_services_v4.pl 94.142.159.5:6557 33 ver-monitor-01.okh.is ts-win-2012 94.142.159.11

my $HOSTBACKENDADDRESS = $ARGV[0];
my $HOSTBACKENDID      = $ARGV[1];
my $HOSTBACKENDNAME    = $ARGV[2];
my $HOSTNAME           = $ARGV[3];
my $HOSTADDRESS        = $ARGV[4];
my $REMOTE_USER        = $ARGV[5];

my $body_text = "The following problems were acknowledged:\n\n";
$body_text .= "Host: $HOSTNAME\n";
$body_text .= "Backend/Site: $HOSTBACKENDNAME\n";
$body_text .= "Acknowledged by: $REMOTE_USER\n";
$body_text .= "-----------------------------------------------------------------------------------\n";


my $nl = Monitoring::Livestatus->new(
                                     peer             => $HOSTBACKENDADDRESS,
                                     timeout          => 5,
                                     keepalive        => 1,
);

my $hosts = $nl->selectall_arrayref("GET hosts\nColumns: name address plugin_output contacts\nFilter: name = $HOSTNAME\nFilter: state != 0\nFilter: acknowledged != 1", { Slice => {} });
my $services = $nl->selectall_arrayref("GET services\nColumns: host_name service_description state host_address plugin_output\nFilter: host_name = $HOSTNAME\nFilter: state != 0\nFilter: acknowledged != 1", { Slice => {} });

print Dumper($hosts);
print Dumper($services);

my $hostproblems = scalar @{$hosts};
my $serviceproblems = scalar @{$services};
my $problems_total = $hostproblems + $serviceproblems;
my $subject = sprintf('Nagios eftirlit - %s', $HOSTNAME);

for my $host (@{$hosts}) {
    # ACKNOWLEDGE_HOST_PROBLEM;<host_name>;<sticky>;<notify>;<persistent>;<author>;<comment>
    $nl->do(sprintf("COMMAND [%d] ACKNOWLEDGE_HOST_PROBLEM;%s;1;1;1;1;%s;Email sent to Autotask", time(), $HOSTNAME, $REMOTE_USER));
    # Body Text message
    $body_text .= sprintf("Host Problem: %s\n", $host->{'plugin_output'});
    $body_text .= sprintf("Host Contacts: %s\n", $host->{'contacts'});
    $body_text .= "-----------------------------------------------------------------------------------\n\n";
}

    $body_text .= " Service Problems                                                                  \n\n";
    $body_text .= "-----------------------------------------------------------------------------------\n\n";

for my $service (@{$services}) {
    # Body Text message
    $body_text .= sprintf("Service: %s\n", $service->{'service_description'}); 
    $body_text .= sprintf("Status Information: %s\n", $service->{'plugin_output'});
    $body_text .= sprintf("State: %s\n", $service->{'state'});
    $body_text .= "-----------------------------------------------------------------------------------\n\n";    
    # Send Ack service command to livestatus socket
    #ACKNOWLEDGE_SVC_PROBLEM;<host_name>;<service_description>;<sticky>;<notify>;<persistent>;<author>;<comment>
    $nl->do(sprintf("COMMAND [%d] ACKNOWLEDGE_SVC_PROBLEM;%s;%s;1;1;1;%s;Email sent to Autotask", time(), $HOSTNAME, $service->{'service_description'}, $REMOTE_USER ));
}

# Close HTML Table
$body_text .= "For more information regarding services on this host, click the link below:\n";
$body_text .= "https://$HOSTBACKENDNAME/thruk/#cgi-bin/status.cgi?hidesearch=2&s0_op=%7E&s0_type=search&add_default_service_filter=1&s0_value=$HOSTNAME";
$body_text .= "\n\nMore info for host on Sysvik:\n";
$body_text .= "https://www.sysvik.com/go/ip=$HOSTNAME";
$body_text .= "\n\nIf you can't find the hostname on Sysvik, try searching for ip address instead:\n";
$body_text .= "https://www.sysvik.com/go/$HOSTADDRESS";

################################################
#	Send to Autotask
################################################
my $autotask_ticket_link = `/opt/code/OkEmailParser/nagios_to_autoask.sh $subject $body_text`;

