from itertools import chain

from ortools.sat.python import cp_model

MINIMUM_PRICE = 20000
SHIPPING_FEE = 2000

def flatten(list_of_list):
    return list(chain.from_iterable(list_of_list))

def unflatten(l, num_rows, num_cols):
    res = []
    for r in range(num_rows):
        res.append(l[r*num_cols:(r+1)*num_cols])
    return res

def transpose(matrix):
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    transposed = [[None]*num_rows for _ in range(num_cols)]
    for r in range(num_rows):
        for c in range(num_rows):
            transposed[c][r] = matrix[r][c]
    return transposed

class SaveOptimalSolution(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.max_value = -1
        self.solutions = []

    def OnSolutionCallback(self):
        solution = []
        for var in self.__variables:
            solution.append(self.Value(var))
        self.solutions.append(solution)
        self.__solution_count += 1

    def SolutionCount(self):
        return self.__solution_count

def get_price_matrix(book_list, store_list):
    num_rows = len(book_list)
    num_cols = len(store_list)
    
    price_matrix =  []
    for r in range(num_rows):
        if book_list[r] is None:
            price_matrix.append([0]*num_cols)
            continue

        row_prices = []
        for c in range(num_cols):
            store_name = store_list[c]
            item = book_list[r].find_item(store_name)
            price = item.price if item is not None else 0
            row_prices.append(price)
        price_matrix.append(row_prices)
    
    return price_matrix
    
def get_item_exist_matrix(book_list, store_list):
    num_rows = len(book_list)
    num_cols = len(store_list)
    
    item_exist_matrix = [[False] * num_cols for  _ in range(num_rows)]
    store_name_to_idx = {store_name:idx for idx, store_name in enumerate(store_list)}
    for r in range(num_rows):
        if book_list[r] is None:
            continue
        for item in book_list[r].item_list:
            store_idx = store_name_to_idx[item.store_name]
            item_exist_matrix[r][store_idx] = True
    
    return item_exist_matrix

def add_variables(model, num_rows, num_cols, price_matrix):
    item_vars = [] # num_books x num_stores
    for r in range(num_rows):
        row_vars = []
        for c in range(num_cols):
            row_vars.append(model.NewBoolVar(f"var_b{r}_s{c}"))
        item_vars.append(row_vars)
    
    store_vars = [model.NewBoolVar(f"store_{c}") for c in range(num_cols)]
    for c, var in enumerate(store_vars):
        model.Add(sum([item_vars[r][c] for r in range(num_rows)]) >= 1).OnlyEnforceIf(var)
        model.Add(sum([item_vars[r][c] for r in range(num_rows)]) < 1).OnlyEnforceIf(var.Not())
    
    below_min_price_vars = [model.NewBoolVar(f"below_min_price_{c}") for c in range(num_cols)]
    for c, var in enumerate(below_min_price_vars):
        col_vars = [item_vars[r][c] for r in range(num_rows)]
        col_prices = [price_matrix[r][c] for r in range(num_rows)]
        model.Add(cp_model.LinearExpr.ScalProd(col_vars, col_prices) < MINIMUM_PRICE).OnlyEnforceIf(var)
        model.Add(cp_model.LinearExpr.ScalProd(col_vars, col_prices) >= MINIMUM_PRICE).OnlyEnforceIf(var.Not())
    
    return item_vars, store_vars, below_min_price_vars    
    
def add_base_constraints(model, item_vars, store_vars, below_min_price_vars, item_exist_matrix, price_matrix, only_free_shipping=False):
    num_rows = len(item_vars)
    num_cols = len(item_vars[0])
    
    # Constraints
    # 1. Max one store for each book.
    for row_vars in item_vars:
        model.Add(cp_model.LinearExpr.Sum(row_vars) <= 1)
    
    # 2. Set zero to the stores that don't have books.
    for r in range(num_rows):
        for c in range(num_cols):
            if not item_exist_matrix[r][c]:
                model.Add(item_vars[r][c] == 0)

    if only_free_shipping:
        # 3. If you have books to buy at each store,
        # you have to exceed the minimum price.
        # Variables for each column.
        # If all values in the column are zero, set False.
        # Otherwise set True.
        
        for c in range(num_cols):
            col_vars = [item_vars[r][c] for r in range(num_rows)]
            col_prices = [price_matrix[r][c] for r in range(num_rows)]
            #model.Add(cp_model.LinearExpr.ScalProd(col_vars, col_prices) >= MINIMUM_PRICE*store_vars[c])
            model.AddBoolAnd([below_min_price_vars[c].Not()]).OnlyEnforceIf(store_vars[c])

def num_buying_items(item_vars):
    return cp_model.LinearExpr.Sum(flatten(item_vars))

def add_shipping_fee_vars(model, item_vars, store_vars, below_min_price_vars, price_matrix):
    num_rows = len(item_vars)
    num_cols = len(item_vars[0])
    
    fee_vars = [model.NewBoolVar(f"fee_{c}") for c in range(num_cols)]
    for c, var in enumerate(fee_vars):
        col_vars = [item_vars[r][c] for r in range(num_rows)]
        col_prices = [price_matrix[r][c] for r in range(num_rows)]
        #tmp = model.NewBoolVar(f"{c}cp_model.LinearExpr.ScalProd(col_vars, col_prices) < MINIMUM_PRICE")
        model.AddBoolAnd([store_vars[c], below_min_price_vars[c]]).OnlyEnforceIf(var)
        model.AddBoolOr([store_vars[c].Not(), below_min_price_vars[c].Not()]).OnlyEnforceIf(var.Not())
        
    return fee_vars

def total_price(model, item_vars, store_vars, fee_vars, price_matrix):
    num_rows = len(item_vars)
    num_cols = len(item_vars[0])
    
    total = 0
    for c in range(num_cols):
        col_vars = [item_vars[r][c] for r in range(num_rows)]
        col_prices = [price_matrix[r][c] for r in range(num_rows)]
        total += cp_model.LinearExpr.ScalProd(col_vars, col_prices)
        total += SHIPPING_FEE*fee_vars[c]
    return total
    
def solve(book_list, store_list, only_free_shipping=False):    
    price_matrix = get_price_matrix(book_list, store_list)
    item_exist_matrix = get_item_exist_matrix(book_list, store_list)
    
    num_rows = len(book_list)
    num_cols = len(store_list)
    
    # Phase 1: Maximize number of buying books.
    model = cp_model.CpModel()
    item_vars, store_vars, below_min_price_vars = add_variables(model, num_rows, num_cols, price_matrix)
    add_base_constraints(model, item_vars, store_vars, below_min_price_vars, item_exist_matrix, price_matrix, only_free_shipping)
    
    model.Maximize(num_buying_items(item_vars))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status != 4:
        raise Exception("Status is not optimal")
    max_num_buying_items = int(solver.ObjectiveValue())

    # Phase 2: Minimize total cost.
    model = cp_model.CpModel()
    item_vars, store_vars, below_min_price_vars = add_variables(model, num_rows, num_cols, price_matrix)    
    add_base_constraints(model, item_vars, store_vars, below_min_price_vars, item_exist_matrix, price_matrix, only_free_shipping)
    
    model.Add(max_num_buying_items == num_buying_items(item_vars))
    fee_vars = add_shipping_fee_vars(model, item_vars, store_vars, below_min_price_vars, price_matrix)
    
    model.Minimize(total_price(model, item_vars, store_vars, fee_vars, price_matrix))
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status != 4:
        raise Exception("Status is not optimal")
    min_price = int(solver.ObjectiveValue())
    
    # Phase 3: Generate all solutions
    model = cp_model.CpModel()
    item_vars, store_vars, below_min_price_vars = add_variables(model, num_rows, num_cols, price_matrix)    
    add_base_constraints(model, item_vars, store_vars, below_min_price_vars, item_exist_matrix, price_matrix, only_free_shipping)
    
    model.Add(max_num_buying_items == num_buying_items(item_vars))
    
    fee_vars = add_shipping_fee_vars(model, item_vars, below_min_price_vars, store_vars, price_matrix)
    model.Add(min_price == total_price(model, item_vars, store_vars, fee_vars, price_matrix))
    
    solver = cp_model.CpSolver()
    callback = SaveOptimalSolution(flatten(item_vars))
    status = solver.SearchForAllSolutions(model, callback)
    if status != 4:
        raise Exception("Status is not optimal")
    
    solutions = []
    for solution in callback.solutions:
        solutions.append(unflatten(solution, num_rows, num_cols))
    return solutions