// readCSV.js
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

// Function to read CSV file and return data
async function readCSV(filePath) {
  const data = [];
  return new Promise((resolve, reject) => {
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        data.push(row);
      })
      .on('end', () => {
        resolve(data);
      })
      .on('error', (err) => {
        reject(err);
      });
  });
}

// Function to load test data (process the CSV data)
async function loadTestData() {
  const filePath = path.join(__dirname, 'testingSample.csv');  // Modify this with your CSV file path
  const csvData = await readCSV(filePath);
  
  return csvData;  // Return the parsed CSV data
}

module.exports = { loadTestData };  // Export the function
