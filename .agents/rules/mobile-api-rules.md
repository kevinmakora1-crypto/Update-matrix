# Mobile API Rules — Frappe + Ionic/CapacitorHttp

> **⚠️ READ THIS BEFORE WRITING ANY NEW MOBILE-FACING API IN ONE FM.**
> These rules were learned the hard way after hours of debugging the `create_resignation` API.
> Every single rule here caused a real production bug.

---

## Rule 1: Frappe Does NOT Parse the Request Body When Using Token Auth

### What Happens
When the mobile app authenticates via `Authorization: token key:secret`, Frappe skips its normal body-parsing pipeline. This means:
- `frappe.form_dict` is **empty**
- Function kwargs are **all `None`**
- Even if you declare explicit params in the signature, they arrive as `None`

### The Fix
**Always manually parse the raw request body.** Use this helper in every mobile-facing API file:

```python
def get_request_data(data=None, **kwargs):
    payload = {}

    # ALWAYS parse raw body first — token auth bypasses form_dict
    if hasattr(frappe, 'request'):
        try:
            body = frappe.request.get_data(as_text=True)
            if body:
                try:
                    parsed = json.loads(body)
                    if isinstance(parsed, dict):
                        payload.update(parsed)
                except Exception:
                    from urllib.parse import parse_qs
                    parsed_qs = parse_qs(body, keep_blank_values=True)
                    for k, v in parsed_qs.items():
                        payload[k] = v[0] if len(v) == 1 else v
        except Exception:
            pass

    # Then merge form_dict (cookie/session auth path)
    for key in payload_keys:
        if not payload.get(key) and frappe.form_dict.get(key):
            payload[key] = frappe.form_dict.get(key)

    return payload
```

---

## Rule 2: `frappe.ExpectationFailed` Does Not Exist

### What Happens
`frappe.throw("msg", frappe.ExpectationFailed)` raises an **`AttributeError`** at runtime — not a validation error. This crashes the `except` block, making the real error invisible.

### The Fix
Use `frappe.ValidationError` instead:

```python
# ❌ WRONG — crashes silently
frappe.throw("Employee not found", frappe.ExpectationFailed)

# ✅ CORRECT
frappe.throw("Employee not found", frappe.ValidationError)
```

---

## Rule 3: Always Resolve `employee_id` to the Frappe PK

### What Happens
The mobile app stores and sends a **custom employee ID** (e.g., `2202025NP191`). Frappe's Employee records use an internal name like `HR-EMP-01873` as the primary key. Passing the custom ID directly to `frappe.get_doc`, `frappe.db.get_value`, or child table links will **silently fail** or create broken records.

### The Fix
Always resolve before using:

```python
def resolve_employee_name(employee_id):
    # Try custom field first
    name = frappe.db.get_value("Employee", {"employee_id": employee_id}, "name")
    if name:
        return name
    # Fallback: maybe they passed the PK directly
    if frappe.db.exists("Employee", employee_id):
        return employee_id
    return None
```

---

## Rule 4: DocTypes With Child Tables Require Items in the Child Table

### What Happens
If a DocType (e.g., `Employee Resignation`) has a mandatory child table (e.g., `employees`), saving the parent doc without adding at least one child row triggers validation errors — even if you set all the top-level fields correctly.

### The Fix
Always `append()` a row to the child table:

```python
doc.append("employees", {
    "employee": employee_name,  # Must use PK, not custom ID
    "employee_name": emp_data.get("employee_name"),
    "designation": emp_data.get("designation"),
    ...
})
doc.insert(ignore_permissions=True)
```

---

## Rule 5: Declare Explicit Function Parameters, Not Just `**kwargs`

### What Happens
Frappe's API router (`frappe.handler`) calls whitelisted functions with `**frappe.form_dict`. If `form_dict` is empty (due to token auth), and you only have `**kwargs`, all parameters arrive as `None`.

### The Fix
Declare all expected parameters **explicitly** in the function signature. This also makes the API self-documenting:

```python
# ✅ CORRECT — explicit params survive even with partial form_dict
@frappe.whitelist()
def create_resignation(
    employee_id=None,
    supervisor=None,
    resignation_initiation_date=None,
    relieving_date=None,
    attachment=None,
    data=None,
    **kwargs
):
    ...
```

---

## Rule 6: Use `frappe.db.set` Instead of `doc.workflow_state` for State Transitions

### What Happens
Setting `doc.workflow_state = "Pending Supervisor"` before `doc.insert()` may get overridden by the workflow engine on save.

### The Fix
Insert first, then force the state with `db_set`:

```python
doc.insert(ignore_permissions=True)
doc.db_set("workflow_state", "Pending Supervisor")
```

---

## Rule 7: Test Both Auth Paths

Every mobile API must be tested with **two curl commands** before declaring it done:

```bash
# Path A: Cookie/Session auth (logged-in browser or first-time login)
curl -X POST "http://SERVER/api/method/one_fm.api.v1.MODULE.FUNCTION" \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"param": "value"}'

# Path B: Token auth (how the mobile app ACTUALLY sends requests after login)
curl -X POST "http://SERVER/api/method/one_fm.api.v1.MODULE.FUNCTION" \
  -H "Authorization: token key12345:secret12345" \
  -d "param=value"

# Both must return success. If only one works, it's not done.
```

---

## Quick Debugging Checklist

When a mobile API returns 417 or 500:

- [ ] Check `frappe.log_error` entries in the Frappe Error Log (not just the browser console)
- [ ] Log `frappe.request.get_data(as_text=True)` — is the body actually arriving?
- [ ] Log `frappe.form_dict` — is it empty despite a non-empty body? → Token auth issue (Rule 1)
- [ ] Check if the error is `AttributeError: module 'frappe' has no attribute 'X'` → Wrong exception class (Rule 2)
- [ ] Check if `employee_id` resolves to a real PK → Rule 3
- [ ] Check if child table rows were added → Rule 4
- [ ] Test with both cookie auth AND token auth curl → Rule 7
