import sys
import numpy as np
from time import perf_counter
import tracemalloc
import gspread
from gspread.exceptions import SpreadsheetNotFound
from google.oauth2.service_account import Credentials
from datetime import datetime

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    merge_sort(left_half)
    merge_sort(right_half)
    i = j = k = 0
    while i < len(left_half) and j < len(right_half):
        if left_half[i] < right_half[j]:
            arr[k] = left_half[i]
            i += 1
        else:
            arr[k] = right_half[j]
            j += 1
        k += 1
    while i < len(left_half):
        arr[k] = left_half[i]
        i += 1
        k += 1
    while j < len(right_half):
        arr[k] = right_half[j]
        j += 1
        k += 1

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


def read_size(prompt='Enter the size of the array to sort: '):
    while True:
        try:
            value = input(prompt)
            return int(value)
        except ValueError:
            print(f"Invalid integer: {value!r}. Please enter a whole number.")


# ── Google Sheets setup ──────────────────────────────────────────────────────
def get_sheet(sheet_name="Sort Benchmarks"):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open(sheet_name).sheet1
        print(f"✓ Connected to Google Sheet: '{sheet_name}'")
    except SpreadsheetNotFound:
        print(f"⚠ Spreadsheet '{sheet_name}' not found. Creating new spreadsheet...")
        sheet = client.create(sheet_name).sheet1
        print(f"✓ Created new Google Sheet: '{sheet_name}'")
    except Exception as e:
        raise Exception(f"Failed to access Google Sheets: {e}")

    # Write header row if the sheet is empty
    if not sheet.get_all_values():
        sheet.append_row([
            "Timestamp", "Array Size", "Algorithm",
            "Time (s)", "Peak Memory (bytes)", "Peak Memory (MB)"
        ])
    return sheet

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
    print(f"\n✓ Results written to Google Sheets ({len(rows)} rows)")
# ────────────────────────────────────────────────────────────────────────────


if sys.stdin.isatty():
    SIZE = read_size()
else:
    print('Non-interactive stdin detected. Using default size = 1000.')
    SIZE = 1000

Data_set = np.random.randint(0, 100000, size=SIZE)

sort_algorithms = (merge_sort, quick_sort, thanos_sort)

times = []
spaces = []
memory_stats = []

# Test each algorithm
for algo in sort_algorithms:
    # Time measurement
    start_time = perf_counter()
    data_copy = Data_set.copy()
    algo(data_copy)
    end_time = perf_counter() - start_time
    times.append(end_time)
    
    # Memory measurement with detailed stats
    mem_stats = test_memory_usage(algo, Data_set, iterations=5)  # Run 5 times for averaging
    spaces.append(mem_stats['peak_memory_bytes'])
    memory_stats.append(mem_stats)

# Print results (unchanged)
min_time = min(times)
fastest_algo = sort_algorithms[times.index(min_time)]
print(f'\n{fastest_algo.__name__} is fastest at {min_time:.7f} seconds')

algo_times = list(zip([algo.__name__ for algo in sort_algorithms], times))
algo_times.sort(key=lambda x: x[1])
for i, (name, time) in enumerate(algo_times, 1):
    print(f'{i}. {name}: {time:.7f} seconds')

algo_spaces = list(zip([algo.__name__ for algo in sort_algorithms], spaces))
algo_spaces.sort(key=lambda x: x[1])
print('\nSpace complexity (peak memory usage):')
for i, (name, space) in enumerate(algo_spaces, 1):
    print(f'{i}. {name}: {space:.0f} bytes ({space / (1024**2):.2f} MB)')

# Write to Google Sheets
try:
    sheet = get_sheet("Sort Benchmarks")   # ← change to your sheet's name
    write_results_to_sheet(sheet, SIZE, sort_algorithms, times, memory_stats)
except Exception as e:
    print(f"⚠ Could not write to Google Sheets: {e}")
    print("\nTroubleshooting steps:")
    print("1. Verify credentials.json is in the project root")
    print("2. Ensure the service account has edit access to the spreadsheet")
    print("3. Check that the spreadsheet name 'Sort Benchmarks' is correct")
    print("4. If creating a new spreadsheet, ensure the service account has Google Drive access")