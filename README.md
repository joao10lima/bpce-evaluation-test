﻿# Reviseur (bpce-evaluation-test)

Reviseur is a project that uses Selenium to perform web crawling, verify snapshots, and handle errors by creating logs, reports, and videos of the session. The expected snapshots for comparison are configured in a `param.xml` file, which comes with default settings that can be customized as needed.

## Features

- Automates web crawling with Selenium.
- Runs operations in the background.
- Compares screenshots to expected snapshots.
- Generates reports and captures video in case of errors.
- Logs all activities for review.

## Requirements

Python 3.11 is required. Package dependencies are managed with **Pipenv**.

## Dependencies
- Install dependencies using pipenv:

```bash
    pipenv install
```
- Activate the pipenv shell:
```bash
    pipenv shell
```

## Running the Project

To start the program, use:

```bash
pipenv run python .\reviseur\main.py
```

## Configuration

- param.xml: The program uses param.xml to specify expected snapshots for comparison with Lackey. A default configuration is provided, but you may customize it as needed for your use case.

## To generate the executable

Use the `.\build.bat` script.

```bash
.\build.bat
```

## Code Quality Tools

To maintain code quality, the following tools are configured in the Pipfile:

isort: Sorts imports automatically.
black: Formats code according to style guidelines.
flake8 (with flake8-bugbear): Provides linting and catches common issues.

Run each tool with the following Pipenv commands:

```bash
pipenv run isort --profile black .
pipenv run black .
pipenv run flake8 .
```

## Pipfile Overview

- The Pipfile manages all dependencies and development tools:

    - Packages:
        - lackey==0.7.4: Provides image-based automation for comparison.
        - numpy==1.26.4: A library for numerical computations.
        - reportlab==4.2.5: Used for generating PDF reports.
        - mss==9.0.2: Enables screen capturing.
        - selenium==4.26.1: Web automation library.

    - Development Packages:
        - pyinstaller==6.11.0: Used for creating standalone executables.
        - black, isort, and flake8-bugbear: Formatting and linting tools.

    - Python Version:
        - Python 3.11

## Error Handling

- If an error occurs during the web crawling process:
    - A video recording of the session is saved.
    - A report is generated.
    - All actions and errors are logged for review.

## Usage Tips
- Ensure Selenium is configured to run in headless mode if background operation is needed.
- Customize the param.xml file with the expected snapshots for your specific tests.
