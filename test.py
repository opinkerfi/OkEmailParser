from OpinKerfiAutoTask.OkAutoTask import OkAutoTask


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
