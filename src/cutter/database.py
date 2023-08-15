from datetime import datetime
import os
from pathlib import Path
from typing import Optional, Tuple
from qtpy.QtSql import QSqlDatabase, QSqlQuery
from cutter.models import Recipe, User
from IPython import embed


local_app_data = Path(os.environ["LOCALAPPDATA"])
cutter_data_path = local_app_data / "cmp-cutter"
database_path = cutter_data_path / "data.db"
DXF_PATH = cutter_data_path / "dxf"

if not os.path.exists(cutter_data_path):
    os.makedirs(cutter_data_path)

if not os.path.exists(DXF_PATH):
    os.makedirs(DXF_PATH)

DB_CONN = QSqlDatabase.addDatabase("QSQLITE")
DB_CONN.setDatabaseName(str(database_path))
DB_CONN.open()


def init_db():
    query = QSqlQuery(DB_CONN)
    tables = DB_CONN.tables()

    if "users" not in tables:
        ret = query.exec_(
            """
            CREATE TABLE users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name VARCHAR,
              password VARCHAR,
              role INTEGER,
              department VARCHAR,
              created_at TIMESTAMP
            )
            """
        )
        print(f"insert users table: {ret}")

        query.prepare(
            """
            INSERT INTO users (name, role, password, created_at)
            VALUES(?, ?, ?, ?)
            """
        )
        query.addBindValue("root")
        query.addBindValue(0)
        query.addBindValue("root")
        query.addBindValue(str(datetime.now()))
        ret = query.exec_()
        print(f"insert root user: {ret}")

    if "recipes" not in tables:
        ret = query.exec_(
            """
            CREATE TABLE recipes (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name VARCHAR,
              file_name VARCHAR,
              thumbnail BLOB,
              tool_radius REAL,
              cutter_offset REAL,
              cutter_deepth REAL,
              rotation_speed INTEGER,
              created_by INTEGER,
              created_at TIMESTAMP,
              updated_by INTEGER,
              updated_at TIMESTAMP
            )
            """
        )
        print(f"insert recipes table: {ret}")


def validate_login(name, password):
    query = QSqlQuery(DB_CONN)
    query.prepare("SELECT * FROM users WHERE name = :name and password = :password")
    query.bindValue(":name", name)
    query.bindValue(":password", password)
    if not query.exec_():
        print("sql error:", query.lastError().text())
        return None
    elif not query.first():
        print("login user not found")
        return None
    else:
        id = query.value("id")
        name = query.value("name")
        role = query.value("role")
        department = query.value("department")
        created_at = query.value("created_at")
        print("find login user: ", name)

        return User(id, name, password, role, department, created_at)


def get_users():
    users = []
    query = QSqlQuery(DB_CONN)
    query.prepare("SELECT * FROM users WHERE 1=1 order by name asc")
    if not query.exec_():
        print("sql error:", query.lastError().text())
    else:
        while query.next():
            id = query.value("id")
            name = query.value("name")
            department = query.value("department")
            role = query.value("role")
            created_at = query.value("created_at")

            u = User(id, name, None, role, department, created_at)
            users.append(u)

    print(f"get_users={users}")

    return users


def create_user(user):
    query = QSqlQuery(DB_CONN)
    query.prepare(
        """
        INSERT INTO users (name, role, password, department, created_at)
        VALUES(?, ?, ?, ?, ?)
        """
    )
    query.addBindValue(user._name)
    query.addBindValue(user._role)
    query.addBindValue(user._password)
    query.addBindValue(user._department)
    query.addBindValue(str(datetime.now()))
    ret = query.exec_()
    print(f"insert user: {ret}")
    ret


