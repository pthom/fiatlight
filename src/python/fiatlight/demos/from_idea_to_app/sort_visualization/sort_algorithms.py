from fiatlight.demos.from_idea_to_app.sort_visualization.number_list import NumbersList


# Just to get started we will write bubble sorts and selection sorts.
def bubble_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using bubble sort"""
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return numbers


def selection_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using selection sort"""
    n = len(numbers)
    for i in range(n):
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
            middle = (left + right) // 2
            merge_sort_recursive(numbers, left, middle)
            merge_sort_recursive(numbers, middle + 1, right)
            merge(numbers, left, middle, right)

    merge_sort_recursive(numbers, 0, len(numbers) - 1)
    return numbers


def quick_sort(numbers: NumbersList) -> NumbersList:
    """Sort the numbers using quick sort"""

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
        if low < high:
            pi = partition(numbers, low, high)
            quick_sort_recursive(numbers, low, pi - 1)
            quick_sort_recursive(numbers, pi + 1, high)

    quick_sort_recursive(numbers, 0, len(numbers) - 1)
    return numbers
