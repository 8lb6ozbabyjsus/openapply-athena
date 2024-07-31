const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 5001;

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// API routes
app.get('/api', (req, res) => {
  res.json({ message: 'Hello from server!' });
});

// All other requests to serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
