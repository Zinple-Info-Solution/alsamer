// Manual Rounding Adjustment — client side of alsamer.overrides.manual_rounding.
// Each form calls alsamer.setup_manual_rounding with its own controller class,
// so only that form's controller is patched (other transactions untouched).

frappe.provide("alsamer");

alsamer.setup_manual_rounding = function (doctype, controller_class) {
	const proto = controller_class.prototype;
	if (!proto.__alsamer_manual_rounding) {
		proto.__alsamer_manual_rounding = true;

		const base_calculate = proto.calculate_taxes_and_totals;
		const base_set_rounded_total = proto.set_rounded_total;

		proto.calculate_taxes_and_totals = function (...args) {
			// Captured first: the cash / non-trade discount path zeroes the field
			// before calling set_rounded_total.
			this.manual_rounding_adjustment = this.frm.doc.custom_manual_rounding
				? flt(this.frm.doc.rounding_adjustment)
				: null;
			return base_calculate.apply(this, args);
		};

		proto.set_rounded_total = function () {
			const doc = this.frm.doc;
			if (!doc.custom_manual_rounding || cint(doc.disable_rounded_total)) {
				return base_set_rounded_total.apply(this);
			}

			doc.rounding_adjustment = flt(
				this.manual_rounding_adjustment ?? doc.rounding_adjustment,
				precision("rounding_adjustment")
			);
			doc.rounded_total = flt(doc.grand_total + doc.rounding_adjustment, precision("rounded_total"));
			this.set_in_company_currency(doc, ["rounding_adjustment", "rounded_total"]);
		};
	}

	frappe.ui.form.on(doctype, {
		custom_manual_rounding(frm) {
			frm.cscript.calculate_taxes_and_totals();
		},

		rounding_adjustment(frm) {
			if (frm.doc.custom_manual_rounding) frm.cscript.calculate_taxes_and_totals();
		},
	});
};
