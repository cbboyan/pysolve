import re
from ..resourcer import Resourcer
from ...tools.human import numeric

Z3_BINARY = "z3"
Z3_STATIC = "-smt2 -st"

Z3_OK = ["sat", "unsat"]
Z3_FAILED = ["unknown", "timeout"]

USAGE = {
   "T": lambda x: "-T:%s" % x,
   "M": lambda x: "-memory:%s" % x
}

KEYS = [
   "total-time",
   "conflicts",
   "decisions",
   "memory",
   "restarts",
   "rlimit-count"
]

PAT = re.compile(r":(%s)\s*([0-9.]*)" % "|".join(KEYS), flags=re.MULTILINE)

class Z3(Resourcer):
   
   def __init__(self, resource="T300", args="", binary=None):
      Resourcer.__init__(self,
         "z3",
         binary if binary else Z3_BINARY,
         f"{Z3_STATIC} {args}" if args else Z3_STATIC,
         resource,
         Z3_OK,
         Z3_FAILED,
         USAGE)

   def parse(self, output):
      status = output[:output.find("\n")]
      result = {key:numeric(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "total-time" in result:
         result["RUNTIME"] = result["total-time"]
         del result["total-time"]
      return result

