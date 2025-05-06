# Translation Management Tool

This directory contains the translation management tool for the Sensorem project. It provides utilities to manage, validate, and extract translations for multiple languages, ensuring consistency across the application's user interface.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview
The translation management tool is designed to handle internationalization (i18n) for the Sensorem application. It supports English (`en`) and French (`fr`) translations, stored in PO (Portable Object) files. The tool includes scripts to validate translations, extract translatable strings from source code, and manage PO files, integrated with a graphical user interface (GUI).

## Features
- **Translation Validation**:
  - Detects inconsistencies in the source language (`en`), such as `msgstr` not matching `msgid`.
  - Identifies missing translations in non-source languages (`fr`).
  - Validates format specifiers (e.g., `{}`) to ensure consistency between `msgid` and `msgstr`.
  - Supports interactive or non-interactive correction of issues.
- **PO File Management**:
  - Loads, creates, and saves PO files for supported languages.
  - Removes duplicate entries in PO files.
- **String Extraction**:
  - Extracts translatable strings from Python source code (e.g., marked with `_lazy()`).
- **Logging**:
  - Comprehensive logging for debugging and tracking operations.
- **Testing**:
  - Unit tests to verify validation, file handling, and absence of false positives.
- **GUI Integration**:
  - Displays translated strings in the application's interface (e.g., `"Processing file: {}"`).

## Directory Structure
```
translations/
├── constants.py            # Language constants (SUPPORTED_LANGS, SOURCE_LANG)
├── extract_translations.py # Script to extract translatable strings
├── logger_config.py        # Logging configuration
├── main_translations.py    # Main script with interactive menu
├── po_utils.py            # Utilities for PO file management
├── validate_translations.py # Translation validation script
├── tests/
│   └── test_translations.py # Unit tests for translation utilities
```

Translation files are stored in:
```
core/locale/
├── en/LC_MESSAGES/messages.po
├── fr/LC_MESSAGES/messages.po
```

## Dependencies
- **Python**: 3.12 or higher
- **External Libraries**:
  - `polib`: For manipulating PO files
  - `re`: For regular expression-based string extraction (standard library)
  - `logging`: For logging operations (standard library)
  - `os`, `sys`, `shutil`, `tempfile`: For file and directory handling (standard library)

Install dependencies:
```bash
pip install polib
```

## Installation
1. Clone the Sensorem repository:
   ```bash
   git clone <repository-url>
   cd Sensorem-1/Sensorem/core/utils/translations
   ```
2. Ensure Python 3.12 is installed.
3. Install `polib`:
   ```bash
   pip install polib
   ```
4. Verify the `core/locale/` directory contains `en` and `fr` PO files.

## Usage
The main entry point is `main_translations.py`, which provides an interactive menu.

### Running the Tool
- **Via PyCharm**:
  1. Open `main_translations.py` in PyCharm.
  2. Right-click and select "Run 'main_translations'".
- **Via Command Line**:
  ```bash
  cd Sensorem-1/Sensorem/core/utils/translations
  python main_translations.py
  ```
- **Via File Explorer**:
  - Double-click `main_translations.py` (ensure Python is associated with `.py` files).

### Menu Options
Upon running `main_translations.py`, a menu appears:
```
Translation Management Menu:
2. Validate translations
6. Run all tasks
9. Check translations
0. Exit
```
- **Option 2 (Validate)**: Validates PO files and proposes corrections interactively.
- **Option 6 (All)**: Runs all translation-related tasks (e.g., validation, extraction).
- **Option 9 (Check)**: Validates PO files non-interactively and reports issues.
- **Option 0 (Exit)**: Exits the program.

### Testing Translations in the GUI
1. Modify a PO file, e.g., `core/locale/en/LC_MESSAGES/messages.po`:
   ```po
   msgid "Processing file: {}"
   msgstr "TEST Processing file: {}"
   ```
2. Run the Sensorem application in English to verify the updated string.
3. For French, check `core/locale/fr/LC_MESSAGES/messages.po`, e.g.:
   ```po
   msgid "English"
   msgstr "Anglais"
   ```

### Extracting Translations
To extract new translatable strings:
```bash
python extract_translations.py
```
This scans Python files for strings marked with `_lazy()` and updates PO files.

## Testing
Unit tests are provided to ensure the reliability of the translation tool.

### Running Tests
- **Via PyCharm**:
  1. Open `tests/test_translations.py`.
  2. Right-click and select "Run 'unittest in test_translations'".
- **Via Command Line**:
  ```bash
  cd Sensorem-1/Sensorem/core/utils/translations/tests
  python test_translations.py
  ```
- **Expected Output**:
  ```
  .....
  Ran 5 tests in 0.XXXs
  OK
  ```

### Test Coverage
- Loading and creating PO files.
- Saving PO files.
- Validating format specifiers.
- Detecting translation inconsistencies.
- Ensuring no false positives in validation.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure tests pass before submitting changes:
```bash
python tests/test_translations.py
```

## License
This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.