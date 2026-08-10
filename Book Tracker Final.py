# Author: Noelyn
# Book Tracking System
# Purpose: Track books loaned to friends or family.

import csv
import json
import os
import re
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote

# -----------------------------
# Constants / configuration
# -----------------------------

DATA_FILE = "book_loans.json"
DATE_FORMAT = "%d/%m/%Y"

CLR_CANVAS = "#F1F5F9"
CLR_SIDEBAR = "#FFFFFF"
CLR_PRIMARY = "#4F46E5"
CLR_SUCCESS = "#10B981"
CLR_DANGER = "#EF4444"
CLR_WARNING = "#D97706"
CLR_TEXT_MAIN = "#1E293B"
CLR_TEXT_MUTED = "#64748B"
CLR_BORDER = "#E2E8F0"

# -----------------------------
# Data functions
# -----------------------------


def load_data():
    """Load book records from JSON and return a list."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Protect the program if the JSON file contains the wrong data type.
        if not isinstance(data, list):
            raise ValueError("Saved data must be a list.")

        return data

    except (json.JSONDecodeError, OSError, ValueError) as error:
        messagebox.showerror(
            "Data Error",
            f"The saved book file could not be loaded.\n\n{error}"
        )
        return []


def save_data(data):
    """Save the supplied list of book records to JSON. Returns True if successful."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True

    except OSError as error:
        messagebox.showerror(
            "Save Error",
            f"The book records could not be saved.\n\n{error}"
        )
        return False


# -----------------------------
# Validation / helper functions
# -----------------------------


def parse_date(date_text):
    """Convert DD/MM/YYYY text into a date object."""
    return datetime.strptime(date_text, DATE_FORMAT).date()


def is_overdue(due_date):
    """Return True when the supplied due date has passed."""
    try:
        return parse_date(due_date) < datetime.now().date()
    except ValueError:
        return False


def valid_email(email):
    """Allow a blank email, otherwise check for a simple email structure."""
    if email == "":
        return True

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def validate_book_data(title, borrower, email, date_out, due_date):
    """
    Validate user input.
    Returns (True, "") if valid, otherwise (False, error_message).
    """
    if not title:
        return False, "Please enter a book title."

    if not borrower:
        return False, "Please enter the borrower's name."

    if not date_out:
        return False, "Please enter the date the book was loaned."

    if not due_date:
        return False, "Please enter the due date."

    if not valid_email(email):
        return False, "Please enter a valid email address, or leave it blank."

    try:
        date_out_value = parse_date(date_out)
        due_date_value = parse_date(due_date)
    except ValueError:
        return False, "Dates must be real dates in DD/MM/YYYY format."

    if due_date_value < date_out_value:
        return False, "The due date cannot be before the date the book was loaned."

    return True, ""


def duplicate_exists(data, title, borrower):
    """Return True when the same title and borrower are already stored."""
    title = title.casefold()
    borrower = borrower.casefold()

    return any(
        str(book.get("title", "")).casefold() == title
        and str(book.get("borrower", "")).casefold() == borrower
        for book in data
    )


def clear_form():
    """Clear entry fields after a successful add."""
    ent_title.delete(0, tk.END)
    ent_borrower.delete(0, tk.END)
    ent_email.delete(0, tk.END)
    ent_out.delete(0, tk.END)
    ent_due.delete(0, tk.END)

    ent_out.insert(0, datetime.now().strftime(DATE_FORMAT))
    ent_title.focus_set()


# -----------------------------
# Main program functions
# -----------------------------


def refresh_table(data_to_display=None):
    """Refresh the table using all records or a supplied filtered list."""
    for item in tree.get_children():
        tree.delete(item)

    data = load_data() if data_to_display is None else data_to_display

    for index, book in enumerate(data):
        due_date = str(book.get("due_date", ""))
        tag = "overdue" if is_overdue(due_date) else "normal"

        tree.insert(
            "",
            "end",
            iid=str(index),
            values=(
                book.get("title", ""),
                book.get("borrower", ""),
                book.get("email", "") or "N/A",
                book.get("date_out", ""),
                due_date,
                "OVERDUE" if tag == "overdue" else "On loan",
            ),
            tags=(tag,),
        )

    status_label.config(text=f"Showing {len(data)} loan record(s)")


