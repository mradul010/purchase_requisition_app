import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_po_from_pr(source_name):

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doc = get_mapped_doc(
        "Purchase Requisition",
        source_name,
        {
            "Purchase Requisition": {
                "doctype": "Purchase Order"
            },
            "Purchase Requisition Item": {
                "doctype": "Purchase Order Item",
                "field_map": {
                    "name": "purchase_requisition_item",
                    "parent": "purchase_requisition"
                }
            }
        },
        None,
        set_missing_values
    )

    doc.insert()
    return doc.name

import frappe
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def make_pr_from_supplier_quotation(source_name):

    def set_missing_values(source, target):
        target.schedule_date = frappe.utils.nowdate()
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    doc = get_mapped_doc(
        "Supplier Quotation",
        source_name,
        {
            "Supplier Quotation": {
                "doctype": "Purchase Requisition"
            },
            "Supplier Quotation Item": {
                "doctype": "Purchase Requisition Item",
                "field_map": {
                    "name": "supplier_quotation_item",
                    "parent": "supplier_quotation"
                }
            }
        },
        None,
        set_missing_values
    )

    # ensure each item has schedule date
    for item in doc.items:
        if not item.schedule_date:
            item.schedule_date = frappe.utils.nowdate()

    doc.insert()

    return doc.name