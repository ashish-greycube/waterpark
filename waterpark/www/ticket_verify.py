import frappe
from frappe.utils import formatdate

no_cache = 1


def get_context(context):
	context.no_cache = 1
	context.title = "Ticket Verification"

	booking_id = frappe.form_dict.get("booking")
	context.booking = None
	context.error = None

	if not booking_id:
		context.error = "No booking reference was provided."
		return

	if not frappe.db.exists("Water Park Booking Request", booking_id):
		context.error = "We couldn't find a booking with this reference."
		return

	doc = frappe.get_doc("Water Park Booking Request", booking_id)

	context.booking = {
		"booking_id": doc.name,
		"customer_name": doc.customer_name,
		"booking_date": formatdate(doc.booking_date, "dd MMM yyyy"),
		"package": "Premium Wave" if doc.premium_wave else "Standard Splash",
		"no_of_persons": doc.no_of_persons,
		"total_amount": doc.total_amount,
		"is_verified": doc.docstatus == 1,
	}
