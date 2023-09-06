# Script to show prototype of numerical quicksort algorithm
# Written by Maria Achim
# Started on 29th July 2023

def partition(array, low, high):
    pivot = array[high] # rightmost element is selected as pivot point
    i = low - 1 # i is always 1 less than low, represents pivot's correct position
    for j in range(low, high): # iterates over each element before pivot point
        if array[j] <= pivot:
            i = i + 1 # increment index of smaller element
            (array[i], array[j]) = (array[j], array[i]) # swap elements
    (array[i + 1], array[high]) = (array[high], array[i + 1]) # move pivot to correct place in array
    return i + 1

def quicksort(array, low, high):
    if low < high:
        pi = partition(array, low, high)
        # recursion - separately sort elements before and after partition
        quicksort(array, low, pi - 1) # sorts left of pivot point
        quicksort(array, pi + 1, high) # sorts right of pivot point

def main_sort(data): # main function for quicksort and unit tests
    quicksort(data, 0, len(data) - 1)
    return data