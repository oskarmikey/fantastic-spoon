import os
import shutil
import time
import psutil
import logging

def is_file_in_use(file_path):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for item in proc.open_files():
                if file_path == item.path:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def copy_with_retry(src, dst, retries=5, delay=0.05):
    for attempt in range(retries):
        try:
            if not is_file_in_use(src):
                shutil.copy2(src, dst)
                return True
            else:
                logging.warning(f"File {src} is in use, retrying...")
        except (PermissionError, FileNotFoundError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error(f"Failed to copy {src} to {dst} after {retries} attempts: {e}")
                return False
        time.sleep(delay)
    return False

def copy_to_backup_and_delete(src, backup_folder, base_path):
    try:
        relative_path = os.path.relpath(src, base_path)
        backup_path = os.path.join(backup_folder, relative_path)
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        if copy_with_retry(src, backup_path):
            os.remove(src)
            logging.info(f"Copied and deleted file from {src} to {backup_path}")
            return True
        else:
            logging.error(f"Failed to copy file to backup: {src}")
            return False
    except Exception as e:
        logging.error(f"Error copying file to backup and deleting {src}: {e}")
        return False
