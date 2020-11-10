# source
# https://developers.google.com/optimization/scheduling/employee_scheduling

from ortools.sat.python import cp_model

def main():

    n_employees = 50
    # n_employees = 10
    n_shifts = 3
    n_days = 30
    # n_days = 7
    n_eps = 15
    # n_eps = 5

    all_employees = range(n_employees)
    all_shifts = range(n_shifts)
    all_days = range(n_days)

    model = cp_model.CpModel()

    shifts = {}
    for n in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # each shift need 15 employees
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_employees) == n_eps)


    # each employee has 9 night shifts (30*15/50)
    #               and 18 day shifts (60*15/50)
    for n in all_employees:
        n_night_worked = 0
        n_day_worked = 0
        for d in all_days:
            for s in all_shifts:
                if s==2:
                    n_night_worked += shifts[(n, d, s)]
                else:
                    n_day_worked += shifts[(n, d, s)]
        model.Add(n_night_worked == 9)
        model.Add(n_day_worked == 18)

    # each employee has 2 consecutive shifts >= 2 shifts (16h)
    for n in all_employees:
        for d in all_days:
            model.Add(sum([
                shifts[(n, d, 0)],
                shifts[(n, (d+1)%n_days, 1)],
                shifts[(n, (d+1)%n_days, 2)]
            ]) <= 1)
            model.Add(sum([
                shifts[(n, d, 1)],
                shifts[(n, (d+1)%n_days, 2)],
                shifts[(n, (d+1)%n_days, 0)]
            ]) <= 1)
            model.Add(sum([
                shifts[(n, d, 2)],
                shifts[(n, (d+1)%n_days, 1)],
                shifts[(n, (d+1)%n_days, 0)]
            ]) <= 1)

    # max
    model.Maximize(sum(shifts[(n, d, s)] for n in all_employees
            for d in all_days for s in all_shifts))


    solver = cp_model.CpSolver()
    solver.Solve(model)
    for d in all_days:
        print('Day', d)
        for n in all_employees:
            for s in all_shifts:
                if solver.Value(shifts[(n, d, s)]) == 1:
                    print('Employee', n, 'works shift', s)
        print()
        break # only print 1st day to check


if __name__ == '__main__':
    main()