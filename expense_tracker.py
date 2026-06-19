import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

DB_NAME = "expenses.db"


def init_db():
    """Creates the expenses table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_expense(date_str, category, amount, description):
    """Inserts one expense row using a parameterized query."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date_str, category, amount, description)
    )
    conn.commit()
    conn.close()


def get_all_expenses():
    """Returns every expense row, most recent date first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_summary_by_category():
    """Returns total spent and entry count, grouped by category."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) AS total, COUNT(*) AS count
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_expense(expense_id):
    """Deletes one expense by its id, using a parameterized query."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        root.title("Expense Tracker")
        root.geometry("720x500")

        # --- Input form ---
        form_frame = tk.Frame(root, padx=10, pady=10)
        form_frame.pack(fill="x")

        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = tk.Entry(form_frame)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=0, column=1, padx=5)

        tk.Label(form_frame, text="Category:").grid(row=0, column=2, sticky="w")
        self.category_entry = tk.Entry(form_frame)
        self.category_entry.grid(row=0, column=3, padx=5)

        tk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky="w")
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=1, column=1, padx=5)

        tk.Label(form_frame, text="Description:").grid(row=1, column=2, sticky="w")
        self.description_entry = tk.Entry(form_frame)
        self.description_entry.grid(row=1, column=3, padx=5)

        tk.Button(form_frame, text="Add Expense", command=self.handle_add).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(form_frame, text="Delete Selected", command=self.handle_delete).grid(row=2, column=2, columnspan=2, pady=10)

        # --- Expense table ---
        table_frame = tk.Frame(root, padx=10)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "date", "category", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        # --- Summary section ---
        summary_frame = tk.Frame(root, padx=10, pady=10)
        summary_frame.pack(fill="x")

        tk.Button(summary_frame, text="Show Summary by Category", command=self.show_summary).pack(side="left")
        self.summary_label = tk.Label(summary_frame, text="", justify="left", anchor="w")
        self.summary_label.pack(side="left", padx=10)

        self.refresh_table()

    def handle_add(self):
        date_str = self.date_entry.get().strip()
        category = self.category_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.description_entry.get().strip()

        if not date_str or not category or not amount_str:
            messagebox.showerror("Missing info", "Date, category, and amount are required.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a number.")
            return

        add_expense(date_str, category, amount, description)
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.refresh_table()

    def handle_delete(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        expense_id = item["values"][0]
        delete_expense(expense_id)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in get_all_expenses():
            self.tree.insert("", "end", values=row)

    def show_summary(self):
        rows = get_summary_by_category()
        if not rows:
            self.summary_label.config(text="No expenses yet.")
            return
        lines = [f"{cat}: ${total:.2f} ({count} entries)" for cat, total, count in rows]
        self.summary_label.config(text="\n".join(lines))


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
