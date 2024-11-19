from pathlib import Path

class MainPath: 
    DIR_MAIN = Path(".")

# database
class DbPaths:
    DIR_DB = MainPath.DIR_MAIN / "db"
    DIR_DB_INVOICES = DIR_DB / "invoices"

# pages
class PagesPaths:
    DIR_PAGES = MainPath.DIR_MAIN / "page"
    PAGE_INVOICES_ADD = DIR_PAGES / "invoices_add.py"
    PAGE_INVOICES_VIEW = DIR_PAGES / "invoices_view.py"
    PAGE_LOGIN = DIR_PAGES / "login.py"
