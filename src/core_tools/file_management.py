import json
import os
import shutil
import traceback
from tempfile import NamedTemporaryFile

from . import value_setter
from . import logger

LOG = logger.create_logger("core_tools.file_management", "file_management.log")

def get_json_dict(filename, input=False, path: str = value_setter.main_dir):
    """
    Retrieves the JSON data from a file.

    Parameters:
        filename (str): The name of the JSON file.
        input (bool): Whether to look in the inputs directory.

    Returns:
        dict: The JSON data.
    """
    if input:
        extfilename = os.path.join(value_setter.inputs_dir, filename)
    elif path:
        extfilename = os.path.join(path, filename)
    else:
        extfilename = os.path.join(value_setter.main_dir, filename)
    if not os.path.isfile(extfilename):
        update_json_dict({}, extfilename)
    with open(extfilename) as f:
        data = json.load(f)
    return data

def update_json_dict(new_data, filepath, log: logger.create_logger = LOG, archive: bool = True):
    """
    Updates a JSON file with new data.

    Parameters:
        new_data (dict): The new data to write to the JSON file.
        filepath (str): The path to the JSON file.

    Returns:
        bool: True if the operation succeeds, False otherwise.
    """
    if archive:
        archive_files(os.path.join(value_setter.main_dir, filepath))
    try:
        if value_setter.main_dir in filepath:
            dir_path = os.path.dirname(filepath)
        else:
            dir_path = os.path.dirname(os.path.join(value_setter.main_dir, filepath))
        if not os.path.isdir(dir_path):
            log.info(f"Creating directory: {dir_path}")
            os.makedirs(dir_path)

        tempfile = NamedTemporaryFile(mode="w", delete=False, encoding="utf-8", newline="")
        with open(tempfile.name, "w") as jsonFile:
            json.dump(new_data, jsonFile)
        jsonFile.close()

        shutil.copyfile(tempfile.name, os.path.join(value_setter.main_dir, filepath))
        tempfile.close()
        os.remove(tempfile.name)
        log.info(f"Updated JSON file: {filepath}")
    except Exception as e:
        log.error(f"Error updating JSON file: {e}")
        log.error(traceback.format_exc())
        return False
    else:
        return True

def archive_files(fileName, archiveCount=10, log: logger.create_logger = LOG):
    """
    Archives the specified file by keeping up to `archiveCount` versions.
    Older archives are shifted up by one index, and the latest file is saved as archive 0.

    Parameters:
        fileName (str): The full path of the file to archive.
        archiveCount (int): The number of archive versions to keep (default is 10).

    Notes:
        - Uses value_setter.archive_dir and value_setter.main_dir for directory paths.
        - Logs all major actions and errors.
    """
    maxArchives = archiveCount
    while archiveCount >= 0:
        base_name, ext = os.path.splitext(fileName)
        ext = ext.lstrip(".")
        archiveFileName = os.path.join(value_setter.archive_dir, f"{base_name}{archiveCount}.{ext}")
        newArchiveFileName = os.path.join(value_setter.archive_dir, f"{base_name}{archiveCount + 1}.{ext}")
        if os.path.isfile(archiveFileName):
            if archiveCount + 1 <= maxArchives:
                try:
                    shutil.copyfile(archiveFileName, newArchiveFileName)
                    log.info(f"Archived {archiveFileName} to {newArchiveFileName}")
                except Exception as e:
                    log.error(f"Error archiving file {archiveFileName} to {newArchiveFileName}: {e}")
        archiveCount -= 1

    try:
        if os.path.isfile(fileName):
            relative_path = fileName.replace(value_setter.main_dir, "", 1)
            dir_path = os.path.dirname(value_setter.archive_dir + relative_path)
            if not os.path.isdir(dir_path):
                log.info(f"Creating archive directory: {dir_path}")
                os.makedirs(dir_path)
            archive0 = os.path.join(value_setter.archive_dir, relative_path.rsplit(".", 1)[0] + "0." + fileName.rsplit(".", 1)[1])
            try:
                shutil.copyfile(fileName, archive0)
                log.info(f"Archived {fileName} to {archive0}")
            except Exception as e:
                log.error(f"Error archiving file {fileName} to {archive0}: {e}")
    except Exception as e:
        log.error(f"Error during archiving process for {fileName}: {e}")
        log.error(traceback.format_exc())
