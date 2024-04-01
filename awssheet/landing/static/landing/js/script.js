/**
 * Exports data to HTML format and triggers download.
 */
function exportToHtml(data, filename = 'table_data.html') {
    let html = '<table border="1"><thead><tr>';

    // Generate table headers
    const headers = Object.keys(data[0]);
    headers.forEach(header => html += `<th>${header}</th>`);
    html += '</tr></thead><tbody>';

    // Generate table rows
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(header => html += `<td>${row[header]}</td>`);
        html += '</tr>';
    });
    html += '</tbody></table>';

    // Trigger download
    download(filename, html, 'text/html');
}

/**
 * Exports data to a DOC format and triggers download.
 */
function exportToDoc(data, filename = 'table_data.doc') {
    exportToHtml(data, filename); // Reuse HTML export function for DOC
}

/**
 * Exports data to a PDF format and triggers download.
 */
function exportToPDF(data, filename = 'table_data.pdf') {
    if (!Array.isArray(data) || data.length === 0) {
        console.error("No data available for export");
        return;
    }

    const doc = new jspdf.jsPDF('p', 'pt', 'a4', true);
    let body = [];
    
    // Prepare data for vertical display
    data.forEach((row, index) => {
        body.push([`Record ${index + 1}`]);
        Object.entries(row).forEach(([key, value]) => {
            body.push([key, value]);
        });
        body.push(['']); // Blank line for separation
    });

    // Configure AutoTable
    doc.autoTable({
        head: [['Key', 'Value']],
        body: body,
        theme: 'grid',
        tableWidth: 'wrap',
        columnStyles: { 0: {cellWidth: 'auto'}, 1: {cellWidth: 'auto'} },
        didDrawPage: data => doc.text("Page " + doc.internal.getNumberOfPages(), data.settings.margin.left, doc.internal.pageSize.height - 10)
    });

    // Trigger download
    doc.save(filename);
}

/**
 * Exports data to a PPTX format and triggers download.
 */
function exportToPPT(data, filename = 'table_data.pptx') {
    let pptx = new PptxGenJS();
    let slide = pptx.addSlide();
    let pptTableData = [Object.keys(data[0])]; // Add column headers

    // Generate table data
    data.forEach(row => pptTableData.push(Object.keys(data[0]).map(header => row[header] || '')));

    // Configure table properties and add to slide
    let pptTableOpts = { x: 0.5, y: 0.5, w: 9.0, h: 6.0, colW: pptTableData[0].map(() => 2.0), border: { pt: '1', color: '000000' } };
    slide.addTable(pptTableData, pptTableOpts);

    // Trigger download
    pptx.writeFile({ fileName: filename });
}

/**
 * Generic download function for text-based data.
 */
