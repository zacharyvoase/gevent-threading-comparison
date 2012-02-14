# Experiment

A performance comparison between gevent and threading for concurrency in
Python.


## Hypothesis

We hypothesised that for low levels of concurrency, threading has a smaller
context-switching overhead than gevent. As concurrency increases, the overhead
of threading grows faster than that of gevent.


## Method

We ran a number of background worker threads/greenlets in a pool configuration.
The number of workers is the **concurrency**—this is the dependent variable.
For gevent we use the included `gevent.pool.Pool` class; for threading we
spawn a number of threads all pulling tasks from a shared instance of
`Queue.Queue`.

Over the course of a single trial, a number of tasks is run over the pool; in
these trials we're running 10,000 tasks.  To remove the influence of varying
performance of the network or other I/O, the task was defined as a sleep
function with a constant time of 5ms.

For varying concurrency levels from 1 to 1,000, going up in steps of 10 (i.e.
1, 10, 20, 30…980, 990, 1000), we ran three trials with each concurrency model.
The 'total time' taken to spawn all tasks and then join the pool was recorded
by calling `time.time()` at the beginning and end, and taking the difference
between the two values.

The 'ideal time' was calculated as the sleep time (5ms), multiplied by the
number of tasks (10,000), divided by the concurrency level (variable). This
value indicates what the total time would be in a system in which spawning and
context switches are perfectly instantaneous (i.e. take no time at all).

Finally, the 'overhead' was calculated as the quotient of the total time and
the ideal time, indicating (as a unit-less number) the overall cost of
scheduling and context switching related to performing the actual task.

Please note that **all of the code used in this experiment can be found in this
repository**. The file `concurrency_test.py` runs a single test, and the file
`trial.py` runs a large batch of these tests, under both concurrency models,
for varying levels of concurrency.


## Results

### Environment

The following software was used:

* Ubuntu 11.04 (Natty)
* Python 2.7.1-0ubuntu5
* Gevent 0.13.6
* Greenlet 0.3.4

This was all run on a 512MB Slicehost instance.

### Raw Data

You can find the raw data collected at the following Google Spreadsheet:
http://bit.ly/xSVs7f

Each row records the concurrency model used (thread or gevent), the sleep time
in milliseconds, the concurrency level and the number of tasks that were run.
Finally they display the 'ideal time' and the 'overhead' as described above.

### Summarized Data

That same spreadsheet has a tab called 'Analysed Data' with a pivot table
displaying summarized data for each model and concurrency level. We plotted a
chart to show how the overhead of threads and gevent changes with the number
of concurrent workers.


## Conclusions

These results seem to verify the initial hypothesis. Initially, gevent's
overhead is around 2.0, whereas threading's is around 1.03. As concurrency
increases, the overhead of threading increases more rapidly than that of
gevent, until the 80-90 concurrent workers mark, at which point threading
becomes slower than gevent.

This leads us to conclude that for a small number of workers, threading
performs *better* than gevent, but this performance edge tails off sharply
after a certain level of concurrency.


## Limitations

* This experiment did not monitor CPU or memory usage at all. Further
  experiments could take a look at internal system variables as well as the
  externally-observable measurements.

* The only external metric taken here was the total time taken to process all
  tasks. Further experiments should measure time taken per job, much like how
  the 'ab' testing tool presents a histogram of individual response times as
  well as aggregate measurements. Nevertheless, for the purpose of this
  experiment it was felt that an attempt to measure these individual times
  would have conflated the results.

* The sleep functions used might not be a true and accurate representation of
  I/O performance. There are very specific code paths invoked in both
  concurrency models when waiting on a file descriptor, which may not have been
  triggered by using a simple `sleep()`, and therefore these results may not be
  indicative of performance under actual I/O load.
