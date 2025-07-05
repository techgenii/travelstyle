"""
User utility functions for TravelStyle AI application.
"""

def extract_user_profile(user):
    """Extract user profile information from a Supabase user object."""
    if not user:
        return None
    return {
        "id": user.id,
        "email": user.email,
        "first_name": getattr(user.user_metadata, 'first_name', None)
        if hasattr(user, 'user_metadata') else None,
        "last_name": getattr(user.user_metadata, 'last_name', None)
        if hasattr(user, 'user_metadata') else None,
        "created_at": getattr(user, 'created_at', None),
        "updated_at": getattr(user, 'updated_at', None),
        "email_confirmed_at": getattr(user, 'email_confirmed_at', None),
        "last_sign_in_at": getattr(user, 'last_sign_in_at', None)
    }
