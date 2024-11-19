class InvoiceMainVarNames:
    INV_DOC_TYPE = "doc_type"
    INV_DOC_NUMBER = "doc_number"
    INV_ISSUE_DATE = "issue_date"
    INV_SELLER_NIP = "seller_nip"
    INV_SELLER_NAME = "seller_name"
    INV_SELLER_ADDRESS = "seller_address"
    INV_BUYER_NIP = "buyer_nip"
    INV_BUYER_NAME = "buyer_name"
    INV_BUYER_ADDRESS = "buyer_address"
    INV_TOTAL_NET_AMOUNT = "total_net_amount"
    INV_TOTAL_GROSS_AMOUNT = "total_gross_amount"
    INV_TOTAL_TAX_AMOUNT = "total_tax_amount"


class InvoiceVarNames(InvoiceMainVarNames):
    INV_DOC_ID = "doc_id"
    INV_DOC_IMAGE = "doc_image"


class InvoiceDateFormats:
    DB_FORMAT = "%Y-%m-%d"
    ALLOWED_FORMATS = [
        DB_FORMAT,
        "%d-%m-%Y",
        "%Y.%m.%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d"
    ]