from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Customer": [
				{
					"fieldname": "custom_mobile_no",
					"label": "Mobile No",
					"fieldtype": "Data",
					"options": "Phone",
					"insert_after": "customer_name",
					"unique": 1,
				}
			]
		}
	)