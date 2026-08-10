import frappe
import json
import hmac
import hashlib
from frappe.utils import nowdate
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

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
            booking_id = next(
                (
                    word
                    for word in words
                    if word.startswith("WPBR") or word.startswith("SHBR") or word.startswith("ACC-SINV")
                ),
                None,
            )
            # invoice_id = description.get("sales_invoice")
            if booking_id:
                if booking_id.startswith("WPBR"):
                    doctype = "Water Park Booking Request"
                elif booking_id.startswith("SHBR"):
                    doctype = "Shott Booking Request"
                elif booking_id.startswith("ACC-SINV"):
                    doctype = "Sales Invoice"

                try:
                    # Lock the row so concurrent/retried webhook deliveries for the
                    # same payment can't race past the checks below.
                    frappe.db.get_value(doctype, booking_id, "name", for_update=True)

                    if doctype == "Sales Invoice":
                        # Nakkashi Studio orders are plain Sales Invoices, not a
                        # custom booking doctype -- there's no payment_status field
                        # to flip, so mark it paid by raising a Payment Entry.
                        si = frappe.get_doc(doctype, booking_id)

                        if si.outstanding_amount <= 0:
                            # Already processed by an earlier delivery of this webhook.
                            frappe.db.commit()
                        else:
                            amount_paid = payment_entity.get("amount") / 100 
                            pe = frappe.new_doc("Payment Entry") 
                            pe.update({
                                "payment_type": "Receive",
                                "party_type": "Customer",
                                "party": si.customer,
                                "paid_amount": amount_paid,
                                "received_amount": amount_paid,
                                "paid_from" : "Debtors - AW",
                                "paid_to": "Razorpay - AW",
                                "paid_from_account_currency" : "INR",
                                "paid_to_account_currency" : "INR",
                                "reference_no": payment_entity.get("id"),
                                "reference_date" : frappe.utils.today()
                            })

                            pe.append("references", {
                                "reference_doctype": "Sales Invoice",
                                "reference_name": si.name,
                                "allocated_amount": amount_paid
                            })

                            pe.insert(ignore_permissions=True)
                            pe.submit()
                            frappe.db.commit()
                    else:
                        booking_doc = frappe.get_doc(doctype, booking_id)

                        if booking_doc.payment_status == "Paid":
                            # Already processed by an earlier delivery of this webhook;
                            # skip so whatsapp_confirmation_sent doesn't get bumped past 1.
                            frappe.db.commit()
                        else:
                            booking_doc.payment_status = "Paid"
                            booking_doc.whatsapp_confirmation_sent = 1
                            booking_doc.save(ignore_permissions=True)
                            frappe.db.commit()

                except Exception as e:
                    frappe.log_error(title="Booking ID not found", message=frappe.get_traceback())