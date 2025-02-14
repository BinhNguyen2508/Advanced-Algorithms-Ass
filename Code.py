import cplex
from cplex.exceptions import CplexError
import math
import sys

days = [[6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2], #Monday
    [6, 10, 7, 7,3, 4, 7, 5, 9, 5, 3, 4, 3], #Tuesday
    [7, 9, 9, 6, 3, 4, 6, 8, 7, 4, 3, 3, 3], #Wednesday
    [6, 9, 8, 6, 4, 4, 5, 8, 7, 5, 4, 3, 4], #Thursday
    [6, 7, 8, 7, 3, 5, 6, 7, 6, 5, 3, 3, 3], #Friday
    [6, 9, 9, 4, 3, 3, 4, 5, 5, 5, 3, 3, 2], #Saturday
    [5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 3, 3, 3]] #Sunday

days_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

hour_name = ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]


shifts = [[1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0], #C1
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 0], #C2
    [0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0], #C3
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0], #C4
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1], #C5
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1]] #C6

shift_name = ["C1", "C2", "C3", "C4", "C5", "C6"]

def solveQ1(hour_name, day, shift_name, shifts):    
    try:
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # Objective function coefficients: [1, 1, 1, 1, 1, 1]
        obj_coefficients = [1] * len(shifts) 
        # Variable names: ["x1", "x2", "x3", "x4", "x5", "x6"]
        var_names = ["x" + str(i + 1) for i in range(len(shift_name))]              
        # Variable types (C: continuous, I: integer): ["I", "I", "I", "I", "I", "I"] 
        var_types = ["I"] * len(shifts)      
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types) 
        
        # left hand side: [[["x1", "x2", "x3", "x4", "x5", "x6"], [1, 0, 0, 0, 0, 1]], ...]
        # right hand side: [6, 9, 9, 8, 3, 3, 7, 8, 8, 5, 3, 3, 2]
        # senses (greater than or equals: G, less than or equals: L, equals: E...): ["G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G", "G"]
        # x1 + x6 >= 6
        rows = [[var_names, [shifts[j][i] for j in range(len(shifts))]] for i in range(len(hour_name))] 
        rhs = day                            
        senses = ["G"] * len(hour_name)
        constraint_names = hour_name # ["8h-9h", "9h-10h", "10h-11h", "11h-12h", "12h-13h", "13h-14h", "14h-15h", "15h-16h", "16h-17h", "17h-18h", "18h-19h", "19h-20h", "20h-21h"]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x     = problem.solution.get_values()

        # for i in range(len(hour_name)):
        #     print ("Constraint %s:  Slack = %d" % (hour_name[i], slack[i]))
        # for i in range(len(shifts)):
        #     print ("Shift %s has %d CSR" % (var_names[i], x[i]))

        # print("Result: " + str(x))
        return x 
    except CplexError as e:
        print(e)

result_Q1 = [[3, 3, 3, 0, 0, 3],    #Monday
    [3, 3, 3, 0, 0, 4],             #Tuesday
    [4, 2, 1, 0, 2, 3],             #Wednesday
    [4, 3, 2, 0, 2, 2],             #Thursday
    [3, 1, 2, 1, 0, 3],             #Friday
    [3, 3, 1, 0, 2, 3],             #Saturday
    [2, 2, 2, 2, 0, 3]]             #Sunday

def solveQ2(shift_name, days_name, result_Q1):
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([result_Q1[i][j] for j in range(len(shift_name))]) for i in range(len(result_Q1))]
    
    # Number of empty slots (ne)
    empty_slots = len(days_name) * max(csr_required_each_day) - sum(csr_required_each_day)

    try:
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: x
        obj_coefficients = [1] 
        var_names = ["x"]
        var_types = ["I"]
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # (nd - 1)x >= max(ncj) - ne
        rows = [[['x'], [len(days_name) - 1]]]
        rhs = [max(csr_required_each_day) - empty_slots]
        senses = ["G"]
        constraint_names = ["empty_slots"]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()
        
        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x     = problem.solution.get_values()

        # for i in range(len(constraint_names)):
        #     print ("Constraint %s:  Slack = %d" % (constraint_names[i], slack[i]))
        # for i in range(len(var_names)):
        #     print ("%s: %d" % (var_names[i], x[i]))

        return x[0]
    except CplexError as e:
        print(e)

