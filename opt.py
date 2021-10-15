from itertools import chain

from ortools.sat.python import cp_model

from book import *

MINIMUM_PRICE = 20000
DEFAULT_MIN_QUALITY = "상"

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

def solve(book_urls):
    store_list = get_store_list()
    store_name_to_idx = {store_name:idx for idx, store_name in enumerate(store_list)}

    print("Start craling...")
    book_list = []
    for book_url in book_urls:
        book = search_book(book_url, DEFAULT_MIN_QUALITY, store_list)
        print(f"Found {len(book.item_list)} items of '{book.title}'...")
        book_list.append(book)
    print("End craling...")

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
    for r in range(num_rows):
        not_selling_stores = set(range(num_cols))
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
            store_name = store_list[c]
            item = book_list[r].find_item(store_name)
            price = item.price if item is not None else 0
            col_prices.append(price)
        model.Add(cp_model.LinearExpr.ScalProd(col_vars, col_prices) >= MINIMUM_PRICE*item_exist_list[c])

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
            for c in range(num_cols):
                if unflattened[r][c] == 1:
                    is_zero_solution = False
                    store_name = store_list[c]
                    tmp.append(book_list[r].find_item(store_name))
        if not is_zero_solution:
            result.append(tmp)
    return result

if __name__ == "__main__":
    from main import print_result
    
    book_urls = [
        "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019", #굴소년
        "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=86321510", #1만시간의 재발견
        "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=61762093", #정리하는 뇌
        "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=14163562", #여행의 기술
        "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=188276096", # 여행의 이유
        "https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=1000152", #채식주의자
        ]
    
    result = solve(book_urls)
    
    print_result(result)
