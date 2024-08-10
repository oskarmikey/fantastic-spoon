import os
import logging
from src.vmt_parser import parse_vmt_file
from src.vmat_converter import convert_vmt_to_vmat
from src.texture_utilities import generate_roughness_maps
from src.file_operations import copy_to_backup_and_delete, copy_with_retry
from src.gui import create_gui

LOG_FILE = "conversion_log.txt"

def main():
    # Setup logging
    setup_logging(LOG_FILE)
    # Call the GUI
    create_gui()

def setup_logging(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.getLogger().addHandler(logging.StreamHandler())

if __name__ == "__main__":
    main()