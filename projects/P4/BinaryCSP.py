# Hint: from collections import deque
from collections import deque

from Interface import *


# = = = = = = = QUESTION 1  = = = = = = = #


def consistent(assignment, csp, var, value):
    """
    Checks if a value assigned to a variable is consistent with all binary constraints in a problem.
    Do not assign value to var.
    Only check if this value would be consistent or not.
    If the other variable for a constraint is not assigned,
    then the new value is consistent with the constraint.

    Args:
        assignment (Assignment): the partial assignment
        csp (ConstraintSatisfactionProblem): the problem definition
        var (string): the variable that would be assigned
        value (value): the value that would be assigned to the variable
    Returns:
        boolean
        True if the value would be consistent with all currently assigned values, False otherwise
    """
    # TODO: Question 1
    for constraint in csp.binaryConstraints:
        # check if this "var" is involved in given constraint
        if constraint.affects(var):
            other_var = constraint.otherVariable(var)
            if assignment.isAssigned(other_var):
                if not constraint.isSatisfied(value, assignment.assignedValues[other_var]):
                    return False
    return True


def recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod):
    """
    Recursive backtracking algorithm.
    A new assignment should not be created.
    The assignment passed in should have its domains updated with inferences.
    In the case that a recursive call returns failure or a variable assignment is incorrect,
    the inferences made along the way should be reversed.
    See maintainArcConsistency and forwardChecking for the format of inferences.

    Examples of the functions to be passed in:
    orderValuesMethod: orderValues, leastConstrainingValuesHeuristic
    selectVariableMethod: chooseFirstVariable, minimumRemainingValuesHeuristic
    inferenceMethod: noInferences, maintainArcConsistency, forwardChecking

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
        orderValuesMethod (function<assignment, csp, variable> returns list<value>):
            a function to decide the next value to try
        selectVariableMethod (function<assignment, csp> returns variable):
            a function to decide which variable to assign next
        inferenceMethod (function<assignment, csp, variable, value> returns set<variable, value>):
            a function to specify what type of inferences to use
    Returns:
        Assignment
        A completed and consistent assignment. None if no solution exists.
    """
    # TODO: Question 1
    if assignment.isComplete():
        return assignment
    var = selectVariableMethod(assignment, csp)
    if not var:
        return None

    inferences = set([])
    for value in orderValuesMethod(assignment, csp, var):
        if consistent(assignment, csp, var, value):
            assignment.assignedValues[var] = value
            inferences = inferenceMethod(assignment, csp, var, value)
            if inferences is not None:
                rslt = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
                if rslt is not None:
                    return rslt
        if inferences:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
        assignment.assignedValues[var] = None
    return None


def eliminateUnaryConstraints(assignment, csp):
    """
    Uses unary constraints to eliminate values from an assignment.

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
    Returns:
        Assignment
        An assignment with domains restricted by unary constraints. None if no solution exists.
    """
    domains = assignment.varDomains
    for var in domains:
        for constraint in (c for c in csp.unaryConstraints if c.affects(var)):
            for value in (v for v in list(domains[var]) if not constraint.isSatisfied(v)):
                domains[var].remove(value)
                # Failure due to invalid assignment
                if len(domains[var]) == 0:
                    return None
    return assignment


def chooseFirstVariable(assignment, csp):
    """
    Trivial method for choosing the next variable to assign.
    Uses no heuristics.
    """
    for var in csp.varDomains:
        if not assignment.isAssigned(var):
            return var


# = = = = = = = QUESTION 2  = = = = = = = #
def DegreeHeuristic(assignment, csp, var):
    degree = 0
    for constraint in csp.binaryConstraints:
        if constraint.affects(var) and not assignment.isAssigned(constraint.otherVariable(var)):
            degree += 1
    return degree


def minimumRemainingValuesHeuristic(assignment, csp):
    """
    Selects the next variable to try to give a value to in an assignment.
    Uses minimum remaining values heuristic to pick a variable. Use degree heuristic for breaking ties.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        the next variable to assign
    """
    nextVar = None
    minRemain = float('inf')
    domains = assignment.varDomains

    for var in domains:
        if not assignment.isAssigned(var):
            if len(domains[var]) < minRemain:
                nextVar = var
                minRemain = len(domains[var])
            elif len(domains[var]) == minRemain and DegreeHeuristic(assignment, csp, var) > DegreeHeuristic(assignment, csp, nextVar):
                nextVar = var
    return nextVar

    # TODO: Question 2


def orderValues(assignment, csp, var):
    """
    Trivial method for ordering values to assign.
    Uses no heuristics.
    """
    return list(assignment.varDomains[var])


# = = = = = = = QUESTION 3  = = = = = = = #


def leastConstrainingValuesHeuristic(assignment, csp, var):
    """
    Creates an ordered list of the remaining values left for a given variable.
    Values should be attempted in the order returned.
    The least constraining value should be at the front of the list.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable to be assigned the values
    Returns:
        list<values>
        a list of the possible values ordered by the least constraining value heuristic
    """
    # TODO: Question 3
    unordered_map = []
    for value in assignment.varDomains[var]:
        count = 0
        for constraint in csp.binaryConstraints:
            if constraint.affects(var):
                otherVar = constraint.otherVariable(var)
                for otherValue in assignment.varDomains[otherVar]:
                    if not constraint.isSatisfied(value, otherValue):
                        count += 1
        unordered_map.append((count,value))
    unordered_map.sort()
    return [item[1] for item in unordered_map]


