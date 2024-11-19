import streamlit as st
from io import BytesIO
import pandas as pd
from pandas import DataFrame

from const.invoice import InvoiceVarNames as vn


@st.dialog("Pobieranie")
def show_export_dialog(df: DataFrame):
    column_headers = {
        vn.INV_DOC_TYPE: "Typ dokumentu",
        vn.INV_DOC_NUMBER: "Numer dokumentu",
        vn.INV_ISSUE_DATE: "Data wystawienia",
        vn.INV_SELLER_NIP: "NIP sprzedawcy",
        vn.INV_SELLER_NAME: "Nazwa sprzedawcy",
        vn.INV_SELLER_ADDRESS: "Adres sprzedawcy",
        vn.INV_BUYER_NIP: "NIP nabywcy",
        vn.INV_BUYER_NAME: "Nazwa nabywcy",
        vn.INV_BUYER_ADDRESS: "Adres nabywcy",
        vn.INV_TOTAL_NET_AMOUNT: "kwota NETTO",
        vn.INV_TOTAL_TAX_AMOUNT: "kwota VAT",
        vn.INV_TOTAL_GROSS_AMOUNT: "kwota BRUTTO"
    }

    export_df = df.copy()
    export_df.rename(columns=column_headers, inplace=True)

    format_choice = st.selectbox(
        "Wybierz format eksportu:", 
        options=['Excel', 'CSV'],
        index=0
    )

    file_name = "Faktury"
    if format_choice == 'CSV':
        data = export_df.to_csv(index=False, sep=';', decimal=',')
        mime_type = 'text/csv'
        file_name += ".csv"
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, index=False, sheet_name='Dane')
            worksheet = writer.sheets['Dane']
            for idx, col in enumerate(export_df.columns):
                column_width = len(col) + 2
                worksheet.set_column(idx, idx, column_width)

        data = output.getvalue()
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_name += ".xlsx"

    st.download_button(
        label=f"Pobierz {format_choice}",
        data=data,
        file_name=file_name,
        mime=mime_type
    )
