from .site_creator import JinjaSiteCreator
import argparse
import logging


def create_site():
    args = handle_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    j = JinjaSiteCreator()
    j.create_site()
    if args.dev:
        j.start_dev_server()

def handle_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", action="store_true", help="Set log level to debug")
    ap.add_argument("--dev", action="store_true", help="Start developement server")
    ap.add_argument("--dev-port", type=int, default=8088, help="Development server port")
    return ap.parse_args()