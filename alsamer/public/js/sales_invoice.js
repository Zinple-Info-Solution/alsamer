alsamer.setup_manual_rounding("Sales Invoice", erpnext.accounts.SalesInvoiceController);

frappe.ui.form.on("Sales Invoice", {
	onload(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},

	refresh(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},
});
