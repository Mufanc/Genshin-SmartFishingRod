import numpy as np

arr = np.array([
    1, 5
])

brr = np.array([
    2, 3
])

arr[arr < brr] = brr[arr < brr]

print(arr)
