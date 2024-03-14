from apps.main.enums import PermissionCategories

vendor_management_permissions = {
    (
        "update_vendor_record",
        "Update vendor record",
        PermissionCategories.VENDOR_MANAGEMENT,
        "Permission to allow users to update vendor record"
    ),
    (
        "delete_vendor_record",
        "Delete vendor record",
        PermissionCategories.VENDOR_MANAGEMENT,
        "Permission to allow users to delete vendor record"
    ),
    (
        "view_vendor_record",
        "View vendor record",
        PermissionCategories.VENDOR_MANAGEMENT,
        "Permission to allow users to view vendor record"
    )
}

product_management_permissions = {
    (
        "add_vendor_product_record",
        "Add vendor product record",
        PermissionCategories.PRODUCT_MANAGEMENT,
        "Permission to allow users to add vendor product record"
    ),
    (
        "update_vendor_product_record",
        "Update vendor product record",
        PermissionCategories.PRODUCT_MANAGEMENT,
        "Permission to allow users to update vendor product record"
    ),
    (
        "delete_vendor_product_record",
        "Delete vendor product record",
        PermissionCategories.PRODUCT_MANAGEMENT,
        "Permission to allow users to delete vendor product record"
    ),
    (
        "view_vendor_product_record",
        "View vendor product record",
        PermissionCategories.PRODUCT_MANAGEMENT,
        "Permission to allow users to view vendor product record"
    ),
    (
        "can_generate_vendor_product_report",
        "Can generate vendor product report",
        PermissionCategories.PRODUCT_MANAGEMENT,
        "Permission to allow users to generate vendor product report"
    )
}
