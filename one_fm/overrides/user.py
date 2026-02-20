from frappe.core.doctype.user.user import *
from frappe.query_builder import DocType
from frappe.utils import add_days, nowdate

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

def unlink_wiki_workspace_from_user(after_days_of_user_creation=30):
    """
    Unlinks the 'Wiki' workspace from users who were created more than 30 days ago
    and have 'Wiki' as their default workspace.
    """

    User = DocType("User")
    days_ago = add_days(nowdate(), -after_days_of_user_creation)
    onboarding_workspace = frappe.db.get_single_value("HR Settings", "onboarding_workspace") or "Wiki"

    frappe.qb.update(User).set(User.default_workspace, "").where(
        (User.default_workspace == onboarding_workspace) & (User.creation <= days_ago)
    ).run()