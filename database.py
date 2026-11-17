"""Шар роботи з БД (SQLite) для АІС управління навчальним процесом коледжу."""
import os
import sqlite3
import sys
from contextlib import closing

# База лежить поруч із програмою (і для .py, і для зібраного .exe)
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "college.db")


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with closing(connect()) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS groups(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL,
            speciality TEXT, course INTEGER);
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY, full_name TEXT NOT NULL, birth_date TEXT,
            phone TEXT, group_id INTEGER REFERENCES groups(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY, full_name TEXT NOT NULL,
            position TEXT, phone TEXT);
        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, hours INTEGER,
            teacher_id INTEGER REFERENCES teachers(id) ON DELETE SET NULL);
        CREATE TABLE IF NOT EXISTS grades(
            id INTEGER PRIMARY KEY,
            student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
            grade INTEGER CHECK(grade BETWEEN 1 AND 100), date TEXT);
        """)
        c.commit()


def query(sql, args=()):
    with closing(connect()) as c:
        return c.execute(sql, args).fetchall()


def execute(sql, args=()):
    """Виконує INSERT/UPDATE/DELETE. Кидає sqlite3.Error при помилці."""
    with closing(connect()) as c:
        c.execute(sql, args)
        c.commit()


def seed_demo():
    if query("SELECT COUNT(*) FROM groups")[0][0]:
        return False
    execute("INSERT INTO groups(name,speciality,course) VALUES('ІПЗ-21','Інженерія ПЗ',2)")
    execute("INSERT INTO groups(name,speciality,course) VALUES('КН-31','Комп''ютерні науки',3)")
    execute("INSERT INTO teachers(full_name,position,phone) VALUES('Коваленко І.П.','Викладач вищої категорії','0501112233')")
    execute("INSERT INTO teachers(full_name,position,phone) VALUES('Шевченко О.М.','Старший викладач','0671234567')")
    execute("INSERT INTO subjects(name,hours,teacher_id) VALUES('Бази даних',90,1)")
    execute("INSERT INTO subjects(name,hours,teacher_id) VALUES('Програмування Python',120,2)")
    for n, g in [("Петренко Андрій", 1), ("Мельник Оксана", 1), ("Бондар Максим", 2)]:
        execute("INSERT INTO students(full_name,birth_date,phone,group_id) VALUES(?,?,?,?)",
                (n, "2005-05-15", "0991234567", g))
    for st, sb, gr in [(1, 1, 92), (1, 2, 85), (2, 1, 78), (3, 2, 95)]:
        execute("INSERT INTO grades(student_id,subject_id,grade,date) VALUES(?,?,?,?)",
                (st, sb, gr, "2026-11-10"))
    return True