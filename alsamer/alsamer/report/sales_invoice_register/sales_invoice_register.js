frappe.query_reports["Sales Invoice Register"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "from_invoice",
			label: __("From Invoice No"),
			fieldtype: "Data",
			default: "00001",
		},
		{
			// Empty = no upper limit.
			fieldname: "to_invoice",
			label: __("To Invoice No"),
			fieldtype: "Data",
		},
	],

	// Company name and logo for the print header, re-read on every refresh
	// so it follows the Company filter.
	after_datatable_render() {
		const report = frappe.query_report;
		frappe
			.xcall("alsamer.api.get_print_header", { company: report.get_filter_value("company") })
			.then((header) => (report.print_header = header));
	},
};
