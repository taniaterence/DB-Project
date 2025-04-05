 // Function to fetch data based on selected table
const fetchTableData = async (tableName) => {
    try {
        const response = await fetch(`/data?table=${tableName}`);
        const data = await response.json();

        // Clear any previous data in the table
        const tableBody = document.querySelector("#table-contents tbody");
        tableBody.innerHTML = '';
        
        // Dynamically create table headers (assuming all rows have the same structure)
        const tableHeaders = Object.keys(data[0]);
        const tableHeaderRow = document.querySelector("#table-contents thead tr");
        tableHeaderRow.innerHTML = '';  // Clear existing headers
        tableHeaders.forEach(header => {
            const th = document.createElement("th");
            th.textContent = header;
            tableHeaderRow.appendChild(th);
        });

        // Populate table rows
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

// Event listener for table selection
document.getElementById('table-selector').addEventListener('change', (event) => {
    const tableName = event.target.value;
    fetchTableData(tableName); // Fetch data for the selected table
});

