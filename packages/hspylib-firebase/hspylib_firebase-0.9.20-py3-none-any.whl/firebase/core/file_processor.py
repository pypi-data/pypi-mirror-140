#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
   TODO Purpose of the file
   @project: HSPyLib
   hspylib.app.firebase.core
      @file: file_processor.py
   @created: Tue, 4 May 2021
    @author: <B>H</B>ugo <B>S</B>aporetti <B>J</B>unior"
      @site: https://github.com/yorevs/hspylib
   @license: MIT - Please refer to <https://opensource.org/licenses/MIT>

   Copyright 2021, HSPyLib team
"""
import json
import os
from abc import ABC
from fnmatch import fnmatch
from typing import List, Union

from hspylib.core.enums.http_code import HttpCode
from hspylib.core.tools.commons import sysout
from hspylib.core.tools.preconditions import check_argument, check_not_none, check_state
from hspylib.modules.fetch.fetch import get, put
from requests.exceptions import HTTPError

from firebase.entity.file_entry import FileEntry


class FileProcessor(ABC):
    """Utility class to upload and download B64 encoded files"""

    @staticmethod
    def upload_files(url: str, file_paths: List[str], glob_exp: str = '*.*') -> int:
        """Upload files to URL"""
        sysout('Uploading files to Firebase ...')
        file_data = []
        for f_path in file_paths:
            check_state(os.path.exists(f_path), f'Input file "{f_path}" does not exist')
            if os.path.isfile(f_path):
                f_entry = FileProcessor._read_and_encode(f_path)
                file_data.append(f_entry)
            else:
                for file in os.listdir(f_path):
                    filename = os.path.join(f_path, file)
                    if os.path.isfile(filename) and fnmatch(file, glob_exp):
                        f_entry = FileProcessor._read_and_encode(filename)
                        file_data.append(f_entry)
        payload = FileProcessor._to_json(file_data)
        response = put(url, payload)
        check_not_none(response)
        if response.status_code != HttpCode.OK:
            raise HTTPError(
                f'{response.status_code} - Unable to upload into={url} with json_string={payload}')
        paths = ', \n\t'.join([f.path for f in file_data])
        sysout(f"%GREEN%File(s) [\n\t{paths}\n] successfully uploaded to: {url}%NC%")

        return len(file_data)

    @staticmethod
    def download_files(url: str, destination_dir: str) -> int:
        """Download files from URL"""
        check_argument(
            destination_dir and os.path.exists(destination_dir),
            "Unable find destination directory: {}", destination_dir)
        sysout(f'Downloading files from Firebase into "{destination_dir}" ...')
        response = get(url)
        check_not_none(response)
        check_not_none(response.body)
        if response.status_code != HttpCode.OK:
            raise HTTPError(
                f'{response.status_code} - Unable to download from={url} with response={response}')
        file_data = FileProcessor._from_json(response.body)
        if file_data and len(file_data) > 0:
            FileProcessor._decode_and_write(destination_dir, file_data)
            return len(file_data)

        sysout(f'%ORANGE%Database alias was not found in: {url} %NC%')

        return 0

    @staticmethod
    def _read_and_encode(file_path: str) -> FileEntry:
        """Read and B64 encode a file"""
        return FileEntry(file_path).encode()

    @staticmethod
    def _decode_and_write(destination_dir: str, data: Union[dict, List[dict]]) -> None:
        """B64 decode and write entries to file"""
        if isinstance(data, list):
            for entry in data:
                FileEntry \
                    .of(f"{destination_dir}/{os.path.basename(entry['path'])}", entry['data'], entry['size']).save()
            paths = ', \n\t'.join([f['path'] for f in data])
        else:
            FileEntry \
                .of(f"{destination_dir}/{os.path.basename(data['path'])}", data['data'], data['size']).save()
            paths = data['path']
        sysout(f"%GREEN%File(s) [\n\t{paths}\n] successfully downloaded into: {destination_dir}%NC%")

    @staticmethod
    def _to_json(file_data: List[FileEntry]) -> str:
        """Convert the file data into json format"""
        return '[' + ','.join([str(entry) for entry in file_data]) + ']'

    @staticmethod
    def _from_json(file_data: str) -> List[dict]:
        """Convert json format into file data"""
        return json.loads(file_data)
