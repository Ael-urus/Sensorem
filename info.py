# info.py
"""
 * Sensorem - info.py module documentation

This module contains information about the software version,
release notes and module descriptions.

project_name = “Sensorem"
description_projet = “This project analyzes sensor signals to make a connection with a reference sensor. Provides a report on calibration processing”.
authors = [Aelurus]
contributor = [Bruno]
date_creation = “2024-06-14”

date = “30/03/2025
version = “0.4.3.9”

version_notes__ =

Several modifications:
* Addition of a database and its management with insertion of sensors for PDF generation (02/02/2025)
* Addition of regression processing with a conversion coefficient (19/01/2025)
* Upgrade of PDF generation: Adaptation of functions to the new GUI (28/12/2024).
* General GUI redesign: Functional implementation (12/25/2024).
* Management of sensor names and positions from GUI: functional implementation (09/12/2024).
* Venturi detection threshold correction: Threshold adjustment (06/12/2024).
* Bug fixes: Various unspecified bug fixes.
* Data clean-up: Removal of “#N/A” and “Calibration” strings when retrieving data (18/02).
* Graph enhancement: Added legends to graphs in the graphical interface (02/18).
* Display of raw data: Display of sensor values in the “Here's the data found” window (02/18).
* Moving average: Addition of a moving average with a step of 2 before the detection of levels. An option to manipulate this parameter in the GUI is planned (03/24/2024).

Bugs corrected and remaining: Some are done, I need to update and check this part

* Bearing detection: Increase in the number of points for bearing detection (from 10 to 13) to resolve problems encountered on some runs (18/02).
* Offset in value tables: Correction of an offset in the filling of value tables (average and deviation) in the case of processing with several sensors, caused by different values in the bearings (02/15).
* Color inversion in PDF legend: Correction of color inversion in PDF report measurement legend (02/18).
* Single sensor display: Fixed bug that displayed only one sensor in the “Here are the data found” window (02/25).
* Clean-up of #DIV/! errors: Added clean-up for #DIV/! values (02/25).
* Loss of selected file: Persistent bug: When validating the username, the selected file is lost and the first file in the list is processed instead.

__modules_description__ =

Summary of current modules and their roles:

* `main.py` : Application entry point. Launches the graphical interface.
* gui_V3.py` : Manages the GUI, user interaction, graphics display and calls to other modules.
* FunctionsCSV.py`: Manages reading and processing of CSV files.
* SignalFunctions.py`: Contains signal processing functions (filtering, step detection, etc.).
* FunctionPdf.py`: Generates PDF reports.
* FunctionsGui_V3.py`: Provides utility functions for the graphical interface (log management, etc.).
* FunctionsBD.py`: Manages the Database window and all database functions.


An idea for refactoring:

Sensorem/
│
├── __init__.py
├── compile_translations.py
├── config.py
├── main.py
├── requirements.txt
├── .env
├── README.md
├── core/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── csv_handler.py     (Refactoring of FunctionsCSV.py)
│   │   └── database_manager.py (Refactoring of FunctionsDB.py)
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── db_tab.py
│   │   ├── main_window.py      (Refactoring of gui_V3.py)
│   │   ├── processing_tab.py
│   │   └── utils.py            (Part of FunctionsGui_V3.py)
│   ├── locale/
│   │   ├── en/LC_MESSAGES/
│   │   │   ├── messages.po
│   │   │   └── messages.mo
│   │   └── fr/LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   ├── processing/
│   │   ├── __init__.py
│   │   └── signal_processor.py (Refactoring of FunctionsSignal.py)
│   ├── reporting/
│   │   ├── __init__.py
│   │   └── pdf_generator.py    (Refactoring of FunctionsPdf.py)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_csv_handler.py
│   │   ├── test_database_manager.py
│   │   ├── test_signal_processor.py
│   │   └── test_pdf_generator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── i18n.py
│   │   └── logger.py           (art of FunctionsGui_V3.py, log management)
│   └──
└──
"""