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
		{"fieldname": "mode_of_payment", "label": _("Mode of Payment"), "fieldtype": "Data", "width": 130},
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
			"custom_mode_of_payment",
			"base_total",
			"base_discount_amount",
			"base_rounding_adjustment",
			"base_total_taxes_and_charges",
			"base_rounded_total",
			"base_grand_total",
		],
		order_by="posting_date asc, name asc",
	)

	start, end = get_invoice_range(filters)
	if start is not None:
		invoices = [
			inv
			for inv in invoices
			if inv.name.isdigit() and int(inv.name) >= start and (end is None or int(inv.name) <= end)
		]

	return [
		{
			"posting_date": inv.posting_date,
			"invoice_no": inv.name,
			"customer": inv.customer_name,
			"mode_of_payment": inv.custom_mode_of_payment or "",
			"amount": inv.base_total,
			"discount": inv.base_discount_amount,
			"round_off": inv.base_rounding_adjustment,
			"vat_amount": inv.base_total_taxes_and_charges,
			"net_amount": inv.base_rounded_total or inv.base_grand_total,
			"currency": frappe.get_cached_value("Company", inv.company, "default_currency"),
		}
		for inv in invoices
	]


def get_invoice_range(filters):
	"""(start, end) of the From / To Invoice No filters, compared as numbers so
	100000 sorts after 99999. (None, None) while they are at their defaults
	(From 00001, To empty): then every invoice is shown, including older ones
	whose names are not plain numbers."""
	from_no = (filters.from_invoice or "").strip()
	to_no = (filters.to_invoice or "").strip()
	for value in (from_no, to_no):
		if value and not value.isdigit():
			frappe.throw(_("Invoice No filters take numbers only, like 00001."))

	start = int(from_no or 1)
	end = int(to_no) if to_no else None
	if start <= 1 and end is None:
		return None, None
	return start, end