function download(filename, text, mimeType = 'text/plain') {
    var element = document.createElement('a');
    element.setAttribute('href', `data:${mimeType};charset=utf-8,` + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/**
 * Exports data to JSON format and triggers download.
 */
function exportJson(data) {
    try {
        var jsonData = JSON.stringify(data, null, 2); // Pretty print JSON
        downloadexportJson("exported_data.json", jsonData);
    } catch (e) {
        console.error("Error exporting JSON:", e);
        alert("An error occurred while exporting JSON.");
    }
}

/**
 * Wrapper function to download JSON data.
 */
function downloadexportJson(filename, text) {
    download(filename, text, 'application/json');
}


function removeActionsPrefix(inputString) {
    // Check if the inputString starts with "actions:"
    if (inputString.startsWith("actions:")) {
      // Remove the "actions:" prefix and return the remaining string
      return inputString.substring("actions:".length);
    } else {
      // If the inputString doesn't start with "actions:", return it as is
      return inputString;
    }
}

  function convertSelectedDataToJSON(selectedData) {
    // Check if selectedData is an array
    if (!Array.isArray(selectedData)) {
        return null;
    }

    // Extract headers from the first array in selectedData
    const keys = selectedData[0];

    // Convert selectedData to JSON
    const jsonData = selectedData.slice(1).map(rowData => {
        const jsonRow = {};
        keys.forEach((key, index) => {
            jsonRow[key] = rowData[index];
        });
        return jsonRow;
    });

    return JSON.stringify(jsonData, null, 2);
}

function postData(url, data, action, successCallback) { // Add successCallback parameter
    console.log("POST URL", url);
    console.log("POST DATA", data);
    return $.ajax({
      url: url,
      type: action,
      data: data,
      headers: { 'X-CSRFToken': '{{ csrf_token }}' },
      success: function (response) {
        console.log("POST SUCCESS", response);
        if (response.status === 'success') {
          console.log("POST SUCCESS", response);

          // Check if you want to navigate to the dynamic_form.html page
          if (response.redirect_to_dynamic_form) {
            console.log("Redirect");
            console.log(response.template_file);
            uniqueKey=response.unique_key;
            
            // Append the unique key as a query parameter to the URL
            var urlWithKey = response.template_file + '?unique_key=' + encodeURIComponent(uniqueKey);
            // window.location.href = urlWithKey;
            var popupWindow = window.open(urlWithKey, 'PopUpWindow', 'height=600,width=800,left=100,top=100,resizable=yes,scrollbars=yes,toolbar=yes,menubar=no,location=no,directories=no,status=yes');
          } else {
            // Update Handsontable data
            loadDataIntoHandsontable(response.json_data);
          }
          // Pass the HTML content to the success callback
          if (successCallback) {
            successCallback(response.post_success_response);
          }
        } else {
          
          console.log("POST DATA ERROR-1", response.responseText, status, response.message);
          alert(response.message); // Handle error
        }
      },
      error: function (request, status, error) {
        console.log("Error Status", status);
        console.log("POST DATA ERROR", request.responseText, status, error);

        // Display the entire responseText as an error message
        alert("An error occurred: " + request.responseText);
      }
    });
  }



  function postDataToGetFile(url, data, action, successCallback) {
    console.log("POST URL", url);
    console.log("POST DATA", data);
    return $.ajax({
        url: url,
        type: action,
        data: data,
        xhrFields: {
            responseType: 'blob' // to handle the binary data
        },
        headers: { 'X-CSRFToken': '{{ csrf_token }}' },
        success: function (response, status, xhr) {
            var contentType = xhr.getResponseHeader("content-type") || "";

            if (contentType.indexOf('application/zip') !== -1) {
                // Assuming it's a file download (zip file)
                var blob = new Blob([response], { type: 'application/zip' });
                var downloadUrl = URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.href = downloadUrl;
                a.download = "downloaded_file.zip"; // Name the download
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                a.remove();
            } else {
                // Handle other responses (assuming JSON)
                console.log("POST SUCCESS", response);
                if (response.status === 'success') {
                    console.log("POST SUCCESS", response);
                    // Add other response handling logic here...

                    // Pass the HTML content to the success callback
                    if (successCallback) {
                        successCallback(response.post_success_response);
                    }
                } else {
                    console.log("POST DATA ERROR", response.responseText, status, response.message);
                    alert(response.message); // Handle error
                }
            }
        },
        error: function (request, status, error) {
            console.log("Error Status", status);
            console.log("POST DATA ERROR", request.responseText, status, error);
            alert("An error occurred: " + request.responseText);
        }
    });
}

function loadDataIntoHandsontable(jsonData) {
    console.log("JSONDATA",jsonData);
    try {
      var data = JSON.parse(jsonData);

      if (!Array.isArray(data)) {
          console.error("Data is not an array for Handsontable");
          return;
      }
      if (data.length === 0) {
          console.warn("Empty data array for Handsontable");
          hotInstance.loadData([]); // Load empty data if the array is empty
          return;
      }
      

      if (hotInstance) {
          // Extract column headers from the first object's keys
          console.log("first");
          var columnHeaders = Object.keys(data[0]);
          console.log("Second");

          // Function to transform each row's data (handle nested objects)
          var transformRowData = (row) => {
              return columnHeaders.reduce((transformedRow, header) => {
                  var cellValue = row[header];
                  if (cellValue && typeof cellValue === 'object') {
                      // Convert object to string or other representation
                      transformedRow[header] = JSON.stringify(cellValue);
                  } else {
                      transformedRow[header] = cellValue;
                  }
                  return transformedRow;
              }, {});
          };

          // Transform each row's data
          var transformedData = data.map(transformRowData);

          // Update Handsontable settings with new data and columns
          hotInstance.updateSettings({
              data: transformedData,
              columns: columnHeaders.map(header => ({ data: header, title: header })),
              colHeaders: columnHeaders
          });
      } else {
          console.error("Handsontable instance is not defined");
      }
  } catch (e) {
      console.error("Error parsing JSON data:", e);
  }
}




function filterList() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('searchBox');
    filter = input.value.toUpperCase();
    ul = document.getElementById('dataList');
    li = ul.getElementsByTagName('li');

    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}