def add_book():
    """Validate the form and add a new book record."""
    title = ent_title.get().strip()
    borrower = ent_borrower.get().strip()
    email = ent_email.get().strip()
    date_out = ent_out.get().strip()
    due_date = ent_due.get().strip()

    valid, error_message = validate_book_data(
        title, borrower, email, date_out, due_date
    )

    if not valid:
        messagebox.showwarning("Invalid Input", error_message)
        return

    data = load_data()

    if duplicate_exists(data, title, borrower):
        messagebox.showwarning(
            "Duplicate Record",
            "This book is already recorded for the same borrower."
        )
        return

    new_book = {
        "title": title,
        "borrower": borrower,
        "email": email,
        "date_out": date_out,
        "due_date": due_date,
    }

    data.append(new_book)

    if save_data(data):
        refresh_table()
        clear_form()
        messagebox.showinfo("Book Added", f"'{title}' was added successfully.")


def get_selected_values():
    """Return values from the selected table row, or None if nothing is selected."""
    selection = tree.selection()

    if not selection:
        messagebox.showinfo("No Selection", "Please select a book record first.")
        return None

    return tree.item(selection[0], "values")


def delete_book():
    """Delete the selected record after confirmation."""
    selected = get_selected_values()

    if selected is None:
        return

    title, borrower = selected[0], selected[1]

    confirmed = messagebox.askyesno(
        "Delete Record",
        f"Delete '{title}' borrowed by {borrower}?"
    )

    if not confirmed:
        return

    data = load_data()

    # Delete only the first exact matching record.
    for index, book in enumerate(data):
        if (
            str(book.get("title", "")) == str(title)
            and str(book.get("borrower", "")) == str(borrower)
        ):
            del data[index]
            break
    else:
        messagebox.showwarning("Not Found", "That book record could not be found.")
        refresh_table()
        return

    if save_data(data):
        refresh_table()
        messagebox.showinfo("Deleted", "The selected book record was deleted.")


def search_books(event=None):
    """Search by title, borrower, or email."""
    query = ent_search.get().strip().casefold()

    if not query:
        refresh_table()
        return

    data = load_data()
    results = []

    for book in data:
        searchable_text = " ".join(
            [
                str(book.get("title", "")),
                str(book.get("borrower", "")),
                str(book.get("email", "")),
            ]
        ).casefold()

        if query in searchable_text:
            results.append(book)

    refresh_table(results)

    if not results:
        messagebox.showinfo("Search", "No matching books found.")


def clear_search():
    """Clear the search field and show every record."""
    ent_search.delete(0, tk.END)
    refresh_table()
    ent_search.focus_set()


def export_csv():
    """Export all saved book records to a CSV file."""
    data = load_data()

    if not data:
        messagebox.showinfo("Nothing to Export", "There are no book records to export.")
        return

    path = filedialog.asksaveasfilename(
        title="Export Book Records",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
    )

    if not path:
        return

    try:
        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["title", "borrower", "email", "date_out", "due_date"],
            )
            writer.writeheader()
            writer.writerows(data)

        messagebox.showinfo("Export Complete", "Book records were exported successfully.")

    except OSError as error:
        messagebox.showerror("Export Error", f"The CSV file could not be saved.\n\n{error}")


def send_email():
    """Open the default email program with a reminder for the selected borrower."""
    selected = get_selected_values()

    if selected is None:
        return

    title, borrower, email, _, due_date, _ = selected

    if not email or email == "N/A":
        messagebox.showwarning(
            "Missing Email",
            "This borrower does not have an email address saved."
        )
        return

    subject = quote(f"Book Return Reminder: {title}")
    body = quote(
        f"Hi {borrower},\n\n"
        f"This is a reminder about the book '{title}', which is due back on {due_date}.\n\n"
        "Thank you."
    )

    webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")


