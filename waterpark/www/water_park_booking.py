import re

import frappe
from frappe import _
import pyqrcode
from frappe.utils import getdate, nowdate, get_url

no_cache = 1

# Keep this in sync with PACKAGE_PRICES in the DocType controller
PACKAGE_PRICES = {
	"Standard Splash": 1,
	"Premium Wave": 1299,
}


def get_context(context):
	context.no_cache = 1
	context.title = "Book Your Water Park Ticket"

def generate_qr_data_uri(data, scale=6):
	"""Generate a QR PNG for `data` and return it as a base64 data URI —
	drop this straight into an <img src="..."> on the frontend."""
	qr = pyqrcode.create(data)
	b64 = qr.png_as_base64_str(scale=scale, quiet_zone=2)
	return f"data:image/png;base64,{b64}"

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
	
	if package == "Standard Splash":
		standard_selected = 1
		premium_selected = 0
	elif package == "Premium Wave":
		standard_selected = 0
		premium_selected = 1

	doc = frappe.get_doc(
		{
			"doctype": "Water Park Booking Request",
			"customer_name": customer_name.strip(),
			"mobile_no": mobile_no.strip(),
			"booking_date": booking_date,
			"no_of_persons": no_of_persons,
			"standard_splash": standard_selected,
			"premium_wave": premium_selected,
			
		}
	)
	# Guest has no create-permission on the doctype by design, so we
	# bypass permissions here -- all real validation already happened
	# above and again inside Document.validate().
	doc.insert(ignore_permissions=True)
	doc.submit()  # triggers on_submit() which creates the Payment Request
	frappe.db.commit()
	verify_url = get_url(f"/ticket_verify?booking={doc.name}")

	return {
		"booking_id": doc.name,
		"amount_per_person": doc.amount_per_person,
		"total_amount": doc.total_amount,
		"redirect_url": doc.payment_url,
		"qr_code": generate_qr_data_uri(verify_url),
	}

@frappe.whitelist(allow_guest=True)
def get_booking_confirmation(booking):
	"""Used by water_park_booking.html to repopulate the confirmation panel
	when the browser is redirected back here after a successful Razorpay
	payment (see on_payment_request_authorized in the Water Park Booking
	Request controller)."""
	doc = frappe.get_doc("Water Park Booking Request", booking)
	verify_url = get_url(f"/ticket_verify?booking={doc.name}")
	return {
		"booking_id": doc.name,
		"customer_name": doc.customer_name,
		"booking_date": str(doc.booking_date),
		"package": "Premium Wave" if doc.premium_wave else "Standard Splash",
		"no_of_persons": doc.no_of_persons,
		"total_amount": doc.total_amount,
		"qr_code": generate_qr_data_uri(verify_url),
	}

import io
import pyqrcode
from frappe.utils import get_url, getdate, nowdate


def generate_qr_data_uri(data, scale=6):
	"""Generate a QR PNG for `data` and return it as a base64 data URI —
	drop this straight into an <img src="..."> on the frontend."""
	qr = pyqrcode.create(data)
	b64 = qr.png_as_base64_str(scale=scale, quiet_zone=2)
	return f"data:image/png;base64,{b64}"