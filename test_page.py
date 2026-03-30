import sys
sys.path.append('apps/frappe')
import frappe
frappe.init(site="recovery.local")
frappe.connect()

print("--- PAGE RECORD ---")
try:
    page = frappe.get_doc("Page", "interview_console")
    print("Module:", page.module)
    print("Standard:", page.standard)
    try:
        path = frappe.get_module_path(page.module, "page", page.name)
        print("Expected Path:", path)
        import os
        print("JS file exists at expected path:", os.path.exists(os.path.join(path, page.name + ".js")))
    except Exception as e:
        print("Path Error:", e)

    print("\n--- DESK GETPAGE API ---")
    from frappe.desk.desk_page import getpage
    res = getpage("interview_console")
    js_content = res.get("script", "")
    html_content = res.get("html", "")
    print(f"Delivered JS Length: {len(js_content)}")
    print(f"Delivered HTML Length: {len(html_content)}")
    
    if len(js_content) > 0:
        print("Starts with:", js_content[:150])
    
except Exception as e:
    print("Global Error:", e)

frappe.destroy()
