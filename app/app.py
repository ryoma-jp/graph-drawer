from flask import Flask, render_template, request, session
import os
import pandas as pd
import numpy as np
import sys
import secrets
import pickle

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GRAPH_VALUES = ['line', 'bar', 'scatter', 'histogram', 'summary_statistics']
GRAPH_NAMES = ['Line Plot', 'Bar Plot', 'Scatter Plot', 'Histogram', 'Summary Statistics']
PICKLE_PATH = '/tmp/params.pkl'

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
            - 'csv_file': csv file.
            - 'status': Status of the application to keep the selected parameters.
    """
    def read_csv_file(csv_file):
        """
        Read csv file.
        """
        df = pd.read_csv(csv_file)
        data = {key: df[key].tolist() for key in df.columns}
        return data
    
    def caluculate_histogram(data, keys, bins):
        """
        Caluculate histogram data.
        """
        # --- caluculate histogram ---
        histogram_min, histogram_max = (min([min(data[key]) for key in keys]), max([max(data[key]) for key in keys]))
        margin = (histogram_max - histogram_min) * 0.01     # 1% margin (tentaive)
        histogram_min = histogram_min - margin
        histogram_max = histogram_max + margin
        x_axis = list(np.linspace(histogram_min, histogram_max, int(bins)+1))
        histogram = {key: pd.cut(data[key], bins=x_axis).value_counts().sort_index().tolist() for key in keys}
        
        return x_axis, histogram
    
    print(f'Request: {request}', file=sys.stderr)
    
    csv_file = None if 'csv_file' not in session else session['csv_file']
    data = None
    if (csv_file is not None):
        csv_file = session['csv_file']
        data = read_csv_file(csv_file)
    status = {
        'file': '',
    } if 'status' not in session else session['status']
    
    if request.method == 'POST':
        print(f'Request Form: {request.form}', file=sys.stderr)
        print(f'  - post_type: {request.form.get("post_type")}', file=sys.stderr)
        if (request.form.get('post_type') == 'Upload'):
            # --- load csv file ---
            file = request.files['file']
            csv_file = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(csv_file)
            session['csv_file'] = str(csv_file)
            data = read_csv_file(csv_file)
            
            # --- save status ---
            data_keys = list(data.keys())
            status['file'] = file.filename
            graph_selected = ['selected' if key=='line' else '' for key in GRAPH_VALUES]
            status['graph_type'] = list(zip(GRAPH_VALUES, GRAPH_NAMES, graph_selected))
            status['radio'] = {key: '' for key in data_keys}
            status['radio'][data_keys[0]] = 'checked'
            status['checkbox'] = {key: '' for key in data_keys}
            
            df_data = pd.DataFrame(data)
            histogram_checked = ['disabled' if dtype_object else 'checked' for dtype_object in df_data.dtypes=='object']
            status['histogram'] = {
                'checked': {key: value for key, value in zip(data_keys, histogram_checked)},
                'bins': '10',
            }
            
            print(f'type(session["csv_file"]) = {type(session["csv_file"])}', file=sys.stderr)
            print(f'type(status["file"]) = {type(status["file"])}', file=sys.stderr)
            print(f'status = {status}', file=sys.stderr)
            session['status'] = status

            # --- params ---
            params = {
                'graph_type': 'line',
                'x_axis': None,
                'y_axis': None,
            }
            with open(PICKLE_PATH, 'wb') as f:
                pickle.dump(params, f)
        elif (request.form.get('post_type') == 'Apply'):
            # --- load graph type ---
            graph_selected_index = [row[2] for row in status['graph_type']].index('selected')
            graph_type = status['graph_type'][graph_selected_index][0]
            
            if (graph_type in ['line', 'bar', 'scatter']):
                # --- set draw items ---
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
                print(f'type(status["file"]) = {type(status["file"])}', file=sys.stderr)
                print(f'status = {status}', file=sys.stderr)
                session['status'] = status
                
                params = {
                    'graph_type': graph_type,
                    'x_axis': x_axis,
                    'y_axis': y_axis,
                }
                print(f'params: {params}', file=sys.stderr)
                with open(PICKLE_PATH, 'wb') as f:
                    pickle.dump(params, f)
            else:
                # --- histogram ---
                keys = request.form.getlist('histogram_items')
                bins = request.form.get('histogram_bins') if request.form.get('histogram_bins')!='' else '10'
                
                # --- caluculate histogram ---
                x_axis, histogram = caluculate_histogram(data, keys, bins)
                print(f'x_axis = {x_axis}', file=sys.stderr)
                print(f'histogram = {histogram}', file=sys.stderr)
                
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
                    'x_axis': x_axis,
                    'histogram_items': histogram,
                    'histogram_bins': bins,
                }
                print(f'params: {params}', file=sys.stderr)
                with open(PICKLE_PATH, 'wb') as f:
                    pickle.dump(params, f)
                
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
                with open(PICKLE_PATH, 'wb') as f:
                    pickle.dump(params, f)
            elif (graph_type == 'histogram'):
                # --- histogram ---
                keys = list(data.keys())
                keys = [key for key in keys if status['histogram']['checked'][key]=='checked']
                bins = status['histogram']['bins']
                
                # --- caluculate histogram ---
                x_axis, histogram = caluculate_histogram(data, keys, bins)
                print(f'x_axis = {x_axis}', file=sys.stderr)
                print(f'histogram = {histogram}', file=sys.stderr)
                
                params = {
                    'graph_type': graph_type,
                    'x_axis': x_axis,
                    'histogram_items': histogram,
                    'histogram_bins': bins,
                }
                with open(PICKLE_PATH, 'wb') as f:
                    pickle.dump(params, f)
            else:
                # --- summary statistics ---
                summary = {}
                for key, value in data.items():
                    summary[key] = {
                        'count': len(value),
                        'min': min(value),
                        'max': max(value),
                        'mean': np.mean(value),
                        'median': np.median(value),
                        'std': np.std(value),
                        'iqr': np.percentile(value, 75) - np.percentile(value, 25),         # Interquartile Range
                        'ci_95': (np.percentile(value, 2.5), np.percentile(value, 97.5)),   # 95% Confidence Interval
                    }
                
                params = {
                    'graph_type': graph_type,
                    'summary': summary,
                }
                with open(PICKLE_PATH, 'wb') as f:
                    pickle.dump(params, f)
            
        else:
            # --- no processes ---
            pass
        
        params = None
        if (os.path.exists(PICKLE_PATH)):
            with open(PICKLE_PATH, 'rb') as f:
                params = pickle.load(f)
        print(f'params: {params}', file=sys.stderr)
        return render_template('index.html', data=data, params=params, status=status)
    return render_template('index.html', status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
