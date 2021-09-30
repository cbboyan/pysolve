import subprocess
import time
import os
import gzip

TIMEOUT = "timeout --kill-after=1 --foreground %s " # note the space at the end

class Solver:
   """
   Generic abstract solver interface.  You need to implement at least method
   `parse` in a derived class.  

   You might want to override the method `cmd` which returns the shell command
   to run the prover, if you need more liberty.
   """

   def __init__(self, name, binary, args, resource, status_ok, status_failed):
      self._name = name
      self.binary = binary
      self.args = args
      self.resource = resource
      self.status_ok = status_ok
      self.status_failed = status_failed
      self.status_all = self.status_ok + self.status_failed

   def cmd(self, problem, strategy, **others):
      """
      You might want to override the method `cmd` which returns the shell
      command to run the prover, if you need more liberty.
      """
      timeout = TIMEOUT % self.timeout()
      cmdln = f"{timeout}{self.binary} {self.args} {strategy} {problem}"
      return cmdln

   def parse(self, output):
      """
      Method `parse` should return a dictionary with results.  Its keys might
      be solver-specific but it should contain at least fields `STATUS` and
      `RUNTIME`.  The value of `STATUS` should be a solver-specific status,
      either in the list `self.status_ok` or `self.status_failed`.
      """
      pass

   def name(self):
      return self._name

   def resources(self):
      return self.resource

   def timeout(self):
      return self.resource
   
   def solved(self, result):
      ok = ("STATUS" in result) and (result["STATUS"] in self.status_ok)
      return ok

   def error(self, result):
      return ("STATUS" not in result) or (result["STATUS"] not in self.status_all)

   def output(self, problem, strategy="", **others):
      "Run the solver and get the output as a byte-array."
      cmd = self.cmd(problem, strategy, **others)
      try:
         output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
         output = e.output
      return output

   def solve(self, problem, strategy="", f_out=None, **others):
      "Run the solver and parse output.  Try to use a cached output."
      if f_out and os.path.isfile(f_out+".gz"):
         output = gzip.decompress(open(f_out+".gz","rb").read())
         return self.parse(output.decode())
      else:
         start = time.time()
         output = self.output(problem, strategy, **others)
         if f_out:
            self.save(output, f_out)
         result = self.parse(output.decode())
         result["REALTIME"] = time.time() - start
         return result

   def save(self, output, f_out):
      "Save output to a cache file."
      if os.path.dirname(f_out):
         os.makedirs(os.path.dirname(f_out), exist_ok=True)
      output = gzip.compress(output)
      open(f_out+".gz", "wb").write(output)

