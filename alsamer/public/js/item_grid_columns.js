// Fixed Items table columns, shared by Quotation and Sales Invoice.
// Form scripts run in the page's global scope, so everything lives under
// `alsamer.` — a top-level `const` here would clash once both forms are opened.

frappe.provide("alsamer");

alsamer.FIXED_ITEM_COLUMNS = [
	{ fieldname: "item_code", columns: 2 },
	{ fieldname: "item_name", columns: 2 },
	{ fieldname: "custom_comments", columns: 2 },
	{ fieldname: "qty", columns: 1 },
	{ fieldname: "uom", columns: 1 },
	{ fieldname: "rate", columns: 1 },
	{ fieldname: "amount", columns: 1 },
];

alsamer.apply_fixed_item_columns = function (frm) {
	const grid = frm.fields_dict.items && frm.fields_dict.items.grid;
	if (!grid) return;

	const child_dt = grid.doctype;
	const settings = frappe.model.user_settings[frm.doctype] || {};
	const grid_view = Object.assign({}, settings.GridView || {});

	// Save the fixed layout if the user's current one is different
	if (JSON.stringify(grid_view[child_dt] || []) !== JSON.stringify(alsamer.FIXED_ITEM_COLUMNS)) {
		grid_view[child_dt] = alsamer.FIXED_ITEM_COLUMNS;
		settings.GridView = grid_view;
		frappe.model.user_settings[frm.doctype] = settings;
		frappe.model.user_settings.save(frm.doctype, "GridView", grid_view);
	}

	// Redraw the items table with the fixed columns
	if (grid.reset_grid) {
		grid.reset_grid();
	}
};
