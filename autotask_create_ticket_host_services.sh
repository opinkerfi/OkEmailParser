#!/usr/bin/env bash

THIS_SCRIPT=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$THIS_SCRIPT")
TICKET_DATA=$(source ${SCRIPT_DIR}/env/bin/activate && python ${SCRIPT_DIR}/autotask_create_ticket_host_services.py "$@")
echo ${TICKET_DATA}

