"""Main."""
from src import constants as cst
from sys import argv
from src import checks
from src.arguments import read

if __name__ == "__main__":
    try:
        cst.init(read(argv)) 
        
        checks.create_important_folders()
        
        checks.check_missing_trains()
        checks.move_files()
        checks.delete_gitkeeps()
        checks.remove_empty_trains()
        
        checks.check_lots_name()
        
        checks.check_common_errors()
        checks.check_parsing_yml()
        checks.check_no_regression()
            
        checks.create_important_files()
        
    except Exception as err:
        raise Exception(f"{cst.project}\n{str(err)}\n---\n") from err
