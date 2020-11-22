import os
import pathlib

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from faker import Faker

import src.files_sort_out.files_sort_out as app


def create_files(path: pathlib.Path, images=False):
    fake = Faker()
    total_files = 5
    image_files = 4

    if images:
        total_files = total_files - image_files
        for _ in range(image_files):
            # TODO Add videos as well
            name = fake.file_name(category='image')
            file = path / name
            file.touch()

    for _ in range(total_files):
        name = fake.file_name()
        file = path / name
        file.touch()

# TODO Move fixtures to conftest.py file
@pytest.fixture()
def temp_filesystem(tmp_path, faker) -> pathlib.Path:
    """Make a dummy file system, and return a Path() to it."""
    test_filesystem = tmp_path / "test_filesystem"
    test_filesystem.mkdir()

    for top_dir in range(3):
        top_dir_name = test_filesystem / f"0{top_dir}"
        top_dir_name.mkdir()
        create_files(top_dir_name)

        for sub_dir in range(3):
            sub_dir_name = top_dir_name / f"0{sub_dir}"
            sub_dir_name.mkdir()
            create_files(sub_dir_name)

            for sub_sub_dir in range(3):
                sub_sub_dir_name = sub_dir_name / f"0{sub_sub_dir}"
                sub_sub_dir_name.mkdir()

                images = sub_sub_dir == 2
                create_files(sub_sub_dir_name, images)

    return test_filesystem


# def test_dummy(temp_filesystem):
#     print("New test")
#     files = list(temp_filesystem.glob("**/*.*"))
#     for f in files:
#         print(str(f))
#     assert False

# def test_init():
#     with patch.object(app, "cli", return_value=None) as cli:
#         with patch.object(app, "__name__", "__main__"):
#             __import__("src.files_sort_out.files_sort_out")
#             assert cli.called_once
#
#
# def test_help():
#     """
#     Test CLI when called with help options
#     """
#     runner = CliRunner()
#     result = runner.invoke(app.cli, ["--help"])
#     assert result.exit_code == 0


def test_list_image_folders(temp_filesystem):
    """
    Test that collect output list of folders where images make up 80% of files
    """
    os.chdir(temp_filesystem)
    with patch("src.files_sort_out.files_sort_out.collect") as listimagefolders:
        runner = CliRunner()
        result = runner.invoke(app.cli, ["collect", str(temp_filesystem)])
        assert result.exit_code == 0
        assert listimagefolders.called_once

        assert "00/00/02" in result.output
        assert "00/01/02" in result.output
        assert "00/02/02" in result.output

        assert "/01/00/02" in result.output
        assert "/01/01/02" in result.output
        assert "/01/02/02" in result.output

        assert "/02/00/02" in result.output
        assert "/02/01/02" in result.output
        assert "/02/02/02" in result.output


def test_copy_all_folders(temp_filesystem):
    """
    Test that collect output list of folders where images make up 80% of files
    """
    os.chdir(temp_filesystem)
    with patch("src.files_sort_out.files_sort_out.collect") as listimagefolders:
        runner = CliRunner()
        result = runner.invoke(app.cli, ["collect", str(temp_filesystem)])
        assert result.exit_code == 0
        assert listimagefolders.called_once

        dest = temp_filesystem / 'destination'
        result = runner.invoke(app.cli, ["copy", str(dest)])
        assert result.exit_code == 0
        assert listimagefolders.called_once

        dirs = sorted(list(dest.iterdir()))
        dirs = map(lambda x: x.name)
        expected = ['00_02', '01_02', '02_02', '03_02', '04_02', '05_02', '06_02', '07_02', '08_02']

        assert expected == dirs

