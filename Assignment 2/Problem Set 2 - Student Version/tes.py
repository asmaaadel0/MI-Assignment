from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented
import copy

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
    # NotImplemented()
    """
    This function applies forward checking to update the domains of unassigned variables after a new assignment.

    Parameters:
    - problem (Problem): The CSP problem instance.
    - assigned_variable (str): The variable that has been assigned a value.
    - assigned_value (Any): The value assigned to the variable.
    - domains (Dict[str, set]): The domains of unassigned variables.

    Returns:
    - bool: True if it is possible to solve the problem after the given assignment, False otherwise.
    """
    # Iterate through the binary constraints involving the assigned variable
    for constraint in problem.constraints:
        if isinstance(constraint, BinaryConstraint) and assigned_variable in constraint.variables:
            other_variable = constraint.get_other(assigned_variable)

            if other_variable not in domains:
                continue

            new_domain = set()
            for value in domains[other_variable]:
                if constraint.is_satisfied({other_variable: value, assigned_variable: assigned_value}):
                    new_domain.add(value)
            # domains[other_variable] = new_domain

            if not new_domain:
                return False
            
            domains[other_variable] = new_domain

    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function
    # NotImplemented()
    """
    Determine the order of values for a given variable based on the "least restraining value" heuristic.

    The "least restraining value" heuristic prioritizes values that remove fewer options from other variables' domains.

    Parameters:
    - problem (Problem): The CSP problem instance.
    - variable_to_assign (str): The variable for which values need to be ordered.
    - domains (Dict[str, set]): The domains of unassigned variables.

    Returns:
    - List[Any]: A list of values for the variable, ordered by their least restraining scores.
    """
    restraining_values = []  # Create a list to store tuples of (value, the number of removed values)

    values = domains[variable_to_assign]  # Get the domain of the variable to assign

    for value in values:  # Check each value in the domain of the variable to assign
        removed_values = 0  # Create a variable to store the number of removed values, initially 0

        for constraint in problem.constraints:  # Check each constraint in the problem
            if isinstance(constraint, BinaryConstraint) and variable_to_assign in constraint.variables:
                # Check if the constraint is binary and the variable to assign is in the constraint
                other_variable = constraint.get_other(variable_to_assign)  # Get the other variable in the constraint
                if domains.get(other_variable) is not None:  # Check if the other variable has a domain
                    for other_value in domains[other_variable]:  # Check each value in the domain of the other variable
                        dicty = {variable_to_assign: value, other_variable: other_value}
                        # Create a dictionary with the variable to assign and its value
                        # and the other variable and its value

                        if not constraint.is_satisfied(dicty):  # Check if the dictionary is not consistent with the constraints
                            removed_values += 1  # If not, increment the number of removed values, don't remove them from the domain of the other variable

        restraining_values.append((value, removed_values))  # Add the value and the number of removed values to the list of restraining values

    restraining_values.sort(key=lambda x: (x[1], x[0]))
    # Sort the list of restraining values based on the number of removed values for each value and then the value itself
    # Sort according to the number of removed values first and then the value itself
    # To make sure that the values with the same number of removed values are sorted in ascending order

    return [x[0] for x in restraining_values]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    #TODO: Write this function
    # NotImplemented()

    if not one_consistency(problem):
        return None
        
    def recursive_search(assignment: Assignment, domains: Dict[str, set])-> Optional[Assignment]:
    
        if problem.is_complete(assignment):
            return assignment
        
        variable = minimum_remaining_values(problem,domains)

        for value in least_restraining_values(problem, variable, domains):
            
            new_assignment = assignment.copy()
            new_assignment [variable] = value
            
            new_domain = domains.copy()
            del new_domain[variable]

            if forward_checking(problem, variable, value, new_domain):
                result = recursive_search(new_assignment, new_domain)
            
                if result is not None:
                    return result
                
        return None
    
    return recursive_search({} ,problem.domains)

















def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
    # NotImplemented()
    """
    This function applies forward checking to update the domains of unassigned variables after a new assignment.

    Parameters:
    - problem (Problem): The CSP problem instance.
    - assigned_variable (str): The variable that has been assigned a value.
    - assigned_value (Any): The value assigned to the variable.
    - domains (Dict[str, set]): The domains of unassigned variables.

    Returns:
    - bool: True if it is possible to solve the problem after the given assignment, False otherwise.
    """
    # Iterate through the binary constraints involving the assigned variable
    for constraint in problem.constraints:
        if isinstance(constraint, BinaryConstraint) and assigned_variable in constraint.variables:
            other_variable = constraint.get_other(assigned_variable)

            if other_variable not in domains:
                continue

            new_domain = set()
            for value in domains[other_variable]:
                if constraint.is_satisfied({other_variable: value, assigned_variable: assigned_value}):
                    new_domain.add(value)
            # domains[other_variable] = new_domain

            if not new_domain:
                return False
            
            domains[other_variable] = new_domain

    return True



