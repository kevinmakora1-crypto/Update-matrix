# Copyright (c) 2026, ONE FM and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate, add_days
from frappe.workflow.doctype.workflow_action.workflow_action import apply_workflow
from unittest.mock import patch


DEPLOYMENT_DOCTYPE = "Temporary Deployment"
ITEM_DOCTYPE = "Temporary Deployment Item"
POST_DOCTYPE = "Temporary Post"


def _get_first_operations_role():
    """Return the name of the first available Operations Role in the DB."""
    roles = frappe.get_all("Operations Role", fields=["name"], limit=1)
    if not roles:
        frappe.throw("No Operations Role found. Please create at least one before running this test.")
    return roles[0].name


def _make_deployment(post_name, operations_role, count, gender="Both", start_date=None, end_date=None):
    """
    Create and insert a Temporary Deployment document with a single child row.
    Returns the saved (unsaved workflow state = Draft) document.
    """
    start_date = start_date or nowdate()
    end_date = end_date or add_days(nowdate(), 30)

    doc = frappe.get_doc({
        "doctype": DEPLOYMENT_DOCTYPE,
        "start_date": start_date,
        "end_date": end_date,
        "operations_post_requirement": [
            {
                "doctype": ITEM_DOCTYPE,
                "post_name": post_name,
                "operations_role": operations_role,
                "gender": gender,
                "count": count,
            }
        ],
    })
    doc.insert(ignore_permissions=True)
    return doc


def _make_deployment_multi(rows, start_date=None, end_date=None):
    """
    Create a Temporary Deployment with multiple child rows.
    `rows` is a list of dicts: {post_name, operations_role, count, gender}.
    """
    start_date = start_date or nowdate()
    end_date = end_date or add_days(nowdate(), 30)

    child_rows = [
        {
            "doctype": ITEM_DOCTYPE,
            "post_name": r["post_name"],
            "operations_role": r["operations_role"],
            "gender": r.get("gender", "Both"),
            "count": r["count"],
        }
        for r in rows
    ]

    doc = frappe.get_doc({
        "doctype": DEPLOYMENT_DOCTYPE,
        "start_date": start_date,
        "end_date": end_date,
        "operations_post_requirement": child_rows,
    })
    doc.insert(ignore_permissions=True)
    return doc


