frappe.query_reports["Customer Statement"] = {
	filters: [
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			reqd: 1,
		},
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
			default: frappe.datetime.year_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
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

	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && ["movement", "closing"].includes(data.row_type)) {
			value = `<b>${value}</b>`;
		}
		return value;
	},
};
