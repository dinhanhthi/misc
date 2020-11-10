# source
# https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model

def main():

    n_employees = 50
    n_days = 30
    n_shifts = 3*n_days
    n_eps = 15

    all_employees = range(n_employees)
    all_shifts = range(n_shifts)

    model = cp_model.CpModel()

    shifts = {}
    for n in all_employees:
        for s in all_shifts:
            shifts[(n, s)] = model.NewBoolVar('shift_n%is%i' % (n, s))

    # each shift need 15 employees
    for s in all_shifts:
        model.Add(sum(shifts[(n, s)] for n in all_employees) == n_eps)


    # each employee has 9 night shifts (30*15/50)
    #               and 18 day shifts (60*15/50)
    for n in all_employees:
        n_night_worked = 0
        n_day_worked = 0
        for s in all_shifts:
            if s%3==2:
                n_night_worked += shifts[(n, s)]
            else:
                n_day_worked += shifts[(n, s)]
        model.Add(n_night_worked == 3*n_days*n_eps // n_employees)
        model.Add(n_day_worked == 2*3*n_days*n_eps // n_employees)

    # each employee has 2 consecutive shifts >= 2 shifts (16h)
    for n in all_employees:
        for s in all_shifts:
            model.Add(sum([
                shifts[(n, s)],
                shifts[(n, (s+1)%n_shifts)],
                shifts[(n, (s+2)%n_shifts)]
            ]) <= 1)

    # max
    model.Maximize(sum(shifts[(n, s)] for n in all_employees for s in all_shifts))


    solver = cp_model.CpSolver()
    solver.Solve(model)
    for s in all_shifts:
        print('Shift', s)
        for n in all_employees:
            if solver.Value(shifts[(n, s)]) == 1:
                pass
                print('Employee', n, 'works shift', s)
        print()
        break # only print 1st shift to check


if __name__ == '__main__':
    main()