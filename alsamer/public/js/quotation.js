frappe.ui.form.on("Quotation", {
	setup(frm) {
		frm.custom_make_buttons = { ...frm.custom_make_buttons, "Sales Invoice": "Sales Invoice" };
	},

	onload(frm) {
		alsamer.apply_fixed_item_columns(frm);
	},

	refresh(frm) {
		alsamer.apply_fixed_item_columns(frm);

		if (frm.doc.docstatus !== 1 || frm.doc.status === "Lost") return;
		if (!frappe.model.can_create("Sales Invoice")) return;

		frm.add_custom_button(
			__("Sales Invoice"),
			() =>
				frappe.model.open_mapped_doc({
					method: "erpnext.selling.doctype.quotation.quotation.make_sales_invoice",
					frm,
				}),
			__("Create")
		);
	},
});
