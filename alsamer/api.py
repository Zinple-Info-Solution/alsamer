import frappe

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}


@frappe.whitelist()
def get_print_header(company=None):
	"""Company name and logo for the Alsamer report print headers.

	The logo is the image attached to the Company record (its Attachments),
	and nothing else.
	"""
	company = (
		company
		or frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
	)
	if not company or not frappe.db.exists("Company", company):
		return {}

	return {
		"company_name": frappe.get_cached_value("Company", company, "company_name"),
		"logo": _attached_image(company),
	}


def _attached_image(company):
	"""Latest image attached to the Company record, public files first (a
	private file cannot be loaded when the PDF is rendered on the server)."""
	files = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Company", "attached_to_name": company, "is_folder": 0},
		fields=["file_url"],
		order_by="is_private asc, creation desc",
	)
	for f in files:
		if (f.file_url or "").lower().rsplit(".", 1)[-1] in IMAGE_EXTENSIONS:
			return f.file_url
	return None
