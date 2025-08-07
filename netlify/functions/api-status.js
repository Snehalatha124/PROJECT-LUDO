const axios = require('axios');

exports.handler = async function(event, context) {
  try {
    // Check backend status
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'https://project-ludo.onrender.com';
    
    const response = await axios.get(`${backendUrl}/api/status`, {
      timeout: 5000
    });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      body: JSON.stringify({
        status: 'success',
        backend: 'connected',
        timestamp: new Date().toISOString(),
        backendUrl: backendUrl
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type'
      },
      body: JSON.stringify({
        status: 'error',
        backend: 'disconnected',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};
