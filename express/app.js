const express = require('express');
const http = require('http');

const app = express();
const flaskUrl = `http://${process.env.FLASK_SERVICE}`;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/proxy', (req, res) => {
  http.get(`${flaskUrl}/fibo/10`, (result) => {
    let data = '';
    result.on('data', (d) => {
      data += d;
    });
    result.on('end', () => {
      res.send(data);
    });
  });
});

module.exports = app;