def noInferences(assignment, csp, var, value):
    """
    Trivial method for making no inferences.
    """
    return set([])


# = = = = = = = QUESTION 4  = = = = = = = #


def forwardChecking(assignment, csp, var, value):
    """
    Implements the forward checking algorithm.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set< tuple<variable, value> >
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    for constraint in (c for c in csp.binaryConstraints if c.affects(var)):
        otherVar = constraint.otherVariable(var)
        for otherValue in assignment.varDomains[otherVar].copy():
            if not constraint.isSatisfied(value, otherValue):
                if len(assignment.varDomains[otherVar]) > 1:
                    inferences.add((otherVar, otherValue))
                    assignment.varDomains[otherVar].remove(value)
                else:
                    for inference in inferences:
                        assignment.varDomains[inference[0]].add(inference[1])
                    return None
    return inferences




    # TODO: Question 4
    raise_undefined_error()


# = = = = = = = QUESTION 5  = = = = = = = #


def revise(assignment, csp, var1, var2, constraint):
    """
    Helper function to maintainArcConsistency and AC3.
    Remove values from var2 domain if constraint cannot be satisfied.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var1 (string): the variable with consistent values
        var2 (string): the variable that should have inconsistent values removed
        constraint (BinaryConstraint): the constraint connecting var1 and var2
    Returns:
        set<tuple<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    for value2 in assignment.varDomains[var2]:
        isSatisfied = False
        for value1 in assignment.varDomains[var1]:
            if constraint.isSatisfied(value1, value2):
                isSatisfied = True
                break
        if not isSatisfied:
            inferences.add((var2, value2))
    # check if all the values in var2's domain are removed
    # which indicates there's no answer
    if len(inferences) == len(assignment.varDomains[var2]):
        return None
    for inference in inferences:
        assignment.varDomains[inference[0]].remove(inference[1])
    return inferences

    # TODO: Question 5


def maintainArcConsistency(assignment, csp, var, value):
    """
    Implements the maintaining arc consistency algorithm.
    Inferences take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    and inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set<<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])
    queue = deque()

    # initialize queue
    for constraint in (c for c in csp.binaryConstraints if c.affects(var)):
        otherVar = constraint.otherVariable(var)
        if not assignment.isAssigned(otherVar):
            queue.append((var, otherVar, constraint))

    while len(queue) > 0:
        Xi, Xj, constraint = queue.pop()
        temp = revise(assignment, csp, Xi, Xj, constraint)
        if temp is None:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
            return None
        if len(temp) != 0:
            inferences = inferences.union(temp)
            for constraint in (c for c in csp.binaryConstraints if c.affects(Xj)):
                otherVar = constraint.otherVariable(Xj)
                if not assignment.isAssigned(otherVar):
                    queue.append((Xj, otherVar, constraint))

    return inferences

    # TODO: Question 5
    #  Hint: implement revise first and use it as a helper function"""
    raise_undefined_error()


# = = = = = = = QUESTION 6  = = = = = = = #


def AC3(assignment, csp):
    """
    AC3 algorithm for constraint propagation.
    Used as a pre-processing step to reduce the problem
    before running recursive backtracking.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        Assignment
        the updated assignment after inferences are made or None if an inconsistent assignment
    """
    inferences = set([])
    queue = deque()

    for var in csp.varDomains:
        for constraint in (c for c in csp.binaryConstraints if c.affects(var)):
            queue.append((var, constraint.otherVariable(var), constraint))

    while len(queue) > 0:
        Xi, Xj, constraint = queue.pop()
        temp = revise(assignment, csp, Xi, Xj, constraint)
        if temp is None:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])
            return None
        if len(temp):
            inferences = inferences.union(temp)
            for constraint in (c for c in csp.binaryConstraints if c.affects(Xj)):
                otherVar = constraint.otherVariable(Xj)
                if not assignment.isAssigned(otherVar):
                    queue.append((Xj, otherVar, constraint))

    return assignment
    # TODO: Question 6
    #  Hint: implement revise first and use it as a helper function"""


def solve(csp, orderValuesMethod=leastConstrainingValuesHeuristic,
          selectVariableMethod=minimumRemainingValuesHeuristic,
          inferenceMethod=forwardChecking, useAC3=True):
    """
    Solves a binary constraint satisfaction problem.

    Args:
        csp (ConstraintSatisfactionProblem): a CSP to be solved
        orderValuesMethod (function): a function to decide the next value to try
        selectVariableMethod (function): a function to decide which variable to assign next
        inferenceMethod (function): a function to specify what type of inferences to use
        useAC3 (boolean): specifies whether to use the AC3 pre-processing step or not
    Returns:
        dictionary<string, value>
        A map from variables to their assigned values. None if no solution exists.
    """
    assignment = Assignment(csp)

    assignment = eliminateUnaryConstraints(assignment, csp)
    if assignment is None:
        return assignment

    if useAC3:
        assignment = AC3(assignment, csp)
        if assignment is None:
            return assignment

    assignment = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
    if assignment is None:
        return assignment

    return assignment.extractSolution()
