import datetime
from OpinKerfiAutoTask.OkAutoTask import OkAutoTask

# Skoða https://atws.readthedocs.io/

def get_employee(employee):
    """Dæmi um upplýsingar frá employee objectinu"""
    print("Nafn: " + employee.LastName)
    print("Netfang: " + employee.Email)
    print("Símanúmer: " + employee.MobilePhone)

# Hér byrjar test kóði sem notar OkAutoTask wrapper klassa
auto_task = OkAutoTask()
employees = auto_task.get_employee_by_email('samuel@ok.is')

for employee in employees:
    get_employee(employee)

# Fletta upp beiðni
tickets = auto_task.get_ticket_by_number('T20190308.0009')
for ticket in tickets:
    print(ticket)

# Stofna miða
now = datetime.datetime.now()
my_ticket = auto_task.create_ticket(
    title="Prufu Ticket frá Python API: " + str(now.hour) + str(now.minute),
    description="Þessi beiðni var útbúin kl: " + str(now),
    queue="Hýsing og netrekstur",
    accountID=0,
    ticketSource='Monitoring Alert',
    ticketType='Alert',
    ticketCategory='AEM Alert'
)

# Fletta upp nýstofnuðum ticket my_ticket
# Todo: Breyta þannig að skilað sé einni niðurstöðu af gerðini ticket en ekki enumeration obj. af ticketum.
tickets = auto_task.get_ticket_by_number(my_ticket.TicketNumber)
for ticket in tickets:
    print(ticket)
