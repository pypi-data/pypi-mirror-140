"""
Unit tests for norwegianblue cache
"""
import tempfile
from pathlib import Path

from freezegun import freeze_time

import norwegianblue


class TestNorwegianBlueCache:
    def setup_method(self):
        # Choose a new cache dir that doesn't exist
        self.original_cache_dir = norwegianblue.CACHE_DIR
        self.temp_dir = tempfile.TemporaryDirectory()
        norwegianblue.CACHE_DIR = Path(self.temp_dir.name) / "norwegianblue"

    def teardown_method(self):
        # Reset original
        norwegianblue.CACHE_DIR = self.original_cache_dir

    @freeze_time("2018-12-26")
    def test__cache_filename(self):
        # Arrange
        url = "https://endoflife.date/api/python.json"

        # Act
        out = norwegianblue._cache_filename(url)

        # Assert
        assert str(out).endswith("2018-12-26-https-endoflife-date-api-python-json.json")

    def test__load_cache_not_exist(self):
        # Arrange
        filename = Path("file-does-not-exist")

        # Act
        data = norwegianblue._load_cache(filename)

        # Assert
        assert data == {}

    def test__load_cache_bad_data(self):
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Invalid JSON!")

        # Act
        data = norwegianblue._load_cache(Path(f.name))

        # Assert
        assert data == {}

    def test_cache_round_trip(self):
        # Arrange
        filename = norwegianblue.CACHE_DIR / "test_cache_round_trip.json"
        data = "test data"

        # Act
        norwegianblue._save_cache(filename, data)
        new_data = norwegianblue._load_cache(filename)

        # Tidy up
        filename.unlink()

        # Assert
        assert new_data == data

    @freeze_time("2021-10-25")
    def test__clear_cache_now(self):
        # Arrange
        # Create old cache file
        cache_file_old = norwegianblue.CACHE_DIR / "2021-10-24-old-cache-file.json"
        cache_file_new = norwegianblue.CACHE_DIR / "2021-10-25-new-cache-file.json"
        norwegianblue._save_cache(cache_file_old, data={})
        norwegianblue._save_cache(cache_file_new, data={})
        assert cache_file_new.exists()
        assert cache_file_old.exists()

        # Act
        norwegianblue._clear_cache_now()

        # Assert
        assert not cache_file_old.exists()
        assert not cache_file_new.exists()

    @freeze_time("2021-10-25")
    def test__clear_cache(self):
        # Arrange
        # Create old cache file
        cache_file_old = norwegianblue.CACHE_DIR / "2021-10-24-old-cache-file.json"
        cache_file_new = norwegianblue.CACHE_DIR / "2021-10-25-new-cache-file.json"
        norwegianblue._save_cache(cache_file_old, data={})
        norwegianblue._save_cache(cache_file_new, data={})
        assert cache_file_new.exists()
        assert cache_file_old.exists()

        # Act
        norwegianblue._clear_cache()

        # Assert
        assert not cache_file_old.exists()
        assert cache_file_new.exists()
