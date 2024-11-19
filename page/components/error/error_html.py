def prepare_html_err_message(msg) -> str:
    inner_msg = str(msg).replace("\n", "<br>")

    html = f'''
    <div style="
            color: #7d353b;
            background-color: #ffecec;
            padding: 10px 20px;
            margin: 10px 0;
            border-radius: 5px;">
        {inner_msg}
    </div>
    '''

    return html
    