def update_user(user):
    query = QSqlQuery(DB_CONN)
    if user._password is not None:
        query.prepare(
            "update users set name=?, role=?, password=?, department=? where id=?"
        )
        query.addBindValue(user._name)
        query.addBindValue(user._role)
        query.addBindValue(user._password)
        query.addBindValue(user._department)
        query.addBindValue(user._id)
    else:
        query.prepare("update users set name=?, role=?, department=? where id=?")
        query.addBindValue(user._name)
        query.addBindValue(user._role)
        query.addBindValue(user._department)
        query.addBindValue(user._id)

    ret = query.exec_()
    print(f"update user: {ret}")
    ret


def delete_user(id):
    query = QSqlQuery(DB_CONN)
    if id is not None:
        query.prepare("delete from users where id=?")
        query.addBindValue(id)
        ret = query.exec_()
        print(f"delete user: {ret}")
        ret


# id=None,
# name=None,
# file_name=None,
# thumbnail=None,
# tool_radius=None,
# cutter_offset=None,
# rotation_speed=None,
# created_by=None,
# created_at=None,
# updated_by=None,
# updated_at=None,
def create_recipe(recipe: Recipe) -> Tuple[bool, Optional[int]]:
    query = QSqlQuery(DB_CONN)
    query.prepare(
        """
        INSERT INTO recipes(name, file_name, tool_radius, cutter_offset, cutter_deepth, rotation_speed, created_by, created_at, updated_by, updated_at)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    query.addBindValue(recipe._name)
    query.addBindValue(recipe._file_name)
    # query.addBindValue(recipe._file_content)
    # query.addBindValue(recipe._thumbnail)
    query.addBindValue(recipe._tool_radius)
    query.addBindValue(recipe._cutter_offset)
    query.addBindValue(recipe._cutter_deepth)
    query.addBindValue(recipe._rotation_speed)
    query.addBindValue(recipe._created_by)
    query.addBindValue(str(datetime.now()))
    query.addBindValue(recipe._updated_by)
    query.addBindValue(str(datetime.now()))
    ret = query.exec_()

    if ret == True:
        return (ret, query.lastInsertId())
    else:
        print(f"insert recipe error: {query.lastError().text()}")
        return (ret, None)


def update_recipe(recipe: Recipe) -> bool:
    query = QSqlQuery(DB_CONN)
    query.prepare(
        """
      update recipes
      set name=?,
          file_name=?,
          tool_radius=?,
          cutter_offset=?,
          cutter_deepth=?,
          rotation_speed=?,
          updated_by=?,
          updated_at=?,
          where id=?
    """
    )
    query.addBindValue(recipe._name)
    query.addBindValue(recipe._file_name)
    # query.addBindValue(recipe._file_content)
    # query.addBindValue(recipe._thumbnail)
    query.addBindValue(recipe._tool_radius)
    query.addBindValue(recipe._cutter_offset)
    query.addBindValue(recipe._cutter_deepth)
    query.addBindValue(recipe._rotation_speed)
    query.addBindValue(recipe._updated_by)
    query.addBindValue(str(datetime.now()))
    query.addBindValue(recipe._id)

    return query.exec_()


def get_recipes():
    recipes = []
    query = QSqlQuery(DB_CONN)
    query.prepare("SELECT * FROM recipes WHERE 1=1 order by name asc")
    if not query.exec_():
        print("sql error:", query.lastError().text())
    else:
        while query.next():
            r = Recipe()
            r._id = query.value("id")
            r._name = query.value("name")
            r._file_name = query.value("file_name")
            r._tool_radius = query.value("tool_radius")
            r._cutter_offset = query.value("cutter_offset")
            r._cutter_deepth = query.value("cutter_deepth")
            r._rotation_speed = query.value("rotation_speed")
            r._created_by = query.value("created_by")
            r._created_at = query.value("created_at")
            r._updated_by = query.value("updated_by")
            r._updated_at = query.value("created_at")
            recipes.append(r)

    return recipes


def delete_recipe(id: int) -> bool:
    query = QSqlQuery(DB_CONN)
    ret = False
    if id is not None:
        query.prepare("delete from recipes where id=?")
        query.addBindValue(id)
        ret = query.exec_()
        print(f"delete recipe: {ret}")

    return ret
