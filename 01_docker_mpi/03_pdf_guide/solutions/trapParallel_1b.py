#trapParallel_1.py
#example to run: mpiexec -n 4 python trapParallel_1.py 0.0 1.0 10000
import numpy
import sys
from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
#takes in command-line arguments [a,b,n]
a = float(sys.argv[1])
b = float(sys.argv[2])
n = int(sys.argv[3])
#we arbitrarily define a function to integrate
def f(x):
	return x*x

#this is the serial version of the trapezoidal rule
#parallelization occurs by dividing the range among processes
def integrateRange(a, b, n):
	integral = -(f(a) + f(b))/2.0
	# n+1 endpoints, but n trapezoids
	for x in numpy.linspace(a,b,n+1):
		integral = integral + f(x)
	integral = integral* (b-a)/n
	return integral

#h is the step size. n is the total number of trapezoids
h = (b-a)/n
#local_n is the number of trapezoids each process will calculate
#note that size must divide n
local_n = n/size
resto = n%size
print "resto =", resto 
#we calculate the interval that each process handles
#local_a is the starting point and local_b is the endpoint
local_a = a + rank*local_n*h
if rank != (size - 1):
	local_b = local_a + local_n*h
else:
	local_b = local_a + (local_n+resto)*h
#initializing variables. mpi4py requires that we pass numpy objects.
integral = numpy.zeros(1)
recv_buffer = numpy.zeros(1)
# perform local computation. Each process integrates its own interval
integral[0] = integrateRange(local_a, local_b, local_n)
# communication
# root node receives results from all processes and sums them
if rank == 0:
	total = integral[0]
	for i in range(1, size):
		comm.Recv(recv_buffer, ANY_SOURCE)
		total += recv_buffer[0]
else:
	# all other process send their result
	comm.Send(integral)

# root process prints results
if comm.rank == 0:
	print "With n =", n, "trapezoids, estimate of the integral from", a, "to", b, "is", total

