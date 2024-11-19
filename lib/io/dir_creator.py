import shutil
from streamlit import session_state

from const.paths import DbPaths
from const.session_names import SessionNames

class DirCreator:
    def create_user_dirs(username: str):
        if not username:
            raise Exception("Missing 'username' value")
    
        dir_invoices = DbPaths.DIR_DB_INVOICES / username
        dir_images = dir_invoices / "images"

        if not dir_invoices.exists():
            dir_invoices.mkdir(parents=True, exist_ok=True)
        if not dir_images.exists():
            dir_images.mkdir(parents=True, exist_ok=True)
        
        session_state[SessionNames.DIR_INVOICES] = dir_invoices
        session_state[SessionNames.DIR_INVOICES_IMAGES] = dir_images


    def remove_user_dirs(username: str):
        user_dir = DbPaths.DIR_DB_INVOICES / username
        shutil.rmtree(user_dir)
