import logging
from .parser import parse_args
from .configurations import configuration
from .requester import send_message

def main() -> None:
    """Main function where the program start"""
    args = parse_args()

    # Initzialize logger
    logging.basicConfig(
        format="%(asctime)-5s %(name)-15s %(levelname)-8s %(message)s",
        level  = args.log_level,
        #filename='/tmp/python-telegram-bot.log',
        encoding='utf-8'
    )

    # Start program
    configuration(args.path)
    send_message()

if __name__ == "__main__":
    main()
