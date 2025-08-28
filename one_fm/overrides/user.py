from frappe.core.doctype.user.user import *

class UserOverride(User):
    """
    Custom override for Frappe User DocType.
    """
    def validate(self):
        # Call the original validate logic
        super(UserOverride, self).validate()
        # On validate, if the user is disabled, clear the mobile field.
        self.validate_mobile()

    def validate_mobile(self):
        # If user is disabled, clear mobile number
        # This ensures no mobile is stored for disabled users
        if not self.enabled:
            self.mobile_no = None