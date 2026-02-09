"""
Unit tests for version_checker utility module.

Tests version comparison, parsing, release fetching, and summary extraction.
"""

import json
from unittest import mock
import urllib.error
import pytest

from channelsmith.utils.version_checker import (
    parse_version,
    compare_versions,
    extract_release_summary,
    build_downloads_dict,
    fetch_latest_release,
    UpdateCheckError,
)


class TestParseVersion:
    """Tests for parse_version function."""

    def test_parse_version_standard(self):
        """Should parse standard semantic version."""
        assert parse_version("0.2.0") == (0, 2, 0)
        assert parse_version("1.0.0") == (1, 0, 0)
        assert parse_version("2.3.4") == (2, 3, 4)

    def test_parse_version_with_v_prefix(self):
        """Should handle v prefix."""
        assert parse_version("v0.2.0") == (0, 2, 0)
        assert parse_version("v1.0.0") == (1, 0, 0)

    def test_parse_version_with_whitespace(self):
        """Should handle leading/trailing whitespace."""
        assert parse_version("  0.2.0  ") == (0, 2, 0)
        assert parse_version("  v1.0.0  ") == (1, 0, 0)

    def test_parse_version_invalid_format(self):
        """Should raise ValueError for malformed versions."""
        with pytest.raises(ValueError):
            parse_version("1.0")

        with pytest.raises(ValueError):
            parse_version("1.0.0.0")

        with pytest.raises(ValueError):
            parse_version("not-a-version")


class TestCompareVersions:
    """Tests for compare_versions function."""

    def test_compare_versions_update_available(self):
        """Should return -1 when update is available."""
        assert compare_versions("0.2.0", "0.3.0") == -1
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("0.1.9", "0.2.0") == -1

    def test_compare_versions_up_to_date(self):
        """Should return 0 when versions match."""
        assert compare_versions("0.2.0", "0.2.0") == 0
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_compare_versions_dev_version(self):
        """Should return 1 when current is newer than latest."""
        assert compare_versions("0.3.0", "0.2.0") == 1
        assert compare_versions("2.0.0", "1.0.0") == 1

    def test_compare_versions_with_v_prefix(self):
        """Should handle v prefix in both versions."""
        assert compare_versions("v0.2.0", "v0.3.0") == -1
        assert compare_versions("v1.0.0", "v1.0.0") == 0

    def test_compare_versions_invalid_defaults_to_up_to_date(self):
        """Should default to up-to-date for unparseable versions."""
        assert compare_versions("invalid", "0.2.0") == 0
        assert compare_versions("0.2.0", "invalid") == 0


class TestExtractReleaseSummary:
    """Tests for extract_release_summary function."""

    def test_extract_release_summary_single_paragraph(self):
        """Should extract first paragraph."""
        body = "This is the first paragraph.\nThis is the second paragraph."
        result = extract_release_summary(body)
        assert "first paragraph" in result

    def test_extract_release_summary_bullet_points(self):
        """Should extract first 3 bullet points."""
        body = "- Feature 1\n- Feature 2\n- Feature 3\n- Feature 4"
        result = extract_release_summary(body)
        assert "Feature 1" in result
        assert "Feature 2" in result
        assert "Feature 3" in result

    def test_extract_release_summary_truncate_long_text(self):
        """Should truncate to max_length at word boundary."""
        long_text = "A" * 350  # Longer than default max_length (300)
        result = extract_release_summary(long_text)
        assert len(result) <= 310  # Some buffer for ellipsis
        assert result.endswith("...")

    def test_extract_release_summary_stops_at_header(self):
        """Should stop at markdown header."""
        body = "First paragraph.\n## Features\n- More content"
        result = extract_release_summary(body)
        assert "first paragraph" in result.lower()
        assert "Features" not in result

    def test_extract_release_summary_empty_body(self):
        """Should return default message for empty body."""
        assert extract_release_summary("") == "No release notes available."
        assert extract_release_summary(None) == "No release notes available."

    def test_extract_release_summary_custom_max_length(self):
        """Should respect custom max_length."""
        body = "A" * 500
        result = extract_release_summary(body, max_length=50)
        assert len(result) <= 60


