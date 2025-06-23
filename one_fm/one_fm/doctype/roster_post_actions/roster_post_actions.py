# Copyright (c) 2021, omar jaber and contributors
# For license information, please see license.txt

from collections import Counter



import frappe
from frappe import _
from collections import defaultdict
from frappe.model.document import Document
from frappe.utils import nowdate, add_to_date, cstr, cint, getdate, get_link_to_form
from one_fm.processor import sendemail
from frappe.permissions import get_doctype_roles
from one_fm.one_fm.page.roster.roster import get_current_user_details

class RosterPostActions(Document):

	def autoname(self):
		self.name = f"{self.start_date}|{self.end_date}|{self.action_type}|{self.supervisor}"

	def after_insert(self):
		# send notification to supervisor
		user_id = frappe.db.get_value("Employee", self.supervisor, ["user_id"])
		if user_id:
			link = get_link_to_form(self.doctype, self.name)
			subject = _("New Action to {action_type}.".format(action_type=self.action_type))
			message = _("""
				You have been issued a Roster Post Action.<br>
				Please review the Post Type for the specified date in the roster, take necessary actions and update the status.<br>
				Link: {link}""".format(link=link))
			sendemail([user_id], subject=subject, message=message, reference_doctype=self.doctype, reference_name=self.name)




@frappe.whitelist()
def get_permission_query_conditions(user):
	"""
		Method used to set the permission to get the list of docs (Example: list view query)
		Called from the permission_query_conditions of hooks for the DocType Roster Employee Actions
		args:
			user: name of User object or current user
		return conditions query
	"""
	if not user: user = frappe.session.user

	if user == "Administrator":
		return ""

	# Fetch all the roles associated with the current user
	user_roles = frappe.get_roles(user)

	if "System Manager" in user_roles:
		return ""
	if "Operation Admin" in user_roles:
		return ""

	# Get roles allowed to Roster Employee Actions doctype
	doctype_roles = get_doctype_roles('Roster Employee Actions')
	# If doctype roles is in user roles, then user permitted
	role_exist = [role in doctype_roles for role in user_roles]

	if role_exist and len(role_exist) > 0 and True in role_exist:
		employee = frappe.get_value("Employee", {"user_id": user}, ["name"])
		if "Shift Supervisor" in user_roles or "Site Supervisor" in user_roles:
			return '(`tabRoster Post Actions`.`supervisor`="{employee}" or `tabRoster Post Actions`.`site_supervisor`="{employee}")'.format(employee = employee)

	return ""

def create():
	frappe.enqueue(create_roster_post_actions, is_async=True, queue='long')

