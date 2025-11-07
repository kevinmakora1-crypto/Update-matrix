import frappe

from erpnext.erpnext.assets.doctype.asset.asset import Asset


class AssetOverride(Asset):
    def validate(self):
        super(Asset, self).validate()
        self.validate_refundable_asset()

    def validate_refundable_asset(self):
        if self.get('custom_is_refundable'):
            self.calculate_depreciation = 0
            
            if self.asset_owner != 'Customer':
                self.asset_owner = 'Customer'
            
            if not self.customer and self.purchase_receipt:
                pr_supplier = frappe.db.get_value('Purchase Receipt', self.purchase_receipt, 'supplier')
                if pr_supplier:
                    customer = frappe.db.get_value('Supplier', pr_supplier, 'represents_company')
                    if customer:
                        self.customer = customer

    def before_save(self):
        if self.get('custom_is_refundable'):
            self.calculate_depreciation = 0

    def make_depreciation_schedule(self):
        if self.get('custom_is_refundable'):
            return

        super(AssetOverride, self).make_depreciation_schedule()

    def get_depreciation_amount(self):
        if self.get('custom_is_refundable'):
            return 0
        
        return super(Asset, self).get_depreciation_amount()