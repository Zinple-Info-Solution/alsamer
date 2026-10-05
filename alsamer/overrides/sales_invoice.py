import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

from alsamer.overrides.manual_rounding import ManualRoundingTaxesAndTotals

# The Customer's Arabic name field differs by site: the ZATCA app's on the live
# site, thameen_erp's on others. The first one that exists is used.
CUSTOMER_ARABIC_NAME_FIELDS = ("custom_customer_name_in_arabic", "custom_arabic_name")


class AlsamerSalesInvoice(SalesInvoice):
	def validate(self):
		self.custom_customer_arabic_name = _customer_arabic_name(self.customer)
		super().validate()

	def calculate_taxes_and_totals(self):
		# Same as AccountsController.calculate_taxes_and_totals, with our calculator.
		ManualRoundingTaxesAndTotals(self)
		self.calculate_commission()
		self.calculate_contribution()


@frappe.whitelist()
def get_customer_arabic_name(customer):
	frappe.has_permission("Customer", "read", customer, throw=True)
	return _customer_arabic_name(customer)


def _customer_arabic_name(customer):
	if not customer:
		return None
	meta = frappe.get_meta("Customer")
	for fieldname in CUSTOMER_ARABIC_NAME_FIELDS:
		if meta.has_field(fieldname):
			return frappe.db.get_value("Customer", customer, fieldname)
	return None
