"""Property Setters, reasserted on every migrate.

Custom fields are in alsamer/fixtures/custom_field.json (see `fixtures` in hooks.py).

Nothing here deletes data: every hidden field comes straight back by clearing
its Property Setter (or unticking Hidden in Customize Form).
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# Sales Invoice sections/fields not used here. The first seven are also hidden
# by thameen_erp; repeated so this app gives the same form on its own.
SALES_INVOICE_HIDDEN_FIELDS = (
	"accounting_dimensions_section",
	"currency_and_price_list",
	"shipping_rule",
	"incoterm",
	"named_place",
	"scan_barcode",
	"time_sheet_list",
	"is_pos",
	"use_company_roundoff_cost_center",
	"pricing_rule_details",
	"loyalty_points_redemption",
)

# Plain 5-digit number, no prefix: 00001, 00002, ... It never resets, and
# credit notes take the next number in the same sequence.
SALES_INVOICE_NAMING_SERIES = (".#####",)


def after_install():
	after_migrate()


def after_migrate():
	setters = [
		*[("Sales Invoice", f, "hidden", "1", "Check") for f in SALES_INVOICE_HIDDEN_FIELDS],
		# More Info tab shown. thameen_erp hides it on every migrate; alsamer is
		# installed after it, so this runs later and wins.
		("Sales Invoice", "more_info_tab", "hidden", "0", "Check"),
		("Sales Invoice", "naming_series", "options", "\n".join(SALES_INVOICE_NAMING_SERIES), "Text"),
		("Sales Invoice", "naming_series", "default", SALES_INVOICE_NAMING_SERIES[0], "Text"),
		# Rounding Adjustment is editable only when Manual Rounding Adjustment is ticked.
		*[
			setter
			for doctype in ("Sales Invoice", "Quotation")
			for setter in (
				(doctype, "rounding_adjustment", "read_only", "0", "Check"),
				(doctype, "rounding_adjustment", "read_only_depends_on", "eval:!doc.custom_manual_rounding", "Data"),
			)
		],
		("Customer", None, "search_fields", _customer_search_fields(), "Data"),
		# Customer fields everywhere show the Customer Name, not the ID.
		("Customer", None, "show_title_field_in_link", "1", "Check"),
		# ERPNext's three Supplier Types, plus Cash and Credit.
		("Supplier", "supplier_type", "options", "Company\nIndividual\nPartnership\nCash\nCredit", "Text"),
	]
	for doctype, fieldname, prop, value, prop_type in setters:
		try:
			make_property_setter(doctype, fieldname, prop, value, prop_type, for_doctype=not fieldname)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Alsamer Property Setter")

	# 48 = bank card, in the UNTDID 4461 payment means codes ZATCA uses.
	_ensure_mode_of_payment("POS", "Bank", zatca_payment_means_code="48")


def _ensure_mode_of_payment(name, mode_type, zatca_payment_means_code=None):
	"""Create the Mode of Payment if missing. An existing one is left alone, so
	its accounts and type stay as the user configured them."""
	if frappe.db.exists("Mode of Payment", name):
		return
	doc = frappe.get_doc({"doctype": "Mode of Payment", "mode_of_payment": name, "type": mode_type, "enabled": 1})
	# Required on sites with the ZATCA app installed; absent elsewhere.
	if zatca_payment_means_code and doc.meta.has_field("custom_zatca_payment_means_code"):
		doc.custom_zatca_payment_means_code = zatca_payment_means_code
	doc.insert(ignore_permissions=True)


def _customer_search_fields():
	"""Add the phone number to Customer link search, keeping whatever is there."""
	fields = [f.strip() for f in (frappe.get_meta("Customer").search_fields or "").split(",") if f.strip()]
	if "custom_phone_number" not in fields:
		fields.append("custom_phone_number")
	return ",".join(fields)