class TestBuildDownloadsDict:
    """Tests for build_downloads_dict function."""

    def test_build_downloads_dict_all_platforms(self):
        """Should extract URLs for all platforms."""
        assets = [
            {
                "name": "ChannelSmith-Windows.zip",
                "browser_download_url": "https://example.com/windows.zip",
            },
            {
                "name": "ChannelSmith-macOS.tar.gz",
                "browser_download_url": "https://example.com/macos.tar.gz",
            },
            {
                "name": "ChannelSmith-Linux.tar.gz",
                "browser_download_url": "https://example.com/linux.tar.gz",
            },
        ]

        result = build_downloads_dict(assets)

        assert result["windows"] == "https://example.com/windows.zip"
        assert result["macos"] == "https://example.com/macos.tar.gz"
        assert result["linux"] == "https://example.com/linux.tar.gz"

    def test_build_downloads_dict_partial_platforms(self):
        """Should include only available platforms."""
        assets = [
            {
                "name": "ChannelSmith-Windows.zip",
                "browser_download_url": "https://example.com/windows.zip",
            },
        ]

        result = build_downloads_dict(assets)

        assert "windows" in result
        assert "macos" not in result
        assert "linux" not in result

    def test_build_downloads_dict_empty_assets(self):
        """Should return empty dict for no assets."""
        assert build_downloads_dict([]) == {}
        assert build_downloads_dict(None) == {}

    def test_build_downloads_dict_missing_url(self):
        """Should skip assets without download URL."""
        assets = [
            {"name": "ChannelSmith-Windows.zip"},  # No browser_download_url
        ]

        result = build_downloads_dict(assets)
        assert "windows" not in result

    def test_build_downloads_dict_variant_names(self):
        """Should match variant naming conventions."""
        assets = [
            {
                "name": "ChannelSmith-win64.exe",
                "browser_download_url": "https://example.com/win64.exe",
            },
            {
                "name": "ChannelSmith-darwin.dmg",
                "browser_download_url": "https://example.com/darwin.dmg",
            },
        ]

        result = build_downloads_dict(assets)
        assert "windows" in result
        assert "macos" in result


class TestFetchLatestRelease:
    """Tests for fetch_latest_release function."""

    @mock.patch("urllib.request.urlopen")
    def test_fetch_latest_release_success(self, mock_urlopen):
        """Should successfully fetch release from GitHub API."""
        response_data = {
            "tag_name": "v0.3.0",
            "html_url": "https://github.com/lod0it/ChannelSmith/releases/tag/v0.3.0",
            "body": "# Release Notes\n- Feature 1\n- Feature 2",
            "assets": [
                {
                    "name": "ChannelSmith-Windows.zip",
                    "browser_download_url": "https://example.com/windows.zip",
                }
            ],
            "published_at": "2026-02-09T12:00:00Z",
        }

        mock_response = mock.MagicMock()
        mock_response.read.return_value = json.dumps(response_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = fetch_latest_release()

        assert result["tag_name"] == "v0.3.0"
        assert result["html_url"] == "https://github.com/lod0it/ChannelSmith/releases/tag/v0.3.0"
        assert "assets" in result

    @mock.patch("urllib.request.urlopen")
    def test_fetch_latest_release_timeout(self, mock_urlopen):
        """Should handle network timeout."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection timed out")

        with pytest.raises(UpdateCheckError) as exc_info:
            fetch_latest_release()

        assert "could not connect" in str(exc_info.value).lower()

    @mock.patch("urllib.request.urlopen")
    def test_fetch_latest_release_rate_limit(self, mock_urlopen):
        """Should handle GitHub rate limit (HTTP 403)."""
        http_error = urllib.error.HTTPError(
            "https://api.github.com/repos/lod0it/ChannelSmith/releases/latest",
            403,
            "Forbidden",
            {},
            None,
        )
        mock_urlopen.side_effect = http_error

        with pytest.raises(UpdateCheckError) as exc_info:
            fetch_latest_release()

        assert "rate limit" in str(exc_info.value).lower()

    @mock.patch("urllib.request.urlopen")
    def test_fetch_latest_release_not_found(self, mock_urlopen):
        """Should handle no releases found (HTTP 404)."""
        http_error = urllib.error.HTTPError(
            "https://api.github.com/repos/lod0it/ChannelSmith/releases/latest",
            404,
            "Not Found",
            {},
            None,
        )
        mock_urlopen.side_effect = http_error

        with pytest.raises(UpdateCheckError) as exc_info:
            fetch_latest_release()

        assert "no releases" in str(exc_info.value).lower()

    @mock.patch("urllib.request.urlopen")
    def test_fetch_latest_release_malformed_json(self, mock_urlopen):
        """Should handle malformed JSON response."""
        mock_response = mock.MagicMock()
        mock_response.read.return_value = b"invalid json {["
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(UpdateCheckError) as exc_info:
            fetch_latest_release()

        assert "invalid response" in str(exc_info.value).lower()
