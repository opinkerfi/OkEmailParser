#!/usr/bin/env bash

THIS_SCRIPT=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$THIS_SCRIPT")
TICKET_DATA=$(source ${SCRIPT_DIR}/env/bin/activate && python ${SCRIPT_DIR}/autotask_create_ticket_host_services.py $1 $2 $3 $4 $5 $6)
echo "$(date) Params: $@" >> /var/log/nagios/thruk_to_autotask.log
echo ${TICKET_DATA}

