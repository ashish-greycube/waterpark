import re

import frappe
from frappe import _
from frappe.utils import getdate, nowdate

no_cache = 1

# Keep this in sync with PACKAGE_PRICES in the DocType controller
PACKAGE_PRICES = {
	"Standard Splash": 499,
	"Premium Wave": 899,
}


def get_context(context):
	context.no_cache = 1
	context.title = "Book Your Water Park Ticket"


@frappe.whitelist(allow_guest=True)
def submit_booking(customer_name, mobile_no, booking_date, no_of_persons, package):
	"""Public endpoint called from the booking form. Re-validates everything
	server-side (never trust the browser) and creates a Water Park Booking.
	"""

	if not (customer_name or "").strip():
		frappe.throw(_("Name is required"))

	if not re.match(r"^[6-9]\d{9}$", (mobile_no or "").strip()):
		frappe.throw(_("Please enter a valid 10-digit mobile number"))

	try:
		no_of_persons = int(no_of_persons)
	except (TypeError, ValueError):
		frappe.throw(_("Number of persons is invalid"))

	if no_of_persons <= 0:
		frappe.throw(_("Number of persons must be greater than 0"))

	if no_of_persons > 50:
		frappe.throw(_("For groups above 50 guests, please contact us directly"))

	if not booking_date or getdate(booking_date) < getdate(nowdate()):
		frappe.throw(_("Please select a valid, upcoming booking date"))

	if package not in PACKAGE_PRICES:
		frappe.throw(_("Please select a package"))

	doc = frappe.get_doc(
		{
			"doctype": "Water Park Booking",
			"customer_name": customer_name.strip(),
			"mobile_no": mobile_no.strip(),
			"booking_date": booking_date,
			"no_of_persons": no_of_persons,
			"package": package,
		}
	)
	# Guest has no create-permission on the doctype by design, so we
	# bypass permissions here -- all real validation already happened
	# above and again inside Document.validate().
	doc.insert(ignore_permissions=True)
	frappe.db.commit()

	return {
		"booking_id": doc.name,
		"amount_per_person": doc.amount_per_person,
		"total_amount": doc.total_amount,
	}