function exportToHtml(data, filename = 'table_data.html') {
    // Create an HTML table
    let html = '<table border="1"><thead><tr>';

    // Add column headers
    const headers = Object.keys(data[0]);
    headers.forEach(header => {
        html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Add rows
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(header => {
            html += `<td>${row[header]}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    // Download the file
    download(filename, html, 'text/html');
}

function exportToDoc(data, filename = 'table_data.doc') {
    // Create an HTML table
    let html = '<table border="1"><thead><tr>';

    // Add column headers
    const headers = Object.keys(data[0]);
    headers.forEach(header => {
        html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Add rows
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(header => {
            html += `<td>${row[header]}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    // Download the file
    download(filename, html, 'text/html');
}


function exportToPDF(data, filename = 'table_data.pdf') {
  const doc = new jspdf.jsPDF('p', 'pt', 'a4', true); // 'p' for portrait mode, you can change to 'l' for landscape

// Check if there is data to export
if (!Array.isArray(data) || data.length === 0) {
    console.error("No data available for export");
    return;
}

// Prepare data for vertical display
let body = [];
data.forEach((row, index) => {
    body.push([`Record ${index + 1}`]);
    Object.entries(row).forEach(([key, value]) => {
        body.push([key, value]);
    });
    body.push(['']); // Adding a blank line after each record
});

// AutoTable options can be used to customize the look and feel
doc.autoTable({
    head: [['Key', 'Value']],
    body: body,
    theme: 'grid',
    tableWidth: 'wrap',  // 'wrap' or a number
    columnStyles: {
        0: {cellWidth: 'auto'}, // Adjust as needed
        1: {cellWidth: 'auto'}  // Adjust as needed
    },
    didDrawPage: function (data) {
        // Page number footer
        doc.text("Page " + doc.internal.getNumberOfPages(), data.settings.margin.left, doc.internal.pageSize.height - 10);
    }
});

// Save the PDF
doc.save(filename);
}


// create PPT

function exportToPPT(data, filename = 'table_data.pptx') {
    let pptx = new PptxGenJS();
    let slide = pptx.addSlide();

    // Create data for the table
    let pptTableData = [];
    
    // Add column headers
    const headers = Object.keys(data[0]);
    pptTableData.push(headers);

    // Add rows
    data.forEach(row => {
        let rowData = headers.map(header => row[header] || '');
        pptTableData.push(rowData);
    });

    // Define table properties
    let pptTableOpts = {
        x: 0.5, y: 0.5, w: 9.0, h: 6.0,
        colW: headers.map(() => 2.0), // Adjust column width as needed
        border: { pt: '1', color: '000000' } // Border styling
    };

    // Add table to the slide
    slide.addTable(pptTableData, pptTableOpts);

    // Save the PPT
    pptx.writeFile({ fileName: filename });
}



// Usage example: exportHandsontableToPdf(myJsonData);

function download(filename, text, mimeType = 'text/plain') {
    var element = document.createElement('a');
    element.setAttribute('href', `data:${mimeType};charset=utf-8,` + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}

function exportJson(data) {
    try {
        // Convert the data object to a JSON string
        var jsonData = JSON.stringify(data, null, 2); // null, 2 for pretty printing
        downloadexportJson("exported_data.json", jsonData);
    } catch (e) {
        console.error("Error exporting JSON:", e);
        alert("An error occurred while exporting JSON.");
    }
}

function downloadexportJson(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}
