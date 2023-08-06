import filecmp
import os
import urllib
from zipfile import ZipFile

import pytest
from urllib.request import Request

from onlinezip.OnlineZip import OnlineZip, HTTPRangeRequestUnsupported

ZIP_FILE_URL = 'https://public-onlinezip.s3.eu-west-1.amazonaws.com/zip.zip'
ZIP_FILE_WITH_PWD_URL = 'https://public-onlinezip.s3.eu-west-1.amazonaws.com/zip_with_password.zip'

PASSWORD = 'testtest'.encode()


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    urllib.request.urlretrieve(ZIP_FILE_URL, 'zip.zip')
    urllib.request.urlretrieve(ZIP_FILE_URL, 'zip_with_password.zip')

    # prepare something ahead of all tests
    # request.addfinalizer(finalizer_function)


def test_filenames_are_identical():
    local_zip_file = ZipFile('zip.zip')
    online_zip_file = OnlineZip(ZIP_FILE_URL)

    diff = set(local_zip_file.namelist()) ^ set(online_zip_file.namelist())
    assert not diff


def test_content_of_files_is_identical():
    local_zip_file = ZipFile('zip.zip')
    online_zip_file = OnlineZip(ZIP_FILE_URL)

    local_zip_dir = 'local_zip'
    online_zip_dir = 'online_zip'

    local_zip_file.extractall(path=local_zip_dir)
    online_zip_file.extractall(path=online_zip_dir)

    dir1_contents = set(os.listdir(local_zip_dir))
    dir2_contents = set(os.listdir(online_zip_dir))
    common = list(dir1_contents & dir2_contents)

    common_files = [f for f in common if os.path.isfile(os.path.join(local_zip_dir, f))]

    match, mismatch, errors = filecmp.cmpfiles(
        local_zip_dir,
        online_zip_dir,
        common_files)

    assert len(match) is 3
    assert len(mismatch) is 0


def test_can_get_only_last_file():
    local_zip_file = ZipFile('zip.zip')
    online_zip_file = OnlineZip(ZIP_FILE_URL)

    local_zip_dir = 'local_zip'
    online_zip_dir = 'online_zip'

    local_zip_file.extract(member=local_zip_file.namelist()[-1], path=local_zip_dir)
    online_zip_file.extract(member=online_zip_file.namelist()[-1], path=online_zip_dir)

    dir1_contents = set(os.listdir(local_zip_dir))
    dir2_contents = set(os.listdir(online_zip_dir))
    common = list(dir1_contents & dir2_contents)

    common_files = [f for f in common if os.path.isfile(os.path.join(local_zip_dir, f))]

    match, mismatch, errors = filecmp.cmpfiles(
        local_zip_dir,
        online_zip_dir,
        common_files)

    assert len(match) is 3
    assert len(mismatch) is 0


@pytest.mark.skip(reason="can't find file that accept HEAD request and not returning ranges xd :(")
def test_raise_when_no_ranges():
    with pytest.raises(HTTPRangeRequestUnsupported, match=r'range request is not supported'):
        OnlineZip('https://files.pythonhosted.org/packages/74/4e/c533c3136427be62c38cc0e038cabf167bb54489c2ced2f6df903c456861/conda-4.3.16.tar.gz')
