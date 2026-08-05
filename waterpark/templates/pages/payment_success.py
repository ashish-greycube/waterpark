import frappe

no_cache = True


def get_context(context):
	doc = frappe.get_doc(frappe.local.form_dict.doctype, frappe.local.form_dict.docname)

	context.payment_message = "Kindly wait, Your Entry QR Pass will be generated shortly. Please do not refresh the page."
	if hasattr(doc, "get_payment_success_message"):
		context.payment_message = doc.get_payment_success_message()