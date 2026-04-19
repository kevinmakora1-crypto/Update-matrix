from __future__ import unicode_literals
from frappe import _


def get_data():
	return {
		"fieldname": "process_name",
		"transactions": [
			{
				"label": _("Pathfinder"),
				"items": ["Pathfinder Log"]
			}
		]
	}
