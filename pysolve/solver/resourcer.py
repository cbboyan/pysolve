from .solver import Solver

TIMEOUT = "timeout --kill-after=1 --foreground %s "

class Resourcer(Solver):
   """
   An abstract solver with a generic support for resource control.

   Field `resource` is a string of format "Xnnn-Ymmm-Zkkk", where `X`,`Y`,...
   are single characters for different resource limits supported by the solver,
   and `nnn`, `mmm`, ...  are their specific values.  This string is translated
   to specific solver command line arguments using the field `usage`. This
   field should be a dictionary with single character keys `X`, `Y`, ... The
   values should be unary functions which translate values `nnn`, `mmm`, ... to
   solver-specific command line arguments.  Character `T` should be used for
   time limit and it possibly adds `timeout` call to limit time resources.  

   For example, with `usage`

   `{"T": lambda x: "--time-limit=%s" % x}`

   and `resource` set to `T100` you will get the argument `--time-limit=100`.

   Additionally, the command will be prefixed with

   `timeout --kill-after=1 --foreground 101`.  

   That is, if the solver does not finish by itself after 100 seconds, it will
   be sent SIGTERM after 101 seconds, and if still running, SIGKILL after 102
   seconds.
   """

   def __init__(self, name, binary, args, resource, status_ok, status_failed, usage, timeout_after=1):
      Solver.__init__(self, name, binary, args, resource, status_ok, status_failed)
      self.limits(usage, timeout_after)

   def cmd(self, problem, strategy, **others):
      cmdargs = f"{self.cmd_timeout}{self.binary} {self.args} {self.cmd_limits} {strategy} {problem}"
      #print(cmdargs)
      return cmdargs

   def timeout(self):
      return self._timeout

   def limits(self, usage, timeout_after):
      lims = {x[0]:x[1:] for x in self.resource.split("-") if x}
      self._timeout = int(lims["T"]) if "T" in lims else None
      timeout = TIMEOUT % (self._timeout+timeout_after) if (TIMEOUT and self._timeout) else ""
      try:
         args = [usage[x](lims[x]) for x in lims]
      except:
         raise Exception("pyprove.prover: Unknown prover limit string ('%s', possible keys are '%s')" % 
               (self.resource, ",".join(usage.keys())))
      self.cmd_timeout = timeout
      self.cmd_limits = " ".join(args)

