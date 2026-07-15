import frappe
import json
import hmac
import hashlib

# ==================================================================================
# Webhook Callback Function
# ==================================================================================
@frappe.whitelist(allow_guest=True)
def on_payment_authorized():
    settings = frappe.get_doc("AquaFun Settings")
    if not settings:
        frappe.throw("AquaFun Settings Not Found.")
        return

    WEBHOOK_SECRET = settings.get_password("webhook_secret", raise_exception=False)
    data = frappe.request.get_data()

    received_signature = frappe.get_request_header("X-Razorpay-Signature")
    if not received_signature:
        frappe.log_error(title="signature error", message="Signature Not Received")

    # Calculate expected HMAC hex digest using SHA256
    expected_signature = hmac.new(
        bytes(WEBHOOK_SECRET, 'utf-8'),
        data,
        hashlib.sha256
    ).hexdigest()

    # Securely compare signatures to protect against timing attacks
    if not hmac.compare_digest(expected_signature, received_signature):
        frappe.log_error(title="Invalid webhook signature verification failed.", message="frappe.PermissionError")

    # Set user as Administrator to avoid permission issue
    frappe.set_user("Administrator")

    event_data = json.loads(data)
    event = event_data.get("event")

    if event == "payment.captured":
        payload = event_data.get("payload", {})
        payment_entity = payload.get("payment", {}).get("entity", {})
        description = payment_entity.get("description", "")

        # amount_paid = payment_entity.get("amount") / 100
        if description:
            words = description.split()
            booking_id = next((word for word in words if word.startswith("WPBR")), None)
            # invoice_id = description.get("sales_invoice")
            try:
                booking_doc = frappe.get_doc("Water Park Booking Request", booking_id)
                booking_doc.payment_status = "Paid"
                booking_doc.save(ignore_permissions=True)
            
            except Exception as e:
                frappe.log_error(title="Booking ID not found", message=frappe.get_traceback())