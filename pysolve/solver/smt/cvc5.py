import re
from ..resourcer import Resourcer
from ...tools.human import numeric

CVC5_BINARY = "cvc5"
CVC5_STATIC = "-L smt2.6 --no-incremental --no-type-checking --no-interactive --stats --stats-expert"

CVC5_OK = ["sat", "unsat"]
CVC5_FAILED = ["unknown", "timeout"]

USAGE = {
   "T": lambda x: "--tlimit=%s" % (1000*int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::steps::resource",
   "Instantiate::Instantiations_Total",
   "SharedTermsDatabase::termsCount",
   "sat::conflicts",
   "sat::decisions",
   "sat::clauses_literals",
   "sat::propagations",
]

PAT = re.compile(r"^(%s) = (.*)$" % "|".join(KEYS), flags=re.MULTILINE)

class Cvc5(Resourcer):
   
   def __init__(self, resource="T300", args="", binary=None):
      Resourcer.__init__(self,
         "cvc5",
         binary if binary else CVC5_BINARY,
         f"{CVC5_STATIC} {args}" if args else CVC5_STATIC,
         resource,
         CVC5_OK,
         CVC5_FAILED,
         USAGE)

   def parse(self, output):
      def parseval(val):
         if val.startswith("{") and val.endswith("}"):
            val = val.strip(" {}")
            val = val.split(",")
            val = [x.split(":") for x in val]
            return {x.strip():numeric(y.strip()) for (x,y) in val}
         return numeric(val)
      status = output[:output.find("\n")]
      if (status not in self.status_all) and ("timeout" in status):
         status = "timeout"
      result = {key:parseval(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "driver::totalTime" in result:
         result["RUNTIME"] = result["driver::totalTime"]
         del result["driver::totalTime"]
      return result

