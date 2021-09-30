import re
from ..resourcer import Resourcer
from ...tools.human import numeric

V_BINARY = "vampire"
V_STATIC = "--proof tptp -stat full --input_syntax tptp"

V_OK = ['Satisfiable', 'Unsatisfiable', 'Theorem', 'CounterSatisfiable', 'ContradictoryAxioms']
V_FAILED = ['ResourceOut', 'GaveUp']

INCOMPLETE_V_OK = ['Unsatisfiable', 'Theorem']
INCOMPLETE_V_FAILED = ['ResourceOut', 'GaveUp', 'Satisfiable', 'CounterSatisfiable', 'ContradictoryAxioms']

USAGE = {
   "T": lambda x: "--time_limit %ss" % x,
   "M": lambda x: "--memory_limit %s" % x
}

PATS = {
   "STATUS":    re.compile(r"^% SZS status (\S*)"),
   "ACTIVE":    re.compile(r"^% Active clauses: (\S*)"),
   "PASSIVE":   re.compile(r"^% Passive clauses: (\S*)"),
   "GENERATED": re.compile(r"^% Generated clauses: (\S*)"),
   "INITIAL":   re.compile(r"^% Initial clauses: (\S*)"),
   "RUNTIME":   re.compile(r"^% Time elapsed: (\S*)"),
   "MEMORY":    re.compile(r"^% Memory used \S*: (\S*)"),
   "SPLITS":    re.compile(r"^% Split clauses: (\S*)")
}

class Vampire(Resourcer):

   def __init__(self, resource="T300", args="", binary=None, complete=True):
      Resourcer.__init__(self,
         "vampire",
         binary if binary else V_BINARY,
         f"{V_STATIC} {args}" if args else V_STATIC,
         resource,
         V_OK if complete else INCOMPLETE_V_OK,
         V_FAILED if complete else INCOMPLETE_V_FAILED,
         USAGE,
         1)

   def parse(self, output):
      result = {}
      result["STATUS"] = "Unknown"
      for line in output.split("\n"):
         line = line.rstrip()
         if (len(line) > 2) and (line[0] == "%" and line[1] == " " ):
            for pat in PATS:
               mo = PATS[pat].search(line)
               if mo:
                  result[pat] = numeric(mo.group(1))
      return result

