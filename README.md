# Personal Journal Application
![Python](https://img.shields.io/badge/python-3.x-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Last Commit](https://img.shields.io/github/last-commit/DeAsiaMcQueen/personal-journal-app)
A secure and feature-rich personal journal app designed to store, search, and export encrypted entries with user authentication.
## Features
- Authentication: Login/Registration system for user accounts.
- Secure Encryption: For data privacy, journal entries are encrypted using `cryptography`.
- Rich Interface: Intuitive GUI with entry creation, category selection, and timestamping.
- Search and Filter: Find journal entries by title, category, or date range.
- Export Functionality: Save journal entries as a `.txt` or `.csv` file.
- Timestamp Accuracy: Localized timestamp is based on the user’s timezone.
## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/DeAsiaMcQueen/personal-journal-app.git
2. Navigate to the project directory
   ```bash
   cd personal-journal-app
3. Install the required dependencies
   ```bash
   pip install tzlocal
   pip install cryptography
   pip install pytz
4. Run the application
## Usage
# Getting started
1. Login/Register
   - When you launch the application, you will see a login screen.
   - If you are a new user, click "Register" to create a new account.
   - Default admin credentials
       - Username: admin
       - Password: password
2. Create Entries
   - Enter a title and select a category from the dropdown menu after logging in.
   - Write your journal entry in the provided text box.
   - Click the "Save Entry" button to save it.
   - Upon successful save, all fields will reset for a new entry, and you will see a confirmation message.
3. View Entries
   - Click "View All Entries" to browse all saved entries.
   - Double-click on any entry to open and view its content in a separate window.
4. Search Entries
   - Use the "Search Entries" button to filter your journal entries by title, category, or date range.
5. Export Entries
   - Click "Export Entries" to save all your entries as a .txt or .csv file for backup or sharing.
# Accessing Encrypted Entries Directly
1. All journal entries are encrypted in the SQLite database for security.
2. To view these encrypted entries manually
   - Download and install DB Browser for SQLite.
   - Open the journal.db file in DB Browser.
   - Browse the journal_entries table to see encrypted data in the entry column.
   - Note: Encrypted data in the database can only be decrypted using this application with the correct encryption key.
## Contributing
We welcome contributions from the community. Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines.
When submitting a pull request, follow the steps outlined in our [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
## Code of Conduct
This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
## Changelog
All notable changes to this project are documented in the [Changelog](CHANGELOG.md).
## License
This project is licensed under the MIT License. Please have a look at the [LICENSE](LICENSE) file for details.
## Acknowledgments
1. cryptography for encryption.
2. pytz for timezone support.
3. SQLite for lightweight database management.
