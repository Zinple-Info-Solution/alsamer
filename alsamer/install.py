"""Property Setters, reasserted on every migrate.

Custom fields are in alsamer/fixtures/custom_field.json (see `fixtures` in hooks.py).

Nothing here deletes data: every hidden field comes straight back by clearing
its Property Setter (or unticking Hidden in Customize Form).
"""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# Sales Invoice sections/fields not used here. The first eight are also hidden
# by thameen_erp; repeated so this app gives the same form on its own.
SALES_INVOICE_HIDDEN_FIELDS = (
	"accounting_dimensions_section",
	"currency_and_price_list",
	"shipping_rule",
	"incoterm",
	"named_place",
	"scan_barcode",
	"time_sheet_list",
	"more_info_tab",
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
		("Sales Invoice", "naming_series", "options", "\n".join(SALES_INVOICE_NAMING_SERIES), "Text"),
		("Sales Invoice", "naming_series", "default", SALES_INVOICE_NAMING_SERIES[0], "Text"),
		# Rounding Adjustment is editable only when Manual Rounding Adjustment is ticked.
		("Sales Invoice", "rounding_adjustment", "read_only", "0", "Check"),
		("Sales Invoice", "rounding_adjustment", "read_only_depends_on", "eval:!doc.custom_manual_rounding", "Data"),
		("Customer", None, "search_fields", _customer_search_fields(), "Data"),
	]
	for doctype, fieldname, prop, value, prop_type in setters:
		try:
			make_property_setter(doctype, fieldname, prop, value, prop_type, for_doctype=not fieldname)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Alsamer Property Setter")


def _customer_search_fields():
	"""Add the phone number to Customer link search, keeping whatever is there."""
	fields = [f.strip() for f in (frappe.get_meta("Customer").search_fields or "").split(",") if f.strip()]
	if "custom_phone_number" not in fields:
		fields.append("custom_phone_number")
	return ",".join(fields)
