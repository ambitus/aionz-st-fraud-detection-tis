#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash
import logging
from logging import Formatter, FileHandler
import json
import requests
from time import localtime, strftime
from flask_cors import CORS, cross_origin
import os
import config

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')


# Get TIS details from env vars
TIS_ENDPOINT = os.environ["TIS_ENDPOINT"]



prediction_detail_names = [
    'Prediction',
    'Deployment ID',
    'Time'
]

predictions = [
]


#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

@app.route('/')
def latest_predictions():
    return render_template('pages/placeholder.latest_predictions.html', predictions=predictions, colnames=prediction_detail_names)

@app.route('/prediction_details/<id>')
def prediction_details(id=None):
    PREDICTION_ID = id

    return render_template('pages/placeholder.prediction_details.html', predction_data=predictions[int(PREDICTION_ID)], feature_data=predictions[int(PREDICTION_ID)]['features'], colnames=prediction_detail_names)

@app.route('/make_prediction')
def make_prediction():
    return render_template('pages/placeholder.make_prediction.html')

@app.route('/run_AI', methods =["GET", "POST"])
def run_AI():
    transaction_data = ''
    prediction = ''
    prediction_result = None

    try:  
        if request.method == "POST":
            transaction_data = request.form["transaction_data"] 
            payload = json.loads(transaction_data)
          
        with open('temp.json', 'w') as f:
            json.dump([payload], f)
        with open('temp.json', 'r') as f:
            input_data = []
            features = ['User', 'Card', 'Year', 'Month', 'Day', 'Time', 'Amount', 'Use Chip', 'Merchant Name', 'Zip']
            for feature in features:
                input_data.append(payload[feature])
            triton_data = {"inputs":[{"name":"IN0","shape":[1,10],"datatype":"BYTES","data":[input_data]}],"outputs":[{"name":"OUT0"}]}

            r = requests.post(TIS_ENDPOINT, json=triton_data)
        
            # Currently only handling one prediction at a time
            prediction = json.loads(r.text)

            # View inferencing results
            print('prediction')
            print(prediction)

            if prediction['outputs'][0]['data'] == "1.0":
                # Fraud/default
                prediction_result = 'Fraud'
            else:
                # Not fraud/do not default
                prediction_result = 'Not fraud'
            
            deployment_id = TIS_ENDPOINT.split('/')[-2]
            current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

            print(payload)

            prediction = {
                'id': len(predictions),
                'Prediction': prediction_result,
                'Deployment ID': deployment_id,
                'Time': current_time,
                'features': {}
            }

            for feature in payload:
                prediction['features'][feature] = payload[feature]

            predictions.append(prediction)

    except Exception as e:
        print(e)
        flash('Something went wrong. Please check your input data.')

    return render_template('pages/placeholder.make_prediction.html', prediction=prediction_result)

@app.route('/fraud_detector', methods =["POST"])
@cross_origin()
def fraud_detector():
    transaction_data = ''
    prediction = ''
    prediction_result = ''

    try:
        if request.method == "POST":
            transaction_data = request.get_json()

            print('TRANSACTION DATA:')
            print(transaction_data)

            payload = transaction_data

            with open('temp.json', 'w') as f:
                json.dump([payload], f)
            with open('temp.json', 'r') as f:
                input_data = []
                features = ['User', 'Card', 'Year', 'Month', 'Day', 'Time', 'Amount', 'Use Chip', 'Merchant Name', 'Zip']
                for feature in features:
                    input_data.append(payload[feature])
                triton_data = {"inputs":[{"name":"IN0","shape":[1,10],"datatype":"BYTES","data":[input_data]}],"outputs":[{"name":"OUT0"}]}

                r = requests.post(TIS_ENDPOINT, json=triton_data)

                # Currently only handling one prediction at a time
                prediction = json.loads(r.text)

                # View inferencing results
                print('prediction')
                print(prediction)

                if prediction['outputs'][0]['data'] == "1.0":
                    # Fraud/default
                    prediction_result = 'Fraud'
                else:
                    # Not fraud/do not default
                    prediction_result = 'Not fraud'

                deployment_id = TIS_ENDPOINT.split('/')[-2]
                current_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

                print(payload)

                prediction = {
                    'id': len(predictions),
                    'Prediction': prediction_result,
                    'Deployment ID': deployment_id,
                    'Time': current_time,
                    'features': {}
                }

                for feature in payload:
                    prediction['features'][feature] = payload[feature]

                predictions.append(prediction)

    except Exception as e:
        print(e)
        print('Something went wrong. Please check your input data.')

    return {'prediction': prediction_result}


@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
