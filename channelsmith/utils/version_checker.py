"""
Version checking utility for ChannelSmith.

Provides functions to fetch the latest release from GitHub API, compare versions,
and extract release information for the update notification system.
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class UpdateCheckError(Exception):
    """Custom exception for version check failures."""

    pass


def fetch_latest_release() -> Dict:
    """
    Fetch the latest release information from GitHub API.

    Queries https://api.github.com/repos/lod0it/ChannelSmith/releases/latest

    Returns:
        Dictionary with release information including tag_name, html_url, body, and assets

    Raises:
        UpdateCheckError: If network error, rate limit, or invalid response occurs
    """
    url = "https://api.github.com/repos/lod0it/ChannelSmith/releases/latest"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ChannelSmith/0.2.0",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            logger.info("Successfully fetched latest release: %s", data.get("tag_name"))
            return data

    except urllib.error.HTTPError as e:
        if e.code == 403:
            # Rate limit error
            raise UpdateCheckError(
                "GitHub rate limit exceeded. Try again in a few minutes."
            ) from e
        elif e.code == 404:
            # No releases found
            raise UpdateCheckError("No releases found on GitHub yet.") from e
        else:
            logger.error("HTTP error fetching release: %s", e.code)
            raise UpdateCheckError(f"GitHub API error: {e.code}") from e

    except urllib.error.URLError as e:
        logger.error("Network error fetching release: %s", e)
        raise UpdateCheckError(
            "Could not connect to GitHub. Check your internet connection."
        ) from e

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON response from GitHub: %s", e)
        raise UpdateCheckError(
            "Received invalid response from GitHub."
        ) from e

    except Exception as e:
        logger.error("Unexpected error fetching release: %s", e)
        raise UpdateCheckError(f"Unexpected error: {str(e)}") from e


def parse_version(version: str) -> Tuple[int, int, int]:
    """
    Parse a semantic version string into tuple of integers.

    Handles both "0.2.0" and "v0.2.0" formats.

    Args:
        version: Version string (e.g., "0.2.0" or "v0.2.0")

    Returns:
        Tuple of (major, minor, patch) as integers

    Raises:
        ValueError: If version string is malformed
    """
    # Strip whitespace first, then 'v' prefix if present
    version_str = version.strip().lstrip("v")

    try:
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")

        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return (major, minor, patch)

    except (ValueError, IndexError) as e:
        raise ValueError(f"Could not parse version '{version}': {str(e)}") from e


def compare_versions(current: str, latest: str) -> int:
    """
    Compare two semantic versions.

    Args:
        current: Current version string (e.g., "0.2.0")
        latest: Latest available version string (e.g., "0.3.0")

    Returns:
        -1 if update available (current < latest)
        0 if up to date (current == latest)
        1 if dev version (current > latest)
    """
    try:
        current_parsed = parse_version(current)
        latest_parsed = parse_version(latest)

        if current_parsed < latest_parsed:
            return -1  # Update available
        elif current_parsed > latest_parsed:
            return 1  # Dev version
        else:
            return 0  # Up to date

    except ValueError as e:
        logger.warning("Error comparing versions: %s", e)
        # Default to up-to-date if we can't parse
        return 0


def extract_release_summary(body: str, max_length: int = 300) -> str:
    """
    Extract a brief summary from release notes markdown.

    Takes the first paragraph or first 3 bullet points, and truncates to max_length.

    Args:
        body: Full release notes markdown text
        max_length: Maximum length of summary in characters

    Returns:
        Truncated summary string, or empty string if body is empty
    """
    if not body or not body.strip():
        return "No release notes available."

    lines = body.strip().split("\n")
    summary_lines = []
    bullet_count = 0

    for line in lines:
        stripped = line.strip()

        # Stop if we hit a section header
        if stripped.startswith("#"):
            break

        # Collect bullet points
        if stripped.startswith("-") or stripped.startswith("*"):
            summary_lines.append(stripped[1:].strip())
            bullet_count += 1
            if bullet_count >= 3:
                break
        # Collect first paragraph (non-empty, non-bullet lines)
        elif stripped and not summary_lines and not bullet_count:
            summary_lines.append(stripped)
            break

    summary = " ".join(summary_lines)

    # Truncate at word boundary if needed
    if len(summary) > max_length:
        truncated = summary[:max_length].rsplit(" ", 1)[0]
        return truncated + "..."

    return summary if summary else "No release notes available."


def build_downloads_dict(assets: list) -> Dict[str, str]:
    """
    Extract download URLs from release assets.

    Matches asset names to platform identifiers (windows, macos, linux).

    Args:
        assets: List of asset dictionaries from GitHub release

    Returns:
        Dictionary with platform names as keys and download URLs as values
    """
    downloads = {}

    if not assets:
        return downloads

    for asset in assets:
        name = asset.get("name", "").lower()
        url = asset.get("browser_download_url", "")

        if not url:
            continue

        # Match asset name to platform
        # Check for .exe first for Windows specificity
        if name.endswith(".exe") or "windows" in name or "win64" in name:
            downloads["windows"] = url
        elif "darwin" in name or ("macos" in name or "mac" in name):
            downloads["macos"] = url
        elif "linux" in name:
            downloads["linux"] = url

    return downloads
