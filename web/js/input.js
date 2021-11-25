import {SolutionContainer} from "./solution.js";

class InputContainer extends React.Component {
    constructor(props) {
        super(props);
        const init_urls = ["https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=16294019",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=86321510",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=14163562",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=188276096",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=1000152",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=175263092",
            "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=508047",
            "abc"] 
        this.state = {
            urls: init_urls,
            disable_list: new Array(init_urls.length).fill(false),
            titles: new Array(init_urls.length).fill(""),
            statuses: new Array(init_urls.length).fill(""),
            use_online: "online",
            min_quality: "상"
        }
        this.handleClick = this.handleClick.bind(this)
        this.handleIncreaseRow = this.handleIncreaseRow.bind(this)
        this.handleRemoveRow = this.handleRemoveRow.bind(this)
        this.handleInputChange = this.handleInputChange.bind(this)
        this.handleInputDisabled = this.handleInputDisabled.bind(this)
        this.handleMinQualityChange = this.handleMinQualityChange.bind(this)
        this.handleUseOnlineChange = this.handleUseOnlineChange.bind(this)
    }

handleClick(e) {
    e.preventDefault()
    const orig_disable_list = [...this.state.disable_list]
    const orig_use_online = this.state.use_online
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
                titles: response.search_result.map((data,idx) => {
                    if (!orig_disable_list[idx] && data !== null)
                        return data.title
                }),
                statuses: response.search_result.map((data, idx) => {
                    if (!orig_disable_list[idx]) {
                        if (data !== null) return `✔️ ${data.store_list.length}`
                        else return `❌`
                    }
                })
            })
             
            const solutions = (
                <React.Fragment>
                    <SolutionContainer heading={"결과"} solutions={response.solutions} use_online={orig_use_online}/>
                    {orig_use_online ==="online" ?
                        <SolutionContainer heading={"결과(무료배송)"} solutions={response.solutions_free_shipping} /> : ""}
                </React.Fragment>
            )
            ReactDOM.render(solutions, document.getElementById("solution-container"))
        })
    }

    handleIncreaseRow() {
        const urls = this.state.urls
        urls.push("")
        const disable_list = this.state.disable_list
        disable_list.push(false)
        this.setState({
            urls: urls,
            disable_list: disable_list
        })
        
    }

    handleRemoveRow(idx) {
        const urls = this.state.urls
        urls.splice(idx, 1);
        const disable_list = this.state.disable_list
        disable_list.splice(idx, 1)
        this.setState({
            urls: urls,
            disable_list: disable_list
        })
    }
    handleInputChange(idx, updated_url) {
        const urls = this.state.urls
        urls[idx] = updated_url
        this.setState(
            {urls: urls}
        )
    }
    
    handleInputDisabled(idx) {
        const disable_list = this.state.disable_list
        disable_list[idx] = !disable_list[idx];
        this.setState({
            disable_list: disable_list
        })
    }

    handleUseOnlineChange(e) {
        this.setState({
            use_online: e.target.value
        })
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
                <label htmlFor="online">구입 방법
                    <select id="online" defaultValue={"online"} value={this.state.use_online} onChange={this.handleUseOnlineChange}>
                        <option value="online">온라인(우주점)</option>
                        <option value="offline">오프라인</option>
                    </select>
                </label>
                <label htmlFor="min_quality">최저 품질
                    <select id="min_quality" defaultValue={"상"} value={this.state.minQualtiy} onChange={this.handleMinQualityChange}>
                        <option value="최상">최상</option>
                        <option value="상">상</option>
                        <option value="중">중</option>
                        <option value="하">하</option>
                    </select>
                </label>
                <InputTable urls={this.state.urls} titles={this.state.titles} statuses={this.state.statuses}
                    numRows={this.state.urls.length} handleInputChange={this.handleInputChange}
                    disable_list={this.state.disable_list} handleInputDisabled={this.handleInputDisabled}
                    handleRemoveRow={this.handleRemoveRow}/>
                <div id="adjust_number">
                    <input type="button" id="add" value="+" onClick={this.handleIncreaseRow} />
                </div>
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
                        return <InputTableRow key={idx.toString()} idx={idx.toString()} url={url}
                            title={this.props.titles[idx]} status={this.props.statuses[idx]}
                            numRows={this.props.numRows} handleInputChange={this.props.handleInputChange}
                            disabled={this.props.disable_list[idx]} handleInputDisabled={this.props.handleInputDisabled}
                            handleRemoveRow={this.props.handleRemoveRow} />
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
        this.handleRemoveRow = this.handleRemoveRow.bind(this);
        this.handleInputDisabled = this.handleInputDisabled.bind(this);
    }

    handleChange(e) {
        const idx = parseInt(e.target.name.slice("url".length))
        this.props.handleInputChange(idx, e.target.value);
    }
    handleRemoveRow(e) {
        const idx = parseInt(this.props.idx)
        this.props.handleRemoveRow(idx);
    }
    handleInputDisabled(e) {
        const idx = parseInt(this.props.idx)
        this.props.handleInputDisabled(idx);
    }
    render() {
        return (
            <tr>
                <td><input type="text" name={`url${this.props.idx}`} value={this.props.url} disabled={this.props.disabled}
                    onChange={this.handleChange}/></td>
                <td className="status">{this.props.status}</td>
                <td>{this.props.title}</td>
                <td><input type="button" id={`disable${this.props.idx}`} value={this.props.disabled ? "Enable" : "Disable"}
                    onClick={this.handleInputDisabled} /></td>
                <td><input type="button" id={`remove${this.props.idx}`} value="-" onClick={this.handleRemoveRow}
                    disabled={this.props.numRows==2} /></td>
            </tr>
        )
    }
}


ReactDOM.render(<InputContainer />, document.getElementById('input-container'))