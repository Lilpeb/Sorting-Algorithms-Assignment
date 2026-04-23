import numpy as np
from time import perf_counter

def merge_sort(arr):
    # Base case: a list with 0 or 1 element is already sorted
    if len(arr) <= 1:
        return arr

    # 1. Divide: Find the middle and split the array into two halves
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # 2. Conquer: Recursively call merge_sort on both halves
    merge_sort(left_half)
    merge_sort(right_half)

    # 3. Combine: Merge the sorted halves back into the original array
    i = j = k = 0

    # Compare elements from left and right halves
    while i < len(left_half) and j < len(right_half):
        if left_half[i] < right_half[j]:
            arr[k] = left_half[i]
            i += 1
        else:
            arr[k] = right_half[j]
            j += 1
        k += 1

    # Copy any remaining elements from left_half
    while i < len(left_half):
        arr[k] = left_half[i]
        i += 1
        k += 1

    # Copy any remaining elements from right_half
    while j < len(right_half):
        arr[k] = right_half[j]
        j += 1
        k += 1


def quick_sort(arr):
    # Base case: arrays with 0 or 1 element are already sorted
    if len(arr) <= 1:
        return arr
    
    # Selecting the middle element as the pivot
    pivot = arr[len(arr) // 2]
    
    # Partitioning the array into three parts
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # Recursively sorting left and right, then joining them
    return quick_sort(left) + middle + quick_sort(right)

def thanos_sort(arr):
    # Base case: arrays with 0 or 1 element are already sorted
    if len(arr) <= 1:
        return arr
    
    # Selecting the middle element as the pivot
    pivot = arr[len(arr) // 2]
    
    # Partitioning the array into three parts
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # Recursively sorting left and right, then joining them
    return thanos_sort(left) + middle + thanos_sort(right)


SIZE = int(input('Enter the size of the array to sort:'))
Data_set = np.random.randint(0, 100000, size=SIZE)

sort_algorithms = (
    merge_sort,
    quick_sort,
    thanos_sort)

times = []
for algo in sort_algorithms:
    start_time = perf_counter()
    Data_set = Data_set.copy()
    algo(Data_set)
    end_time = perf_counter() - start_time
    times.append(end_time)


min_time = min(times)
fastest_algo = sort_algorithms[times.index(min_time)]
print(f'\n{fastest_algo.__name__} is fastest at {min_time:.7f} seconds')

algo_times = list(zip([algo.__name__ for algo in sort_algorithms], times))
algo_times.sort(key=lambda x: x[1])
for i, (name, time) in enumerate(algo_times, 1):
    print(f'{i}. {name}: {time:.7f} seconds')








