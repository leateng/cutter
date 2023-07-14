class User:
    def __init__(
        self,
        id=None,
        name=None,
        password=None,
        role=None,
        department=None,
        created_at=None,
    ) -> None:
        self._id = id
        self._name = name
        self._password = password
        self._role = role
        self._department = department
        self._created_at = created_at


class Recipe:
    def __init__(
        self,
        id=None,
        name=None,
        file_name=None,
        file_content=None,
        thumbnail=None,
        tool_radius=None,
        offset=None,
        rotation_speed=None,
        created_by=None,
        created_at=None,
        updated_by=None,
        updated_at=None,
    ) -> None:
        self._id = id
        self._name = name
        self._file_name = file_name
        self._file_content = file_content
        self._thumbnail = thumbnail
        self._tool_radius = tool_radius
        self._offset = offset
        self._rotation_speed = rotation_speed
        self._created_by = created_by
        self._created_at = created_at
        self._updated_by = updated_by
        self._updated_at = updated_at
