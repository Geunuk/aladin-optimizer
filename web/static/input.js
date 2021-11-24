var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

import { SolutionContainer } from "./solution.js";

var InputContainer = function (_React$Component) {
    _inherits(InputContainer, _React$Component);

    function InputContainer(props) {
        _classCallCheck(this, InputContainer);

        var _this = _possibleConstructorReturn(this, (InputContainer.__proto__ || Object.getPrototypeOf(InputContainer)).call(this, props));

        _this.state = {
            urls: ["https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=86321510", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=14163562", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=188276096", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=1000152", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=175263092", "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=508047", "abc"],
            titles: ["", "", "", "", "", "", ""],
            statuses: ["", "", "", "", "", "", ""],
            min_quality: "상"
        };
        _this.handleClick = _this.handleClick.bind(_this);
        _this.handleIncreaseRow = _this.handleIncreaseRow.bind(_this);
        _this.handleDecreaseRow = _this.handleDecreaseRow.bind(_this);
        _this.onInputChange = _this.onInputChange.bind(_this);
        _this.handleMinQualityChange = _this.handleMinQualityChange.bind(_this);
        return _this;
    }

    _createClass(InputContainer, [{
        key: "handleClick",
        value: function handleClick(e) {
            var _this2 = this;

            e.preventDefault();
            var requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.state)
            };

            fetch('http://127.0.0.1:5000/input', requestOptions).then(function (response) {
                return response.json();
            }).then(function (response) {
                console.log(JSON.stringify(response, null, 2));
                _this2.setState({
                    titles: response.search_result.map(function (data) {
                        if (data !== null) return data.title;
                    }),
                    statuses: response.search_result.map(function (data) {
                        if (data !== null) return "\u2714\uFE0F " + data.store_list.length;else return "\u274C";
                    })
                });
                ReactDOM.render(React.createElement(SolutionContainer, { solutions: response.opt_result }), document.getElementById("solution-container"));
            });
        }
    }, {
        key: "handleIncreaseRow",
        value: function handleIncreaseRow() {
            var urls = this.state.urls;
            urls.push("");

            this.setState({
                urls: urls
            });
        }
    }, {
        key: "handleDecreaseRow",
        value: function handleDecreaseRow() {
            var urls = this.state.urls;
            urls.pop();

            this.setState({
                urls: urls
            });
        }
    }, {
        key: "onInputChange",
        value: function onInputChange(idx, updated_url) {
            var urls = this.state.urls;
            urls[idx] = updated_url;
            this.setState({ urls: urls });
        }
    }, {
        key: "handleMinQualityChange",
        value: function handleMinQualityChange(e) {
            this.setState({
                min_quality: e.target.value
            });
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "form",
                { action: "/input", method: "post" },
                React.createElement(
                    "button",
                    { type: "button", id: "opt", onClick: this.handleClick },
                    "\uCD5C\uC801\uD654"
                ),
                React.createElement(
                    "label",
                    { htmlFor: "min_quality" },
                    "\uCD5C\uC800 \uD488\uC9C8",
                    React.createElement(
                        "select",
                        { id: "min_quality", value: this.state.minQualtiy, onChange: this.handleMinQualityChange },
                        React.createElement(
                            "option",
                            { value: "\uCD5C\uC0C1" },
                            "\uCD5C\uC0C1"
                        ),
                        React.createElement(
                            "option",
                            { value: "\uC0C1", defaultValue: true },
                            "\uC0C1"
                        ),
                        React.createElement(
                            "option",
                            { value: "\uC911" },
                            "\uC911"
                        ),
                        React.createElement(
                            "option",
                            { value: "\uD558" },
                            "\uD558"
                        )
                    )
                ),
                React.createElement(InputTable, { urls: this.state.urls, titles: this.state.titles, statuses: this.state.statuses, onInputChange: this.onInputChange }),
                React.createElement(AdjustButton, { numRows: this.state.urls.length,
                    handleIncreaseRow: this.handleIncreaseRow, handleDecreaseRow: this.handleDecreaseRow })
            );
        }
    }]);

    return InputContainer;
}(React.Component);

var InputTable = function (_React$Component2) {
    _inherits(InputTable, _React$Component2);

    function InputTable(props) {
        _classCallCheck(this, InputTable);

        return _possibleConstructorReturn(this, (InputTable.__proto__ || Object.getPrototypeOf(InputTable)).call(this, props));
    }

    _createClass(InputTable, [{
        key: "render",
        value: function render() {
            var _this4 = this;

            return React.createElement(
                "table",
                { id: "input_table" },
                React.createElement(
                    "tbody",
                    null,
                    React.createElement(
                        "tr",
                        null,
                        React.createElement(
                            "th",
                            null,
                            "Input"
                        ),
                        React.createElement(
                            "th",
                            null,
                            "Status"
                        ),
                        React.createElement(
                            "th",
                            null,
                            "Name"
                        )
                    ),
                    this.props.urls.map(function (url, idx) {
                        return React.createElement(InputTableRow, { key: idx.toString(), idx: idx.toString(), url: url, title: _this4.props.titles[idx], status: _this4.props.statuses[idx], onInputChange: _this4.props.onInputChange });
                    })
                )
            );
        }
    }]);

    return InputTable;
}(React.Component);

var InputTableRow = function (_React$Component3) {
    _inherits(InputTableRow, _React$Component3);

    function InputTableRow(props) {
        _classCallCheck(this, InputTableRow);

        var _this5 = _possibleConstructorReturn(this, (InputTableRow.__proto__ || Object.getPrototypeOf(InputTableRow)).call(this, props));

        _this5.handleChange = _this5.handleChange.bind(_this5);
        return _this5;
    }

    _createClass(InputTableRow, [{
        key: "handleChange",
        value: function handleChange(e) {
            var idx = parseInt(e.target.name.slice("url".length));
            this.props.onInputChange(idx, e.target.value);
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "tr",
                null,
                React.createElement(
                    "td",
                    null,
                    React.createElement("input", { type: "text", name: "url" + this.props.idx, value: this.props.url, onChange: this.handleChange })
                ),
                React.createElement(
                    "td",
                    { className: "status" },
                    this.props.status
                ),
                React.createElement(
                    "td",
                    null,
                    this.props.title
                )
            );
        }
    }]);

    return InputTableRow;
}(React.Component);

var AdjustButton = function (_React$Component4) {
    _inherits(AdjustButton, _React$Component4);

    function AdjustButton() {
        _classCallCheck(this, AdjustButton);

        return _possibleConstructorReturn(this, (AdjustButton.__proto__ || Object.getPrototypeOf(AdjustButton)).apply(this, arguments));
    }

    _createClass(AdjustButton, [{
        key: "render",
        value: function render() {
            return React.createElement(
                "div",
                { id: "adjust_number" },
                React.createElement("input", { type: "button", id: "add", value: "+", onClick: this.props.handleIncreaseRow }),
                React.createElement("input", { type: "button", id: "remove", value: "-", onClick: this.props.handleDecreaseRow, disabled: this.props.numRows == 2 })
            );
        }
    }]);

    return AdjustButton;
}(React.Component);

ReactDOM.render(React.createElement(InputContainer, null), document.getElementById('input-container'));