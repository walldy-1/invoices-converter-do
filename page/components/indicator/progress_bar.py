import streamlit as st


class ProgressBar:
    def __init__(self, init_progress: float = 0.0, init_text: str = ""):
        self.bar = st.progress(init_progress, init_text)


    def update(self, progress: float, text: str):
        self.bar.progress(progress, text)
    

    def update_files_counter(self, current_value : int, total_value : int):
        progress = float(current_value) / float(total_value)
        text = f"Przetworzono {current_value} z {total_value} plików"
        self.update(progress, text)


    def empty(self):
        self.bar.empty()
