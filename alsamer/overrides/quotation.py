from erpnext.selling.doctype.quotation.quotation import Quotation

from alsamer.overrides.manual_rounding import ManualRoundingTaxesAndTotals


class AlsamerQuotation(Quotation):
	def calculate_taxes_and_totals(self):
		# Same as AccountsController.calculate_taxes_and_totals (which adds no
		# commission / contribution step for Quotation), with our calculator.
		ManualRoundingTaxesAndTotals(self)
