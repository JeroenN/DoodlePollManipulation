def partition(arr, idx, low, high):
    pivot = arr[high]

    i = low - 1

    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            idx[i], idx[j] = idx[j], idx[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    idx[i + 1], idx[high] = idx[high], idx[i + 1]
    return i + 1

def quick_sort(arr, idx, low, high):
    if low < high:
        pi = partition(arr, idx, low, high)

        quick_sort(arr, idx, low, pi - 1)
        quick_sort(arr, idx, pi + 1, high)

