# Copyright (c) 2026, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re
from frappe import _
from frappe.utils import getdate, nowdate, get_url
import json
import erpnext
from erpnext import get_default_company

# Keep this in sync with the PACKAGE_PRICES map in www/water_park_booking.py
PACKAGE_PRICES = {
	"standard_splash": 899,
	"premium_wave": 1299,
}


class WaterParkBookingRequest(Document):
	def validate(self):
		self.validate_customer_name()
		self.validate_mobile_no()
		self.validate_no_of_persons()
		self.validate_booking_date()
		self.calculate_amount()

	def on_submit(self):
		self.create_payment_request()

	def validate_customer_name(self):
		if not (self.customer_name or "").strip():
			frappe.throw(_("Name is required"))

	def validate_mobile_no(self):
		# 10-digit Indian mobile number starting 6-9. Adjust the pattern
		# below if you need to support other country formats.
		if not re.match(r"^[6-9]\d{9}$", self.mobile_no or ""):
			frappe.throw(_("Please enter a valid 10-digit mobile number"))
		if self.mobile_no:
			## add country code if not present
			if not self.mobile_no.startswith("91"):
				self.mobile_no = "91" + self.mobile_no

	def validate_no_of_persons(self):
		if not self.no_of_persons or self.no_of_persons <= 0:
			frappe.throw(_("Number of persons must be greater than 0"))
		if self.no_of_persons > 50:
			frappe.throw(_("For groups above 50 guests, please contact us directly"))

	def validate_booking_date(self):
		if self.booking_date and getdate(self.booking_date) < getdate(nowdate()):
			frappe.throw(_("Booking date cannot be in the past"))

	def calculate_amount(self):
		if self.standard_splash == 1:
			self.amount_per_person = PACKAGE_PRICES["standard_splash"]
		elif self.premium_wave == 1:
			self.amount_per_person = PACKAGE_PRICES["premium_wave"]
		self.total_amount = self.amount_per_person * self.no_of_persons

	def create_payment_request(self):
		# Create a Payment Request document for the booking.
		# reference_doctype is not one of ERPNext's ALLOWED_DOCTYPES_FOR_PAYMENT_REQUEST,
		# so validate_payment_request_amount() can't compute ref_amount via get_amount().
		# Populating payment_reference makes that core check return early instead of
		# always failing with "Payment Entry is already created".

		payment_gateway_account = frappe.get_doc("Payment Gateway Account", {
			"company": get_default_company(),
			"payment_gateway" : "Razorpay",
		})
		payment_request = frappe.new_doc("Payment Request")
		payment_request.update(
			{
				"payment_request_type": "Inward",
				"reference_doctype": "Water Park Booking Request",
				"reference_name": self.name,
				"grand_total": self.total_amount,
				"company": get_default_company(),
			}
		)
		payment_request.append("payment_reference", {"amount": self.total_amount})

		payment_request.payment_gateway_account = payment_gateway_account.name
		payment_request.subject = "Payment Request for {0}".format(self.name)

		payment_request.payment_gateway = payment_gateway_account.payment_gateway
		payment_request.payment_account = payment_gateway_account.payment_account

		payment_request.insert(ignore_permissions=True)
		payment_request.submit()
		frappe.msgprint(f"Payment Request {payment_request.name} created for Booking ID : {self.name}",alert=True)
		self.payment_url = payment_request.payment_url
		return payment_request.payment_url


def on_payment_request_authorized(payment_request, method, status):
	# Registered against Payment Request's on_payment_authorized in hooks.py.
	# Razorpay only knows about the Payment Request (see reference_doctype/
	# reference_docname in erpnext's Payment Request.get_payment_url), so this
	# is the hook point for telling it where to send the browser back to for
	# our booking specifically.
	if payment_request.reference_doctype != "Water Park Booking Request":
		return

	return get_url(
		f"/water_park_booking?booking={payment_request.reference_name}&paid=1"
	)