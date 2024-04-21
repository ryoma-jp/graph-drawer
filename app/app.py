from flask import Flask, render_template, request
import pandas as pd
import json
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    print(f'Request: {request.method}', file=sys.stderr)
    if request.method == 'POST':
        csv_file = request.files['file']
        graph_type = request.form.get('graph_type')
        print(f'{graph_type}, {csv_file}', file=sys.stderr)
        df = pd.read_csv(csv_file)
        data = {
            'x': df['x'].tolist(),
            'y': df['y'].tolist(),
            'graph_type': graph_type
        }
        data = json.dumps(data).replace("'", '"')
        print(f'{data}', file=sys.stderr)
        return render_template('index.html', data=data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
