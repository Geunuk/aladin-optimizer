import {SolutionContainer} from "./solution.js";

class InputContainer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            urls: ["https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=86321510",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=14163562",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=188276096",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=1000152",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=175263092",
                "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=508047",
                "abc"],
            titles: [
                "", "", "", "", "", "", ""
            ],
            statuses: [
                "", "", "", "", "", "", ""
            ],
            min_quality: "상"
        }
        this.handleClick = this.handleClick.bind(this)
        this.handleIncreaseRow = this.handleIncreaseRow.bind(this)
        this.handleDecreaseRow = this.handleDecreaseRow.bind(this)
        this.onInputChange = this.onInputChange.bind(this)
        this.handleMinQualityChange = this.handleMinQualityChange.bind(this)
    }

handleClick(e) {
    e.preventDefault()
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.state)
    };
    
    fetch('http://127.0.0.1:5000/input', requestOptions)
        .then(response => response.json())
        .then(response => {
            console.log(JSON.stringify(response, null, 2))
            this.setState({
                titles: response.search_result.map(data =>{if (data !== null) return data.title}),
                statuses: response.search_result.map(data =>{
                    if (data !== null) return `✔️ ${data.count}`
                    else return `❌`})
            }
            )
            ReactDOM.render(<SolutionContainer solutions={response.opt_result} />,document.getElementById("solution-container"))
        })
    }

    handleIncreaseRow() {
        const urls = this.state.urls
        urls.push("")

        this.setState({
            urls: urls
        })
        
    }

    handleDecreaseRow() {
        const urls = this.state.urls
        urls.pop()
        
        this.setState({
            urls:urls
        })
    }

    onInputChange(idx, updated_url) {
        const urls = this.state.urls
        urls[idx] = updated_url
        this.setState(
            {urls: urls}
        )
    }

    handleMinQualityChange(e) {
        this.setState({
            min_quality: e.target.value
        })
    }

    render() {
        return (
            <form action="/input" method="post">
                <button type="button" id="opt" onClick={this.handleClick}>최적화</button>
                <label htmlFor="min_quality">최저 품질
                <select id="min_quality" value={this.state.minQualtiy} onChange={this.handleMinQualityChange}>
                    <option value="최상">최상</option>
                    <option value="상" defaultValue>상</option>
                    <option value="중">중</option>
                    <option value="하">하</option>
                </select>
                </label>
                <InputTable urls={this.state.urls} titles={this.state.titles} statuses={this.state.statuses} onInputChange={this.onInputChange}/>
                <AdjustButton numRows={this.state.urls.length}
                    handleIncreaseRow={this.handleIncreaseRow} handleDecreaseRow={this.handleDecreaseRow}/>
            </form>
        )
    }
}

class InputTable extends React.Component {
    constructor(props) {
        super(props);
        
    }
    
    render() {
        return (
            <table id="input_table">
                <tbody>
                    <tr><th>Input</th><th>Status</th><th>Name</th></tr>
                    {this.props.urls.map((url, idx) => {
                        return <InputTableRow key={idx.toString()} idx={idx.toString()} url={url} title={this.props.titles[idx]} status={this.props.statuses[idx]}onInputChange={this.props.onInputChange}/>
    })}
                
                </tbody>
            </table>
        )
    }
}
class InputTableRow extends React.Component {
    constructor(props) {
        super(props)
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        const idx = parseInt(e.target.name.slice("url".length))
        this.props.onInputChange(idx, e.target.value);
    }
    render() {
        return (
            <tr>
                <td><input type="text" name={`url${this.props.idx}`} value={this.props.url} onChange={this.handleChange}/></td>
                <td className="status">{this.props.status}</td>
                <td>{this.props.title}</td>
            </tr>
        )
    }
}
class AdjustButton extends React.Component {
    
    render() {
        return (
            <div id="adjust_number">
                <input type="button" id="add" value="+" onClick={this.props.handleIncreaseRow} />
                <input type="button" id="remove" value="-" onClick={this.props.handleDecreaseRow} disabled={this.props.numRows==2} />
                
            </div>
        )
    }
}

ReactDOM.render(<InputContainer />, document.getElementById('input-container'))