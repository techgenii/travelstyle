"""
User utility functions for TravelStyle AI application.
"""

def extract_user_profile(user):
    """Extract user profile information from a Supabase user object."""
    if not user:
        return None

    # Get names from user metadata
    first_name = None
    last_name = None

    # Try different ways to access metadata
    if hasattr(user, 'user_metadata') and user.user_metadata:
        # If user_metadata is a dictionary
        if isinstance(user.user_metadata, dict):
            first_name = user.user_metadata.get('first_name')
            last_name = user.user_metadata.get('last_name')
        # If user_metadata is an object with attributes
        else:
            first_name = getattr(user.user_metadata, 'first_name', None)
            last_name = getattr(user.user_metadata, 'last_name', None)

    return {
        "id": user.id,
        "email": user.email,
        "first_name": first_name,
        "last_name": last_name,
        "created_at": getattr(user, 'created_at', None),
        "updated_at": getattr(user, 'updated_at', None),
        "email_confirmed_at": getattr(user, 'email_confirmed_at', None),
        "last_sign_in_at": getattr(user, 'last_sign_in_at', None)
    }
