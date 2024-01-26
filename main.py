from tensorflow import keras
from tensorflow.keras.preprocessing import image
from flask import Flask, request, jsonify
from google.cloud import storage
from io import BytesIO
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Define class names
class_names = ['Coelogyne', 'Cymbidium', 'Dendrobium', 'Phalaenopsis','Vanda']

def load_model_from_storage():
    # Create a client to interact with Google Cloud Storage
    storage_client = storage.Client()

    # Specify the details of your model in Google Cloud Storage
    bucket_name = 'orchid-azvaden'
    model_folder = 'mlModel'
    model_filename = 'mlModel.h5'

    # Download the model file from Google Cloud Storage to a local directory
    local_model_path = '/tmp/mlModel.h5'
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(os.path.join(model_folder, model_filename))
    blob.download_to_filename(local_model_path)

    # Load the H5 model using Keras
    loaded_model = keras.models.load_model(local_model_path)

    return loaded_model

# Load the model during the container startup
model1 = load_model_from_storage()

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'})

    image_file = request.files['image']

    try:
        img = image.load_img(BytesIO(image_file.read()), target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array /= 255
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model1.predict(img_array, verbose=0)
        predicted_class = np.argmax(predictions[0])
        class_name = class_names[predicted_class]
        accuracy = "{:.2f}".format(predictions[0][predicted_class] * 100)

        return jsonify({'accuracy': str(accuracy),
                        'class_id': str(predicted_class),
                        'class': str(class_name)
                        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = int(os.environ.get('PORT', 8080)), debug=False, threaded=True)
