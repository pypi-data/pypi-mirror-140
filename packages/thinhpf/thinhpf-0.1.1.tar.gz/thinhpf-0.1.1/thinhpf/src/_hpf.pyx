# distutils: language = c++

from libc.stdint cimport int32_t, uint32_t
from .src._hpf cimport *

cimport cython

ctypedef int32_t CapInt32
ctypedef float CapFloat32

# 
cdef class HpfCapInt32HFFIFO:
    cdef Hpf[CapInt32, HF, FIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapInt32, HF, FIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapInt32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapInt32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapInt32HFLIFO:
    cdef Hpf[CapInt32, HF, LIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapInt32, HF, LIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapInt32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapInt32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapInt32LFFIFO:
    cdef Hpf[CapInt32, LF, FIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapInt32, LF, FIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapInt32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapInt32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapInt32LFLIFO:
    cdef Hpf[CapInt32, LF, LIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapInt32, LF, LIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapInt32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapInt32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapFloat32HFFIFO:
    cdef Hpf[CapFloat32, HF, FIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapFloat32, HF, FIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapFloat32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapFloat32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapFloat32HFLIFO:
    cdef Hpf[CapFloat32, HF, LIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapFloat32, HF, LIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapFloat32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapFloat32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapFloat32LFFIFO:
    cdef Hpf[CapFloat32, LF, FIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapFloat32, LF, FIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapFloat32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapFloat32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# 

cdef class HpfCapFloat32LFLIFO:
    cdef Hpf[CapFloat32, LF, LIFO]* c_hpf

    def __cinit__(self, size_t expected_nodes=0, size_t expected_arcs=0):
        self.c_hpf = new Hpf[CapFloat32, LF, LIFO](expected_nodes, expected_arcs)

    def __dealloc__(self):
        del self.c_hpf

    def reserve_nodes(self, size_t num):
        self.c_hpf.reserve_nodes(num)

    def reserve_edges(self, size_t num):
        self.c_hpf.reserve_edges(num)

    def add_node(self, size_t num):
        return self.c_hpf.add_node(num)

    def add_edge(self, uint32_t i, uint32_t j, CapFloat32 capacity):
        self.c_hpf.add_edge(i, j, capacity)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    def add_edges(self,  uint32_t[::1] i, uint32_t[::1] j, CapFloat32[::1] capacity):
        cdef Py_ssize_t length = i.shape[0]

        assert i.shape[0] == j.shape[0] == capacity.shape[0]

        for n in range(length):
            self.c_hpf.add_edge(i[n], j[n], capacity[n])

    def mincut(self):
        self.c_hpf.mincut()

    def what_label(self, uint32_t node):
        return self.c_hpf.what_label(node)

    def compute_maxflow(self):
        return self.c_hpf.compute_maxflow()

    def recover_flow(self):
        self.c_hpf.recover_flow()

    def set_source(self, uint32_t s):
        self.c_hpf.set_source(s)

    def set_sink(self, uint32_t t):
        self.c_hpf.set_sink(t)

# </template>