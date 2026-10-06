frappe.ui.form.on("Delivery Note", {
	onload(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},

	refresh(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},
});
