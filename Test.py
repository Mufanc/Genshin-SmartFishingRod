import numpy as np

arr = np.array([
    [[1, 1, 1], [1, 1, 1], [1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
    [[1, 1, 1], [1, 1, 1], [1, 1, 1], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
])

# print(np.average(arr, axis=0) == np.array([[3, 3, 3], [4, 4, 4]]))
#
# print(np.sum(arr, axis=2))
# print(np.sum(arr, axis=(2, 0)))

sample = np.average(arr, axis=0)
print(sample)
print('----------------')

yellow = [(1, 1, 1), (2, 2, 2)]


def polar(index):
    segment = sample[index-1:index+2]
    if any(np.all(segment == color) for color in yellow):
        return 'yellow'
    # if np.all(segment == green):
    #     return 'progress'
    # return 'normal'


smooth = [polar(i) for i in range(1, len(sample) - 1)]
print(smooth)

entity = [(0, 4), (1, 3)]
print(np.average([p[1] - p[0] for p in entity]))
