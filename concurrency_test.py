import argparse
import Queue
import sys
import threading
import time

import gevent.queue


class WorkerPool(object):

    Exit = NotImplemented
    Queue = NotImplemented

    def start_thread(self):
        raise NotImplementedError

    def __init__(self, maxsize):
        self.queue = self.Queue(maxsize)
        self.threads = [self.start_thread() for i in xrange(maxsize)]

    def _process(self):
        """The main loop of a worker thread."""
        while True:
            func, args, kwargs = self.queue.get()
            try:
                func(*args, **kwargs)
            except self.Exit:
                break
            except Exception, exc:
                import traceback
                traceback.print_exc()
            finally:
                self.queue.task_done()

    def spawn(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def join(self):
        self.queue.join()

    def die(self):
        raise self.Exit

    def kill(self, block=True):
        for t in self.threads:
            self.spawn(self.die)
        if block:
            self.join()


class ThreadPool(WorkerPool):

    Exit = SystemExit
    Queue = Queue.Queue

    def start_thread(self):
        t = threading.Thread(target=self._process)
        t.daemon = True
        t.start()
        return t


class GreenletPool(WorkerPool):

    Exit = gevent.GreenletExit
    Queue = gevent.queue.JoinableQueue

    def start_thread(self):
        return gevent.spawn(self._process)


parser = argparse.ArgumentParser()

parser.add_argument('-t', '--time', type=int, default=5,
                    help="The number of milliseconds to sleep for in each task (default: 5).")

parser.add_argument('-c', '--concurrency', type=int, default=1000,
                    help="The number of workers to execute (default: 1,000).")

parser.add_argument('-n', '--number', type=int, default=10000,
                    help="The number of tasks to run (default: 10,000).")

parser.add_argument('model', choices=('gevent', 'thread'),
                    help="The concurrency model to use.")


def report(model, time, concurrency, number, total_time):
    print "%s\t%d\t%d\t%d\t%.8f" % (model, time, concurrency, number, total_time)


def main():
    args = parser.parse_args()

    if args.model == 'gevent':
        pool = GreenletPool(args.concurrency)
        sleep = gevent.sleep
    else:
        pool = ThreadPool(args.concurrency)
        sleep = time.sleep

    start_time = time.time()
    for i in xrange(args.number):
        pool.spawn(sleep, (args.time / 1000.0))
    pool.join()
    end_time = time.time()
    total_time = end_time - start_time
    ideal_time = (args.time / 1000.0) * args.number / args.concurrency
    print >>sys.stderr, "Total time: %.5f seconds" % (total_time,)
    print >>sys.stderr, "Ideal time: %.5f seconds" % (ideal_time,)
    print >>sys.stderr, "Overhead: %.5fx" % (total_time / ideal_time,)
    pool.kill()
    report(args.model, args.time, args.concurrency, args.number, total_time)


if __name__ == '__main__':
    main()