def create_roster_post_actions():
    """
    This function creates a Roster Post Actions document that issues actions to supervisors to fill post types that are not filled for a given date range.
    """
    # clear existing

    op_shift = frappe.db.sql(f"""
    	SELECT oss.supervisor, sh.name FROM `tabOperations Shift` sh
        JOIN `tabOperations Shift Supervisor` oss ON oss.parent = sh.name
        WHERE
        sh.status='Active'
    """, as_dict=1)
    
    shift_dict = {}
    for item in op_shift:
        if item.supervisor in shift_dict.keys():
            shift_dict[item.supervisor].append(item.name)
        else:
            shift_dict[item.supervisor] = [item.name]

    # start date to be from tomorrow
    start_date = add_to_date(cstr(getdate()), days=1)
    # end date to be 14 days after start date
    end_date = add_to_date(start_date, days=14)


    operations_roles_not_filled_set = set()
    operations_roles_over_filled_set = set()

    list_of_dict_of_operations_roles_not_filled = []
    list_of_dict_of_operations_roles_over_filled = []


    # Fetch post schedules in the date range that are active
    post_schedules = frappe.db.sql(f"""
		SELECT ps.name, ps.date, ps.shift, ps.operations_role, ps.post
        FROM `tabPost Schedule` ps
        JOIN `tabOperations Site` os ON ps.site=os.name
        JOIN `tabOperations Post` op ON ps.post=op.name
        JOIN `tabOperations Role` opr ON ps.operations_role=opr.name
        JOIN `tabProject` pr ON opr.project=pr.name
          WHERE
        ps.post_status='Planned' AND os.status='Active'
        AND op.status='Active' AND opr.status='Active'
        AND pr.is_active='Yes'
        AND ps.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date ASC
    """, as_dict=1)


    # Fetch employee schedules for employees who are working
    employee_schedules = frappe.db.get_list("Employee Schedule", {'date': ['between', (start_date, end_date)], 'employee_availability': 'Working'}, ["date", "shift", "operations_role"], order_by="date asc")

    post_counts = Counter((ps["date"], ps["operations_role"], ps["shift"]) for ps in post_schedules)
    employee_counts = Counter((es["date"], es["operations_role"], es["shift"]) for es in employee_schedules)

    for ps in post_schedules:
        # if there is not any employee schedule that matches the post schedule for the specified date, add to post types not filled
        if not any(es.date == ps.date and es.shift == ps.shift and es.operations_role == ps.operations_role for es in employee_schedules):
            if ps.operations_role:
                operations_roles_not_filled_set.add(ps.operations_role)
                list_of_dict_of_operations_roles_not_filled.append(ps)

    for key, emp_count in employee_counts.items():
        post_count = post_counts.get(key, 0)  # Default to 0 if no post schedule exists

        if emp_count > post_count:
            date, role, shift = key
            operations_roles_over_filled_set.add(role)

            list_of_dict_of_operations_roles_over_filled.append({
                "date": date,
                "shift": shift,
                "operations_role": role,
                "quantity": emp_count - post_count
            })

    # Convert set to tuple for passing it in the sql query as a parameter
    operations_roles_not_filled = tuple(operations_roles_not_filled_set)
    operations_roles_over_filled = tuple(operations_roles_over_filled_set)

    if not operations_roles_not_filled and not operations_roles_over_filled:
        return

    #Fetch supervisor and post types in his/her shift
    operations_roles = operations_roles_not_filled + operations_roles_over_filled

    result = frappe.db.sql(f"""
        SELECT sv.employee, GROUP_CONCAT(DISTINCT ps.operations_role),
            sh.site
        FROM `tabPost Schedule` ps
        JOIN `tabOperations Shift` sh ON sh.name = ps.shift
        JOIN `tabOperations Shift Supervisor` oss ON oss.parent = ps.shift
        JOIN `tabEmployee` sv ON oss.supervisor = sv.employee
        WHERE ps.operations_role IN ({', '.join(['%s'] * len(operations_roles))})
        AND sh.status = 'Active' AND sv.status = 'Active'
        GROUP BY sv.employee
    """, operations_roles)
    

    # For each supervisor, create post actions to fill post type specifying the post types not filled
    for res in result:
        try:
            supervisor = res[0]
            site = frappe.get_value("Operations Site", res[2], 'account_supervisor')
            operations_roles = res[1].split(",")

            not_filled_dict = defaultdict(int)
            overfilled_dict = defaultdict(int)

            for val in list_of_dict_of_operations_roles_not_filled:
                if val["operations_role"] in operations_roles and val["shift"] in shift_dict[supervisor]:
                    key = (val["date"], val["shift"], val["operations_role"])
                    not_filled_dict[key] += 1

            for val in list_of_dict_of_operations_roles_over_filled:
                if val["operations_role"] in operations_roles and val["shift"] in shift_dict[supervisor]:
                    key = (val["date"], val["shift"], val["operations_role"])
                    overfilled_dict[key] += val["quantity"]

            if not_filled_dict or overfilled_dict:
                roster_post_actions_doc = frappe.new_doc("Roster Post Actions")
                roster_post_actions_doc.start_date = start_date
                roster_post_actions_doc.end_date = end_date
                roster_post_actions_doc.status = "Pending"
                roster_post_actions_doc.action_type = "Fill Post Type"
                roster_post_actions_doc.supervisor = supervisor
                roster_post_actions_doc.site_supervisor = site

                for (date, shift, operations_role), quantity in not_filled_dict.items():
                    roster_post_actions_doc.append('operations_roles_not_filled', {
                        'operations_role': operations_role,
                        "operations_shift": shift,
                        "date": date,
                        "quantity": quantity
                    })

                for (date, shift, operations_role), quantity in overfilled_dict.items():
                    roster_post_actions_doc.append('overfilled_posts', {
                        'operations_role': operations_role,
                        "operations_shift": shift,
                        "date": date,
                        "quantity": quantity
                    })


                roster_post_actions_doc.save()
                frappe.db.commit()
        except:
            frappe.log_error(frappe.get_traceback(), "Error while creating post actions")

