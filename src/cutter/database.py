from datetime import datetime

from cutter.models import User
from qtpy.QtSql import QSqlDatabase
from qtpy.QtSql import QSqlQuery


DB_CONN = QSqlDatabase.addDatabase("QSQLITE")
DB_CONN.setDatabaseName("cutter.db")
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
            u = {
                "id": query.value("id"),
                "name": query.value("name"),
                "department": query.value("department"),
                "role": query.value("role"),
                "created_at": query.value("created_at"),
            }
            users.append(u)

    print(f"get_users={users}")

    return users
