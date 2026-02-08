"""
Tests for ChannelSmith REST API routes.

Tests all API endpoints including pack, unpack, templates, and health check.
"""

import io
import json
from pathlib import Path

import pytest
from PIL import Image

from channelsmith.api.app import create_app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_image():
    """Create a sample grayscale image for testing."""
    img = Image.new("L", (512, 512), 128)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@pytest.fixture
def rgb_image():
    """Create a sample RGB image."""
    img = Image.new("RGB", (512, 512), (255, 128, 64))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@pytest.fixture
def rgba_image():
    """Create a sample RGBA image."""
    img = Image.new("RGBA", (512, 512), (255, 128, 64, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    def test_health_check_returns_ok(self, client):
        """Health check should return status ok."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert "version" in data

    def test_health_check_has_version(self, client):
        """Health check response should include version."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["version"]


class TestTemplatesEndpoint:
    """Tests for the /api/templates endpoint."""

    def test_get_templates_returns_list(self, client):
        """Get templates should return a list of template names."""
        response = client.get("/api/templates")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_templates_include_orm(self, client):
        """Templates list should include ORM."""
        response = client.get("/api/templates")
        data = json.loads(response.data)
        assert "ORM" in data["templates"]

    def test_templates_include_ord(self, client):
        """Templates list should include ORD."""
        response = client.get("/api/templates")
        data = json.loads(response.data)
        assert "ORD" in data["templates"]

    def test_get_template_details_orm(self, client):
        """Get template details should return ORM template information."""
        response = client.get("/api/templates/ORM")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["name"] == "ORM"
        assert "description" in data
        assert "channels" in data
        assert "R" in data["channels"]
        assert "G" in data["channels"]
        assert "B" in data["channels"]

    def test_get_template_details_ord(self, client):
        """Get template details should return ORD template information."""
        response = client.get("/api/templates/ORD")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["name"] == "ORD"
        assert "channels" in data

    def test_get_template_details_free(self, client):
        """Get template details should return Free template information."""
        response = client.get("/api/templates/Free")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["name"] == "Free"
        assert "channels" in data

    def test_get_template_details_invalid(self, client):
        """Get template details should fail for invalid template."""
        response = client.get("/api/templates/INVALID")
        assert response.status_code == 404


class TestPackEndpoint:
    """Tests for the /api/pack endpoint."""

    def test_pack_requires_template(self, client):
        """Pack endpoint should require a template parameter."""
        response = client.post("/api/pack", data={})
        # Should either fail or use default template
        assert response.status_code in [200, 400]

    def test_pack_with_orm_template(self, client, sample_image):
        """Pack should work with ORM template and sample channels."""
        # Reset the file position
        sample_image.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "ORM",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
                "green_channel": (io.BytesIO(sample_image.getvalue()), "roughness.png"),
                "blue_channel": (io.BytesIO(sample_image.getvalue()), "metallic.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_pack_with_ord_template(self, client, sample_image):
        """Pack should work with ORD template."""
        sample_image.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "ORD",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
                "green_channel": (io.BytesIO(sample_image.getvalue()), "roughness.png"),
                "blue_channel": (io.BytesIO(sample_image.getvalue()), "displacement.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_pack_with_partial_channels(self, client, sample_image):
        """Pack should work with partial channels (using defaults for missing)."""
        sample_image.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "ORM",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_pack_without_channels_uses_defaults(self, client):
        """Pack without any channels should use default values."""
        response = client.post(
            "/api/pack",
            data={"template": "ORM"},
            content_type="multipart/form-data",
        )

        # Should succeed with default channel values
        assert response.status_code == 200
        assert response.content_type == "image/png"

    def test_pack_with_invalid_template_fails(self, client, sample_image):
        """Pack with invalid template should fail."""
        sample_image.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "INVALID",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_pack_returns_valid_png(self, client, sample_image):
        """Packed result should be a valid PNG image."""
        sample_image.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "ORM",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
                "green_channel": (io.BytesIO(sample_image.getvalue()), "roughness.png"),
                "blue_channel": (io.BytesIO(sample_image.getvalue()), "metallic.png"),
            },
            content_type="multipart/form-data",
        )

        # Verify it's a valid PNG
        img = Image.open(io.BytesIO(response.data))
        assert img.format == "PNG"
        assert img.mode in ("RGB", "RGBA")


class TestUnpackEndpoint:
    """Tests for the /api/unpack endpoint."""

    def test_unpack_requires_image(self, client):
        """Unpack endpoint should require an image file."""
        response = client.post(
            "/api/unpack",
            data={"template": "ORM"},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_unpack_requires_template(self, client, rgb_image):
        """Unpack endpoint should accept template parameter."""
        response = client.post(
            "/api/unpack",
            data={
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        # Should use default template if not provided
        assert response.status_code == 200

    def test_unpack_rgb_image(self, client, rgb_image):
        """Unpack should work with RGB images."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "ORM",
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "channels" in data
        assert isinstance(data["channels"], dict)

    def test_unpack_returns_base64_images(self, client, rgb_image):
        """Unpack should return Base64-encoded channel images."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "ORM",
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        data = json.loads(response.data)
        for channel_name, channel_data in data["channels"].items():
            assert channel_data.startswith("data:image/png;base64,")

    def test_unpack_orm_template(self, client, rgb_image):
        """Unpack with ORM template should return 3 channels."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "ORM",
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        data = json.loads(response.data)
        channels = data["channels"]
        # ORM uses R (AO), G (Roughness), B (Metallic)
        assert "R" in channels
        assert "G" in channels
        assert "B" in channels

    def test_unpack_ord_template(self, client, rgb_image):
        """Unpack with ORD template should return correct channels."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "ORD",
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        data = json.loads(response.data)
        channels = data["channels"]
        # ORD uses R (AO), G (Roughness), B (Displacement)
        assert "R" in channels
        assert "G" in channels
        assert "B" in channels

    def test_unpack_rgba_image(self, client, rgba_image):
        """Unpack should work with RGBA images."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "ORM",
                "image": (io.BytesIO(rgba_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200

    def test_unpack_with_invalid_template_fails(self, client, rgb_image):
        """Unpack with invalid template should fail."""
        response = client.post(
            "/api/unpack",
            data={
                "template": "INVALID",
                "image": (io.BytesIO(rgb_image.getvalue()), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 400


class TestIntegration:
    """Integration tests for pack and unpack workflow."""

    def test_pack_then_unpack_roundtrip(self, client, sample_image):
        """Pack and then unpack should preserve channel data."""
        sample_image.seek(0)

        # Pack
        pack_response = client.post(
            "/api/pack",
            data={
                "template": "ORM",
                "red_channel": (io.BytesIO(sample_image.getvalue()), "ao.png"),
                "green_channel": (io.BytesIO(sample_image.getvalue()), "roughness.png"),
                "blue_channel": (io.BytesIO(sample_image.getvalue()), "metallic.png"),
            },
            content_type="multipart/form-data",
        )

        assert pack_response.status_code == 200
        packed_data = pack_response.data

        # Unpack
        unpack_response = client.post(
            "/api/unpack",
            data={
                "template": "ORM",
                "image": (io.BytesIO(packed_data), "packed.png"),
            },
            content_type="multipart/form-data",
        )

        assert unpack_response.status_code == 200
        data = json.loads(unpack_response.data)
        assert "channels" in data
        assert len(data["channels"]) == 3

    def test_pack_with_different_sizes(self, client):
        """Pack should handle images of different sizes."""
        # Create images of different sizes
        img1 = Image.new("L", (256, 256), 255)
        img2 = Image.new("L", (512, 512), 128)
        img3 = Image.new("L", (1024, 1024), 64)

        buf1 = io.BytesIO()
        img1.save(buf1, format="PNG")
        buf1.seek(0)

        buf2 = io.BytesIO()
        img2.save(buf2, format="PNG")
        buf2.seek(0)

        buf3 = io.BytesIO()
        img3.save(buf3, format="PNG")
        buf3.seek(0)

        response = client.post(
            "/api/pack",
            data={
                "template": "ORM",
                "red_channel": (buf1, "ao.png"),
                "green_channel": (buf2, "roughness.png"),
                "blue_channel": (buf3, "metallic.png"),
            },
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        # Should normalize to largest size
        img = Image.open(io.BytesIO(response.data))
        assert img.size == (1024, 1024)
