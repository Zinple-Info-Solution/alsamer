alsamer.setup_manual_rounding("Sales Invoice", erpnext.accounts.SalesInvoiceController);

frappe.ui.form.on("Sales Invoice", {
	onload(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},

	refresh(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},

	// Not a "Fetch From": the Customer's Arabic name field is named differently
	// per site, so the server picks whichever exists (also re-set on save).
	customer(frm) {
		if (!frm.doc.customer) {
			frm.set_value("custom_customer_arabic_name", "");
			return;
		}
		frappe
			.xcall("alsamer.overrides.sales_invoice.get_customer_arabic_name", { customer: frm.doc.customer })
			.then((arabic_name) => frm.set_value("custom_customer_arabic_name", arabic_name || ""));
	},
});
