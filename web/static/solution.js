export function SolutionContainer(_ref) {
    var heading = _ref.heading,
        solutions = _ref.solutions;

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            "h2",
            null,
            heading
        ),
        solutions.map(function (sol, idx) {
            return React.createElement(SolutionTable, { key: "Solution " + (idx + 1), name: "Solution " + (idx + 1), solution: sol });
        })
    );
}

function SolutionTable(_ref2) {
    var name = _ref2.name,
        solution = _ref2.solution;

    var numTotalItems = 0;
    var _iteratorNormalCompletion = true;
    var _didIteratorError = false;
    var _iteratorError = undefined;

    try {
        for (var _iterator = solution.stores[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
            var _ref3 = _step.value;
            var item_list = _ref3.item_list;

            numTotalItems += item_list.length;
        }
    } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
    } finally {
        try {
            if (!_iteratorNormalCompletion && _iterator.return) {
                _iterator.return();
            }
        } finally {
            if (_didIteratorError) {
                throw _iteratorError;
            }
        }
    }

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            "h3",
            null,
            name
        ),
        React.createElement(
            "table",
            { className: "solution" },
            React.createElement(
                "tbody",
                null,
                solution.stores.map(function (_ref4, store_idx) {
                    var store_name = _ref4.store_name,
                        item_list = _ref4.item_list,
                        store_price = _ref4.store_price,
                        discount = _ref4.discount;

                    return React.createElement(StoreRows, { key: store_idx.toString(), store_idx: store_idx,
                        total_price: solution.total_price, numTotalItems: numTotalItems,
                        store_name: store_name, item_list: item_list, store_price: store_price,
                        discount: discount });
                })
            )
        )
    );
}

function StoreRows(_ref5) {
    var store_idx = _ref5.store_idx,
        total_price = _ref5.total_price,
        numTotalItems = _ref5.numTotalItems,
        store_name = _ref5.store_name,
        item_list = _ref5.item_list,
        store_price = _ref5.store_price,
        discount = _ref5.discount;

    return React.createElement(
        React.Fragment,
        null,
        item_list.map(function (_ref6, item_idx) {
            var title = _ref6.title,
                quality = _ref6.quality,
                price = _ref6.price,
                link = _ref6.link;

            if (store_idx === 0 && item_idx === 0) return React.createElement(
                ItemRow,
                { key: item_idx.toString(), store_name: store_name, title: title, quality: quality, price: price, link: link },
                React.createElement(
                    "td",
                    { rowSpan: item_list.length.toString(), className: discount ? "discount" : "" },
                    store_price
                ),
                React.createElement(
                    "td",
                    { rowSpan: numTotalItems },
                    total_price
                )
            );else if (item_idx === 0) return React.createElement(
                ItemRow,
                { key: item_idx.toString(), store_name: store_name, title: title, quality: quality, price: price, link: link },
                React.createElement(
                    "td",
                    { rowSpan: item_list.length.toString(), className: discount ? "discount" : "" },
                    store_price
                )
            );else return React.createElement(ItemRow, { key: item_idx.toString(), store_name: store_name, title: title, quality: quality, price: price, link: link });
        })
    );
}
function ItemRow(_ref7) {
    var store_name = _ref7.store_name,
        title = _ref7.title,
        quality = _ref7.quality,
        price = _ref7.price,
        link = _ref7.link,
        children = _ref7.children;

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            "tr",
            null,
            React.createElement(
                "td",
                null,
                store_name
            ),
            React.createElement(
                "td",
                null,
                title
            ),
            React.createElement(
                "td",
                null,
                quality
            ),
            React.createElement(
                "td",
                null,
                price
            ),
            children,
            React.createElement(
                "td",
                null,
                React.createElement(
                    "a",
                    { href: link },
                    "\uB9C1\uD06C"
                )
            )
        )
    );
}