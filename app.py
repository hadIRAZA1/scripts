from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/run-script')
def run_script():
    script_type = request.args.get('type')
    script_map = {
        'student_spellingbee': 'stdspellingbee.py',
        'teacher_spellingbee': 'spellingbee.py',
        'student_activepassive': 't_activepassive.py',
        'teacher_activepassive': 'activepassive.py',
        'student_currency': 'c.py',
        'teacher_currency': 'currency.py',
        'student_imagedescribe': 'id.py',
        'teacher_imagedescribe': 'imagedescribe.py',
        'student_readrespond': 'rr.py',
        'teacher_readrespond': 'Readrespond.py',
        'student_science': 'sci.py',
        'teacher_science': 'science.py',
        'student_storygen': 'storygenstd.py',
        'teacher_storygen': 'storygen.py',
    }
    script = script_map.get(script_type)
    if not script:
        return jsonify({'message': 'Invalid script type'}), 400
    try:
        subprocess.Popen(['python', script])
        return jsonify({'message': f'Running {script}...'})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    try:
        open('automation_logs.json', 'w').close()
        return jsonify({'message': 'Logs cleared successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000)