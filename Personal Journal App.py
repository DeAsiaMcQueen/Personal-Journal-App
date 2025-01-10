import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime
import pytz
from tzlocal import get_localzone
from cryptography.fernet import Fernet
# Encryption setup
KEY_FILE = "key.key"
def generate_key():
    """Generate a key and save it to a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
def load_key():
    """Load the key from the file."""
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()
KEY = load_key()
cipher = Fernet(KEY)
# Database setup
DB_FILE = "journal.db"
def initialize_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            entry BLOB,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()
def add_default_user():
    """Adds a default user for first-time setup."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "password"))
    conn.commit()
    conn.close()
# Journal Application Class
class PersonalJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Journal Application")
        self.root.geometry("800x600")
        self.local_timezone = get_localzone()
        # Title Input
        ttk.Label(root, text="Entry Title:").pack(pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.title_var, width=50).pack(pady=5)
        # Category Input
        ttk.Label(root, text="Category:").pack(pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            root,
            textvariable=self.category_var,
            values=["Personal", "Work", "Ideas", "Miscellaneous"],
            state="readonly"
        )
        self.category_dropdown.pack(pady=5)
        self.category_dropdown.set("Select Category")
        # Entry Text Area
        ttk.Label(root, text="Journal Entry:").pack(pady=5)
        self.text_area = tk.Text(root, wrap="word", height=15)
        self.text_area.pack(padx=10, pady=5, fill="both", expand=True)
        # Buttons
        ttk.Button(root, text="Save Entry", command=self.save_entry).pack(pady=10)
        ttk.Button(root, text="View All Entries", command=self.view_entries).pack(pady=5)
        ttk.Button(root, text="Search Entries", command=self.search_entries).pack(pady=5)
        ttk.Button(root, text="Export Entries", command=self.export_entries).pack(pady=5)
        # Feedback Label
        self.feedback_label = ttk.Label(root, text="", foreground="green")
        self.feedback_label.pack(pady=5)
    def save_entry(self):
        """Save a journal entry to the database."""
        title = self.title_var.get().strip()
        category = self.category_var.get()
        entry = self.text_area.get("1.0", "end").strip()
        if not title or not entry or category == "Select Category":
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        encrypted_entry = cipher.encrypt(entry.encode())
        timestamp = datetime.now(self.local_timezone).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO journal_entries (title, category, entry, timestamp)
            VALUES (?, ?, ?, ?)
        """, (title, category, encrypted_entry, timestamp))
        conn.commit()
        conn.close()
        self.feedback_label.config(text="Entry saved successfully!")
        self.root.after(3000, lambda: self.feedback_label.config(text=""))  # Clear feedback after 3 seconds
        self.title_var.set("")
        self.category_dropdown.set("Select Category")
        self.text_area.delete("1.0", "end")
    def view_entries(self):
        """Open a new window to display all journal entries."""
        entries_window = tk.Toplevel(self.root)
        entries_window.title("Journal Entries")
        entries_window.geometry("800x400")
        tree = ttk.Treeview(entries_window, columns=("ID", "Title", "Category", "Timestamp"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Title", text="Title")
        tree.heading("Category", text="Category")
        tree.heading("Timestamp", text="Timestamp")
        tree.pack(fill="both", expand=True)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, category, timestamp FROM journal_entries ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            tree.insert("", "end", values=row)
        def open_entry(event):
            selected_item = tree.selection()[0]
            entry_id = tree.item(selected_item)["values"][0]
            self.open_entry_by_id(entry_id)
        tree.bind("<Double-1>", open_entry)
    def open_entry_by_id(self, entry_id):
        """Open an individual journal entry."""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT title, category, entry, timestamp FROM journal_entries WHERE id = ?", (entry_id,))
        entry = cursor.fetchone()
        conn.close()
        if entry:
            decrypted_entry = cipher.decrypt(entry[2]).decode()
            entry_window = tk.Toplevel(self.root)
            entry_window.title(entry[0])
            entry_window.geometry("600x400")
            ttk.Label(entry_window, text=f"Category: {entry[1]}").pack(pady=5)
            ttk.Label(entry_window, text=f"Timestamp: {entry[3]}").pack(pady=5)
            text_area = tk.Text(entry_window, wrap="word", height=15)
            text_area.pack(padx=10, pady=5, fill="both", expand=True)
            text_area.insert("1.0", decrypted_entry)
            text_area.config(state="disabled")
    def search_entries(self):
        """Open a new window to search for journal entries."""
        search_window = tk.Toplevel(self.root)
        search_window.title("Search Journal Entries")
        search_window.geometry("800x400")
        # Search by Title
        ttk.Label(search_window, text="Search by Title:").pack(pady=5)
        title_var = tk.StringVar()
        ttk.Entry(search_window, textvariable=title_var, width=50).pack(pady=5)
        # Filter by Category
        ttk.Label(search_window, text="Filter by Category:").pack(pady=5)
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(
            search_window,
            textvariable=category_var,
            values=["All", "Personal", "Work", "Ideas", "Miscellaneous"],
            state="readonly"
        )
        category_dropdown.pack(pady=5)
        category_dropdown.set("All")
        # Filter by Date Range
        ttk.Label(search_window, text="Filter by Date Range (YYYY-MM-DD):").pack(pady=5)
        date_from_var = tk.StringVar()
        date_to_var = tk.StringVar()
        ttk.Entry(search_window, textvariable=date_from_var, width=20).pack(pady=5, side="left", padx=(5, 2))
        ttk.Entry(search_window, textvariable=date_to_var, width=20).pack(pady=5, side="left")
        ttk.Button(search_window, text="Search", command=lambda: self.perform_search(
            title_var.get(),
            category_var.get(),
            date_from_var.get(),
            date_to_var.get(),
            search_window
        )).pack(pady=10)
    def perform_search(self, title, category, date_from, date_to, window):
        """Perform the search and display results."""
        query = "SELECT id, title, category, timestamp FROM journal_entries WHERE 1=1"
        params = []
        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)
        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        # Display results
        results_tree = ttk.Treeview(window, columns=("ID", "Title", "Category", "Timestamp"), show="headings")
        results_tree.heading("ID", text="ID")
        results_tree.heading("Title", text="Title")
        results_tree.heading("Category", text="Category")
        results_tree.heading("Timestamp", text="Timestamp")
        results_tree.pack(fill="both", expand=True)
        for row in rows:
            results_tree.insert("", "end", values=row)
    def export_entries(self):
        """Export journal entries to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Entries",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")]
        )
        if not file_path:
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT title, category, entry, timestamp FROM journal_entries ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                if file_path.endswith(".csv"):
                    file.write("Title,Category,Entry,Timestamp\n")
                for row in rows:
                    title, category, encrypted_entry, timestamp = row
                    entry = cipher.decrypt(encrypted_entry).decode()
                    if file_path.endswith(".csv"):
                        file.write(f'"{title}","{category}","{entry}","{timestamp}"\n')
                    else:
                        file.write(f"Title: {title}\nCategory: {category}\nEntry: {entry}\nTimestamp: {timestamp}\n\n")
            messagebox.showinfo("Success", f"Entries exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export entries: {e}")
