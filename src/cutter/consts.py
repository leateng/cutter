from typing import Optional

from cutter.models import User


VERSION: str = "1.0.0"
ROLE_NAMES: dict[str, str] = {"0": "Admin", "1": "PM", "2": "PE", "3": "OP"}
SUPPORTED_ENTITY_TYPES: list[str] = ["LINE", "ARC", "CIRCLE"]
COLUMN_NAME_MAPPING: list[str] = ["name", "department", "role", "created_at"]
CURRENT_USER: Optional[User] = None
PLC_ADDR: str = "169.254.54.209.1.1"
