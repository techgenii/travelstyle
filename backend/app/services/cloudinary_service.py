# This file is part of TravelSytle AI.
#
# Copyright (C) 2025  Trailyn Ventures, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Cloudinary service for image processing and storage.
Handles profile picture uploads with automatic resizing and optimization.
"""

import logging
import uuid

import cloudinary
import cloudinary.api
import cloudinary.uploader

from app.core.config import settings

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Cloudinary service for image processing and storage."""

    def __init__(self):
        """Initialize Cloudinary configuration."""
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

    async def upload_profile_picture(
        self, user_id: str, file_content: bytes, filename: str
    ) -> str | None:
        """
        Upload and process profile picture using Cloudinary.

        Args:
            user_id: The user's ID
            file_content: The file content as bytes
            filename: Original filename

        Returns:
            Public URL of the processed image or None if failed
        """
        try:
            # Generate unique public ID
            file_extension = filename.split(".")[-1] if "." in filename else "jpg"
            public_id = f"travelstyle/profile_pictures/{user_id}/{uuid.uuid4()}"

            # Upload to Cloudinary with transformations
            result = cloudinary.uploader.upload(
                file_content,
                public_id=public_id,
                transformation=[
                    # Resize to 300x300 with smart cropping
                    {
                        "width": 300,
                        "height": 300,
                        "crop": "fill",
                        "gravity": "face",  # Smart face detection
                        "quality": "auto",
                        "fetch_format": "auto",
                    }
                ],
                folder="travelstyle/profile_pictures",
                resource_type="image",
                overwrite=True,
                invalidate=True,  # Clear CDN cache
            )

            if result and result.get("secure_url"):
                logger.info(f"Profile picture uploaded successfully for user {user_id}")
                return result["secure_url"]
            else:
                logger.error(f"Failed to upload profile picture for user {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error uploading profile picture for user {user_id}: {e}")
            return None

    async def delete_profile_picture(self, image_url: str) -> bool:
        """
        Delete a profile picture from Cloudinary.

        Args:
            image_url: The URL of the image to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Extract public ID from URL
            # Cloudinary URLs are in format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/folder/filename.jpg
            url_parts = image_url.split("/")
            if "cloudinary.com" not in image_url:
                logger.warning(f"Not a Cloudinary URL: {image_url}")
                return False

            # Find the upload part and extract public ID
            upload_index = url_parts.index("upload")
            if upload_index == -1:
                logger.warning(f"Could not find upload part in URL: {image_url}")
                return False

            # Get everything after upload/v1234567890/
            public_id_parts = url_parts[upload_index + 2 :]  # Skip upload and version
            public_id = "/".join(public_id_parts).split(".")[0]  # Remove file extension

            # Delete from Cloudinary
            result = cloudinary.uploader.destroy(public_id)

            if result and result.get("result") == "ok":
                logger.info(f"Profile picture deleted successfully: {public_id}")
                return True
            else:
                logger.error(f"Failed to delete profile picture: {public_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting profile picture: {e}")
            return False

    def generate_initials_avatar(self, first_name: str, last_name: str, size: int = 200) -> str:
        """
        Generate an initials avatar using Cloudinary's text overlay.

        Args:
            first_name: User's first name
            last_name: User's last name
            size: Size of the avatar in pixels

        Returns:
            Cloudinary URL for the initials avatar
        """
        try:
            # Get initials
            first_initial = first_name[0].upper() if first_name else ""
            last_initial = last_name[0].upper() if last_name else ""
            initials = f"{first_initial}{last_initial}"

            if not initials:
                initials = "U"  # Default if no name provided

            # Create initials avatar using Cloudinary
            public_id = f"travelstyle/initials/{uuid.uuid4()}"

            # Generate avatar with text overlay
            result = cloudinary.uploader.upload(
                # Create a blank image with purple background
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjOEI1Q0Y2Ii8+Cjwvc3ZnPgo=",
                public_id=public_id,
                transformation=[
                    {"width": size, "height": size, "crop": "fill"},
                    {
                        "overlay": {
                            "font_family": "Arial",
                            "font_size": size // 2,
                            "font_weight": "bold",
                            "text": initials,
                            "color": "white",
                        },
                        "gravity": "center",
                    },
                ],
                folder="travelstyle/initials",
            )

            if result and result.get("secure_url"):
                return result["secure_url"]
            else:
                # Fallback to simple SVG
                return f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0i{size}IiBoZWlnaHQ9Ii{size}IiB2aWV3Qm94PSIwIDAg{size}IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0i{size}IiBoZWlnaHQ9Ii{size}IiBmaWxsPSIjOEI1Q0Y2Ii8+Cjx0ZXh0IHg9Ii{size // 2}IiB5PSI{(size // 2) + 10}IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9Ii{size // 3}Ij57aW5pdGlhbHN9PC90ZXh0Pgo8L3N2Zz4K"

        except Exception as e:
            logger.error(f"Error generating initials avatar: {e}")
            # Return a simple fallback
            return f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0i{size}IiBoZWlnaHQ9Ii{size}IiB2aWV3Qm94PSIwIDAg{size}IiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8cmVjdCB3aWR0aD0i{size}IiBoZWlnaHQ9Ii{size}IiBmaWxsPSIjOEI1Q0Y2Ii8+Cjx0ZXh0IHg9Ii{size // 2}IiB5PSI{(size // 2) + 10}IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9Ii{size // 3}Ij5VPC90ZXh0Pgo8L3N2Zz4K"

    async def test_connection(self) -> bool:
        """
        Test Cloudinary connection and configuration.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get account info
            result = cloudinary.api.ping()
            if result and result.get("status") == "ok":
                logger.info("Cloudinary connection successful")
                return True
            else:
                logger.error("Cloudinary connection failed")
                return False
        except Exception as e:
            logger.error(f"Cloudinary connection error: {e}")
            return False
