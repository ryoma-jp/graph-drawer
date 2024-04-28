from flask import Flask, render_template, request, session
import pandas as pd
import json
import sys
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

GRAPH_VALUES = ['line', 'bar', 'scatter', 'histogram']
GRAPH_NAMES = ['Line Plot', 'Bar Plot', 'Scatter Plot', 'Histogram']

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Top page of the application.
    
    Specification:
        - Forms:
            - 'post_type'
                - Upload: Upload a csv file.
                - Apply: Apply the graph type and axis.
            - 'graph_type':
                - Selected graph type.
        - Sessions:
            - 'data': Data of the csv file.
            - 'params': Parameters of the graph.
            - 'status': Status of the application to keep the selected parameters.
    """
    print(f'Request: {request}', file=sys.stderr)
    
    data = None if 'data' not in session else session['data']
    params = None if 'params' not in session else session['params']
    status = {
        'file': '',
    } if 'status' not in session else session['status']
    
    if request.method == 'POST':
        print(f'Request Form: {request.form}', file=sys.stderr)
        print(f'  - post_type: {request.form.get("post_type")}', file=sys.stderr)
        if (request.form.get('post_type') == 'Upload'):
            # --- Initialize parameters ---
            if 'params' in session:
                del session['params']
                params = None
            
            # --- load csv file ---
            csv_file = request.files['file']
            
            df = pd.read_csv(csv_file)
            data = {key: df[key].tolist() for key in df.columns}
            session['data'] = data
            print(f'data = {data}', file=sys.stderr)
            
            # --- save status ---
            status['file'] = csv_file.filename
            graph_selected = ['selected' if key=='line' else '' for key in GRAPH_VALUES]
            status['graph_type'] = list(zip(GRAPH_VALUES, GRAPH_NAMES, graph_selected))
            status['radio'] = {key: '' for key in df.columns}
            status['radio'][df.columns[0]] = 'checked'
            status['checkbox'] = {key: '' for key in df.columns}
            status['histogram'] = {
                'checked': {key: '' for key in df.columns},
                'bins': '10',
            }
            print(f'status = {status}', file=sys.stderr)
            session['status'] = status

            # --- params ---
            params = {
                'graph_type': 'line',
                'x_axis': None,
                'y_axis': None,
            }
        elif (request.form.get('post_type') == 'Apply'):
            # --- load graph type ---
            graph_selected_index = [row[2] for row in status['graph_type']].index('selected')
            graph_type = status['graph_type'][graph_selected_index][0]
            
            if (graph_type in ['line', 'bar', 'scatter']):
                # --- set draw items ---
                data = session['data']
                x_axis_key = request.form.get('x_axis')
                x_axis = data[x_axis_key]
                y_axis_keys = request.form.getlist('y_axis')
                y_axis = {key: data[key] for key in y_axis_keys}
                
                # --- update status ---
                status = session['status']
                status['radio'] = {key: '' for key in data.keys()}
                status['radio'][x_axis_key] = 'checked'
                status['checkbox'] = {key: '' for key in data.keys()}
                for key in y_axis_keys:
                    status['checkbox'][key] = 'checked'
                print(f'status = {status}', file=sys.stderr)
                session['status'] = status
                
                params = {
                    'graph_type': graph_type,
                    'x_axis': x_axis,
                    'y_axis': y_axis,
                }
                print(f'params: {params}', file=sys.stderr)
                session['params'] = params
            else:
                # --- histogram ---
                data = session['data']
                keys = request.form.getlist('keys')
                items = {key: data[key] for key in keys}
                bins = request.form.get('bins')
                
                # --- update status ---
                status = session['status']
                status['histogram']['checked'] = {key: '' for key in data.keys()}
                for key in keys:
                    status['histogram']['checked'][key] = 'checked'
                status['histogram']['bins'] = bins
                print(f'status = {status}', file=sys.stderr)
                session['status'] = status
                
                params = {
                    'graph_type': graph_type,
                    'histogram_items': items,
                    'histogram_bins': bins,
                }
                print(f'params: {params}', file=sys.stderr)
                session['params'] = params
                
        elif ('graph_type' in request.form):
            graph_type = request.form.get('graph_type')
            graph_selected = ['selected' if key==graph_type else '' for key in GRAPH_VALUES]
            status['graph_type'] = list(zip(GRAPH_VALUES, GRAPH_NAMES, graph_selected))
            print(f'status = {status}', file=sys.stderr)
            session['status'] = status
            
            if (graph_type in ['line', 'bar', 'scatter']):
                keys = list(data.keys())
                x_axis_key = [key for key in keys if status['radio'][key]=='checked'][0]
                x_axis = data[x_axis_key]
                y_axis_keys = [key for key in keys if status['checkbox'][key]=='checked']
                y_axis = {key: data[key] for key in y_axis_keys}
                
                params = {
                    'graph_type': graph_type,
                    'x_axis': x_axis,
                    'y_axis': y_axis,
                }
            else:
                # --- histogram ---
                keys = list(data.keys())
                keys = [key for key in keys if status['histogram']['checked'][key]=='checked']
                items = {key: data[key] for key in keys}
                bins = status['histogram']['bins']
                
                params = {
                    'graph_type': graph_type,
                    'histogram_items': items,
                    'histogram_bins': bins,
                }
            
        else:
            # --- no processes ---
            pass
        
        return render_template('index.html', data=data, params=params, status=status)
    return render_template('index.html', status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