def show_help():
    """Show simple instructions inside the program."""
    messagebox.showinfo(
        "How to Use BookTracker",
        "1. Enter the book and borrower details.\n"
        "2. Use DD/MM/YYYY for both dates.\n"
        "3. Click ADD NEW LOAN to save the record.\n"
        "4. Use the search box to find a title, borrower, or email.\n"
        "5. Select a row before deleting or sending a reminder.\n"
        "6. Red rows marked OVERDUE have passed their due date."
    )


def fill_form_from_selection(event=None):
    """Optional usability feature: double-click a row to copy its values into the form."""
    selected = tree.selection()

    if not selected:
        return

    values = tree.item(selected[0], "values")

    clear_form()
    ent_title.insert(0, values[0])
    ent_borrower.insert(0, values[1])

    if values[2] != "N/A":
        ent_email.insert(0, values[2])

    ent_out.delete(0, tk.END)
    ent_out.insert(0, values[3])
    ent_due.insert(0, values[4])


# -----------------------------
# GUI setup
# -----------------------------

root = tk.Tk()
root.title("BookTracker - Loan Manager")
root.geometry("1180x760")
root.minsize(1000, 650)
root.configure(bg=CLR_CANVAS)

# ttk styling
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="white",
    fieldbackground="white",
    rowheight=38,
    font=("Segoe UI", 10),
    borderwidth=0,
)

style.configure(
    "Treeview.Heading",
    background=CLR_SIDEBAR,
    foreground=CLR_TEXT_MAIN,
    font=("Segoe UI", 9, "bold"),
    borderwidth=1,
)

style.map(
    "Treeview",
    background=[("selected", CLR_PRIMARY)],
    foreground=[("selected", "white")],
)

# -----------------------------
# Sidebar
# -----------------------------

sidebar = tk.Frame(
    root,
    bg=CLR_SIDEBAR,
    width=320,
    highlightbackground=CLR_BORDER,
    highlightthickness=1,
)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="📚 BookTracker",
    fg=CLR_PRIMARY,
    bg=CLR_SIDEBAR,
    font=("Segoe UI", 20, "bold"),
).pack(pady=(28, 4))

tk.Label(
    sidebar,
    text="Track books loaned to family and friends",
    fg=CLR_TEXT_MUTED,
    bg=CLR_SIDEBAR,
    font=("Segoe UI", 9),
).pack(pady=(0, 22))


def create_input(label, hint=""):
    """Create and return a labelled Entry widget."""
    tk.Label(
        sidebar,
        text=label.upper(),
        fg=CLR_TEXT_MUTED,
        bg=CLR_SIDEBAR,
        font=("Segoe UI", 8, "bold"),
    ).pack(anchor="w", padx=30)

    entry = tk.Entry(
        sidebar,
        bg=CLR_CANVAS,
        fg=CLR_TEXT_MAIN,
        font=("Segoe UI", 10),
        bd=0,
        highlightthickness=1,
        highlightbackground=CLR_BORDER,
        highlightcolor=CLR_PRIMARY,
    )
    entry.pack(fill="x", padx=30, pady=(4, 13), ipady=7)

    if hint:
        entry.insert(0, hint)

    return entry


ent_title = create_input("Book Title")
ent_borrower = create_input("Borrower Name")
ent_email = create_input("Email Address (optional)")
ent_out = create_input("Date Out", datetime.now().strftime(DATE_FORMAT))
ent_due = create_input("Due Date")


def make_sidebar_button(text, color, command):
    """Create a consistent sidebar button."""
    button = tk.Button(
        sidebar,
        text=text,
        bg=color,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        cursor="hand2",
        command=command,
        activebackground=color,
        activeforeground="white",
    )
    button.pack(fill="x", padx=30, pady=4, ipady=9)
    return button


