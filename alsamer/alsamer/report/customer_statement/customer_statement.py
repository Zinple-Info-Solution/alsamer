"""Customer Statement: opening balance, one row per voucher, running balance.

Built from GL Entries against the customer (company currency), so invoices,
receipts, credit notes and journal entries all appear. Entries marked
"Is Opening" count towards the opening balance whatever their date.
"""

import frappe
from frappe import _
from frappe.query_builder.functions import Min, Sum
from frappe.utils import flt

DOC_TYPE_LABELS = {
	"Sales Invoice": "SALES",
	"Payment Entry": "SR",
	"Journal Entry": "JV",
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.customer:
		frappe.throw(_("Please select a Customer"))
	return get_columns(), get_data(filters)


def get_columns():
	def currency(fieldname, label):
		return {"fieldname": fieldname, "label": _(label), "fieldtype": "Currency", "options": "currency", "width": 130}

	return [
		{"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
		{"fieldname": "voucher_no", "label": _("Doc No"), "fieldtype": "Dynamic Link", "options": "voucher_type", "width": 170},
		{"fieldname": "doc_type", "label": _("Doc Type"), "fieldtype": "Data", "width": 90},
		{"fieldname": "po_no", "label": _("PO No"), "fieldtype": "Data", "width": 120},
		{"fieldname": "remarks", "label": _("Remarks"), "fieldtype": "Data", "width": 200},
		currency("debit", "Debit"),
		currency("credit", "Credit"),
		currency("balance", "Balance"),
	]


def get_data(filters):
	gle = frappe.qb.DocType("GL Entry")
	base = (
		frappe.qb.from_(gle)
		.where(gle.party_type == "Customer")
		.where(gle.party == filters.customer)
		.where(gle.is_cancelled == 0)
	)
	if filters.company:
		base = base.where(gle.company == filters.company)

	currency = frappe.get_cached_value(
		"Company", filters.company or frappe.defaults.get_user_default("Company"), "default_currency"
	)
	customer_fields = ["customer_name", "mobile_no"]
	if frappe.get_meta("Customer").has_field("custom_phone_number"):
		customer_fields.append("custom_phone_number")
	customer = frappe.db.get_value("Customer", filters.customer, customer_fields, as_dict=True)

	# Opening: everything before From Date, plus entries flagged Is Opening.
	opening_query = base.select(Sum(gle.debit - gle.credit))
	if filters.from_date:
		opening_query = opening_query.where((gle.posting_date < filters.from_date) | (gle.is_opening == "Yes"))
	else:
		opening_query = opening_query.where(gle.is_opening == "Yes")
	opening = flt(opening_query.run()[0][0])

	period_query = (
		base.select(
			gle.posting_date,
			gle.voucher_type,
			gle.voucher_no,
			Sum(gle.debit).as_("debit"),
			Sum(gle.credit).as_("credit"),
		)
		.where(gle.is_opening == "No")
		.groupby(gle.posting_date, gle.voucher_type, gle.voucher_no)
		.orderby(gle.posting_date)
		.orderby(Min(gle.creation))  # entry order within a day
	)
	if filters.from_date:
		period_query = period_query.where(gle.posting_date >= filters.from_date)
	if filters.to_date:
		period_query = period_query.where(gle.posting_date <= filters.to_date)
	entries = period_query.run(as_dict=True)

	invoices = get_invoice_details([e.voucher_no for e in entries if e.voucher_type == "Sales Invoice"])
	journal_remarks = get_journal_remarks([e.voucher_no for e in entries if e.voucher_type == "Journal Entry"])

	data = [
		{
			"row_type": "opening",
			"posting_date": filters.from_date,
			"remarks": _("Opening Balance"),
			"debit": opening if opening > 0 else 0,
			"credit": -opening if opening < 0 else 0,
			"balance": opening,
			"currency": currency,
			# Header details for the print format.
			"customer_name": customer.customer_name,
			"customer_phone": customer.get("custom_phone_number") or customer.mobile_no or "",
		}
	]

	balance = opening
	total_debit = total_credit = 0
	for entry in entries:
		balance += flt(entry.debit) - flt(entry.credit)
		total_debit += flt(entry.debit)
		total_credit += flt(entry.credit)

		invoice = invoices.get(entry.voucher_no, {})
		doc_type = DOC_TYPE_LABELS.get(entry.voucher_type, entry.voucher_type)
		if invoice.get("is_return"):
			doc_type = "RETURN"

		data.append(
			{
				"posting_date": entry.posting_date,
				"voucher_type": entry.voucher_type,
				"voucher_no": entry.voucher_no,
				"doc_type": doc_type,
				"po_no": invoice.get("po_no") or "",
				"remarks": journal_remarks.get(entry.voucher_no, ""),
				"debit": entry.debit,
				"credit": entry.credit,
				"balance": balance,
				"currency": currency,
			}
		)

	data.append(
		{
			"row_type": "movement",
			"remarks": _("Movement Total"),
			"debit": total_debit,
			"credit": total_credit,
			"balance": total_debit - total_credit,
			"currency": currency,
		}
	)
	data.append(
		{
			"row_type": "closing",
			"remarks": _("Closing Balance"),
			"debit": data[0]["debit"] + total_debit,
			"credit": data[0]["credit"] + total_credit,
			"balance": balance,
			"currency": currency,
		}
	)
	return data


def get_invoice_details(names):
	if not names:
		return {}
	rows = frappe.get_all(
		"Sales Invoice", filters={"name": ["in", names]}, fields=["name", "po_no", "is_return"]
	)
	return {row.name: row for row in rows}


def get_journal_remarks(names):
	if not names:
		return {}
	rows = frappe.get_all("Journal Entry", filters={"name": ["in", names]}, fields=["name", "user_remark"])
	return {row.name: row.user_remark or "" for row in rows}
