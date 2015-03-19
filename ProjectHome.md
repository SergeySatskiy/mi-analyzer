mi is a Linux command line utility that can identify potential deadlocks in multi-threaded applications.

It can also collect statistics such as number of successful and failed mutex operations, time spent acquiring mutex locks, etc.

It can also show call stacks for all mutex operations.

It is able to identify the following conditions:
  * the order of locking two mutexes in one thread is opposite to the order of locking the same mutexes in another thread
  * unlocking a mutex that was not locked earlier
  * a mutex is left locked after an application has finished
  * the order of unlocking mutexes does not correspond to the reverse order of locking these mutexes
  * unlocking a mutex that was locked earlier in another thread.