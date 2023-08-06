from maxoptics.config import Config
import re
import traceback
from math import *
from .cdl import global_constraints, local_constraints

BETA = Config.BETA


class Restrainer:
    class __Constraint:
        regex = "^([\\+\\-\\*\\/\\(\\)\\[\\]0-9]+|sin|cos|sinh|cosh|tan|tanh|arcsin|arccos|arctan|exp|log|==|abs|\\*\\*|int|float|bool|!=|not)$"
        reg = re.compile(regex)

        def __init__(self, cdl: str) -> None:
            cdl = cdl.strip()
            head, tail = cdl.split(" = ")

            is_builtin = lambda ex: re.match(self.reg, ex)
            raw_expressions = tail.split(" ")
            self.triggers = [ex for ex in raw_expressions if not is_builtin(ex)]
            expressions = [ex if is_builtin(ex) else f'ob.get("{ex}")' for ex in raw_expressions]
            self.reassembly = " ".join(expressions)
            self.dest = head.strip()

        def __call__(self, ob, escape: list):
            if BETA:
                print(self.reassembly, self.dest)

            # TODO: Redshift
            # print('\33[5;32mObject:  ', ob.name, self.__dict__, '\33[5;0m')
            for trigger in self.triggers:
                if trigger not in escape:
                    escape.append(trigger)
                if ob.get(trigger, silent=True) is None:
                    return
            if ob.get(self.dest, silent=True) is None:
                return
            # TODO: Speedup
            try:
                result = eval(self.reassembly)
            except ZeroDivisionError:
                return
            except Exception as e:
                traceback.print_exc()
                return
            if self.dest not in escape:
                escape.append(self.dest)
            ob.set(self.dest, result, escape)

    def __init__(self, domain=None):
        self.constraints = [self.__Constraint(c) for c in global_constraints]
        if domain:
            self.constraints += [self.__Constraint(c) for c in local_constraints[domain]]
        self.mapping = {}
        for c in self.constraints:
            for trigger in c.triggers:
                if trigger not in self.mapping:
                    self.mapping[trigger] = []
                if c not in self.mapping[trigger]:
                    self.mapping[trigger].append(c)

    def check(self, ob, key, escape):
        if BETA:
            print("CHECK", key not in self.mapping, key)
        if key not in self.mapping:
            return
        for constraint in self.mapping[key]:
            if constraint.dest in escape or "*" in escape:
                if BETA:
                    print("ESCAPED", constraint.dest in escape, "*" in escape)

                continue
            else:
                constraint(ob, escape)
