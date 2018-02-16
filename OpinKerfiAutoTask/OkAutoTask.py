import atws
import atws.monkeypatch.attributes
import credentials as config

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
