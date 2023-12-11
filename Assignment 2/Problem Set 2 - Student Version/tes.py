from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        #TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).
        # LSH0_chars = [char for char in LHS0]
        # LSH1_chars = [char for char in LHS1]
        
        letters = set(LHS0 + LHS1 + RHS)
        
        problem.variables = list(letters)
        problem.variables.extend(set(f"carry{i}" for i in range(max(len(LHS0), len(LHS1)))))
        
        all_variables = list(letters) + list(f"carry{i}" for i in range(len(RHS) - 1))
        
        problem.domains = {}
        for var in all_variables:
            if var == LHS0[0] or var == LHS1[0] or var == RHS[0]:
                problem.domains[var] = set(range(1, 10))
            elif var.startswith("carry"):
                problem.domains[var] = set(range(2))
            else:
                problem.domains[var] = set(range(0, 10))

        problem.constraints = []
        for i in range(max(len(LHS0), len(LHS1))):
            aux1 = (LHS0[-(i + 1)], LHS1[-(i + 1)])
            aux2 = (RHS[-(i + 1)], f"carry{i}")
            
            problem.variables.extend([aux1, aux2])
            
            domain = set()
            for x in problem.domains[LHS0[-(i + 1)]]:
                for y in problem.domains[LHS1[-(i + 1)]]:
                    domain.add((x, y))
            # print(domain, aux1, '\n\n')        
            problem.domains[aux1] = domain
            
            domain = set()
            for x in problem.domains[RHS[-(i + 1)]]:
                for y in problem.domains[f"carry{i}"]:
                    domain.add((x, y))
            problem.domains[aux2] = domain
            
            problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)], aux1), lambda a, b: a == b[0]))
            problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)], aux1), lambda a, b: a == b[1]))
            problem.constraints.append(BinaryConstraint((RHS[-(i + 1)], aux2), lambda a, b: a == b[0]))
            problem.constraints.append(BinaryConstraint((f"carry{i}", aux2), lambda a, b: a == b[1]))
            
            # Constraint for the first character
            if i == 0:
                print(aux1, aux2)
                problem.constraints.append(BinaryConstraint((aux1, aux2), lambda a, b: a[0] + a[1] == b[0] + 10 * b[1]))
        
            # aux3 = (aux1, aux2)
            # problem.variables.extend([aux3])
            
            
            # problem.constraints.append(BinaryConstraint((aux1, aux3), lambda a, b: a == b[0]))
            # problem.constraints.append(BinaryConstraint((aux2, aux3), lambda a, b: a == b[1]))

            # # Constraints for the middle characters
            # if i < len(LHS0) and i < len(LHS1) and  i != 0:
            #     print(aux3, f"carry{i-1}")
            #     problem.constraints.append(BinaryConstraint((aux3, f"carry{i-1}"), lambda a, b: b + a[0][0] + a[0][1] == a[1][0] + a[1][1]))

        # # Constraints for the last character
        # print(RHS[-(len(RHS))], f"carry{len(RHS) - 2}")
        # problem.constraints.append(BinaryConstraint((RHS[-(len(RHS))], f"carry{len(RHS) - 2}"), lambda a, b: a == b))
            
        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())