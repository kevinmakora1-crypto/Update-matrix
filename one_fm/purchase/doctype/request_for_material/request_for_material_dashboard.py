from __future__ import unicode_literals
from frappe import _

def get_data():
    """
    Returns the configuration for the Request for Material connections dashboard.
    This dashboard shows two-way links between Issue/Transfer RFMs and Purchase RFMs.
    """
    return {
        # The primary field used to find connections.
        'fieldname': 'linked_purchase_rfm',

        # A dictionary of other fields to check for connections.
        # This allows the dashboard to find links in both directions.
        'non_standard_fieldnames': {
            'Request for Material Item': 'linked_request_for_material'
        },
        
        'transactions': [
            {
                # This section will appear on the Purchase RFM,
                # showing the original Issue/Transfer RFM it is linked to.
                'label': _('Issue/Transfer Request for Material'),
                'items': ['Request for Material'],
                'filters': {
                    'purpose': ['in', ['Issue', 'Transfer']]
                }
            }
        ]
    }