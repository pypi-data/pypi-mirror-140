import logging
import subprocess
from .parser import parse_args
import getpass

def write_env(env,value):
    """This functions store credentials inside .env file (CREDENTIALS_DIR variable)"""
    # if not os.path.isdir(CREDENTIALS_DIR):
    #     raise Exception("Directory don't exists")
    # else:
    with open("/tmp/python-telegram-bot/.env", "a+") as file:
        logging.info(f"🔧 - Storing variables inside {CREDENTIALS_DIR}/.env")
        file.writelines(f"{env}={value}" + "\n")
        logging.debug(f"🆗 - Variable {env} stored in {CREDENTIALS_DIR}/.env")
    subprocess.call(['chmod', '0700', '/tmp/python-telegram-bot/.env'])


def set_credentials():
    """This function get the credentials from cli argument and save to a .env file that only root can read"""
    args = parse_args()

    if args.interactive:
        logging.info("Mode interactive")
        telegram_token = getpass.getpass("Introduce your telegram token: ")
        write_env("TELEGRAM_TOKEN",telegram_token)
        chat_id = getpass.getpass("Introduce your chat id: ")
        write_env("CHAT_ID",chat_id)
    else:
        if args.telegram_token and args.chat_id:
            logging.info("Mode non-interactive")
            write_env("TELEGRAM_TOKEN",args.telegram_token)
            write_env("CHAT_ID",args.chat_id)
        else:
            raise Exception("Credentials not provided")
