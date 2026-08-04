import frappe
from frappe.utils import formatdate

no_cache = 1

# Keep this in sync with ACTIVITY_LABELS in www/shott_booking.py
SHOTT_ACTIVITY_LABELS = {
	"bowling": "Bowling",
	"laser_wars": "Laser Wars",
	"arcade": "Arcade",
	"virtual_reality": "Virtual Reality",
	"go_karting": "Go-Karting",
	"trampoline": "Trampoline",
}


def get_context(context):
	context.no_cache = 1
	context.title = "Ticket Verification"

	booking_id = frappe.form_dict.get("booking")
	context.booking = None
	context.error = None
	context.brand = None

	if not booking_id:
		context.error = "No booking reference was provided."
		return

	if frappe.db.exists("Water Park Booking Request", booking_id):
		doc = frappe.get_doc("Water Park Booking Request", booking_id)
		context.brand = "AquaFun Water Park"
		context.booking = {
			"booking_id": doc.name,
			"customer_name": doc.customer_name,
			"booking_date": formatdate(doc.booking_date, "dd MMM yyyy"),
			"package": "Premium Wave" if doc.premium_wave else "Standard Splash",
			"no_of_persons": doc.no_of_persons,
			"total_amount": doc.total_amount,
			"is_verified": doc.docstatus == 1,
		}
	elif frappe.db.exists("Shott Booking Request", booking_id):
		doc = frappe.get_doc("Shott Booking Request", booking_id)
		activity = next(
			(label for fieldname, label in SHOTT_ACTIVITY_LABELS.items() if doc.get(fieldname)),
			None,
		)
		context.brand = "Shott"
		context.booking = {
			"booking_id": doc.name,
			"customer_name": doc.customer_name,
			"booking_date": formatdate(doc.booking_date, "dd MMM yyyy"),
			"package": activity,
			"no_of_persons": doc.no_of_persons,
			"total_amount": doc.total_amount,
			"is_verified": doc.docstatus == 1,
		}
	else:
		context.error = "We couldn't find a booking with this reference."
