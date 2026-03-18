import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import save_file


@frappe.whitelist()
def make_po_from_pr(source_name):

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")
        target.purchase_requisition = source.name

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
    copy_attachments(source_name, doc.name)
    return doc.name

def copy_attachments(pr_name, po_name): 
    files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Purchase Requisition",
            "attached_to_name": pr_name
        },
        fields=["file_name", "file_url", "is_private"]
    )

    for file in files:
        file_content = None
        file_doc = frappe.get_doc("File", {
            "file_url": file.file_url
        })

        file_path = file_doc.get_full_path()

        with open(file_path, "rb") as f:
            file_content = f.read()

        save_file(
            fname=file.file_name,
            content=file_content,
            dt="Purchase Order",
            dn=po_name,
            is_private=file.is_private
        )

# def copy_assignments(pr_name, po_name):
#     todos = frappe.get_all(
#         "ToDo",
#         filters={
#             "reference_type": "Purchase Requisition",
#             "reference_name": pr_name,
#             "status": ("!=", "Cancelled")
#         },
#         fields=["allocated_to", "description", "priority"]
#     )

#     for todo in todos:

#         # جلوگیری duplicate assignment
#         if not frappe.db.exists("ToDo", {
#             "reference_type": "Purchase Order",
#             "reference_name": po_name,
#             "allocated_to": todo.allocated_to
#         }):
#             frappe.get_doc({
#                 "doctype": "ToDo",
#                 "allocated_to": todo.allocated_to,
#                 "description": todo.description,
#                 "priority": todo.priority,
#                 "reference_type": "Purchase Order",
#                 "reference_name": po_name
#             }).insert(ignore_permissions=True)

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

