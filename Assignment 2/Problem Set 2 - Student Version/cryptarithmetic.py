from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use
from itertools import product, combinations

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

        problem.variables = []
        problem.domains = {}
        problem.constraints = []
        
        # assign variables
        letters = list(set(LHS0 + LHS1 + RHS))
        carries = [f'carry{i}' for i in range(len(RHS) - 1 )]
        problem.variables = letters + carries

        # assign domains
        for var in letters:
            problem.domains[var] = set(range(1, 10)) if var == LHS0[0] or var == LHS1[0] or var == RHS[0] else set(range(10))

        for c in carries:
            problem.domains[c] = set(range(2))
        
        # No two letters have the same value
        for val1, val2 in combinations(letters, 2):
            problem.constraints.append(BinaryConstraint((val1, val2), lambda a, b: a != b))

        for i in range(len(RHS)): 
            # A + B = C + 10*carry
            if i == 0:

                aux1 = (LHS0[-(i + 1)], LHS1[-(i + 1)])
                aux2 = (RHS[-(i + 1)], carries[i])

                # Add auxiliaries to variables
                problem.variables.append(aux1)
                problem.variables.append(aux2) 

                # Add domains for auxiliaries
                domain = set(product(problem.domains[LHS0[-(i + 1)]], problem.domains[LHS1[-(i + 1)]]))
                problem.domains[aux1] = domain
                domain = set(product(problem.domains[RHS[-(i + 1)]], problem.domains[carries[i]]))
                problem.domains[aux2] = domain
                
                # Add Binary Constraints
                problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)], aux1), lambda a, b: a == b[0])) # first  item in aux1 = LHS0[-(i + 1)]
                problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)], aux1), lambda a, b: a == b[1])) # second item in aux1 = LHS0[-(i + 1)]
                problem.constraints.append(BinaryConstraint((RHS[-(i + 1)], aux2), lambda a, b: a == b[0]))  # first  item in aux2 = RHS[-(i + 1)]
                problem.constraints.append(BinaryConstraint((carries[i], aux2), lambda a, b: a == b[1]))     # second item in aux2 = carries[i]
                problem.constraints.append(BinaryConstraint((aux1, aux2), lambda a, b: a[0] + a[1]  == b[0] + 10 * b[1])) # A + B = C + 10*carry0

            elif i == len(RHS) - 1:
                # A + B + carry0 = C 
                if i < len(LHS0) and i < len(LHS1):

                    aux1 = (LHS0[-(i + 1)], LHS1[-(i + 1)], carries[i - 1])
                    problem.variables.append(aux1) 

                    # Add domains for auxiliaries
                    domain = set(product(
                        problem.domains[LHS0[-(i + 1)]],
                        problem.domains[LHS1[-(i + 1)]],
                        problem.domains[carries[i - 1]]
                    ))
                    
                    problem.domains[aux1] = domain
                    
                    # Add Binary Constraints
                    problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)], aux1), lambda a, b: a == b[0])) # first  item in aux1 = LHS0[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)], aux1), lambda a, b: a == b[1])) # second item in aux1 = LHS1[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i - 1], aux1), lambda a, b: a == b[2]))   # first  item in aux2 = carries[i - 1]
                    problem.constraints.append(BinaryConstraint((aux1, RHS[-(i + 1)]), lambda a, b: a[0] + a[1] + a[2] == b)) # A + B + carry0 = C 
                
                # carry1 + A = C
                elif i < len(LHS0) and i >= len(LHS1):

                    aux1 = (LHS0[-(i + 1)], carries[i - 1])
                    problem.variables.append(aux1) 

                    # Add domains for auxiliaries
                    domain = set(product(problem.domains[LHS0[-(i + 1)]], problem.domains[carries[i - 1]]))
                    problem.domains[aux1] = domain
                    
                    # Add Binary Constraints
                    problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)], aux1), lambda a, b: a == b[0])) # first  item in aux1 = LHS0[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i - 1], aux1), lambda a, b: a == b[1])) # second item in aux1 = carries[i - 1]
                    problem.constraints.append(BinaryConstraint((aux1, RHS[-(i + 1)]), lambda a, b: a[0] + a[1] == b)) # carry1 + A = C

                # carry1 + B = C
                elif i >= len(LHS0) and i<len(LHS1):
                    aux1 = (LHS1[-(i + 1)], carries[i - 1])
                    problem.variables.append(aux1) 

                    # Add domains for auxiliaries
                    domain = set(product(problem.domains[LHS1[-(i + 1)]], problem.domains[carries[i - 1]]))
                    problem.domains[aux1] = domain
                    
                    # Add Binary Constraints
                    problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)], aux1), lambda a, b: a == b[0])) # first  item in aux1 = LHS1[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i - 1], aux1), lambda a, b: a == b[1])) # second item in aux1 = carries[i - 1]
                    problem.constraints.append(BinaryConstraint((aux1, RHS[-(i + 1)]), lambda a, b: a[0] + a[1] + a[2] == b)) # carry1 + B = C

                # carry1 = C
                elif i >= len(LHS0) and i >= len(LHS1):
                    problem.constraints.append(BinaryConstraint((carries[i - 1], RHS[-(i + 1)]), lambda a, b: a == b)) # carry1 = C
 
            else: 
                # A + B + carry1 = C + 10*carry2
                if i < len(LHS0) and i < len(LHS1):
                    aux1 = (LHS0[-(i + 1)], LHS1[-(i + 1)], carries[i - 1])
                    aux2 = (RHS[-(i + 1)], carries[i])

                    problem.variables.append(aux1) 
                    problem.variables.append(aux2) 

                    # Add domains for auxiliaries
                    domain = set(product(
                        problem.domains[LHS0[-(i + 1)]],
                        problem.domains[LHS1[-(i + 1)]],
                        problem.domains[carries[i - 1]]
                    ))
                    problem.domains[aux1] = domain

                    domain = set(product(problem.domains[RHS[-(i + 1)]], problem.domains[carries[i]]))
                    problem.domains[aux2] = domain

                    # Add Binary Constraints
                    problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)], aux1), lambda a, b: a == b[0])) # first  item in aux1 = LHS0[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)], aux1), lambda a, b: a == b[1])) # second item in aux1 = LHS1[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i - 1], aux1), lambda a, b: a == b[2])) # third  item in aux1 = carries[i - 1]
                    problem.constraints.append(BinaryConstraint((RHS[-(i + 1)], aux2), lambda a, b: a  == b[0])) # first  item in aux2 = RHS[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i], aux2), lambda a, b: a  == b[1]))    # second item in aux2 = carries[i]
                    problem.constraints.append(BinaryConstraint((aux1, aux2), lambda a, b: a[0] + a[1] + a[2] == b[0] + 10 * b[1])) # A + B + carry1 = C + 10*carry2
                
                # A (or) B + carry1 = C + 10 carry2
                else:
                    # A + C1 = C + 10 C2
                    if i < len(LHS0) and i>=len(LHS1):
                        aux1 = (LHS0[-(i + 1)] , carries[i - 1])
                        aux2 = (RHS[-(i + 1)] , carries[i])

                        problem.variables.append(aux1)
                        problem.variables.append(aux2) 

                        # Add domains for auxiliaries
                        domain = set(product(problem.domains[LHS0[-(i + 1)]], problem.domains[carries[i - 1]]))
                        problem.domains[aux1] = domain
                        domain = set(product(problem.domains[RHS[-(i + 1)]], problem.domains[carries[i]]))
                        problem.domains[aux2] = domain

                        # Add Binary Constraints
                        problem.constraints.append(BinaryConstraint((LHS0[-(i + 1)],aux1), lambda a, b: a == b[0])) # first item in aux1 = LHS0[-(i + 1)]

                    # B + carry1 = C + 10 carry2
                    elif i >= len(LHS0) and i<len(LHS1):
                        aux1 = (LHS1[-(i + 1)] , carries[i - 1])
                        aux2 = (RHS[-(i + 1)] , carries[i])

                        problem.variables.append(aux1)
                        problem.variables.append(aux2) 
                        
                        # Add domains for auxiliaries
                        domain = set(product(problem.domains[LHS1[-(i + 1)]], problem.domains[carries[i - 1]]))
                        problem.domains[aux1] = domain
                        domain = set(product(problem.domains[RHS[-(i + 1)]], problem.domains[carries[i]]))
                        problem.domains[aux2] = domain

                        # Add Binary Constraints
                        problem.constraints.append(BinaryConstraint((LHS1[-(i + 1)],aux1), lambda a, b: a == b[0])) # first item in aux1 = LHS1[-(i + 1)]

                    problem.constraints.append(BinaryConstraint((carries[i - 1], aux1), lambda a, b: a == b[1])) # second item in aux1 = carries[i - 1]
                    problem.constraints.append(BinaryConstraint((RHS[-(i + 1)], aux2), lambda a, b: a == b[0]))  # first  item in aux2 = RHS[-(i + 1)]
                    problem.constraints.append(BinaryConstraint((carries[i], aux2), lambda a, b: a == b[1]))     # second item in aux2 = carries[i]
                    problem.constraints.append(BinaryConstraint((aux1,aux2), lambda a, b: a[0] + a[1]  == b[0] + 10 * b[1])) # A (or) B + carry1 = C + 10 carry2

                    
        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())