result_Q2 = 1

def solveQ3(shift_name, shifts, hour_name, days, days_name, result_Q1, result_Q2):
    # Number of CSR required each day (ncj, j = 1, 2, ..., 7)
    csr_required_each_day = [sum([result_Q1[i][j] for j in range(len(shift_name))]) for i in range(len(result_Q1))]
    
    # Number of CSR required each shift (nck, k = 1, 2, ..., 6)
    csr_required_each_shift = [sum([result_Q1[i][j] for i in range(len(result_Q1))]) for j in range(len(shift_name))]
    
    # Number of CSR required in a week nc
    csr_required = result_Q2 + max(csr_required_each_day)
    
    # CSR names (CSR1, CSR2, ..., CSRnc)
    csr_name = ["CSR" + str(i) for i in range(1, csr_required + 1)]
    
    try:
        problem = cplex.Cplex()
        problem.objective.set_sense(problem.objective.sense.minimize)

        # objective function: all coefficients is 1
        obj_coefficients = [1] * len(csr_name) * len(days_name) * len(shift_name)
        
        # variables: CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, CSR1_Tuesday_C2, ..., CSR1_Tuesday_C6, ..., CSRnc_Sunday_C6
        var_names = [csr_name[i] + "_" + days_name[j] + "_" + shift_name[k] for i in range(len(csr_name)) for j in range(len(days_name)) for k in range(len(shift_name))]
        
        # variable types: all variables are binary
        var_types = ["B"] * len(csr_name) * len(days_name) * len(shift_name)
        problem.variables.add(obj = obj_coefficients, names = var_names, types = var_types)

        # Constraint 1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6], 
        #                  [1, 1, ..., 1]] 
        #                       for every CSR 
        #                           and every day
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for k in range(len(shift_name))], 
                [1] * len(shift_name)] 
                    for i in range(len(csr_name)) 
                        for j in range(len(days_name))]
        
        # Right hand side: 1 for every CSR and every day
        rhs = [1] * len(csr_name) * len(days_name)
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name) * len(days_name)
        
        # constrant names: Con1_CSR1_Monday, Con1_CSR1_Tuesday, ..., Con1_CSRnc_Sunday
        constraint_names = ["Con1_" + csr_name[i] + "_" + days_name[j] for i in range(len(csr_name)) for j in range(len(days_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 2:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR1_Tuesday_C1, ... CSR1_Sunday_C6], 
        #                  [1, 1, ..., 1]] 
        #                      for every CSR
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(len(days_name)) for k in range(len(shift_name))], 
                [1] * len(days_name) * len(shift_name)] 
                    for i in range(len(csr_name))]
        
        # Right hand side: nd - 1, for all csr
        rhs = [len(days_name) - 1] * len(csr_name)
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name)

        # constrant names: Con2_CSR1, Con2_CSR2, ..., Con2_CSRnc
        constraint_names = ["Con2_" + csr_name[i] for i in range(len(csr_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 3:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Monday_C2, ..., CSR1_Monday_C6, CSR2_Monday_C1, ..., CSRnc_Monday_C6], 
        #                  [shift[0][t], shift[1][t], ..., shift[6][t], shift[0][t], ..., shift[6][t]] 
        #                       for every day (Monday - Sunday) 
        #                           and every hour t
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for i in range(len(csr_name)) for k in range(len(shift_name))],
                 [shifts[k][t] for i in range(len(csr_name)) for k in range(len(shift_name))]] 
                    for j in range(len(days_name)) 
                        for t in range(len(hour_name))]
        
        # Right hand side: day[j][t] for every day j and every hour t
        rhs = [days[j][t] for j in range(len(days_name)) for t in range(len(hour_name))]
        
        # Sense: all constraints are greater than or equal to
        senses = ["G"] * len(days_name) * len(hour_name)
        
        # constrant names: Con3_Monday_8h-9h, Con3_Monday_9h-10h, ..., Con3_Sunday_20h-21h
        constraint_names = ["Con3_" + days_name[j] + "_" + hour_name[t] for j in range(len(days_name)) for t in range(len(hour_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_1:
        # Left hand side: [[CSR1_Monday_C1, CSR1_Tuesday_C1...], [1, 1, ...]] for every CSR and every shift
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(len(days_name))],
                [1] * len(days_name)] 
                    for i in range(len(csr_name)) 
                        for k in range(len(shift_name))]
        
        # Right hand side: ceil(nck/nc) for every CSR and every shift
        rhs = [math.ceil(csr_required_each_shift[k]/csr_required) for i in range(len(csr_name)) for k in range(len(shift_name))]
        
        # Sense: all constraints are less than or equal to
        senses = ["L"] * len(csr_name) * len(shift_name)

        # constrant names: Con4_1_CSR1_C1, Con4_1_CSR1_C2, ..., Con4_1_CSRnc_C6
        constraint_names = ["Con4_1_" + csr_name[i] + "_" + shift_name[k] for i in range(len(csr_name)) for k in range(len(shift_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        #Constraint 4_2:
        rows = [[[var_names[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for j in range(len(days_name))],
                [1] * len(days_name)] 
                    for i in range(len(csr_name)) 
                        for k in range(len(shift_name))]
        rhs = [math.floor(csr_required_each_shift[k]/csr_required) for i in range(len(csr_name)) for k in range(len(shift_name))]
        senses = ["G"] * len(csr_name) * len(shift_name)
        constraint_names = ["Con4_2_" + csr_name[i] + "_" + shift_name[k] for i in range(len(csr_name)) for k in range(len(shift_name))]
        problem.linear_constraints.add(lin_expr = rows, senses = senses, rhs = rhs, names = constraint_names)

        problem.solve()

        # print("solution status = ", problem.solution.get_status())
        # print("solution value = ", problem.solution.get_objective_value())
        # print("solution = ", problem.solution.get_values())
        # slack = problem.solution.get_linear_slacks()
        x     = problem.solution.get_values()

        # constraint_names = problem.linear_constraints.get_names()
        # for i in range(len(constraint_names)):
        #     print ("Constraint %s:  Slack = %d" % (constraint_names[i], slack[i]))
        # for i in range(len(var_names)):
        #     print ("%s: %d" % (var_names[i], x[i]))        

        return [[[x[k + j * len(shift_name) + i * len(days_name) * len(shift_name)] for k in range(len(shift_name))] for j in range(len(days_name))] for i in range(len(csr_name))]
    except CplexError as e:
        print(e)

if __name__ == "__main__":
    rs1 = [sum(solveQ1(day = days[i], shift_name=shift_name, shifts=shifts, hour_name=hour_name)) for i in range(len(days_name))]
    rs2 = solveQ2(shift_name=shift_name, days_name=days_name, result_Q1=result_Q1)
    rs3 = solveQ3(shift_name=shift_name, shifts=shifts, hour_name=hour_name, days=days, days_name=days_name, result_Q1=result_Q1, result_Q2=result_Q2)

    print("Result Q1: " + str(rs1))
    print("Result Q2: " + str(rs2 + max(rs1)))

    def getShiftName(arr):
        for i in range(len(arr)):
            if arr[i] == 1:
                return shift_name[i]
        return "EM"

    print("Result Q3: ")
    for i in range(len(rs3)):
        for j in range(len(days_name)):
            sys.stdout.write(getShiftName(rs3[i][j]) + " ")
        print()