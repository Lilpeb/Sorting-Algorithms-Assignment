# Sorting Algorithms Benchmark GUI

A PyQt6 GUI application for benchmarking sorting algorithms with Google Sheets integration.

## Files

- `SortingGUI.py` - Complete GUI application with sorting algorithms and Google Sheets upload
- `credentials.json` - Google Sheets API credentials (required for Sheets upload)
- `Info` - Additional information

## Features

- **Array Size Selection**: Choose array size from 10 to 100,000 elements
- **Algorithm Selection**: Check/uncheck which algorithms to benchmark:
  - Merge Sort
  - Quick Sort
  - Thanos Sort
- **Google Sheets Integration**: Optional upload of results to Google Sheets
- **Real-time Progress**: Shows progress during benchmarking
- **Detailed Results**: Displays timing and memory usage statistics
- **Memory Profiling**: Tracks peak memory usage for each algorithm

## Requirements

- Python 3.8+
- PyQt6
- NumPy
- Google API client libraries (for Google Sheets integration)

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install PyQt6 numpy gspread google-auth google-auth-oauthlib
   ```

## Usage

Run the GUI application:
```bash
python SortingGUI.py
```

### GUI Controls

1. **Set array size** using the spin box (10-100,000 elements)
2. **Choose algorithms** by checking/unchecking the boxes
3. **Enable Google Sheets upload** by checking the "Upload results to Google Sheets" option
4. **Click "Run Benchmark"** to start
5. **Watch progress** in the status bar
6. **View results** in the text area below

## Google Sheets Setup

To enable Google Sheets upload:

1. Set up a Google Cloud Project with the Google Sheets API enabled
2. Create a service account and download the `credentials.json` file
3. Place `credentials.json` in the project root directory
4. Share your Google Sheet with the service account email
5. Check the "Upload results to Google Sheets" option in the GUI

The application will automatically create a spreadsheet called "Sort Benchmarks" if it doesn't exist.

## Algorithms

- **Merge Sort**: O(n log n) time, stable sort, in-place merge
- **Quick Sort**: O(n log n) average time, in-place partitioning
- **Thanos Sort**: Variant of quicksort using list comprehensions