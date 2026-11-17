"""Універсальна вкладка CRUD: форма + таблиця + пошук."""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import database as db


class CrudTab(ttk.Frame):
    def __init__(self, parent, table, fields, list_sql, headers, defaults=None):
        super().__init__(parent)
        self.table, self.fields, self.list_sql = table, fields, list_sql
        self.defaults = defaults or {}
        self.widgets, self.maps, self.selected, self.rows = {}, {}, None, []

        # --- форма ---
        form = ttk.LabelFrame(self, text="Картка запису")
        form.pack(side="left", fill="y", padx=8, pady=8)
        for i, (label, col, lookup, _num) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", padx=6, pady=4)
            w = (ttk.Combobox(form, state="readonly", width=28) if lookup
                 else ttk.Entry(form, width=31))
            w.grid(row=i, column=1, padx=6, pady=4)
            self.widgets[col] = w
        bf = ttk.Frame(form)
        bf.grid(row=len(fields), column=0, columnspan=2, pady=10)
        for text, cmd in [("Додати", self.add), ("Зберегти", self.update),
                          ("Видалити", self.delete), ("Очистити", self.clear)]:
            ttk.Button(bf, text=text, command=cmd, width=9).pack(side="left", padx=2)

        # --- таблиця + пошук ---
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        sf = ttk.Frame(right)
        sf.pack(fill="x")
        ttk.Label(sf, text="Пошук:").pack(side="left")
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.apply_filter())
        ttk.Entry(sf, textvariable=self.search).pack(side="left", fill="x", expand=True, padx=6)

        self.tree = ttk.Treeview(right, columns=headers, show="headings", selectmode="browse")
        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=120)
        sb = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, pady=6)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.refresh()

    # ---------- дані ----------
    def refresh(self):
        for _l, col, lookup, _n in self.fields:
            if lookup:
                data = db.query(lookup)
                self.maps[col] = {name: id_ for id_, name in data}
                self.widgets[col]["values"] = list(self.maps[col])
        self.rows = db.query(self.list_sql)
        self.apply_filter()

    def apply_filter(self):
        q = self.search.get().lower()
        self.tree.delete(*self.tree.get_children())
        for r in self.rows:
            vals = ["" if v is None else v for v in r[1:]]
            if q in " ".join(map(str, vals)).lower():
                self.tree.insert("", "end", iid=str(r[0]), values=vals)

    def read(self):
        vals = []
        for label, col, lookup, numeric in self.fields:
            raw = self.widgets[col].get().strip()
            if lookup:
                v = self.maps[col].get(raw)
            elif numeric and raw:
                if not raw.isdigit():
                    messagebox.showwarning("Помилка", f"«{label}» має бути числом")
                    return None
                v = int(raw)
            else:
                v = raw or None
            vals.append(v)
        if not vals[0]:
            messagebox.showwarning("Помилка", f"Поле «{self.fields[0][0]}» обов'язкове")
            return None
        return vals

    def run(self, sql, args):
        try:
            db.execute(sql, args)
        except sqlite3.Error as e:
            messagebox.showerror("Помилка БД", str(e))
            return False
        return True

    # ---------- дії ----------
    def add(self):
        vals = self.read()
        if vals is None:
            return
        cols = [f[1] for f in self.fields]
        sql = f"INSERT INTO {self.table}({','.join(cols)}) VALUES({','.join('?' * len(cols))})"
        if self.run(sql, vals):
            self.clear()
            self.refresh()

    def update(self):
        if self.selected is None:
            messagebox.showinfo("Увага", "Оберіть запис у таблиці")
            return
        vals = self.read()
        if vals is None:
            return
        sets = ",".join(f"{f[1]}=?" for f in self.fields)
        if self.run(f"UPDATE {self.table} SET {sets} WHERE id=?", vals + [self.selected]):
            self.refresh()

    def delete(self):
        if self.selected is None:
            messagebox.showinfo("Увага", "Оберіть запис у таблиці")
            return
        if messagebox.askyesno("Підтвердження", "Видалити вибраний запис?"):
            if self.run(f"DELETE FROM {self.table} WHERE id=?", (self.selected,)):
                self.clear()
                self.refresh()

    def clear(self):
        self.selected = None
        for _l, col, lookup, _n in self.fields:
            w = self.widgets[col]
            if lookup:
                w.set("")
            else:
                w.delete(0, "end")
                w.insert(0, self.defaults.get(col, ""))

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected = int(sel[0])
        cols = ",".join(f[1] for f in self.fields)
        row = db.query(f"SELECT {cols} FROM {self.table} WHERE id=?", (self.selected,))[0]
        for (_l, col, lookup, _n), v in zip(self.fields, row):
            w = self.widgets[col]
            if lookup:
                names = {i: n for n, i in self.maps[col].items()}
                w.set(names.get(v, ""))
            else:
                w.delete(0, "end")
                w.insert(0, "" if v is None else v)
