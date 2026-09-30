from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

from alsamer.overrides.manual_rounding import ManualRoundingTaxesAndTotals


class AlsamerSalesInvoice(SalesInvoice):
	def calculate_taxes_and_totals(self):
		# Same as AccountsController.calculate_taxes_and_totals, with our calculator.
		ManualRoundingTaxesAndTotals(self)
		self.calculate_commission()
		self.calculate_contribution()
