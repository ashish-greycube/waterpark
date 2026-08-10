import json
import re

import erpnext
import frappe
from frappe import _
from frappe.utils import cint, flt, get_url

no_cache = 1

ITEM_GROUP = "Products"
PRICE_LIST = "Standard Selling"
CUSTOMER_GROUP = "Individual"
TERRITORY = "India"

# Payment Requests created from this page carry this subject prefix so
# on_payment_request_authorized (see hooks.py) can tell them apart from
# Payment Requests raised elsewhere against a Sales Invoice.
PAYMENT_SUBJECT_PREFIX = "Nakkashi Studio Order"


def get_context(context):
	context.no_cache = 1
	context.title = "Nakkashi Studio"
	context.items = get_sellable_items()


def get_sellable_items():
	"""Items in the boutique's Item Group that have a Standard Selling price."""
	items = frappe.get_all(
		"Item",
		filters={"item_group": ITEM_GROUP, "disabled": 0},
		fields=["item_code", "item_name", "description", "image"],
		order_by="item_name",
	)
	if not items:
		return []

	rates = dict(
		frappe.get_all(
			"Item Price",
			filters={
				"item_code": ["in", [i.item_code for i in items]],
				"price_list": PRICE_LIST,
				"selling": 1,
			},
			fields=["item_code", "price_list_rate"],
			as_list=True,
		)
	)
	for item in items:
		item.rate = flt(rates.get(item.item_code))
	return [item for item in items if item.rate > 0]


def get_or_create_customer(customer_name, mobile_no):
	existing = frappe.db.get_value("Customer", {"custom_mobile_no": mobile_no}, "name")
	if existing:
		return existing

	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": "Individual",
			"customer_group": CUSTOMER_GROUP,
			"territory": TERRITORY,
			"custom_mobile_no": mobile_no,
		}
	)
	customer.insert(ignore_permissions=True)
	return customer.name


@frappe.whitelist(allow_guest=True)
def submit_order(customer_name, mobile_no, items):
	"""Public endpoint called from the Nakkashi Studio form. Re-validates
	everything server-side, then creates/reuses the Customer, raises a
	submitted Sales Invoice and a Payment Request against it."""

	if not (customer_name or "").strip():
		frappe.throw(_("Name is required"))

	if not re.match(r"^[6-9]\d{9}$", (mobile_no or "").strip()):
		frappe.throw(_("Please enter a valid 10-digit mobile number"))

	if isinstance(items, str):
		items = json.loads(items)
	if not items:
		frappe.throw(_("Please select at least one item"))

	sellable = {item.item_code: item for item in get_sellable_items()}

	si_items = []
	for row in items:
		item_code = row.get("item_code")
		qty = cint(row.get("qty"))
		if item_code not in sellable:
			frappe.throw(_("Invalid item selected"))
		if qty <= 0:
			frappe.throw(_("Quantity must be greater than 0"))
		si_items.append({"item_code": item_code, "qty": qty, "rate": sellable[item_code].rate})

	customer = get_or_create_customer(customer_name.strip(), mobile_no.strip())

	si = frappe.get_doc(
		{
			"doctype": "Sales Invoice",
			"customer": customer,
			"company": erpnext.get_default_company(),
			"items": si_items,
		}
	)
	si.set_missing_values()
	si.insert(ignore_permissions=True)
	si.submit()
	frappe.db.commit()

	payment_url = create_payment_request(si)

	return {
		"invoice": si.name,
		"total_amount": si.grand_total,
		"redirect_url": payment_url,
	}


def create_payment_request(si):
	payment_gateway_account = frappe.get_doc(
		"Payment Gateway Account",
		{"company": si.company, "payment_gateway": "Razorpay"},
	)
	payment_request = frappe.new_doc("Payment Request")
	payment_request.update(
		{
			"payment_request_type": "Inward",
			"reference_doctype": "Sales Invoice",
			"reference_name": si.name,
			"grand_total": si.grand_total,
			"company": si.company,
			"party_type": "Customer",
			"party": si.customer,
			"payment_gateway_account": payment_gateway_account.name,
			"payment_gateway": payment_gateway_account.payment_gateway,
			"payment_account": payment_gateway_account.payment_account,
			"subject": f"{PAYMENT_SUBJECT_PREFIX} {si.name}",
		}
	)
	payment_request.insert(ignore_permissions=True)
	payment_request.submit()
	frappe.msgprint(f"Payment Request {payment_request.name} created for Invoice: {si.name}", alert=True)
	return payment_request.payment_url


@frappe.whitelist(allow_guest=True)
def get_order_confirmation(invoice):
	"""Used by nakkashi_studio.html to repopulate the confirmation panel
	when the browser is redirected back here after a successful Razorpay
	payment (see on_payment_request_authorized in hooks.py)."""
	si = frappe.get_doc("Sales Invoice", invoice)
	return {
		"invoice": si.name,
		"customer_name": si.customer_name,
		"total_amount": si.grand_total,
		"items": [
			{"item_name": d.item_name, "qty": d.qty, "amount": d.amount} for d in si.items
		],
	}


def on_payment_request_authorized(payment_request, method, status):
	# Registered against Payment Request's on_payment_authorized in hooks.py.
	# Sales Invoice is a shared doctype, so the subject prefix set in
	# create_payment_request() is what tells us this Payment Request belongs
	# to a Nakkashi Studio order rather than some other Sales Invoice flow.
	if payment_request.reference_doctype != "Sales Invoice":
		return
	if not (payment_request.subject or "").startswith(PAYMENT_SUBJECT_PREFIX):
		return

	return get_url(f"/nakkashi_studio?invoice={payment_request.reference_name}&paid=1")