import os.path
import sqlite3
from pathlib import Path

from jllama.config import get_db_url
from jllama.env import jllama_version, cpp_version, factory_version
from jllama.util.logutil import Logger

logger = Logger(__name__)


def prepare_conn():
    db_file = get_db_url().split("///", 1)[-1]
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    return conn, cursor


def update_version():
    conn, cursor = prepare_conn()
    update_sql = "update sys_info set cpp_version=?,factory_version=?,self_version=? where id=999"
    try:
        cursor.execute(update_sql, (cpp_version, factory_version, jllama_version))
        conn.commit()
    except Exception as e:
        logger.error(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def update_other():
    update_sql_file = f"update/{jllama_version}/update.sql"
    update_sql_file = str(Path(__file__).parent.parent / f"{update_sql_file}")
    if os.path.exists(update_sql_file):
        with open(update_sql_file, encoding="utf-8") as f:
            update_sql = f.read()
            if update_sql and len(update_sql) > 0:
                conn, cursor = prepare_conn()
                for sql in update_sql.split(';'):
                    if sql and len(sql) > 0:
                        logger.info(f"start to execute update sql: {sql}")
                        try:
                            cursor.execute(sql)
                        except Exception as e:
                            logger.error(e)
                            conn.rollback()
                cursor.close()
                conn.close()
