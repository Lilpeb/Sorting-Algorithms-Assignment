import sys
import numpy as np
from time import perf_counter
import tracemalloc
import gspread
from gspread.exceptions import SpreadsheetNotFound
from google.oauth2.service_account import Credentials
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QCheckBox, QTextEdit, QProgressBar, QGroupBox,
                             QSpinBox, QMessageBox, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

# Sorting algorithms
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    left_sorted = merge_sort(left_half)
    right_sorted = merge_sort(right_half)

    # Merge the sorted halves
    result = []
    i = j = 0
    while i < len(left_sorted) and j < len(right_sorted):
        if left_sorted[i] < right_sorted[j]:
            result.append(left_sorted[i])
            i += 1
        else:
            result.append(right_sorted[j])
            j += 1

    result.extend(left_sorted[i:])
    result.extend(right_sorted[j:])

    # Copy back to original array for in-place behavior
    for i in range(len(result)):
        arr[i] = result[i]
    return arr

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def thanos_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return thanos_sort(left) + middle + thanos_sort(right)

def test_memory_usage(algorithm, data, iterations=1):
    """
    Test memory usage of a sorting algorithm over multiple iterations.

    Args:
        algorithm: The sorting function to test
        data: The data array to sort
        iterations: Number of times to run the test for averaging

    Returns:
        dict: Memory statistics including peak memory usage
    """
    peak_memories = []

    for _ in range(iterations):
        tracemalloc.start()
        data_copy = data.copy()
        algorithm(data_copy)
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        peak_memories.append(peak_mem)

    avg_peak = sum(peak_memories) / len(peak_memories)

    return {
        'algorithm': algorithm.__name__,
        'iterations': iterations,
        'peak_memory_bytes': avg_peak,
        'peak_memory_mb': avg_peak / (1024**2)
    }

# Google Sheets functions
def get_sheet(sheet_name="Sort Benchmarks"):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(sheet_name).sheet1
        return sheet, f"✓ Connected to Google Sheet: '{sheet_name}'"
    except SpreadsheetNotFound:
        sheet = client.create(sheet_name).sheet1
        return sheet, f"✓ Created new Google Sheet: '{sheet_name}'"
    except Exception as e:
        raise Exception(f"Failed to access Google Sheets: {e}")

def write_results_to_sheet(sheet, size, sort_algorithms, times, memory_stats):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for algo, time, mem_stat in zip(sort_algorithms, times, memory_stats):
        rows.append([
            timestamp,
            size,
            algo.__name__,
            round(time, 7),
            mem_stat['peak_memory_bytes'],
            round(mem_stat['peak_memory_mb'], 4)
        ])
    sheet.append_rows(rows)
    return f"✓ Results written to Google Sheets ({len(rows)} rows)"

class BenchmarkWorker(QThread):
    """Worker thread to run benchmarks without blocking the GUI"""
    progress = pyqtSignal(str)  # Signal for progress updates
    finished = pyqtSignal(dict)  # Signal when all benchmarks are done
    sheets_result = pyqtSignal(str)  # Signal for Google Sheets upload result

    def __init__(self, algorithms, data_size, upload_to_sheets=False):
        super().__init__()
        self.algorithms = algorithms
        self.data_size = data_size
        self.upload_to_sheets = upload_to_sheets

    def run(self):
        self.progress.emit("Generating random data...")
        data = np.random.randint(0, 100000, size=self.data_size)

        results = {
            'times': [],
            'memory_stats': [],
            'algorithms': []
        }

        for i, algo in enumerate(self.algorithms):
            self.progress.emit(f"Running {algo.__name__}...")

            # Time measurement
            start_time = perf_counter()
            data_copy = data.copy()
            algo(data_copy)
            end_time = perf_counter() - start_time

            # Memory measurement
            mem_stats = test_memory_usage(algo, data, iterations=3)

            results['times'].append(end_time)
            results['memory_stats'].append(mem_stats)
            results['algorithms'].append(algo)

        self.progress.emit("Benchmark complete!")

        # Upload to Google Sheets if requested
        if self.upload_to_sheets:
            self.progress.emit("Uploading to Google Sheets...")
            try:
                sheet, connect_msg = get_sheet("Sort Benchmarks")
                upload_msg = write_results_to_sheet(sheet, self.data_size,
                                                  results['algorithms'],
                                                  results['times'],
                                                  results['memory_stats'])
                self.sheets_result.emit(f"{connect_msg}\n{upload_msg}")
            except Exception as e:
                self.sheets_result.emit(f"⚠ Could not write to Google Sheets: {e}")
        else:
            self.sheets_result.emit("")

        self.finished.emit(results)

class SortingBenchmarkGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sorting Algorithms Benchmark")
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        layout = QVBoxLayout(central_widget)

        # Input section
        input_group = QGroupBox("Benchmark Configuration")
        input_layout = QVBoxLayout(input_group)

        # Array size input
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Array Size:"))
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(10, 100000)
        self.size_spinbox.setValue(1000)
        self.size_spinbox.setSingleStep(100)
        size_layout.addWidget(self.size_spinbox)
        size_layout.addStretch()
        input_layout.addLayout(size_layout)

        # Algorithm selection
        algo_group = QGroupBox("Select Algorithms")
        algo_layout = QVBoxLayout(algo_group)

        self.merge_checkbox = QCheckBox("Merge Sort")
        self.merge_checkbox.setChecked(True)
        algo_layout.addWidget(self.merge_checkbox)

        self.quick_checkbox = QCheckBox("Quick Sort")
        self.quick_checkbox.setChecked(True)
        algo_layout.addWidget(self.quick_checkbox)

        self.thanos_checkbox = QCheckBox("Thanos Sort")
        self.thanos_checkbox.setChecked(True)
        algo_layout.addWidget(self.thanos_checkbox)

        # Google Sheets option
        self.sheets_checkbox = QCheckBox("Upload results to Google Sheets")
        self.sheets_checkbox.setChecked(False)
        algo_layout.addWidget(self.sheets_checkbox)

        input_layout.addWidget(algo_group)

        # Run button
        self.run_button = QPushButton("Run Benchmark")
        self.run_button.clicked.connect(self.run_benchmark)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        input_layout.addWidget(self.run_button)

        layout.addWidget(input_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.status_label)

        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier New", 10))
        results_layout.addWidget(self.results_text)

        layout.addWidget(results_group)

        # Initialize worker
        self.worker = None
        self.sheets_message = ""

    def run_benchmark(self):
        # Get selected algorithms
        selected_algorithms = []
        if self.merge_checkbox.isChecked():
            selected_algorithms.append(merge_sort)
        if self.quick_checkbox.isChecked():
            selected_algorithms.append(quick_sort)
        if self.thanos_checkbox.isChecked():
            selected_algorithms.append(thanos_sort)

        if not selected_algorithms:
            QMessageBox.warning(self, "No Algorithms Selected",
                              "Please select at least one sorting algorithm to benchmark.")
            return

        # Get array size
        data_size = self.size_spinbox.value()

        # Disable run button and show progress
        self.run_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Starting benchmark...")
        self.results_text.clear()

        # Create and start worker thread
        self.worker = BenchmarkWorker(selected_algorithms, data_size, self.sheets_checkbox.isChecked())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.display_results)
        self.worker.sheets_result.connect(self.handle_sheets_result)
        self.worker.start()

    def update_progress(self, message):
        self.status_label.setText(message)

    def handle_sheets_result(self, message):
        self.sheets_message = message
        if message and "⚠" in message:
            QMessageBox.warning(self, "Google Sheets Error", message)
        elif message:
            QMessageBox.information(self, "Google Sheets", message)

    def display_results(self, results):
        # Hide progress and re-enable button
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.status_label.setText("Benchmark complete!")

        # Format and display results
        output = "SORTING ALGORITHMS BENCHMARK RESULTS\n"
        output += "=" * 50 + "\n\n"

        # Time results
        times = results['times']
        algorithms = results['algorithms']

        min_time = min(times)
        fastest_algo = algorithms[times.index(min_time)]

        output += f"Fastest Algorithm: {fastest_algo.__name__} at {min_time:.7f} seconds\n\n"

        output += "TIMING RESULTS (sorted by speed):\n"
        algo_times = list(zip([algo.__name__ for algo in algorithms], times))
        algo_times.sort(key=lambda x: x[1])
        for i, (name, time) in enumerate(algo_times, 1):
            output += f"{i}. {name}: {time:.7f} seconds\n"

        # Memory results
        memory_stats = results['memory_stats']
        output += "\nMEMORY USAGE RESULTS (sorted by efficiency):\n"
        algo_spaces = list(zip([algo.__name__ for algo in algorithms],
                              [stat['peak_memory_bytes'] for stat in memory_stats]))
        algo_spaces.sort(key=lambda x: x[1])
        for i, (name, space) in enumerate(algo_spaces, 1):
            output += f"{i}. {name}: {space:.0f} bytes ({space / (1024**2):.2f} MB)\n"

        # Detailed memory stats
        output += "\nDETAILED MEMORY STATISTICS:\n"
        for stat in memory_stats:
            output += f"\n{stat['algorithm']}:\n"
            output += f"  Iterations: {stat['iterations']}\n"
            output += f"  Peak Memory: {stat['peak_memory_bytes']:.0f} bytes ({stat['peak_memory_mb']:.2f} MB)\n"

        # Add Google Sheets message if any
        if self.sheets_message:
            output += f"\n{self.sheets_message}\n"

        self.results_text.setText(output)

def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    window = SortingBenchmarkGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()