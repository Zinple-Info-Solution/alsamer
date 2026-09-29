"""Submitted Sales Invoices, one row each, in company currency.

Amount is before the additional discount; Net Amount is what the customer owes
(Rounded Total, or Grand Total when rounding is disabled). Credit notes are
included and show as negative rows.
"""

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


def get_columns():
	def currency(fieldname, label):
		return {"fieldname": fieldname, "label": _(label), "fieldtype": "Currency", "options": "currency", "width": 120}

	return [
		{"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "invoice_no", "label": _("Invoice No"), "fieldtype": "Link", "options": "Sales Invoice", "width": 170},
		{"fieldname": "customer", "label": _("Customer"), "fieldtype": "Data", "width": 240},
		{"fieldname": "sales_person", "label": _("Sales Person"), "fieldtype": "Data", "width": 140},
		currency("amount", "Amount"),
		currency("discount", "Discount"),
		currency("round_off", "Round off"),
		currency("vat_amount", "VAT Amount"),
		currency("net_amount", "Net Amount"),
	]


def get_data(filters):
	conditions = {"docstatus": 1}
	if filters.company:
		conditions["company"] = filters.company
	if filters.from_date and filters.to_date:
		conditions["posting_date"] = ["between", [filters.from_date, filters.to_date]]
	elif filters.from_date:
		conditions["posting_date"] = [">=", filters.from_date]
	elif filters.to_date:
		conditions["posting_date"] = ["<=", filters.to_date]

	invoices = frappe.get_list(
		"Sales Invoice",
		filters=conditions,
		fields=[
			"name",
			"posting_date",
			"company",
			"customer_name",
			"base_total",
			"base_discount_amount",
			"base_rounding_adjustment",
			"base_total_taxes_and_charges",
			"base_rounded_total",
			"base_grand_total",
		],
		order_by="posting_date asc, name asc",
	)
	if not invoices:
		return []

	sales_persons = get_sales_persons([inv.name for inv in invoices])

	return [
		{
			"posting_date": inv.posting_date,
			"invoice_no": inv.name,
			"customer": inv.customer_name,
			"sales_person": sales_persons.get(inv.name, ""),
			"amount": inv.base_total,
			"discount": inv.base_discount_amount,
			"round_off": inv.base_rounding_adjustment,
			"vat_amount": inv.base_total_taxes_and_charges,
			"net_amount": inv.base_rounded_total or inv.base_grand_total,
			"currency": frappe.get_cached_value("Company", inv.company, "default_currency"),
		}
		for inv in invoices
	]


def get_sales_persons(invoice_names):
	rows = frappe.get_all(
		"Sales Team",
		filters={"parenttype": "Sales Invoice", "parent": ["in", invoice_names]},
		fields=["parent", "sales_person"],
		order_by="idx asc",
	)
	persons = {}
	for row in rows:
		persons.setdefault(row.parent, []).append(row.sales_person)
	return {parent: ", ".join(names) for parent, names in persons.items()}
