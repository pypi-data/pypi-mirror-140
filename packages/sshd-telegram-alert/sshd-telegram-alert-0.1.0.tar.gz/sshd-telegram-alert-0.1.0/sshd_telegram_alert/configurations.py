import os
import logging
from .credentials import set_credentials

def validate_dir(dir: str) -> None:
    """Validate if the directory where you are going to save credentials exists"""
    logging.info("Validating if directory exists or could be created")
    if not os.path.isdir(dir):
        logging.warning(f"Directory {dir} don't exists")
        create_directory = input(str(f"Do you want to create a new one ({dir}) [yes/no]?: "))
        if create_directory == "yes":
            os.mkdir(dir)
        else:
            raise Exception(f"Anwer should be yes or not, can't create the directory {dir}")
    else:
        logging.info("Directory exists")

def validate(dir: str) -> None:
    """Check if file exists before create a new one"""
    validate_dir(dir)
    logging.info("Validating if .env exists")
    if os.path.isfile(dir+"/.env"):
        logging.info("File .env exists")
        if input(str("Do you want to remove the file [yes/no]?: ")) == "yes":
            os.remove(CREDENTIALS_DIR+"/.env")
            set_credentials()
    else:
        logging.warning("🔧 - File .env not found")
        set_credentials()

def configuration(dir: str) -> None:
    """Validate directory and if .env exists"""
    validate(dir)