make_sidebar_button("ADD NEW LOAN", CLR_PRIMARY, add_book)
make_sidebar_button("CLEAR FORM", CLR_TEXT_MUTED, clear_form)
make_sidebar_button("EXPORT TO CSV", CLR_TEXT_MAIN, export_csv)
make_sidebar_button("HELP", CLR_WARNING, show_help)

# -----------------------------
# Main content
# -----------------------------

content = tk.Frame(root, bg=CLR_CANVAS)
content.pack(side="right", fill="both", expand=True, padx=35, pady=30)

header = tk.Frame(content, bg=CLR_CANVAS)
header.pack(fill="x", pady=(0, 18))

tk.Label(
    header,
    text="Loan Records",
    bg=CLR_CANVAS,
    fg=CLR_TEXT_MAIN,
    font=("Segoe UI", 22, "bold"),
).pack(side="left")

# Search bar
search_frame = tk.Frame(content, bg=CLR_CANVAS)
search_frame.pack(fill="x", pady=(0, 18))

ent_search = tk.Entry(
    search_frame,
    font=("Segoe UI", 11),
    bd=0,
    highlightthickness=1,
    highlightbackground=CLR_BORDER,
    highlightcolor=CLR_PRIMARY,
)
ent_search.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
ent_search.bind("<Return>", search_books)

tk.Button(
    search_frame,
    text="SEARCH",
    bg=CLR_TEXT_MAIN,
    fg="white",
    font=("Segoe UI", 9, "bold"),
    bd=0,
    command=search_books,
    cursor="hand2",
    padx=18,
).pack(side="left", ipady=9)

tk.Button(
    search_frame,
    text="SHOW ALL",
    bg=CLR_TEXT_MUTED,
    fg="white",
    font=("Segoe UI", 9, "bold"),
    bd=0,
    command=clear_search,
    cursor="hand2",
    padx=18,
).pack(side="left", ipady=9, padx=(8, 0))

# Table
table_container = tk.Frame(
    content,
    bg="white",
    highlightbackground=CLR_BORDER,
    highlightthickness=1,
)
table_container.pack(fill="both", expand=True)

columns = ("title", "borrower", "email", "date_out", "due_date", "status")
tree = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    selectmode="browse",
)

headings = {
    "title": "BOOK TITLE",
    "borrower": "BORROWER",
    "email": "EMAIL",
    "date_out": "DATE OUT",
    "due_date": "DUE DATE",
    "status": "STATUS",
}

widths = {
    "title": 190,
    "borrower": 150,
    "email": 200,
    "date_out": 95,
    "due_date": 95,
    "status": 90,
}

for column in columns:
    tree.heading(column, text=headings[column], anchor="w")
    tree.column(column, anchor="w", width=widths[column], minwidth=70)

tree.tag_configure(
    "overdue",
    foreground=CLR_DANGER,
    font=("Segoe UI", 10, "bold"),
)
tree.tag_configure("normal", foreground=CLR_TEXT_MAIN)

tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(
    table_container,
    orient="vertical",
    command=tree.yview,
)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

tree.bind("<Double-1>", fill_form_from_selection)

# Footer actions
footer = tk.Frame(content, bg=CLR_CANVAS)
footer.pack(fill="x", pady=(18, 0))

tk.Button(
    footer,
    text="✉ SEND EMAIL REMINDER",
    bg=CLR_SUCCESS,
    fg="white",
    font=("Segoe UI", 9, "bold"),
    bd=0,
    padx=18,
    pady=9,
    command=send_email,
    cursor="hand2",
).pack(side="left", padx=(0, 10))

tk.Button(
    footer,
    text="🗑 DELETE RECORD",
    bg=CLR_DANGER,
    fg="white",
    font=("Segoe UI", 9, "bold"),
    bd=0,
    padx=18,
    pady=9,
    command=delete_book,
    cursor="hand2",
).pack(side="left")

status_label = tk.Label(
    footer,
    text="",
    bg=CLR_CANVAS,
    fg=CLR_TEXT_MUTED,
    font=("Segoe UI", 9),
)
status_label.pack(side="right")

# Initial display
refresh_table()
ent_title.focus_set()
root.mainloop()
