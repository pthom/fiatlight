from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList

ABORTING = False


def is_aborting() -> bool:
    global ABORTING
    return ABORTING


def set_aborting(v: bool) -> None:
    global ABORTING
    ABORTING = v


def bubble_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using bubble sort. Very slow"""
    n = len(numbers)
    for i in range(n):
        if ABORTING:
            return numbers
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return numbers


def selection_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using selection sort"""
    n = len(numbers)
    for i in range(n):
        if ABORTING:
            return numbers
        min_index = i
        for j in range(i + 1, n):
            if numbers[j] < numbers[min_index]:
                min_index = j
        numbers[i], numbers[min_index] = numbers[min_index], numbers[i]
    return numbers


def insertion_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using insertion sort"""
    n = len(numbers)
    for i in range(1, n):
        if ABORTING:
            return numbers
        key = numbers[i]
        j = i - 1
        while j >= 0 and key < numbers[j]:
            numbers[j + 1] = numbers[j]
            j -= 1
        numbers[j + 1] = key
    return numbers


def merge_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using merge sort"""

    def merge(numbers: NumbersList, left: int, middle: int, right: int) -> None:
        n1 = middle - left + 1
        n2 = right - middle
        left_array = numbers.slice(left, middle + 1).copy()
        right_array = numbers.slice(middle + 1, right + 1).copy()

        i = j = 0
        k = left
        while i < n1 and j < n2:
            if left_array[i] <= right_array[j]:
                numbers[k] = left_array[i]
                i += 1
            else:
                numbers[k] = right_array[j]
                j += 1
            k += 1

        while i < n1:
            numbers[k] = left_array[i]
            i += 1
            k += 1

        while j < n2:
            numbers[k] = right_array[j]
            j += 1
            k += 1

    def merge_sort_recursive(numbers: NumbersList, left: int, right: int) -> None:
        if left < right:
            if ABORTING:
                return
            middle = (left + right) // 2
            merge_sort_recursive(numbers, left, middle)
            merge_sort_recursive(numbers, middle + 1, right)
            merge(numbers, left, middle, right)

    merge_sort_recursive(numbers, 0, len(numbers) - 1)
    return numbers


def quick_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using quick sort. *Might be slow for some edge cases, like sorted/reverse sorted list, etc.*"""

    def partition(numbers: NumbersList, low: int, high: int) -> int:
        i = low - 1
        pivot = numbers[high]
        for j in range(low, high):
            if numbers[j] < pivot:
                i += 1
                numbers[i], numbers[j] = numbers[j], numbers[i]
        numbers[i + 1], numbers[high] = numbers[high], numbers[i + 1]
        return i + 1

    def quick_sort_recursive(numbers: NumbersList, low: int, high: int) -> None:
        if ABORTING:
            return
        if low < high:
            pi = partition(numbers, low, high)
            quick_sort_recursive(numbers, low, pi - 1)
            quick_sort_recursive(numbers, pi + 1, high)

    quick_sort_recursive(numbers, 0, len(numbers) - 1)
    return numbers


def quick_sort_median_of_three(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using quick sort with median-of-three pivot selection
    A little optimization to avoid the worst case scenarios of quick sort (i.e. reverse sorted list, etc.)
    """

    def median_of_three(numbers: NumbersList, low: int, high: int) -> int:
        mid = (low + high) // 2
        if numbers[low] > numbers[mid]:
            numbers[low], numbers[mid] = numbers[mid], numbers[low]
        if numbers[low] > numbers[high]:
            numbers[low], numbers[high] = numbers[high], numbers[low]
        if numbers[mid] > numbers[high]:
            numbers[mid], numbers[high] = numbers[high], numbers[mid]
        return mid

    def partition(numbers: NumbersList, low: int, high: int) -> int:
        mid = median_of_three(numbers, low, high)
        numbers[mid], numbers[high] = numbers[high], numbers[mid]
        pivot = numbers[high]
        i = low - 1
        for j in range(low, high):
            if numbers[j] < pivot:
                i += 1
                numbers[i], numbers[j] = numbers[j], numbers[i]
        numbers[i + 1], numbers[high] = numbers[high], numbers[i + 1]
        return i + 1

    def quick_sort_recursive(numbers: NumbersList, low: int, high: int) -> None:
        if ABORTING:
            return
        if low < high:
            pi = partition(numbers, low, high)
            quick_sort_recursive(numbers, low, pi - 1)
            quick_sort_recursive(numbers, pi + 1, high)

    quick_sort_recursive(numbers, 0, len(numbers) - 1)
    return numbers
