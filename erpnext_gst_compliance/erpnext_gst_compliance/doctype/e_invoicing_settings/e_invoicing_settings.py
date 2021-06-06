# Copyright (c) 2021, Frappe and contributors
# For license information, please see license.txt

import six
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form
from erpnext_gst_compliance.utils import safe_load_json

class EInvoicingSettings(Document):
	def validate(self):
		if not frappe.db.get_single_value(self.service_provider, 'enabled'):
			settings_form = get_link_to_form(self.service_provider, self.service_provider)
			frappe.throw(_('Selected Service Provider is disabled. Please enable it by visitng {} Form.').format(
				settings_form
			))

def parse_sales_invoice(sales_invoice):
	if isinstance(sales_invoice, six.string_types):
		sales_invoice = safe_load_json(sales_invoice)
		if not isinstance(sales_invoice, dict):
			frappe.throw(_('Invalid Argument: Sales Invoice')) # TODO: better message
		sales_invoice = frappe._dict(sales_invoice)

	return sales_invoice

def get_service_provider():
	service_provider = frappe.db.get_single_value('E Invoicing Settings', 'service_provider')
	controller = frappe.get_doc(service_provider)
	connector = controller.get_connector()

	return connector

@frappe.whitelist()
def generate_irn(sales_invoice):
	sales_invoice = parse_sales_invoice(sales_invoice)
	connector = get_service_provider()

	success, errors = connector.generate_irn(sales_invoice)

	if not success:
		frappe.throw(errors, title=_('IRN Generation Failed'), as_list=1)

	return success

@frappe.whitelist()
def cancel_irn(sales_invoice, reason, remark):
	sales_invoice = parse_sales_invoice(sales_invoice)
	connector = get_service_provider()

	success, errors = connector.cancel_irn(sales_invoice, reason, remark)

	if not success:
		frappe.throw(errors, title=_('IRN Cancellation Failed'), as_list=1)

	return success