//Steven Toub
//CS530-900
//Semester Project

//populates the listing of engines
function updateEnginesListing(retrievedData,tableString){

    var uniqueEngines = new Array();
    var engineItemTally = new Array();
    var overdueItemTally = new Array();
    var todaysDate = new Date();

    //populate uniqueEngines for purposes of tallying item counts
    for(var i = 0; i < retrievedData.length; i++){

        var item = retrievedData[i];

        if(!(uniqueEngines.includes(item.eid))){

            uniqueEngines.push(item.eid);
        }
    }

    //tallys item counts
    for(var a = 0; a < retrievedData.length; a++){

        var item = retrievedData[a];
        var eid = item.eid;

        eidIndex = uniqueEngines.indexOf(eid);

        if(engineItemTally[eidIndex] == null) {

            engineItemTally[eidIndex] = 0;
        
            if(item.date != "0"){

                engineItemTally[eidIndex] = (engineItemTally[eidIndex] + 1);
            }
        }

        else if(item.date != "0") {
            engineItemTally[eidIndex] = (engineItemTally[eidIndex] + 1);
        }
    }

    //tallys numbers of overdue items
    for(var c = 0; c < retrievedData.length; c++){

        var item = retrievedData[c];
        var eid = item.eid;

        overdueIndex = uniqueEngines.indexOf(eid);

        var dateString = item.date;

        if(dateString != "0") {

            var itemDate = new Date(dateString);

            if(overdueItemTally[overdueIndex] == null && itemDate < todaysDate){

                overdueItemTally[overdueIndex] = 1;
            }
            else if(overdueItemTally[overdueIndex] != null && itemDate < todaysDate){

                overdueItemTally[overdueIndex] = (overdueItemTally[overdueIndex] + 1);
            }   

            else if(overdueItemTally[overdueIndex] == null && itemDate >= todaysDate){

                overdueItemTally[overdueIndex] = 0;
            }
        }
    }

    //populates table rows.
    for(var b = 0; b < uniqueEngines.length; b++){

        if(overdueItemTally[b] == null){

            overdueItemTally[b] = 0;
        }

        const tableRow = $(`<tr class="engine-row"><td>${uniqueEngines[b]}</td><td>${engineItemTally[b]}</td><td>${overdueItemTally[b]}</td></tr>`);

        $(tableString).append(tableRow);
    }
}

//removes an engine and all its items from the database
function deleteEngine(eid) {
            $.get("api/deleteEngine", {
                eid: eid
            });
}

//updates inventory tables for a specific engine
function updateInventory(engineIndex,tableString){

    $(function() {

        $.get("/api/engines", function(retrievedData) {

            updateEngineInventory(retrievedData);
        });
    });

    function updateEngineInventory(retrievedData) {

        for(z = 0; z < retrievedData.length; z++){

            var item = retrievedData[z];

                if(item.eid == engineIndex && item.date != "0"){

                    const tableRow = $(`<tr class="item-row"><td>${item.name}</td><td>${item.date}</td><td>${item.status}</td><td>${item.quantity}</td></tr>`);
                
                    $(tableString).append(tableRow);
                }
        }
    }
}

//adds an item to the engines table in the database
function addItem(eid,name,date,status,quantity) {
    $.get("api/add", {
        eid: eid,
        name: name,
        date: date,
        status: status,
        quantity: quantity
    });
}

//removes an item from the engines table in the database
function delItem(eid,name,date,status,quantity) {
    $.get("api/deleteItem", {
        eid: eid,
        name: name,
        date: date,
        status: status,
        quantity: quantity
    });
}

//modifies an item in the engines table in the database
function modifyItem(eid,name,date,status,quantity,eidOld,nameOld,dateOld,statusOld,quantityOld){
    $.get("api/modifyItem", {
        eid: eid,
        name: name,
        date: date,
        status: status,
        quantity: quantity,
        eidOld: eidOld,
        nameOld: nameOld,
        dateOld: dateOld,
        statusOld: statusOld,
        quantityOld: quantityOld
    });
}

function deleteItem(eid,name,date,status,quantity){
    $.get("api/deleteItem", {
        eid: eid,
        name: name,
        date: date,
        status: status,
        quantity: quantity
    });
}

//populates a table with the access data from the access table in the database, and makes it readable
function updateAccess(retrievedData, tableString) {

    for(d = 0; d < retrievedData.length; d++){

        var item = retrievedData[d];

        if(item.action == 'added item'){

            itemSplit = item.item.split('=');

            actionString =  "Added " + itemSplit[1] + " onto Engine " + itemSplit[0];
    
            const tableRow = $(`<tr class="item-row"><td>${item.date}</td><td>${item.name}</td><td>${actionString}</td></tr>`);
                    
            $(tableString).append(tableRow);
        }

        else if(item.action == 'added engine'){

            itemSplit = item.item.split('=');

            actionString = "Created Engine " + itemSplit[0];

            const tableRow = $(`<tr class="item-row"><td>${item.date}</td><td>${item.name}</td><td>${actionString}</td></tr>`);
                    
            $(tableString).append(tableRow);
        }

        else if(item.action == 'modified item'){

            itemSplit = item.item.split('+');
            strNew = itemSplit[0].split('=');
            strOld = itemSplit[1].split("=");

            actionString = "Modified " + strOld[1] + " on Engine " + strOld[0];

            const tableRow = $(`<tr class="item-row"><td>${item.date}</td><td>${item.name}</td><td>${actionString}</td></tr>`);
                    
            $(tableString).append(tableRow);
        }

        else if(item.action == 'deleted item'){

            itemSplit = item.item.split('=');

            actionString =  "Deleted " + itemSplit[1] + " from Engine " + itemSplit[0];

            const tableRow = $(`<tr class="item-row"><td>${item.date}</td><td>${item.name}</td><td>${actionString}</td></tr>`);
                    
            $(tableString).append(tableRow);
        }

        //deleted engine
        else{

            actionString = "Deleted Engine " + item.item;

            const tableRow = $(`<tr class="item-row"><td>${item.date}</td><td>${item.name}</td><td>${actionString}</td></tr>`);
                    
            $(tableString).append(tableRow);
        }

    }
}
