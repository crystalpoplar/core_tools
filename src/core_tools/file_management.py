import json
import os
import shutil
import traceback
from tempfile import NamedTemporaryFile

from . import value_setter
from . import logger

fm_log = logger.mainLog


def getJsonDict(filename, input=False):
    """
    Retrieves the JSON data from a file.

    Parameters:
        filename (str): The name of the JSON file.
        input (bool): Whether to look in the inputs directory.

    Returns:
        dict: The JSON data.
    """
    if input:
        extfilename = value_setter.inputs_dir + filename
    else:
        extfilename = value_setter.main_dir + filename
    if not os.path.isfile(extfilename):
        updateJsonFile({}, filename)
    with open(extfilename) as f:
        data = json.load(f)
    return data


def get_json_dict(filename, input=False):
    """Preferred snake_case API for getJsonDict."""
    return getJsonDict(filename, input=input)


def updateJsonFile(new_data, filepath):
    """
    Updates a JSON file with new data.

    Parameters:
        new_data (dict): The new data to write to the JSON file.
        filepath (str): The path to the JSON file.

    Returns:
        bool: True if the operation succeeds, False otherwise.
    """
    archiveFiles(value_setter.main_dir + filepath)
    try:
        if value_setter.main_dir in filepath:
            dir_path = os.path.dirname(filepath)
        else:
            dir_path = os.path.dirname(value_setter.main_dir + filepath)
        if not os.path.isdir(dir_path):
            fm_log.info(f"Creating directory: {dir_path}")
            os.makedirs(dir_path)

        tempfile = NamedTemporaryFile(mode="w", delete=False, encoding="utf-8", newline="")
        with open(tempfile.name, "w") as jsonFile:
            json.dump(new_data, jsonFile)
        jsonFile.close()

        shutil.copyfile(tempfile.name, value_setter.main_dir + filepath)
        tempfile.close()
        os.remove(tempfile.name)
        fm_log.info(f"Updated JSON file: {filepath}")
    except Exception as e:
        fm_log.error(f"Error updating JSON file: {e}")
        fm_log.error(traceback.format_exc())
        return False
    else:
        return True


def update_json_file(new_data, filepath):
    """Preferred snake_case API for updateJsonFile."""
    return updateJsonFile(new_data, filepath)


def archiveFiles(fileName, archiveCount=10):
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
        archiveFileName = value_setter.archive_dir + base_name + str(archiveCount) + "." + ext
        newArchiveFileName = value_setter.archive_dir + base_name + str(archiveCount + 1) + "." + ext
        if os.path.isfile(archiveFileName):
            if archiveCount + 1 <= maxArchives:
                try:
                    shutil.copyfile(archiveFileName, newArchiveFileName)
                    fm_log.info(f"Archived {archiveFileName} to {newArchiveFileName}")
                except Exception as e:
                    fm_log.error(f"Error archiving file {archiveFileName} to {newArchiveFileName}: {e}")
        archiveCount -= 1

    try:
        if os.path.isfile(fileName):
            relative_path = fileName.replace(value_setter.main_dir, "", 1)
            dir_path = os.path.dirname(value_setter.archive_dir + relative_path)
            if not os.path.isdir(dir_path):
                fm_log.info(f"Creating archive directory: {dir_path}")
                os.makedirs(dir_path)
            archive0 = value_setter.archive_dir + relative_path.rsplit(".", 1)[0] + "0." + fileName.rsplit(".", 1)[1]
            try:
                shutil.copyfile(fileName, archive0)
                fm_log.info(f"Archived {fileName} to {archive0}")
            except Exception as e:
                fm_log.error(f"Error archiving file {fileName} to {archive0}: {e}")
    except Exception as e:
        fm_log.error(f"Error during archiving process for {fileName}: {e}")
        fm_log.error(traceback.format_exc())


def archive_files(file_name, archive_count=10):
    """Preferred snake_case API for archiveFiles."""
    return archiveFiles(file_name, archiveCount=archive_count)


__all__ = [
    "archiveFiles",
    "archive_files",
    "fm_log",
    "getJsonDict",
    "get_json_dict",
    "updateJsonFile",
    "update_json_file",
]
