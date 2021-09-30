import re
from ..resourcer import Resourcer
from ...tools.human import numeric

CVC4_BINARY = "cvc4"
CVC4_STATIC = "-L smt2.6 --no-incremental --no-type-checking --no-interactive --stats"

CVC4_OK = ["sat", "unsat"]
CVC4_FAILED = ["unknown", "timeout"]

USAGE = {
   "T": lambda x: "--tlimit=%s" % (1000*int(x)),
   "R": lambda x: "--rlimit=%s" % x
}

KEYS = [
   "driver::totalTime",
   "resource::resourceUnitsUsed",
   "resource::RewriteStep",
   "resource::PreprocessStep",
   "Instantiate::Instantiations_Total",
   "SharedTermsDatabase::termsCount",
   "sat::conflicts",
   "sat::decisions",
   #"theory::\S*::lemmas",
   #"theory::\S*::conflicts",
]

PAT = re.compile(r"^(%s), (\S*)" % "|".join(KEYS), flags=re.MULTILINE)

class Cvc4(Resourcer):
   
   def __init__(self, resource="T300", args="", binary=None):
      Resourcer.__init__(self,
         "cvc4",
         binary if binary else CVC4_BINARY,
         f"{CVC4_STATIC} {args}" if args else CVC4_STATIC,
         resource,
         CVC4_OK,
         CVC4_FAILED,
         USAGE)

   def parse(self, output):
      status = output[:output.find("\n")]
      if (status not in self.status_all) and ("timeout" in status):
         status = "timeout"
      result = {key:numeric(val) for (key,val) in PAT.findall(output)}
      result["STATUS"] = status
      if "driver::totalTime" in result:
         result["RUNTIME"] = result["driver::totalTime"]
         del result["driver::totalTime"]
      return result

