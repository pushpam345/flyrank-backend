from database import get_connection


class PostgresTaskRepository:

    def get_all(self):
        conn = get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, title, done FROM tasks ORDER BY id"
                )
                rows = cursor.fetchall()

                return [
                    {
                        "id": row[0],
                        "title": row[1],
                        "done": row[2]
                    }
                    for row in rows
                ]

        finally:
            conn.close()

    def get_by_id(self, task_id: int):
        conn = get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, title, done FROM tasks WHERE id = %s",
                    (task_id,)
                )

                row = cursor.fetchone()

                if row is None:
                    return None

                return {
                    "id": row[0],
                    "title": row[1],
                    "done": row[2]
                }

        finally:
            conn.close()

    def create(self, title: str):
        conn = get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (title, done)
                    VALUES (%s, %s)
                    RETURNING id, title, done
                    """,
                    (title, False)
                )

                row = cursor.fetchone()
                conn.commit()

                return {
                    "id": row[0],
                    "title": row[1],
                    "done": row[2]
                }

        finally:
            conn.close()

    def update(self, task_id: int, title: str, done: bool):
        conn = get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tasks
                    SET title = %s, done = %s
                    WHERE id = %s
                    RETURNING id, title, done
                    """,
                    (title, done, task_id)
                )

                row = cursor.fetchone()

                if row is None:
                    conn.rollback()
                    return None

                conn.commit()

                return {
                    "id": row[0],
                    "title": row[1],
                    "done": row[2]
                }

        finally:
            conn.close()

    def delete(self, task_id: int):
        conn = get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM tasks WHERE id = %s",
                    (task_id,)
                )

                deleted = cursor.rowcount
                conn.commit()

                return deleted > 0

        finally:
            conn.close()