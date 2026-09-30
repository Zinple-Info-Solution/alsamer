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
