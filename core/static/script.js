let currentStock = 0;

function changeCurrentStock(stockIndex) {
    document.getElementById('stock-detailed-' + currentStock).classList.add('d-none');
    document.getElementById('select-stock-' + currentStock).classList.remove('bg-light', 'border-start', 'border-primary', 'border-5');
    currentStock = stockIndex;
    document.getElementById('stock-detailed-' + currentStock).classList.remove('d-none');
    document.getElementById('select-stock-' + currentStock).classList.add('bg-light', 'border-start', 'border-primary', 'border-5');
}

function calculateReturnPercentage(averagePrice, currentPrice, quantity) {
    return ((currentPrice - averagePrice) / averagePrice) * 100;
}


function getAllStockIDs() {
    // find all the elements that name ends with buy-price
    const buyPrices = document.querySelectorAll("[name$='buy-price']");

    let stockIDS = [];

    // loop through all the elements
    for (let i = 0; i < buyPrices.length; i++) {
        // get the name of the element
        let name = buyPrices[i].getAttribute('name');
        // get the id of the stock
        name = name.split('-')[0];
        if (!stockIDS.includes(name)) {
            // check its not empty
            if (name) {
                // add the id to the array
                stockIDS.push(name);
            }
        }
    }
    return stockIDS;
}

function getAllStockPrice(stockID) {
    socket.send(JSON.stringify({
        'stockIDS': stockID
    }));
}

const socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/return-stock-data/'
);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data);

    const stockID = data['stock_id'];
    const stockPrice = data['price'];

    // update the price
    const pricingElements = document.getElementsByName(stockID + '-buy-price');

    for (let i = 0; i < pricingElements.length; i++) {
        console.log(pricingElements[i]);
        pricingElements[i].innerHTML = '£' + stockPrice;
    }
};

// trigger a function when the socket is opened
socket.onopen = function() {
    console.log('Socket opened');
    // get all the stock ids
    const stockIDS = getAllStockIDs();
    // send the stock ids to the server
    getAllStockPrice(stockIDS);
}

socket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};
