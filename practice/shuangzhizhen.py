def code_167():
    numbers = [2, 7, 11, 15]
    target = 9

    i = 0
    j = len(numbers) - 1

    while i < j:
        if numbers[i] + numbers[j] < target:
            i += 1
        elif numbers[i] + numbers[j] > target:
            j -= 1
        else:
            print((numbers[i], numbers[j]))
            break


def code_11():
    heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    i, j = 0, len(heights) - 1
    maxarea = -1
    while i < j:
        x = j - i
        y = min(heights[i], heights[j])
        area = x * y
        if heights[i] <= heights[j]:
            i += 1
        elif heights[i] > heights[j]:
            j -= 1

        if area > maxarea:
            maxarea = area
    print(maxarea)


def code_15():
    li = [-1, 0, 1, 2, -1, -4]
    sli = sorted(li)  # -4,-1,-1,0,1,2
    i,j = 0, len(sli)-1
    while i<j:
        


    assert ans == [[-1, -1, 2], [-1, 0, 1]]


code_11()
