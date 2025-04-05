 // ==========================
// SHOW TABLE FUNCTIONALITY
// ==========================

// Fetch and display data from the selected table
const fetchTableData = async (tableName) => {
    try {
        // Make a GET request to the backend with table name as query param
        const response = await fetch(`/data?table=${tableName}`);
        const data = await response.json();

        // Clear any previous table contents
        const tableBody = document.querySelector("#table-contents tbody");
        tableBody.innerHTML = '';

        // Get the column names (keys of the first row)
        const tableHeaders = Object.keys(data[0]);
        const tableHeaderRow = document.querySelector("#table-contents thead tr");
        tableHeaderRow.innerHTML = '';

        // Create table headers
        tableHeaders.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            tableHeaderRow.appendChild(th);
        });

        // Create table rows from the data
        data.forEach(row => {
            const tr = document.createElement("tr");
            tableHeaders.forEach(header => {
                const td = document.createElement("td");
                td.textContent = row[header];
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });

    } catch (error) {
        console.error("Error fetching data:", error);
    }
};

// Add click event to "Show Table" button
document.querySelectorAll("button")[0].addEventListener("click", () => {
    const tableName = document.getElementById("table").value;
    if (tableName) {
        fetchTableData(tableName);  // Load and display table
    } else {
        alert("Please select a table.");  // Error message for empty selection
    }
});



// ADD SUPPLIER FUNCTIONALITY


// Add click event to "Add Supplier" button
document.querySelectorAll("button")[1].addEventListener("click", async () => {
    const supplierName = document.getElementById("supplier").value.trim();

    if (!supplierName) {
        alert("Please enter a supplier name.");
        return;
    }

    try {
        // Send POST request to server to add the new supplier
        const response = await fetch("/add-supplier", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name: supplierName })
        });

        const result = await response.json();

        if (response.ok) {
            alert("Supplier added successfully!");
        } else {
            alert("Failed to add supplier: " + result.message);
        }

    } catch (error) {
        console.error("Error adding supplier:", error);
        alert("An error occurred while adding the supplier.");
    }
});



// ANNUAL EXPENSES FOR PARTS FUNCTIONALITY


// Create and append a "Calculate Expenses" button dynamically
const expensesButton = document.createElement("button");
expensesButton.textContent = "Calculate Expenses";
document.getElementById("end-year").parentNode.appendChild(expensesButton);

// Add click event to "Calculate Expenses" button
expensesButton.addEventListener("click", async () => {
    const start = document.getElementById("start-year").value.trim();
    const end = document.getElementById("end-year").value.trim();

    if (!start || !end) {
        alert("Please enter both start and end year.");
        return;
    }

    try {
        // Fetch expense data between the given years
        const response = await fetch(`/expenses?start=${start}&end=${end}`);
        const data = await response.json();

        if (!response.ok) {
            alert("Error: " + data.message);
            return;
        }

        // Build and display expense results
        let output = "Annual Expenses:\n";
        for (const year in data) {
            output += `${year}: $${data[year]}\n`;
        }
        alert(output);

    } catch (error) {
        console.error("Error fetching expenses:", error);
        alert("An error occurred while fetching expenses.");
    }
});



// BUDGET PROJECTION FUNCTIONALITY

// Create and append a "Project Budget" button dynamically
const projectionButton = document.createElement("button");
projectionButton.textContent = "Project Budget";
document.getElementById("inflation-rate").parentNode.appendChild(projectionButton);

// Add click event to "Project Budget" button
projectionButton.addEventListener("click", async () => {
    const years = parseInt(document.getElementById("num-years").value.trim());
    const rate = parseFloat(document.getElementById("inflation-rate").value.trim());

    if (isNaN(years) || isNaN(rate)) {
        alert("Please enter valid numbers for years and inflation rate.");
        return;
    }

    try {
        // Fetch budget projection based on years and inflation rate
        const response = await fetch(`/budget-projection?years=${years}&rate=${rate}`);
        const data = await response.json();

        if (!response.ok) {
            alert("Error: " + data.message);
            return;
        }

        // Build and show projection results
        let output = "Budget Projection:\n";
        for (const year in data) {
            output += `${year}: $${data[year].toFixed(2)}\n`;
        }
        alert(output);

    } catch (error) {
        console.error("Error calculating projection:", error);
        alert("An error occurred while calculating budget projection.");
    }
});
