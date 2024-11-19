from const.invoice import InvoiceVarNames as cn

ai_response_template = [
    {
        cn.INV_DOC_TYPE: "typ dokumentu, np. faktura, paragon, umowa, bilet parkingowy, itp.",
        cn.INV_DOC_NUMBER: "numer dokumentu",
        cn.INV_ISSUE_DATE: "data wystawienia dokumentu",
        cn.INV_SELLER_NIP: "numer nip sprzedawcy",
        cn.INV_SELLER_NAME: "nazwa sprzedawcy",
        cn.INV_SELLER_ADDRESS: "adres sprzedawcy",
        cn.INV_BUYER_NIP: "numer nip nabywcy",
        cn.INV_BUYER_NAME: "nazwa nabywcy",
        cn.INV_BUYER_ADDRESS: "adres nabywcy",
        cn.INV_TOTAL_NET_AMOUNT: "wartość (suma) całkowita netto",
        cn.INV_TOTAL_GROSS_AMOUNT: "wartość (suma) całkowita brutto",
        cn.INV_TOTAL_TAX_AMOUNT: "wartość (suma) całkowita VAT"
    }
]
