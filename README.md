# Book Tracking System
#Author: Noelyn Nasilasila
#Achievement Standard: AS91896 and 91897

#PROGRAM PURPOSE

Book Tracking System is a Python program that allows users to keep track of books they have loaned to friends or family.

The program allows users to add book records, search for books, view current loans, delete records, identify overdue books, export records to a CSV file, and send email reminders.

Book records are saved using a JSON file so the information remains available after the program is closed.

#INSTALLATION

1. Install Python 3.
2. Save the program as `Book Tracker Final.py`.
3. Open the file in a Python editor such as IDLE.
4. Click Run.
5. Click Run Module to start the program.

#LIBRARIES / MODULES

The program uses the following Python modules:

* tkinter
* json
* csv
* os
* re
* webbrowser
* datetime
* urllib.parse

These are used for the graphical interface, saving and loading book records, exporting CSV files, validating information, checking dates, and opening email reminders.

#MINIMUM REQUIREMENTS

* Windows, macOS, or Linux
* Python 3
* Tkinter support
* Recommended screen resolution: 1200 × 800 or higher
* Permission to read and write files for JSON and CSV storage

#STEPS TO START THE PROGRAM

1. Open `Book Tracker Option Final.py`.
2. Open the file using IDLE or another Python editor.
3. Click Run.
4. Click Run Module.
5. The BookTracker window will open.

#INSTRUCTIONS ON HOW TO USE THE PROGRAM

#Adding a Book

1. Enter the Book Title.
2. Enter the Borrower Name.
3. Enter the borrower's Email Address if required. This field is optional.
4. Enter the Date Out using `DD/MM/YYYY`.
5. Enter the Due Date using `DD/MM/YYYY`.
6. Click ADD NEW LOAN.
7. The program will validate the information and save the book record.

#Searching for a Book

1. Click the search box above the book records.
2. Enter part or all of a book title, borrower name, or email address.
3. Click SEARCH or press Enter.
4. Matching records will be displayed.
5. Click SHOW ALL to display all book records again.

#Deleting a Book

1. Select the book record you want to remove.
2. Click DELETE RECORD.
3. A confirmation message will appear.
4. Confirm that you want to delete the record.
5. The book will be removed from the saved records.

#Overdue Books

The program automatically checks the due date of each book.

If the due date has passed, the record will be marked OVERDUE and highlighted so it is easier to identify.

#Sending an Email Reminder

1. Select a book record that contains a borrower's email address.
2. Click SEND EMAIL REMINDER.
3. Your default email program will open.
4. A reminder message containing the book title and due date will be prepared.
5. Check the message before sending it.

#Exporting Records

1. Click EXPORT TO CSV.
2. Choose where you want to save the CSV file.
3. Enter a file name.
4. Save the file.
5. Your book loan records will be exported to the CSV file.

#Clearing the Form

Click CLEAR FORM to remove the information currently entered in the input fields.

#Help

Click HELP to display instructions explaining how to use the main features of BookTracker.

#INPUT VALIDATION

The program checks information before a book is saved.

It checks for:

* Missing book titles
* Missing borrower names
* Missing dates
* Invalid email addresses
* Invalid dates
* Incorrect date formats
* Due dates that are before the date the book was loaned
* Duplicate book and borrower records

Dates must be entered using:

`DD/MM/YYYY`

For example:

`13/08/2026`

If invalid information is entered, the program displays an error message explaining what needs to be corrected.

#DATA STORAGE

Book records are stored in:

`book_loans.json`

JSON storage allows the records to remain available when the program is closed and reopened.

#IMPORTANT

Do not delete or manually change the `book_loans.json` file while using the program, as this could cause saved book information to become unavailable or invalid.
