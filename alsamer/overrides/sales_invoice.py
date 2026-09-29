"""Sales Invoice: manual Rounding Adjustment.

ERPNext always derives `rounding_adjustment` as `rounded_total - grand_total`.
When "Manual Rounding Adjustment" is ticked, the figure the user typed is kept
and the Rounded Total is built from it instead. Everything downstream
(outstanding amount, payment schedule, the round-off GL entry) reads
`rounded_total` / `base_rounding_adjustment`, so it follows automatically.
"""

from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from erpnext.controllers.taxes_and_totals import calculate_taxes_and_totals
from frappe.utils import flt


class ManualRoundingTaxesAndTotals(calculate_taxes_and_totals):
	def __init__(self, doc):
		# Captured before calculate() runs: the cash / non-trade discount path
		# zeroes rounding_adjustment on the doc before calling set_rounded_total.
		self.manual_rounding_adjustment = (
			flt(doc.rounding_adjustment) if doc.get("custom_manual_rounding") else None
		)
		super().__init__(doc)

	def set_rounded_total(self):
		if self.manual_rounding_adjustment is None or self.doc.is_rounded_total_disabled():
			return super().set_rounded_total()

		self.doc.rounding_adjustment = flt(
			self.manual_rounding_adjustment, self.doc.precision("rounding_adjustment")
		)
		self.doc.rounded_total = flt(
			self.doc.grand_total + self.doc.rounding_adjustment, self.doc.precision("rounded_total")
		)
		self._set_in_company_currency(self.doc, ["rounding_adjustment", "rounded_total"])


class AlsamerSalesInvoice(SalesInvoice):
	def calculate_taxes_and_totals(self):
		# Same as AccountsController.calculate_taxes_and_totals, with our calculator.
		ManualRoundingTaxesAndTotals(self)
		self.calculate_commission()
		self.calculate_contribution()
