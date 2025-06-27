import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_user_profile(user_id: str, profile_data: dict):
    """Saves or updates a user's profile information."""
    try:
        data_to_save = {"user_id": user_id}
        data_to_save.update(profile_data) # Include all profile data
        response = supabase.table("user_profiles").upsert(
            data_to_save,
            on_conflict="user_id"
        ).execute()
        return response.data
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return None

def get_user_profile(user_id: str):
    """Retrieves a user's profile information."""
    try:
        response = supabase.table("user_profiles").select("*").eq("user_id", user_id).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None

def save_meal_plan(user_id: str, meal_plan_details: dict):
    """Saves a confirmed meal plan for a user."""
    try:
        response = supabase.table("meal_plans").insert(
            {"user_id": user_id, "meal_plan_details": meal_plan_details}
        ).execute()
        return response.data
    except Exception as e:
        print(f"Error saving meal plan: {e}")
        return None

def get_meal_plans(user_id: str):
    """Retrieves all meal plans for a user."""
    try:
        response = supabase.table("meal_plans").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error retrieving meal plans: {e}")
        return None 