class TestTemporaryDeployment(FrappeTestCase):
    """
    Test suite for auto-creation of Temporary Post documents
    when a Temporary Deployment is approved through the workflow.

    Business rule:
        workflow_state == "Approved"  →  for each child row, create `count`
        Temporary Post records with post_name suffixed as -1, -2, … -N.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def setUp(self):
        frappe.set_user("Administrator")
        self.operations_role = _get_first_operations_role()

        # Clean any leftover test records from previous runs
        self._cleanup()

    def tearDown(self):
        self._cleanup()
        frappe.db.rollback()
        frappe.set_user("Administrator")

    def _cleanup(self):
        """Remove all Temporary Post and Deployment records created by tests."""
        # Delete temporary posts linked to test deployments
        frappe.db.delete(POST_DOCTYPE, {"temporary_deployment": ["like", "TD-%"]})

        # Delete temporary deployments (child rows cascade automatically)
        for td in frappe.get_all(DEPLOYMENT_DOCTYPE, fields=["name"]):
            try:
                doc = frappe.get_doc(DEPLOYMENT_DOCTYPE, td.name)
                if doc.docstatus == 1:
                    doc.cancel()
                frappe.delete_doc(DEPLOYMENT_DOCTYPE, td.name, force=True, ignore_permissions=True)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Workflow helper
    # ------------------------------------------------------------------

    def _approve(self, doc):
        """Push a Temporary Deployment through the full approval workflow."""
        apply_workflow(doc, "Submit for Review")
        doc.reload()
        apply_workflow(doc, "Approve")
        doc.reload()

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    @patch("frappe.sendmail")
    def test_single_item_count_one_creates_one_post(self, mock_sendmail):
        """
        Test 1: A single child row with count=1 creates exactly 1 Temporary Post
        named '<post_name>-1'.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment(
            post_name="Guard",
            operations_role=self.operations_role,
            count=1,
        )

        self._approve(doc)

        posts = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            fields=["name", "post_name", "status", "gender"],
        )

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].post_name, "Guard-1")
        self.assertEqual(posts[0].status, "Active")

    @patch("frappe.sendmail")
    def test_single_item_count_three_creates_three_posts_with_suffix(self, mock_sendmail):
        """
        Test 2: A single child row with count=3 creates 3 Temporary Posts
        suffixed Guard-1, Guard-2, Guard-3.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment(
            post_name="Guard",
            operations_role=self.operations_role,
            count=3,
            gender="Male",
        )

        self._approve(doc)

        posts = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            fields=["post_name", "gender"],
            order_by="name asc",
        )

        self.assertEqual(len(posts), 3)

        expected_names = {"Guard-1", "Guard-2", "Guard-3"}
        actual_names = {p.post_name for p in posts}
        self.assertEqual(actual_names, expected_names)

        # All posts must carry the gender from the child row
        for post in posts:
            self.assertEqual(post.gender, "Male")

    @patch("frappe.sendmail")
    def test_multiple_items_total_count_matches(self, mock_sendmail):
        """
        Test 3: Two child rows (count=2 and count=3) → 5 Temporary Posts total.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment_multi(
            rows=[
                {"post_name": "Cashier", "operations_role": self.operations_role, "count": 2, "gender": "Female"},
                {"post_name": "Guard",   "operations_role": self.operations_role, "count": 3, "gender": "Male"},
            ]
        )

        self._approve(doc)

        posts = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            fields=["post_name", "gender"],
        )

        self.assertEqual(len(posts), 5)

        cashier_posts = [p for p in posts if p.post_name.startswith("Cashier")]
        guard_posts   = [p for p in posts if p.post_name.startswith("Guard")]

        self.assertEqual(len(cashier_posts), 2)
        self.assertEqual(len(guard_posts), 3)

        # Spot-check suffixes
        cashier_names = {p.post_name for p in cashier_posts}
        self.assertIn("Cashier-1", cashier_names)
        self.assertIn("Cashier-2", cashier_names)

        guard_names = {p.post_name for p in guard_posts}
        self.assertIn("Guard-1", guard_names)
        self.assertIn("Guard-3", guard_names)

    @patch("frappe.sendmail")
    def test_all_posts_have_status_active(self, mock_sendmail):
        """
        Test 4: Every created Temporary Post must have status = 'Active'
        regardless of the number of rows or gender.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment_multi(
            rows=[
                {"post_name": "Inspector", "operations_role": self.operations_role, "count": 2, "gender": "Both"},
                {"post_name": "Steward",   "operations_role": self.operations_role, "count": 1, "gender": "Female"},
            ]
        )

        self._approve(doc)

        statuses = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            pluck="status",
        )

        self.assertTrue(len(statuses) > 0, "No Temporary Posts were created.")
        for status in statuses:
            self.assertEqual(status, "Active", f"Expected 'Active', got '{status}'")

    @patch("frappe.sendmail")
    def test_posts_link_back_to_parent_deployment(self, mock_sendmail):
        """
        Test 5: The `temporary_deployment` field on every created post must
        point back to the originating Temporary Deployment.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment(
            post_name="Supervisor",
            operations_role=self.operations_role,
            count=2,
        )

        self._approve(doc)

        linked = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            pluck="temporary_deployment",
        )

        self.assertEqual(len(linked), 2)
        for link in linked:
            self.assertEqual(link, doc.name)

    @patch("frappe.sendmail")
    def test_posts_inherit_dates_from_deployment(self, mock_sendmail):
        """
        Test 6: Created Temporary Posts must carry the start_date and end_date
        from the parent Temporary Deployment document.
        """
        mock_sendmail.return_value = None
        start = nowdate()
        end   = add_days(nowdate(), 60)

        doc = _make_deployment(
            post_name="Technician",
            operations_role=self.operations_role,
            count=1,
            start_date=start,
            end_date=end,
        )

        self._approve(doc)

        post = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            fields=["start_date", "end_date"],
            limit=1,
        )

        self.assertEqual(len(post), 1)
        self.assertEqual(str(post[0].start_date), start)
        self.assertEqual(str(post[0].end_date),   end)

    @patch("frappe.sendmail")
    def test_gender_defaults_to_both_when_not_set(self, mock_sendmail):
        """
        Test 7: When the child row does not specify a gender, the created
        Temporary Post must default to 'Both'.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment(
            post_name="Operator",
            operations_role=self.operations_role,
            count=1,
            gender="",          # intentionally blank
        )

        self._approve(doc)

        posts = frappe.get_all(
            POST_DOCTYPE,
            filters={"temporary_deployment": doc.name},
            pluck="gender",
        )

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0], "Both")

    @patch("frappe.sendmail")
    def test_posts_not_created_before_approval(self, mock_sendmail):
        """
        Test 8: A Temporary Deployment that is only in 'Pending Approval' state
        (not yet Approved) must NOT have any Temporary Posts created.
        """
        mock_sendmail.return_value = None
        doc = _make_deployment(
            post_name="Analyst",
            operations_role=self.operations_role,
            count=2,
        )

        # Move to pending approval only — do NOT approve
        apply_workflow(doc, "Submit for Review")
        doc.reload()

        post_count = frappe.db.count(
            POST_DOCTYPE,
            {"temporary_deployment": doc.name},
        )

        self.assertEqual(
            post_count, 0,
            "Temporary Posts must not be created until the deployment is Approved.",
        )
