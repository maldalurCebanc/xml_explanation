# XML Processing Tools

This project provides a set of tools for working with XML data, including XML to SQL conversion, XPath queries, and XQuery processing. It demonstrates various ways to handle and transform XML data using Python.

## Project Structure

- `empleados_complejos.xml` - Sample XML file containing employee data
- `empleados_schema.xsd` - XML Schema definition for the employee data
- `xml_sql_converter.py` - Tool to convert XML data to SQL statements
- `xpath_xquery_examples.py` - Examples of XPath and XQuery operations
- `requirements.txt` - Project dependencies

## Features

### XML to SQL Converter
- Converts XML data to SQL INSERT statements
- Handles complex XML structures
- Supports data type mapping
- Configurable through environment variables

### XPath and XQuery Examples
The `xpath_xquery_examples.py` file demonstrates:
- XPath queries for data extraction
- Complex data filtering
- Aggregation operations
- Formatted data output using XQuery

## Requirements

- Python 3.x
- lxml>=4.9.3
- mysql-connector-python==8.2.0
- python-dotenv==1.0.0
- python-baseX>=10.1

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### XML to SQL Converter
```bash
python xml_sql_converter.py
```

### XPath and XQuery Examples
```bash
python xpath_xquery_examples.py
```

Note: For XQuery functionality, you need to have BaseX Server running locally.

## Environment Configuration

Create a `.env` file with the following variables:
```
DB_HOST=your_host
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

## XML Schema

The project includes an XML Schema (`empleados_schema.xsd`) that defines the structure for employee data. The schema validates:
- Employee personal information
- Employment details
- Department information
- Salary data

## Contributing

Feel free to submit issues and enhancement requests.
