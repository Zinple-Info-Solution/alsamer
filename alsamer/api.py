import re

import frappe

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp"}


@frappe.whitelist()
def get_print_header(company=None):
	"""Company name and logo for the Alsamer report print headers.

	The logo is the first found of: the Company Logo field, an image attached
	to the Company record, or the image of its Default Letter Head (its Image,
	or else the first <img> in its HTML).
	"""
	company = (
		company
		or frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company")
	)
	if not company or not frappe.db.exists("Company", company):
		return {}

	company_name, logo, letter_head = frappe.get_cached_value(
		"Company", company, ["company_name", "company_logo", "default_letter_head"]
	)
	logo = (
		logo
		or _attached_image(company)
		or _letter_head_image(
			letter_head or frappe.db.get_value("Letter Head", {"is_default": 1, "disabled": 0})
		)
	)

	return {"company_name": company_name, "logo": logo}


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


def _letter_head_image(letter_head):
	if not letter_head:
		return None
	lh = frappe.db.get_value("Letter Head", letter_head, ["image", "content"], as_dict=True)
	if not lh:
		return None
	if lh.image:
		return lh.image
	match = re.search(r"""<img[^>]+src=["']([^"']+)["']""", lh.content or "")
	return match.group(1) if match else None
