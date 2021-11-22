from itertools import chain

from ortools.sat.python import cp_model

MINIMUM_PRICE = 20000

def flatten(list_of_list):
    return list(chain.from_iterable(list_of_list))

def unflatten(l, num_rows, num_cols):
    res = []
    for r in range(num_rows):
        res.append(l[r*num_cols:(r+1)*num_cols])
    return res

class SaveOptimalSolution(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.max_value = -1
        self.solutions = []

    def OnSolutionCallback(self):
        solution = []
        num_buying = 0
        for var in self.__variables:
            solution.append(self.Value(var))
            if self.Value(var) == 1:
                num_buying += 1

        if num_buying > self.max_value:
            self.max_value = num_buying
            self.solutions = [solution]
            self.__solution_count = 1
        elif num_buying == self.max_value:
            self.solutions.append(solution)
            self.__solution_count += 1

    def SolutionCount(self):
        return self.__solution_count

def solve(book_list, store_list):
    model = cp_model.CpModel()
    
    # Variables
    num_rows = len(book_list)
    num_cols = len(store_list)
    var_matrix = [] # num_books x num_stores
    for r in range(num_rows):
        row_vars = []
        for c in range(num_cols):
            row_vars.append(model.NewBoolVar(f"var_b{r}_s{c}"))
        var_matrix.append(row_vars)

    # Constraints
    # 1. Max one store for each book.
    for row_vars in var_matrix:
        model.Add(cp_model.LinearExpr.Sum(row_vars) <= 1)
    
    # 2. Set zero to the stores that don't have books.
    store_name_to_idx = {store_name:idx for idx, store_name in enumerate(store_list)}
    for r in range(num_rows):
        not_selling_stores = set(range(num_cols))
        if book_list[r] is None:
            continue
        for item in book_list[r].item_list:
            store_idx = store_name_to_idx[item.store_name]
            if store_idx in not_selling_stores:
                not_selling_stores.remove(store_idx)
        for idx in not_selling_stores:
            model.Add(var_matrix[r][idx] == 0)
    
    # 3. If you have books to buy at each store,
    # you have to exceed the minimum price.
    # Variables for each column.
    # If all values in the column are zero, set False.
    # Otherwise set True.
    item_exist_list = [model.NewBoolVar(f"var_exist{c}") for c in range(num_cols)]
    for c, var in enumerate(item_exist_list):
        model.Add(sum([var_matrix[r][c] for r in range(num_rows)]) >= 1).OnlyEnforceIf(var)
        model.Add(sum([var_matrix[r][c] for r in range(num_rows)]) < 1).OnlyEnforceIf(var.Not())
    
    for c in range(num_cols):
        col_vars = [var_matrix[r][c] for r in range(num_rows)]
        col_prices = []
        for r in range(num_rows):
            if book_list[r] is None:
                col_prices.append(0)
                continue
            store_name = store_list[c]
            item = book_list[r].find_item(store_name)
            price = item.price if item is not None else 0
            col_prices.append(price)
        model.Add(cp_model.LinearExpr.ScalProd(col_vars, col_prices) >= MINIMUM_PRICE*item_exist_list[c])

    for r in range(num_rows):
        if book_list[r] is None:
            for c in range(num_cols):
                model.Add(var_matrix[r][c] == 0)
    
    solver = cp_model.CpSolver()
    callback = SaveOptimalSolution(flatten(var_matrix))
    status = solver.SearchForAllSolutions(model, callback)
    if status != 4:
        raise Exception("Status is not optimal")
    
    result = []
    for solution in callback.solutions:
        tmp = []
        unflattened = unflatten(solution, num_rows, num_cols)
        is_zero_solution = True
        for r in range(num_rows):
            if book_list[r] is None:
                tmp.append(None)
                continue
            for c in range(num_cols):
                if unflattened[r][c] == 1:
                    is_zero_solution = False
                    store_name = store_list[c]
                    tmp.append(book_list[r].find_item(store_name))
        if not is_zero_solution:
            result.append(tmp)
    return result
