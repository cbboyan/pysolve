from multiprocessing import Pool, Manager
import progress
from progress.bar import FillingCirclesBar, FillingSquaresBar
from math import ceil

class ProgressBar(FillingSquaresBar):
   
   def __init__(self, message, max):
      FillingSquaresBar.__init__(self, message, max=max)
      self.suffix = "%(percent)5.1f%% | %(elapsed_td)s | ETA %(eta_td)s"

class SolvedBar(FillingCirclesBar):
   
   def __init__(self, message, max, tail=None):
      FillingCirclesBar.__init__(self, message, max=max)
      self._solved = 0
      self.suffix = "%(percent)5.1f%% | +%(solved)5s @ %(elapsed_td)s | EST +%(eta_solved)5s @ %(eta_td)s"
      if tail:
         self.suffix += " | %s " % tail

   def inc_solved(self):
      self._solved += 1

   @property
   def eta(self):
      return int(ceil((self.elapsed/self.progress)-self.elapsed)) if self.progress else 0

   @property
   def solved(self):
      return self._solved

   @property
   def eta_solved(self):
      return int(ceil((self._solved / self.progress))) if self.progress else 0

TIMEOUT = 7*24*60*60

def applies(msg, fun, args, cores=4, callback=None, bar=None):
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   todo = len(args)
   if bar: bar.start()
   runner = pool.map_async(fun, [arg+(queue,) for arg in args], chunksize=1)
   while todo:
      (arg,res) = queue.get(TIMEOUT)
      if callback:
         callback(arg, res, bar)
      todo -= 1
      if bar: bar.next()
   if bar: bar.finish()
   pool.close()
   pool.join()
   return runner.get(TIMEOUT)

def run(fun, job):
   arg = job[:-1]
   queue = job[-1]
   try:
      res = fun(*arg)
   except Exception as e:
      print(e)
      #import traceback
      #print("Error: "+traceback.format_exc())
      res = None
   queue.put((arg, res))
   return res