from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented
import copy

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
    # NotImplemented()
    """
    This function applies forward checking to update the domains of unassigned variables after a new assignment.

    Parameters:
    - problem (Problem): The CSP problem instance.
    - assigned_variable (str): The variable that has been assigned a value.
    - assigned_value (Any): The value assigned to the variable.
    - domains (Dict[str, set]): The domains of unassigned variables.

    Returns:
    - bool: True if it is possible to solve the problem after the given assignment, False otherwise.
    """
    # Iterate through the binary constraints involving the assigned variable
    for constraint in problem.constraints:
        if isinstance(constraint, BinaryConstraint) and assigned_variable in constraint.variables:
            other_variable = (set(constraint.variables) - {assigned_variable}).pop()

            if other_variable not in domains:
                continue

            new_domain = set()
            for value in domains[other_variable]:
                if constraint.condition(assigned_value, value):
                    new_domain.add(value)
            domains[other_variable] = new_domain

            if not domains[other_variable]:
                return False

    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function
    # NotImplemented()
    """
    Determine the order of values for a given variable based on the "least restraining value" heuristic.

    The "least restraining value" heuristic prioritizes values that remove fewer options from other variables' domains.

    Parameters:
    - problem (Problem): The CSP problem instance.
    - variable_to_assign (str): The variable for which values need to be ordered.
    - domains (Dict[str, set]): The domains of unassigned variables.

    Returns:
    - List[Any]: A list of values for the variable, ordered by their least restraining scores.
    """
    restraining_values = []  # Create a list to store tuples of (value, the number of removed values)

    values = domains[variable_to_assign]  # Get the domain of the variable to assign

    for value in values:  # Check each value in the domain of the variable to assign
        removed_values = 0  # Create a variable to store the number of removed values, initially 0

        for constraint in problem.constraints:  # Check each constraint in the problem
            if isinstance(constraint, BinaryConstraint) and variable_to_assign in constraint.variables:
                # Check if the constraint is binary and the variable to assign is in the constraint
                other_variable = constraint.get_other(variable_to_assign)  # Get the other variable in the constraint
                if domains.get(other_variable) is not None:  # Check if the other variable has a domain
                    for other_value in domains[other_variable]:  # Check each value in the domain of the other variable
                        dicty = {variable_to_assign: value, other_variable: other_value}
                        # Create a dictionary with the variable to assign and its value
                        # and the other variable and its value

                        if not constraint.is_satisfied(dicty):  # Check if the dictionary is not consistent with the constraints
                            removed_values += 1  # If not, increment the number of removed values, don't remove them from the domain of the other variable

        restraining_values.append((value, removed_values))  # Add the value and the number of removed values to the list of restraining values

    restraining_values.sort(key=lambda x: (x[1], x[0]))
    # Sort the list of restraining values based on the number of removed values for each value and then the value itself
    # Sort according to the number of removed values first and then the value itself
    # To make sure that the values with the same number of removed values are sorted in ascending order

    return [x[0] for x in restraining_values]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    #TODO: Write this function
    # NotImplemented()
    """
    Solves a CSP problem using backtracking search with forward checking.

    Parameters:
    - problem (Problem): The CSP problem instance.

    Returns:
    - Optional[Assignment]: The first solution found (a complete assignment satisfying the problem constraints),
      or None if no solution was found.
    """
    # Apply 1-Consistency to handle unary constraints
    if not one_consistency(problem):
        return None

    def backtrack(assignment: Assignment,domains:Dict[str, set]) -> Optional[Assignment]:
        """
        Recursive function to perform backtracking search with forward checking for a CSP problem.

        Parameters:
        - problem (Problem): The CSP problem instance.
        - assignment (Assignment): The current assignment.
        - domains (Dict[str, Set[Any]]): The domains of unassigned variables.

        Returns:
        - Optional[Assignment]: The first solution found (a complete assignment satisfying the problem constraints),
        or None if no solution was found.
        """
        # Check if the assignment is complete (satisfies all constraints)
        if problem.is_complete(assignment):
            return assignment

        # Select the next unassigned variable based on the Minimum Remaining Values (MRV) heuristic
        variable = minimum_remaining_values(problem, domains)

        # Get the ordered values based on the "least restraining value" heuristic
        # ordered_values = least_restraining_values(problem, variable, domains)

        # Try each value for the variable
        # for value in ordered_values:
        #     # Assign the variable to the value
        #     assignment[var] = value

        #     # Create a copy of the domain of the variable to assign, use deepcopy to avoid changing the original domain
        #     domain_after_assign = copy.deepcopy(domains)

        #     # Delete the assigned value from the dictionary
        #     domain_after_assign.pop(var)

        #     # Use forward checking to update domains of unassigned variables
        #     if forward_checking(problem, var, value, domain_after_assign):
        #         # Recursively explore the next assignment
        #         result = backtrack(problem, assignment, domain_after_assign)

        #         # If a solution is found, return it
        #         if result is not None:
        #             return result

        #         # If no solution found, backtrack by removing the variable from the assignment
        #         assignment[var] = None

        for value in least_restraining_values(problem, variable, domains):
            new_assignment = assignment.copy()
            new_assignment[variable] = value
            
            new_domain = domains.copy()
            del new_domain[variable]
            
            if forward_checking(problem, variable, value, new_domain):
                result = backtrack(new_assignment, new_domain)
                
                if result is not None:
                    return result

        # Return None if no solution is found
        return None

    return backtrack({}, problem.domains)



















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