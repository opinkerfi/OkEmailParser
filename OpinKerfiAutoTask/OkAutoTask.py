#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atws
import atws.monkeypatch.attributes
import credentials as config
import datetime

class OkAutoTask(object):
    """Wrapper class fyrir AutoTask"""

    def __init__(self):
        """Init fall"""
        self.at = atws.connect(
            username=config.autoTaskCredentials['username'],
            password=config.autoTaskCredentials['password']
        )

    def get_ticket_by_number(self, ticketnumber):
        """Sækja beiðnir eftir T00000.111 númeri"""
        try:
            query = atws.Query('Ticket')
            query.WHERE('TicketNumber', query.Equals, ticketnumber)
            return self.at.query(query)
        except ValueError:
            print("Sláðu inn ticketnúmer")

    def get_employee_by_email(self, email):
        """Sækja starfsmann eftir netfangi"""
        try:
            query = atws.Query('Resource')
            query.WHERE('ResourceType', query.Equals, 'Employee')
            query.AND('Active', query.Equals, True)
            query.AND('Email', query.Equals, email)
            return self.at.query(query)
        except ValueError:
            print("Sláðu inn netfang")

    def create_ticket(self, title, description, queue, accountID=0):
        now = datetime.datetime.now()
        ticket = self.at.new('Ticket')
        # Gildi sem við ætlum að bæta við.
        ticket.QueueID = self.at.picklist['Ticket']['QueueID'][queue]
        ticket.Title = title
        ticket.Description = description

        # Restin eru lágmarksreitir sem þarf að fylla út.
        ticket.AccountID = accountID  # Opin Kerfi = 0
        ticket.DueDateTime = str(now)
        ticket.Status = self.at.picklist['Ticket']['Status']['New']
        ticket.Priority = self.at.picklist['Ticket']['Priority']['Medium']
        ticket.Source = self.at.picklist['Ticket']['Source']['Monitoring Alert']
        ticket.create()
        return ticket
