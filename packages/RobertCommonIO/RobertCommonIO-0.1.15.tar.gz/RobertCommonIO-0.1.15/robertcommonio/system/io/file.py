import csv
import json
from typing import Any, NamedTuple
from enum import Enum

import pyzipper

from robertcommonbasic.basic.os.file import get_file_folder, rename_file
from robertcommonbasic.basic.os.path import create_dir_if_not_exist

class FileType(Enum):
    AES_ZIP = 'aes_zip'
    CSV = 'csv'
    JSON = 'json'
    Excel = 'excel'


class FileConfig(NamedTuple):
    PATH: str
    MODE: FileType
    NAME: str = ''
    PSW: str = ''
    FORMAT: str = 'w+'  # r+ 读写  w+ 覆盖 a+ 追加 rb+ 二进制
    ENCODE: str = 'utf-8'


class FileAccessor:

    def __init__(self, config: FileConfig):
        self.config = config

    def save(self, file_content: Any, file_mode: str='w+'):
        create_dir_if_not_exist(get_file_folder(self.config.PATH))

        if self.config.MODE == FileType.AES_ZIP:
            return self.__save_aes_zip(self.config.PATH, self.config.NAME, file_content, self.config.PSW)
        elif self.config.MODE == FileType.CSV:
            return self.__save_csv_file(self.config.PATH, file_content, file_mode, self.config.ENCODE)
        elif self.config.MODE == FileType.JSON:
            return self.__save_json_file(self.config.PATH, file_content, file_mode, self.config.ENCODE)

    def __save_aes_zip(self, zip_path: str, file_name: str, file_content: Any, zip_pw: Any = None):
        tmp_path = f"{zip_path}.tmp"
        with pyzipper.AESZipFile(tmp_path, 'a', compression=pyzipper.ZIP_DEFLATED) as zip:
            if isinstance(zip_pw, str):
                zip.setpassword(zip_pw.encode('utf-8'))
            zip.setencryption(pyzipper.WZ_AES, nbits=256)
            if isinstance(file_content, str):
                zip.writestr(file_name, data=file_content)
        rename_file(tmp_path, zip_path)

    def __save_csv_file(self, file_path: str, file_content: Any, file_mode: str='w+', encoding: str='utf-8', newline: str=''):
        tmp_path = f"{file_path}.tmp"
        with open(file_path, mode=file_mode, encoding=encoding) as f:
            if isinstance(file_content, str):
                f.write(file_content)
            elif isinstance(file_content, bytes):
                f.write(file_content)
            elif isinstance(file_content, list):
                for content in file_content:
                    f.write(content)
        rename_file(tmp_path, file_path)

    def __save_json_file(self, file_path: str, file_content: Any, file_mode: str='w+', encoding: str='utf-8', newline: str=''):
        tmp_path = f"{file_path}.tmp"
        with open(file_path, mode=file_mode, encoding=encoding, newline=newline) as f:
            writer = csv.DictWriter(f, fieldnames=file_content[0].keys())
            writer.writeheader()
            for row in file_content:
                writer.writerow(row)
        rename_file(tmp_path, file_path)

    def read(self):
        if self.config.MODE == FileType.AES_ZIP:
            return self.__read_aes_zip(self.config.PATH, self.config.NAME, self.config.PSW)
        elif self.config.MODE == FileType.CSV:
            return self.__read_csv_dict(self.config.PATH)
        elif self.config.MODE == FileType.JSON:
            return self.__read_json_dict(self.config.PATH)

    def __read_aes_zip(self, zip_path: str, file_name: str='', zip_pw: Any = None) -> dict:
        results = {}
        with pyzipper.AESZipFile(zip_path) as zip:
            if isinstance(zip_pw, str):
                zip.setpassword(zip_pw.encode('utf-8'))
            if len(file_name) > 0:
                results[file_name] = zip.read(file_name)
            else:
                for file in zip.namelist():
                    results[file] = zip.read(file)
        return results

    def __read_csv_dict(self, file_path: str, newline: str=''):
        with open(file_path, newline=newline) as file:
            reader = csv.DictReader(file)
            return [row for row in reader]

    def __read_csv_row(self, file_path: str, newline: str=''):
        with open(file_path, newline=newline) as file:
            reader = csv.reader(file)
            return [row for row in reader]

    def __write_csv_row(self, file_path: str, rows: list, file_mode: str='w', newline: str=''):
        with open(file_path, file_mode, newline=newline) as file:
            writer = csv.writer(file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                writer.writerow(row)

    def __write_csv_dict(self, file_path: str, rows: dict, file_mode: str='w', newline: str=''):
        with open(file_path, file_mode, newline=newline) as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

    def __read_json_dict(self, file_path: str):
        with open(file_path) as file:
            return json.loads(file.read())