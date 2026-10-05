"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.volunteer_hours import VolunteerHours

__all__ = ["User", "VolunteerHours"]
