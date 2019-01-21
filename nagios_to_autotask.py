#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from OpinKerfiAutoTask.OkAutoTask import OkAutoTask
auto_task = OkAutoTask()

parser = argparse.ArgumentParser()
parser.add_argument("title")
parser.add_argument("description")
args = parser.parse_args()
print(args.title)
print(args.description)

ticket = auto_task.create_ticket(
    title = args.title,
    description = args.description,
    queue = "Hýsing og netrekstur",
    accountID=34019
)

nagios_link = "Beiðni: <a href=\"https://ww4.autotask.net/Mvc/ServiceDesk/TicketDetail.mvc?&ticketId=" + \
    str(ticket.id) + "\">" + str(ticket.TicketNumber) + "</a>"
print(nagios_link)
