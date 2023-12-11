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
    """
    Performs forward checking in a Constraint Satisfaction Problem (CSP) after assigning a value to a variable.

    Forward checking updates the domains of other variables based on the constraints in the CSP.

    Parameters:
    - problem (Problem): The CSP for which forward checking is performed.
    - assigned_variable (str): The variable to which a value has been assigned.
    - assigned_value (Any): The value assigned to the variable.
    - domains (Dict[str, set]): The current domains for all variables in the CSP.

    Returns:
    - bool: True if forward checking is successful and consistent with the constraints, False otherwise.
    """

    for constraint in problem.constraints:
        # Check if the constraint is binary and the assigned variable is in the constraint
        if isinstance(constraint, BinaryConstraint) and (assigned_variable in constraint.variables):
            other_variable = constraint.get_other(assigned_variable)  # Get the other variable in the constraint besides the assigned variable
            accepted_values = []  # Create a list to store the accepted values to replace them in the domain of the other variable

            if domains.get(other_variable) is not None:  # Check if the other variable has a domain
                for value in domains[other_variable]:  # Check each value in the domain of the other variable
                    dicty = {assigned_variable: assigned_value, other_variable: value}  # Create a dictionary with the assigned variable and its value and the other variable and its value
                    # Check if the dictionary is consistent with the constraints
                    if constraint.is_satisfied(dicty):
                        accepted_values.append(value)  # If yes, add the value to the list of accepted values

                domains[other_variable] = set(accepted_values)  # Update the domain of the other variable to be the list of accepted values
                # This implicitly removes the values that are not consistent with the constraints

                if len(domains[other_variable]) == 0:  # If the domain is empty, return False (no solution)
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
    """
    Finds and returns the least restraining values for a variable to be assigned in a Constraint Satisfaction Problem (CSP).

    The least restraining values are the values for the variable that remove the fewest values from the domains of other variables.

    Parameters:
    - problem (Problem): The CSP for which the values are determined.
    - variable_to_assign (str): The variable for which least restraining values are sought.
    - domains (Dict[str, set]): The current domains for all variables in the CSP.

    Returns:
    - List[Any]: A list of values for the variable that are least restraining, sorted based on the number of removed values.
    """

    restraining_values = []  # Create a list to store tuples of (values that remove values from other variables, the number of removed values)
    values = domains[variable_to_assign]  # Get the domain of the variable to assign

    for value in values:  # Check each value in the domain of the variable to assign
        removed_values = 0  # Create a variable to store the number of removed values, initially 0

        for constraint in problem.constraints:  # Check each constraint in the problem
            # Check if the constraint is binary and the variable to assign is in the constraint
            if isinstance(constraint, BinaryConstraint) and (variable_to_assign in constraint.variables):
                other_variable = constraint.get_other(variable_to_assign)  # Get the other variable in the constraint besides the variable to assign

                if domains.get(other_variable) is not None:  # Check if the other variable has a domain
                    for other_value in domains[other_variable]:  # Check each value in the domain of the other variable
                        dicty = {variable_to_assign: value, other_variable: other_value}  # Create a dictionary with the variable to assign and its value and the other variable and its value
                        # Check if the dictionary is not consistent with the constraints
                        if not constraint.is_satisfied(dicty):
                            removed_values += 1  # If not, increment the number of removed values, don't remove them from the domain of the other variable

        restraining_values.append((value, removed_values))  # Add the value and the number of removed values to the list of restraining values

    restraining_values.sort(key=lambda x: (x[1], x[0]))  # Sort the list of restraining values based on the number of removed values for each value and then the value itself
    # Sort according to the number of removed values first and then the value itself to make sure that the values with the same number of removed values are sorted in ascending order

    return [x[0] for x in restraining_values]  # Return the list of sorted values in the list of restraining values


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
    """
    Solves a Constraint Satisfaction Problem (CSP) using a recursive depth-first search algorithm.

    Parameters:
    - problem (Problem): The CSP to be solved.

    Returns:
    - Optional[Assignment]: A valid assignment that satisfies the CSP constraints or None if no solution is found.
    """
    # Check for one-consistency before starting the search
    if not one_consistency(problem):
        return None
        
    def backtrack(assignment: Assignment, domains: Dict[str, set]) -> Optional[Assignment]:
        """
        Recursively searches for a valid assignment using depth-first search.

        Parameters:
        - assignment (Assignment): The current partial assignment.
        - domains (Dict[str, set]): The remaining domains for each variable.

        Returns:
        - Optional[Assignment]: A valid assignment that satisfies the CSP constraints or None if no solution is found.
        """

        # If the assignment is complete, return it
        if problem.is_complete(assignment):
            return assignment
        
        # Choose the variable with the minimum remaining values
        variable = minimum_remaining_values(problem, domains)

        # Iterate over the least restraining values for the chosen variable
        for value in least_restraining_values(problem, variable, domains):
            
            # Create a new assignment with the chosen value
            new_assignment = assignment.copy()
            new_assignment[variable] = value
            
            # Update the domains by removing the chosen variable
            new_domain = domains.copy()
            del new_domain[variable]

            # Check if the assignment is forward checking consistent
            if forward_checking(problem, variable, value, new_domain):
                # Recursively continue the search with the new assignment and updated domains
                result = backtrack(new_assignment, new_domain)
            
                # If a valid assignment is found, return it
                if result is not None:
                    return result
                
        return None
    
    # Start the recursive search with an empty assignment and the initial domains
    return backtrack({}, problem.domains)

