#!/usr/bin/env bash 

THIS_SCRIPT=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$THIS_SCRIPT")
TICKET_DATA=$(source ${SCRIPT_DIR}/venv/bin/activate && python ${SCRIPT_DIR}/nagios_to_autotask.py "$@")
echo ${TICKET_DATA}

