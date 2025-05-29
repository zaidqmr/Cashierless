from flask import Flask, render_template, request, jsonify, redirect
import base64
import os
from ultralytics import YOLO
from flask_cors import CORS
import cv2
import sys
from io import StringIO
from flask import send_from_directory

app = Flask(__name__)
CORS(app)
@app.route('/processed-image/<filename>')
def processed_image(filename):
    return send_from_directory('static/output', filename)


@app.route('/process-image', methods=['POST'])
def process_image():
    data = request.get_json()
    image_data = data['image']

    # Convert base64 image to bytes
    image_bytes = base64.b64decode(image_data.split(',')[1])

    # Save the image to a file
    image_path = os.path.join(app.static_folder,'uploads', 'processed_image.jpg')
    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    # Process the image further if needed
    # ...
        output=image_process()
    # Return the processed image URL
    processed_image_url = 'static\processed_image.jpg'
    return jsonify({'processed_image': processed_image_url,'output':output})
def image_process():
        # Save the uploaded image
        image_path = os.path.join('static', 'uploads', 'processed_image.jpg')

        # Load the input image
        frame = cv2.imread(image_path)
        H, W, _ = frame.shape

        # Create the output image with the same dimensions as the input image
        output_frame = frame.copy()

        model_path = os.path.join('.', 'runs', 'detect', 'train33', 'weights', 'last.pt')

        # Capture the model output
        output_buffer = StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer

        # Load a model
        model = YOLO(model_path)  # load a custom model

        threshold = 0.6

        class_name_dict = {0: 'kurkure', 1: 'parleg', 2: 'lays',3:'redbull'}

        results = model(frame)[0]
        output = []
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            output.append(int(result[5]))
            if score > threshold:
                cv2.rectangle(output_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
                cv2.putText(output_frame, class_name_dict[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)

        # Restore the standard output and retrieve the model output
        sys.stdout = old_stdout

        # Save the annotated image
        output_image_path = os.path.join('static','output','processed_image.jpg')
        cv2.imwrite(output_image_path, output_frame)
        return (output)


if __name__ == '__main__':
    app.run(debug=True)

