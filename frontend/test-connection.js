#!/usr/bin/env node

const fetch = require('node-fetch');

// URL to test connection
const url = process.env.API_URL || 'http://localhost:8000/health';

console.log(`Testing connection to: ${url}`);

fetch(url)
  .then(response => {
    console.log(`Status: ${response.status} ${response.statusText}`);
    return response.text();
  })
  .then(text => {
    console.log(`Response: ${text}`);
    console.log('\nConnection successful! ✅');
  })
  .catch(error => {
    console.error(`\nConnection failed: ${error.message} ❌`);
    console.error('\nPossible issues:');
    console.error('1. Backend server is not running');
    console.error('2. Incorrect port (check docker-compose.yml and run.sh)');
    console.error('3. Network issue or firewall blocking connection');
    console.error('\nSuggested solutions:');
    console.error('- Make sure backend is running: docker-compose logs backend');
    console.error('- Check the PORT environment variable in your .env file');
    console.error('- Try accessing http://localhost:8000/health in your browser');
  });
