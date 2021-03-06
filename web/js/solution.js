export function SolutionContainer({heading, solutions, use_online}) {
    return (
        <React.Fragment>
            <h2>{heading}</h2>
            {solutions.map((sol, idx) => {
                return <SolutionTable key={`Solution ${idx+1}`} name={`Solution ${idx+1}`}
                        solution={sol} use_online={use_online}/>
            })}
        </React.Fragment>
    );
}

function SolutionTable({name, solution, use_online}) {
    let numTotalItems = 0;
    for ({item_list} of solution.stores) {
        numTotalItems += item_list.length;
    }
    
    return (
        <React.Fragment>
            <h3>{name}</h3>
            <table className="solution">
                <tbody>
                {
                    solution.stores.map(({store_name, item_list, store_price, discount}, store_idx) => {
                        return <StoreRows key={store_idx.toString()} store_idx={store_idx}
                                total_price={solution.total_price} numTotalItems={numTotalItems}
                                store_name={store_name} item_list={item_list} store_price={store_price}
                                discount={discount} use_online={use_online}/>          
                    })
                }
                </tbody>
            </table>
        </React.Fragment>
    )
}

function StoreRows({store_idx, total_price, numTotalItems, store_name, item_list, store_price, discount, use_online}) {
    return (
        <React.Fragment>
            {
                item_list.map(({title,quality,price,link}, item_idx) => {
                    if (store_idx === 0 && item_idx === 0)
                        return (
                            <ItemRow key={item_idx.toString()} store_name={store_name} title={title}
                            quality={quality} price={price} link={link} use_online={use_online}>
                                <td rowSpan={item_list.length.toString()} className={discount ? "discount":""}>{store_price}</td>
                                <td rowSpan={numTotalItems}>{total_price}</td>    
                            </ItemRow>
                        )    
                    else if (item_idx === 0)
                        return (
                            <ItemRow key={item_idx.toString()} store_name={store_name} title={title}
                            quality={quality} price={price} link={link} use_online={use_online}>
                                <td rowSpan={item_list.length.toString()} className={discount ? "discount":""}>{store_price}</td>    
                            </ItemRow>
                        )       
                    else
                        return <ItemRow key={item_idx.toString()} store_name={store_name} title={title}
                                quality={quality} price={price} link={link} use_online={use_online}/>     
                })
            }
        </React.Fragment>
    )
}
function ItemRow({store_name, title, quality, price, link, use_online, children}) {
    return (
        <React.Fragment>
            <tr><td>{store_name}</td><td>{title}</td><td>{quality}</td><td>{price}</td>{children}
            {use_online === "online" ? <td><a href={link}>??????</a></td> : ""}</tr>
        </React.Fragment>
    )
}