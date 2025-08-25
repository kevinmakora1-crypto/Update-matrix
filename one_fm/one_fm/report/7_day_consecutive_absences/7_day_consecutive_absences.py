from frappe import _

from one_fm.utils import get_consecutive_absences_data

def execute(filters=None):
    columns = get_columns()
    data = get_consecutive_absences_data(filters)
    return columns, data

def get_columns():
    return [
        _("Employee") + ":Link/Employee:250",
        _("Employee Name") + ":Data:250",
        _("Department") + ":Data:250",
        _("Start Date") + ":Date:150",
        _("End Date") + ":Date:150",
        _("No of Days") + ":Data:150",
    ]