@frappe.whitelist()
def get_overfilled_underfilled_posts():
    """ Get the roster post action data for the next 2 weeks"""
    user, user_roles, user_employee = get_current_user_details()

    if not user_employee:
        frappe.throw("No employee record linked to current user")
    # start date to be from tomorrow
    start_date = add_to_date(cstr(getdate()), days=1)
    # end date to be 14 days after start date
    end_date = add_to_date(start_date, days=15)
    shifts = get_applicable_shifts(user_employee.get('name'),user_roles)
    if not shifts:
        return {
            "under_filled": f"""<div class='dialog-box' style='padding: 20px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; text-align: center;'>
                            <h4 style='margin: 0; color: #343a40;'>No Shifts found for User {frappe.session.user}</h4>
                            </div>""",
            "over_filled": f"""<div class='dialog-box' style='padding: 20px; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; text-align: center;'>
                            <h4 style='margin: 0; color: #343a40;'>No Shifts found for User {frappe.session.user}</h4>
                            </div>"""
        }


        # frappe.throw("No shifts found")
    shift_tuple = tuple(shifts)
    shifts_sub_query = f" AND ps.shift in {shift_tuple}" if len(shift_tuple) > 1 else f" AND ps.shift = '{shift_tuple[0]}'"
    # Fetch post schedules in the date range that are active
    post_schedules = frappe.db.sql(f"""
		SELECT ps.name, ps.date, ps.shift, ps.operations_role, ps.post
        FROM `tabPost Schedule` ps
        JOIN `tabOperations Site` os ON ps.site=os.name
        JOIN `tabOperations Post` op ON ps.post=op.name
        JOIN `tabOperations Role` opr ON ps.operations_role=opr.name
        JOIN `tabProject` pr ON opr.project=pr.name
          WHERE
        ps.post_status='Planned' AND os.status='Active'
        AND op.status='Active' AND opr.status='Active'
        AND pr.is_active='Yes' {shifts_sub_query}
        AND ps.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY date ASC
    """, as_dict=1)


    # Fetch employee schedules for employees who are working
    employee_schedules = frappe.db.get_all("Employee Schedule", {'shift':['IN',shift_tuple],'date': ['between', (start_date, end_date)], 'employee_availability': 'Working'}, ["date", "shift", "operations_role"], order_by="date asc")
    roles_not_filled = set()
    roles_over_filled_set = set()
    list_of_dict_of_operations_roles_not_filled = []
    list_of_dict_of_operations_roles_over_filled = []
    post_counts = Counter((ps["date"], ps["operations_role"], ps["shift"]) for ps in post_schedules)
    employee_counts = Counter((es["date"], es["operations_role"], es["shift"]) for es in employee_schedules)
    # Create a set of tuples (date, shift, operations_role) from employee_schedules for O(1) lookup

    employee_schedule_set = {(es["date"], es["shift"], es["operations_role"]) for es in employee_schedules}
    # First check for unfilled positions
    for ps in post_schedules:
        if ps.operations_role and (ps.date, ps.shift, ps.operations_role) not in employee_schedule_set:
            roles_not_filled.add(ps.operations_role)
            list_of_dict_of_operations_roles_not_filled.append(ps)

    # Then check for overfilled positions separately
    post_schedule_dict = {(ps["date"], ps["operations_role"], ps["shift"]): ps for ps in post_schedules}
    for key, emp_count in employee_counts.items():
        post_count = post_counts.get(key, 0)
        if emp_count > post_count:
            matching_ps = post_schedule_dict.get(key)
            if matching_ps:
                roles_over_filled_set.add(key[1])
                list_of_dict_of_operations_roles_over_filled.append({
                    "name": matching_ps["name"],
                    "date": key[0],
                    "shift": key[2],
                    "operations_role": key[1],
                    "post": matching_ps["post"],
                    "quantity": emp_count - post_count
                })


    roles_not_filled_html = render_operations_roles_html(list_of_dict_of_operations_roles_not_filled)\
          if list_of_dict_of_operations_roles_not_filled else "<div class='alert text-center' role='alert'><h4 class='mb-0'>No Post Count Issues</h4><h5 class='mb-0'>Posts are filled correctly for the next 2 weeks. Great Job!</h5></div>"
    role_over_filled_html = render_operations_roles_html(list_of_dict_of_operations_roles_over_filled,is_over_filled_list=True)\
        if list_of_dict_of_operations_roles_over_filled else "<div class='alert text-center' role='alert'><h4 class='mb-0'>No Post Count Issues</h4><h5 class='mb-0'>Posts are filled correctly for the next 2 weeks. Great Job!</h5></div>"

    return {
         'under_filled':roles_not_filled_html,
         'over_filled':role_over_filled_html
    }




