from flask import Flask, render_template, request, session
import pandas as pd
import numpy as np
import sys
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

GRAPH_VALUES = ['line', 'bar', 'scatter', 'histogram', 'summary_statistics']
GRAPH_NAMES = ['Line Plot', 'Bar Plot', 'Scatter Plot', 'Histogram', 'Summary Statistics']

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
    def caluculate_histogram(data, keys, bins):
        """
        Caluculate histogram data.
        """
        histogram_min, histogram_max = (min([min(data[key]) for key in keys]), max([max(data[key]) for key in keys]))
        margin = (histogram_max - histogram_min) * 0.01     # 1% margin (tentaive)
        histogram_min = histogram_min - margin
        histogram_max = histogram_max + margin
        x_axis = list(np.linspace(histogram_min, histogram_max, int(bins)+1))
        histogram = {key: pd.cut(data[key], bins=x_axis).value_counts().sort_index().tolist() for key in keys}
        
        return x_axis, histogram
    
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
            status['histogram']['checked'][df.columns[0]] = 'checked'
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
                keys = request.form.getlist('histogram_items')
                #items = {key: data[key] for key in keys}
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
            elif (graph_type == 'histogram'):
                # --- histogram ---
                data = session['data']
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
            else:
                # --- summary statistics ---
                data = session['data']
                
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
            
        else:
            # --- no processes ---
            pass
        
        return render_template('index.html', data=data, params=params, status=status)
    return render_template('index.html', status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
