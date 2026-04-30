import frappe
from one_fm.api.v1.resignation import create_resignation
import sys

def execute():
    try:
        # Create a mock payload based on what the mobile app sends
        payload = {
            "employee_id": "HR-EMP-00001", # Assume this exists, or use a guest if not
            "supervisor": "Administrator",
            "attachment": {
                "attachment_name": "test.pdf",
                "attachment": "JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nDPU0FDQy0x1LCpKVrCG0DkF+SUKrkCWpZGSrYKhkoKhgiVQSAHITE/NzwEAgwkK3QplbmRzdHJlYW0KZW5kb2JqCgozIDAgb2JqCjQ4CmVuZG9iagoKMSAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDU5NSA4NDJdL1Jlc291cmNlczw8L1hPYmplY3Q8PC9EaWN0MSAyIDAgUj4+Pj4vQ29udGVudHMgMiAwIFIvUGFyZW50IDQgMCBSPj4KZW5kb2JqCgo0IDAgb2JqCjw8L1R5cGUvUGFnZXMvQ291bnQgMS9LaWRzWzEgMCBSXT4+CmVuZG9iagoKNSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgNCAwIFI+PgplbmRvYmoKCjYgMCBvYmoKPDwvUHJvZHVjZXIoUHlQREYyKS9DcmVhdG9yKFB5UERGMik+PgplbmRvYmoK"
            }
        }
        res = create_resignation(payload)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        print("CRASHED!")
        traceback.print_exc()

execute()
