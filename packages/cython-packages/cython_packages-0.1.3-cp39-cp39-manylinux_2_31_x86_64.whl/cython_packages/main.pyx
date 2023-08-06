cpdef say(int x):
    cdef str y = "Hello World"
    cdef int i
    for i in range(x):
        print(y)