def get_applicable_shifts(employee,user_roles):
    try:
        shifts = []
        if "Operations Manager" in user_roles:
            shifts += get_all_shifts()
        if "Projects Manager" in user_roles:
            shifts += get_project_shifts(employee)
        if "Site Supervisor" in user_roles:
            shifts += get_site_shifts(employee)
        if "Shift Supervisor" in user_roles:
            shifts += get_assigned_shifts(employee)
        if not shifts:
            return []
        return list(set(shifts)) #Remove duplicates

    except:
         frappe.log_error(title = "Error Fetching Post Data",message=frappe.get_traceback())
         frappe.throw("An Error Occurred")


def get_all_shifts():
     all_shifts = frappe.get_all("Operations Shift",{'status':'Active'},pluck ="name")
     return all_shifts


def get_project_shifts(employee):
    active_projects = frappe.get_all("Project",{'status':"Open",'account_manager':employee},pluck ="name")
    if active_projects:
        all_shifts = frappe.get_all("Operations Shift",{'status':'Active','project':['in',active_projects]},pluck ="name")
        return all_shifts
    else:
        return []

def get_site_shifts(employee):
    active_sites = frappe.get_all("Operations Site",{'status':"Active",'account_supervisor':employee},pluck ="name")
    if active_sites:
        all_shifts = frappe.get_all("Operations Shift",{'status':'Active','site':['in',active_sites]},pluck ="name")
        return all_shifts
    else:
        return []


def get_assigned_shifts(employee):
    all_shifts = frappe.db.sql(f"""Select os.name from `tabOperations Shift` os
                                JOIN `tabOperations Shift Supervisor` opss ON os.name = opss.parent
                               WHERE os.status ='Active' and opss.supervisor = '{employee}' """,as_dict=1)
    return [i.name for i in all_shifts]



def render_operations_roles_html(post_list, is_over_filled_list=False):
    """
    Renders HTML table for operations roles that are not filled and overfilled
    Args:
        not_filled_list: List of dicts containing unfilled operations roles
        over_filled_list: List of dicts containing overfilled operations roles
    Returns:
        HTML string containing formatted table
    """


    html = "<table class='table table-bordered'>"
    html += """<thead>
                <tr>
                    <th>Operations Post</th>
                    <th>Operations Role</th>
                    <th>Date</th>
                    <th>Shift</th>
                    <th>Quantity</th>

                </tr>
            </thead><tbody>"""

    # Add not filled roles
    for item in post_list:
        html += f"""<tr>
                        <td>{item.get('post', '')}</td>
                        <td><a  target="_blank" href="/app/roster?main_view='roster'&sub_view='basic'&roster_type='basic'&operations_role={item.get('post')}">{item.get('operations_role', '')}</a></td>
                        <td>{item.get('date', '')}</td>
                        <td>{item.get('shift', '')}</td>
                        {f'<td>{item.get("quantity", "")}</td>'  if  is_over_filled_list else '<td>1</td>' }


                    </tr>"""
    html += "</tbody></table>"
    return html