# Authentication Class
class Authentication:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("400x300")
        ttk.Label(root, text="Username:").pack(pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.username_var).pack(pady=5)
        ttk.Label(root, text="Password:").pack(pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.password_var, show="*").pack(pady=5)
        ttk.Button(root, text="Login", command=self.login).pack(pady=10)
        ttk.Button(root, text="Register", command=self.register).pack(pady=10)
    def login(self):
        """Authenticate the user."""
        username = self.username_var.get()
        password = self.password_var.get()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            self.root.destroy()
            main_root = tk.Tk()
            app = PersonalJournalApp(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    def register(self):
        """Register a new user."""
        register_window = tk.Toplevel(self.root)
        register_window.title("Register")
        register_window.geometry("400x300")
        ttk.Label(register_window, text="New Username:").pack(pady=5)
        new_username_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=new_username_var).pack(pady=5)
        ttk.Label(register_window, text="New Password:").pack(pady=5)
        new_password_var = tk.StringVar()
        ttk.Entry(register_window, textvariable=new_password_var, show="*").pack(pady=5)
        ttk.Button(register_window, text="Create Account", command=lambda: self.create_account(new_username_var.get(), new_password_var.get(), register_window)).pack(pady=10)
    def create_account(self, username, password, window):
        """Add a new user to the database."""
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose another.")
        conn.close()
# Main Program
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        initialize_db()
        add_default_user()
    root = tk.Tk()
    auth_app = Authentication(root)
    root.mainloop()