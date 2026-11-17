"""Вкладка звітів: успішність студентів (середній бал) з фільтром за групою."""
import tkinter as tk
from tkinter import ttk
import database as db


class ReportTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Label(top, text="Група:").pack(side="left")
        self.group = ttk.Combobox(top, state="readonly", width=20)
        self.group.pack(side="left", padx=6)
        ttk.Button(top, text="Сформувати звіт", command=self.build).pack(side="left")

        cols = ["Студент", "Група", "К-сть оцінок", "Середній бал"]
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=140)
        self.tree.pack(fill="both", expand=True, padx=8)
        self.total = tk.StringVar()
        ttk.Label(self, textvariable=self.total, font=("Arial", 11, "bold")).pack(pady=8)
        self.refresh()

    def refresh(self):
        names = [r[0] for r in db.query("SELECT name FROM groups ORDER BY name")]
        self.group["values"] = ["Усі"] + names
        if not self.group.get():
            self.group.set("Усі")
        self.build()

    def build(self):
        sql = """SELECT s.full_name, g.name, COUNT(gr.id), ROUND(AVG(gr.grade),1)
                 FROM students s LEFT JOIN groups g ON g.id=s.group_id
                 LEFT JOIN grades gr ON gr.student_id=s.id"""
        args = ()
        if self.group.get() not in ("", "Усі"):
            sql += " WHERE g.name=?"
            args = (self.group.get(),)
        sql += " GROUP BY s.id ORDER BY 4 DESC"
        rows = db.query(sql, args)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=["" if v is None else v for v in r])
        avgs = [r[3] for r in rows if r[3] is not None]
        self.total.set(f"Студентів: {len(rows)}   |   Середній бал: "
                       f"{sum(avgs) / len(avgs):.1f}" if avgs else f"Студентів: {len(rows)}")
