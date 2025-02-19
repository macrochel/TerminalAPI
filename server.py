from flask import Flask, request, jsonify, send_from_directory
from subprocess import PIPE, run
from PIL import Image
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_adb():
    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    try:
        result = run('{command}'.format(command=command), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return jsonify({'output': result.stdout}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/check', methods=['POST'])
def check_img():
    image_path = request.json.get('image_path')
    if not image_path:
        return jsonify({'error': 'No image_path provided'}), 400
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        common_color = most_common_used_color(img)
        return jsonify({'output': common_color}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/images/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'images'), filename)

@app.route('/clean_images', methods=['GET'])
def clean_images():
    try:
        cutoff_date_str = request.args.get('cutoff_date')
        if not cutoff_date_str:
            return jsonify({'error': 'cutoff_date query parameter is required'}), 400
        try:
            cutoff_date = datetime.strptime(cutoff_date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        images_directory = os.path.join(app.root_path, 'images')
        deleted_files = []
        for filename in os.listdir(images_directory):
            file_path = os.path.join(images_directory, filename)
            if os.path.isfile(file_path):
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mod_time < cutoff_date:
                    os.remove(file_path)
                    deleted_files.append(filename)
        return jsonify({
            'message': 'Images cleaned successfully',
            'deleted_files': deleted_files
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def most_common_used_color(img):
    width, height = img.size
    r_total = 0
    g_total = 0
    b_total = 0
    count = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = img.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1
    return (r_total/count, g_total/count, b_total/count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3440)