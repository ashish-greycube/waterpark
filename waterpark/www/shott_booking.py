import io
import re

import frappe
from frappe import _
import pyqrcode
from frappe.utils import getdate, nowdate, get_url
from frappe.utils.file_manager import save_file

no_cache = 1

# Keep this in sync with ACTIVITY_PRICES in the DocType controller
ACTIVITY_PRICES = {
	"bowling": 1,
	"laser_wars": 399,
	"arcade": 299,
	"virtual_reality": 449,
	"go_karting": 499,
	"trampoline": 349,
}

ACTIVITY_LABELS = {
	"bowling": "Bowling",
	"laser_wars": "Laser Wars",
	"arcade": "Arcade",
	"virtual_reality": "Virtual Reality",
	"go_karting": "Go-Karting",
	"trampoline": "Trampoline",
}


def get_context(context):
	context.no_cache = 1
	context.title = "Book Your Shott Experience"

def generate_qr_data_uri(data, scale=6):
	"""Generate a QR PNG for `data` and return it as a base64 data URI —
	drop this straight into an <img src="..."> on the frontend."""
	qr = pyqrcode.create(data)
	b64 = qr.png_as_base64_str(scale=scale, quiet_zone=2)
	return f"data:image/png;base64,{b64}"

def save_qr_code_attachment(doc, data, scale=6):
	"""Generate a QR PNG for `data`, attach it to `doc` as a File, and
	return the file URL to store in the qr_code (Attach Image) field."""
	qr = pyqrcode.create(data)
	buffer = io.BytesIO()
	qr.png(buffer, scale=scale, quiet_zone=2)
	file_doc = save_file(
		f"{doc.name}-qr.png",
		buffer.getvalue(),
		doc.doctype,
		doc.name,
		is_private=0,
	)
	return file_doc.file_url

@frappe.whitelist(allow_guest=True)
def submit_booking(customer_name, mobile_no, booking_date, no_of_persons, activity):
	"""Public endpoint called from the booking form. Re-validates everything
	server-side (never trust the browser) and creates a Shott Booking Request.
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

	if activity not in ACTIVITY_PRICES:
		frappe.throw(_("Please select an activity"))

	doc = frappe.get_doc(
		{
			"doctype": "Shott Booking Request",
			"customer_name": customer_name.strip(),
			"mobile_no": mobile_no.strip(),
			"booking_date": booking_date,
			"no_of_persons": no_of_persons,
			activity: 1,
		}
	)
	# Guest has no create-permission on the doctype by design, so we
	# bypass permissions here -- all real validation already happened
	# above and again inside Document.validate().
	doc.insert(ignore_permissions=True)
	doc.submit()  # triggers on_submit() which creates the Payment Request
	frappe.db.commit()
	verify_url = get_url(f"/ticket_verify?booking={doc.name}")
	qr_file_url = save_qr_code_attachment(doc, verify_url)
	frappe.db.set_value("Shott Booking Request", doc.name, "qr_code", qr_file_url)
	return {
		"booking_id": doc.name,
		"amount_per_person": doc.amount_per_person,
		"total_amount": doc.total_amount,
		"redirect_url": doc.payment_url,
		"qr_code": generate_qr_data_uri(verify_url),
	}

@frappe.whitelist(allow_guest=True)
def get_booking_confirmation(booking):
	"""Used by shott_booking.html to repopulate the confirmation panel
	when the browser is redirected back here after a successful Razorpay
	payment (see on_payment_request_authorized in the Shott Booking
	Request controller)."""
	doc = frappe.get_doc("Shott Booking Request", booking)
	verify_url = get_url(f"/ticket_verify?booking={doc.name}")

	activity = next((a for a in ACTIVITY_PRICES if doc.get(a) == 1), None)

	return {
		"booking_id": doc.name,
		"customer_name": doc.customer_name,
		"booking_date": str(doc.booking_date),
		"activity": ACTIVITY_LABELS.get(activity, activity),
		"no_of_persons": doc.no_of_persons,
		"total_amount": doc.total_amount,
		"qr_code": generate_qr_data_uri(verify_url),
	}
