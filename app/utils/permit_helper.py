from functools import wraps
from flask import current_app, abort
from flask_login import current_user
from permit import Permit
import asyncio
from functools import partial


def get_permit():
    """Initialize and return Permit.io client"""
    try:
        return Permit(
            pdp=current_app.config["PERMIT_PDP_URL"],
            token=current_app.config["PERMIT_API_KEY"],
        )
    except Exception as e:
        current_app.logger.error(f"Failed to initialize Permit client: {str(e)}")
        raise


def check_permission(action: str, resource: str):
    """
    Async decorator to check if user has permission to perform action on resource
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            permit = get_permit()
            try:
                # Build the resource context
                resource_context = {
                    "type": resource,
                }

                # Add resource ID if available in kwargs
                if "id" in kwargs:
                    resource_context["id"] = str(kwargs["id"])

                # Run permission check in event loop
                loop = asyncio.get_event_loop()
                allowed = await permit.check(
                    str(current_user.id), action, resource_context
                )

                if not allowed:
                    current_app.logger.warning(
                        f"Permission denied for user {current_user.id}: {action} on {resource}"
                    )
                    abort(403)

                return await f(*args, **kwargs)

            except Exception as e:
                current_app.logger.error(f"Authorization error: {str(e)}")
                abort(500)

        return decorated_function

    return decorator


async def create_permit_user(user):
    """Create a user in Permit.io"""
    permit = get_permit()
    try:
        await permit.api.users.sync(
            {
                "key": str(user.id),
                "email": user.email,
                "first_name": user.username,
                "last_name": user.username,
            }
        )
    except Exception as e:
        current_app.logger.error(f"User sync failed: {str(e)}")
        raise


async def assign_role(user_id: str, role: str):
    """Assign a role to a user in Permit.io"""
    permit = get_permit()
    try:
        await permit.api.users.assign_role(
            {"user": user_id, "role": role, "tenant": "default"}
        )
    except Exception as e:
        current_app.logger.error(f"Role assignment failed: {str(e)}")
        raise
