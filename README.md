# Predictive Prefetching using HTTP 2.0 and Machine Learning

This project predicts the next page a user will visit based on his behaviour on the website and prefetch its resources to improve page load time.

## Overview

1. Collect and represent user navigation data.
2. Train an LSTM model to predict the next page.
3. Serve the site through a Python backend.
4. Use predictions to prefetch the most likely next page and its assets.

## Setup
```bash

1. Install dependencies
pip install -r requirements.txt

2. Training the model
(The repository does not include the trained model file.)
cd backend
python train_model.py
(This will create a model.h5 and label_mapping.json)

3. Running the backend
cd backend
python app.py
Then open: http://localhost:5000
(This will open the demo store page)
```

### Run with HTTP/2.0 using Hypercorn
```bash
Steps:
1. Generate a self-signed certificate (for local testing)
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365

2. Start the Flask app using Hypercorn with HTTP/2.0
cd backend
hypercorn app:app --bind 0.0.0.0:8443 --certfile cert.pem --keyfile key.pem --alpn h2
Then open:
https://localhost:8443
```

## Workflow
The browser sends events to /api/event <br>
The backend logs navigation history <br>
'model.h5' returns predicted_pages and Link headers <br>
Client script adds prefetch hints based on these predictions <br>