"""Проєктування АІС управління навчальним процесом коледжу — точка входу."""
import tkinter as tk
from tkinter import ttk, messagebox
import database as db
from tabs import groups_tab, students_tab, teachers_tab, subjects_tab, grades_tab
from report_tab import ReportTab


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("АІС управління навчальним процесом коледжу")
        self.geometry("980x520")
        self.minsize(820, 420)

        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Заповнити демо-даними", command=self.demo)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.destroy)
        menu.add_cascade(label="Файл", menu=file_menu)
        menu.add_command(label="Про програму", command=lambda: messagebox.showinfo(
            "Про програму", "АІС управління навчальним процесом коледжу\nPython + Tkinter + SQLite"))
        self.config(menu=menu)

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self.tabs = []
        for title, factory in [("Групи", groups_tab), ("Студенти", students_tab),
                               ("Викладачі", teachers_tab), ("Дисципліни", subjects_tab),
                               ("Журнал оцінок", grades_tab), ("Звіти", ReportTab)]:
            tab = factory(self.nb)
            self.nb.add(tab, text=title)
            self.tabs.append(tab)
        self.nb.bind("<<NotebookTabChanged>>", self.on_tab)

    def on_tab(self, _e):
        self.tabs[self.nb.index("current")].refresh()

    def demo(self):
        msg = "Демо-дані додано" if db.seed_demo() else "БД вже містить дані"
        messagebox.showinfo("Демо", msg)
        self.on_tab(None)


if __name__ == "__main__":
    db.init_db()
    App().mainloop()
