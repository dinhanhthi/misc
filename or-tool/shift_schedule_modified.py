from ortools.sat.python import cp_model



class employeesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts, num_employees, num_days, num_shifts, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_employees = num_employees
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solutions = set(sols)
        self._solution_count = 0

    def on_solution_callback(self):
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            #for d in range(self._num_days):
                # #print result by shift
                # print('Day %i' % d)
                # for s in range(self._num_shifts):
                #     print('Shift %i covered by : ' % s, end='')
                #     for n in range(self._num_employees):
                #         if self.Value(self._shifts[(n,d,s)]):
                #             print(' %i, ' % n, end='')
                #     print()

                #print result by employee
                # for n in range(self._num_employees):
                #     is_working = False
                #     for s in range(self._num_shifts):
                #         if self.Value(self._shifts[(n, d, s)]):
                #             is_working = True
                #             print('  employee %i works shift %i' % (n, s))
                #     if not is_working:
                #         print('  employee {} does not work'.format(n))
            #print()
            for n in range(self._num_employees):
                num_total_shift = 0; 
                num_day_shift = 0
                num_night_shift = 0
                print('---------Employee %i ---------------' %n)
                for d in range(self._num_days):
                    print('day %i ' % d, end='')
                    for s in range(self._num_shifts):
                        if self.Value(self._shifts[(n,d,s)]):
                            print('shift %i ' %s, end='')
                            num_total_shift += 1
                            if s == 2:
                                num_night_shift += 1
                            else:
                                num_day_shift += 1
                    print()
                print('employee %i will work %i shift (%i day shift and %i night shift)' %(n, num_total_shift, num_day_shift, num_night_shift))
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count




def main():
    # Data.
    num_employees = 50
    num_employees_per_shift = 15; 
    num_shifts = 3
    num_days = 10
    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(n, d, s)]: employee 'n' works shift 's' on day 'd'.
    shifts = {}
    for n in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d,
                        s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Each shift is assigned to exactly one employee in the schedule period.
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_employees) == num_employees_per_shift)

    # Each employee works at most one shift per day.
    for n in all_employees:
        for d in all_days:
            model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)
    # Try to distribute the shifts evenly (for day and night), so that each employee works
    # min_shifts_per_employee shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of employees, some employees will
    # be assigned one more shift.

    min_shifts_per_employee = (num_shifts * num_days * num_employees_per_shift) // num_employees
    if num_shifts * num_days * num_employees_per_shift % num_employees == 0:
        max_shifts_per_employee = min_shifts_per_employee
    else:
        max_shifts_per_employee = min_shifts_per_employee + 1
    min_night_shift_per_employee = num_days * num_employees_per_shift // num_employees
    if num_days * num_employees_per_shift % num_employees == 0:
        max_night_shift_per_employee = min_night_shift_per_employee
    else:
        max_night_shift_per_employee = min_night_shift_per_employee + 1
    for n in all_employees:
        num_shifts_worked = 0
        num_night_shift_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
                if s == 2:
                    num_night_shift_worked += shifts[(n, d, s)]
                if d < num_days-1: 
                    model.AddBoolAnd([shifts[n, d+1, 0].Not()]).OnlyEnforceIf(shifts[n, d, 2])
                    model.AddBoolAnd([shifts[n,d+1,0].Not()]).OnlyEnforceIf(shifts[n,d,1])
        model.Add(min_shifts_per_employee <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_employee)
        model.Add(min_night_shift_per_employee <= num_night_shift_worked)
        model.Add(num_night_shift_worked <= max_night_shift_per_employee)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Display the first five solutions.
    a_few_solutions = range(1)
    solution_printer = employeesPartialSolutionPrinter(shifts, num_employees,
                                                    num_days, num_shifts,
                                                    a_few_solutions)
    solver.SolveWithSolutionCallback(model, solution_printer)
    # solver.SearchForAllSolutions(model, solution_printer)
    # Statistics.
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - wall time       : %f s' % solver.WallTime())
    print('  - solutions found : %i' % solution_printer.solution_count())


if __name__ == '__main__':
    main()