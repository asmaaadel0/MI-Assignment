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

    return backtrack(problem, {}, problem.domains)

def backtrack(problem: Problem, assignment: Assignment,domains:Dict[str, set]) -> Optional[Assignment]:
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
    var = minimum_remaining_values(problem, domains)

    # Get the ordered values based on the "least restraining value" heuristic
    ordered_values = least_restraining_values(problem, var, domains)

    # Try each value for the variable
    for value in ordered_values:
        # Assign the variable to the value
        assignment[var] = value

        # Create a copy of the domain of the variable to assign, use deepcopy to avoid changing the original domain
        domain_after_assign = copy.deepcopy(domains)

        # Delete the assigned value from the dictionary
        domain_after_assign.pop(var)

        # Use forward checking to update domains of unassigned variables
        if forward_checking(problem, var, value, domain_after_assign):
            # Recursively explore the next assignment
            result = backtrack(problem, assignment, domain_after_assign)

            # If a solution is found, return it
            if result is not None:
                return result

            # If no solution found, backtrack by removing the variable from the assignment
            assignment[var] = None

    # Return None if no solution is found
    return None