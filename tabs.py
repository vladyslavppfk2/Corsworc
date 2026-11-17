"""Описи вкладок: групи, студенти, викладачі, предмети, журнал оцінок."""
from datetime import date
from base_tab import CrudTab


def F(label, col, lookup=None, numeric=False):
    return (label, col, lookup, numeric)


def groups_tab(p):
    return CrudTab(p, "groups",
        [F("Назва групи", "name"), F("Спеціальність", "speciality"), F("Курс", "course", numeric=True)],
        "SELECT id,name,speciality,course FROM groups ORDER BY name",
        ["Група", "Спеціальність", "Курс"])


def students_tab(p):
    return CrudTab(p, "students",
        [F("ПІБ", "full_name"), F("Дата народження", "birth_date"), F("Телефон", "phone"),
         F("Група", "group_id", "SELECT id,name FROM groups ORDER BY name")],
        """SELECT s.id,s.full_name,s.birth_date,s.phone,g.name FROM students s
           LEFT JOIN groups g ON g.id=s.group_id ORDER BY s.full_name""",
        ["ПІБ", "Дата народження", "Телефон", "Група"])


def teachers_tab(p):
    return CrudTab(p, "teachers",
        [F("ПІБ", "full_name"), F("Посада", "position"), F("Телефон", "phone")],
        "SELECT id,full_name,position,phone FROM teachers ORDER BY full_name",
        ["ПІБ", "Посада", "Телефон"])


def subjects_tab(p):
    return CrudTab(p, "subjects",
        [F("Дисципліна", "name"), F("Годин", "hours", numeric=True),
         F("Викладач", "teacher_id", "SELECT id,full_name FROM teachers ORDER BY full_name")],
        """SELECT s.id,s.name,s.hours,t.full_name FROM subjects s
           LEFT JOIN teachers t ON t.id=s.teacher_id ORDER BY s.name""",
        ["Дисципліна", "Годин", "Викладач"])


def grades_tab(p):
    return CrudTab(p, "grades",
        [F("Студент", "student_id", "SELECT id,full_name FROM students ORDER BY full_name"),
         F("Дисципліна", "subject_id", "SELECT id,name FROM subjects ORDER BY name"),
         F("Оцінка (1-100)", "grade", numeric=True), F("Дата", "date")],
        """SELECT gr.id,s.full_name,sub.name,gr.grade,gr.date FROM grades gr
           JOIN students s ON s.id=gr.student_id JOIN subjects sub ON sub.id=gr.subject_id
           ORDER BY gr.date DESC, s.full_name""",
        ["Студент", "Дисципліна", "Оцінка", "Дата"],
        defaults={"date": date.today().isoformat()})
