from flask import Flask, render_template, request, session
import pandas as pd
import json
import sys
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

@app.route('/', methods=['GET', 'POST'])
def home():
    print(f'Request: {request}', file=sys.stderr)
    
    data = None if 'data' not in session else session['data']
    params = None if 'params' not in session else session['params']
    
    if request.method == 'POST':
        print(f'Request Form: {request.form}', file=sys.stderr)
        print(f'  - post_type: {request.form.get("post_type")}', file=sys.stderr)
        if (request.form.get('post_type') == 'Upload'):
            if 'params' in session:
                del session['params']
                params = None
            
            csv_file = request.files['file']
            
            df = pd.read_csv(csv_file)
            data = {key: df[key].tolist() for key in df.columns}
            session['data'] = data
            print(f'{data}', file=sys.stderr)
            
        elif (request.form.get('post_type') == 'Apply'):
            graph_type = request.form.get('graph_type')
            
            params = {
                'graph_type': graph_type
            }
            session['params'] = params
        
        return render_template('index.html', data=data, params=params)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
