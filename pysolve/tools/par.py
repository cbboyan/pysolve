from multiprocessing import Pool, Manager
import multiprocessing
import multiprocessing.pool

TIMEOUT = 7*24*60*60

class NoDaemonProcess(multiprocessing.Process):
    @property
    def daemon(self):
        return False

    @daemon.setter
    def daemon(self, value):
        pass


class NoDaemonContext(type(multiprocessing.get_context())):
    Process = NoDaemonProcess

# We sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class NestablePool(multiprocessing.pool.Pool):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = NoDaemonContext()
        super(NestablePool, self).__init__(*args, **kwargs)


def apply(fun, args, cores=4, callback=None, bar=None, barmsg=None, chunksize=1):
   #pool = NestablePool(cores)
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   todo = len(args)
   if barmsg and not bar:
      from .bar import ProgressBar
      bar = ProgressBar(barmsg, max=todo)
   if bar: bar.start()

   store = callback is None
   args = [(fun,job,queue,store) for job in args]
   runner = pool.starmap_async(run, args, chunksize=chunksize)
   while todo:
      res = queue.get(TIMEOUT)
      if callback:
         callback(res, bar)
      todo -= 1
      if bar: bar.next()
   if bar: bar.finish()
   pool.close()
   pool.join()
   return None if callback else runner.get(TIMEOUT)

def run(fun, job, queue, store):
   try:
      res = fun(*job)
   except Exception as e:
      print(e)
      import traceback
      print("Error: "+traceback.format_exc())
      res = None
   queue.put(res)
   return res if store else None

