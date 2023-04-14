from viz import calculate_segments_straight_up, calculate_segments_angles, calculate_shortest_distance
from app_background import get_processinfo, prep_segments_to_display
import plotly.graph_objs as go
import dash
from preprocess import preprocess
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

ats, infoinggroups=preprocess() # sets window size, directory, and which outlier function to take

app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
load_figure_template('LUX')

timestamps = []
sensorids = []

total_sum = 0
for sublist in range(len(ats)):
    total_sum += len(ats[sublist][2]) # this is for correctly numbering the ats on the legend

#this is the first trace 
first_line_x = ats[0][2][0]
first_line_y = ats[0][3][0]

#this is to keep track of already clicked points
segments_to_display_short = []
segments_to_display_angles = []
sec_segments_to_display_same = []


@app.callback(
    dash.dependencies.Output('line-graph3', 'figure'),
    [dash.dependencies.Input('line-graph3', 'clickData'),
     dash.dependencies.Input('scaling-factor3', 'value'),
     dash.dependencies.Input('spacing3', 'value')])

def update_line4(clickData, value, spacing3):
    try:
        if clickData:
            if len(segments_to_display_angles) > 0:
                for elem in segments_to_display_angles:
                    elem[0]['visible'] = False
            point = clickData['points'][0]
            x_val = point['x']
            distance = 0.1
            segments_to_display5, unedited2, indices_xval = calculate_segments_angles(ats, x_val, value, spacing3, distance)
            tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
            segments_to_display6 = prep_segments_to_display(segments_to_display5, unedited2, tstamps, sensids)
        else:
            segments_to_display6 = []
    except:
        segments_to_display6 = []

    return {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace 1', 'showlegend':True, 'visible': True},
            {'x' : ats[-1][2][-1], 'y' : ats[-1][3][-1], 'type': 'line', 'name': 'trace ' + str(total_sum), 'hoverinfo': 'none', 'showlegend':True, 'visible': True},
            {'x' : ats[-1][0][0], 'y' : ats[-1][1].ravel(), 'type': 'line', 'name': 'ats '+ str(len(ats)), 'hoverinfo': 'none', 'showlegend':True, 'visible': True, 'fill' : 'tonexty'},
            *segments_to_display6
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} }
    }

@app.callback(
    dash.dependencies.Output('line-graphx', 'figure'),
    [dash.dependencies.Input('line-graphx', 'clickData'),
     dash.dependencies.Input('scaling-factorx', 'value'),
     dash.dependencies.Input('spacingx', 'value')])

def update_linex(clickData, value, spacingx):
    try:
        if clickData:
            if len(segments_to_display_short) > 0:
                for elem in segments_to_display_short:
                    elem[0]['visible'] = False
            point = clickData['points'][0]
            x_val = point['x']
            segments_to_displayz, unedited2, indices_xval = calculate_shortest_distance(ats, x_val, value, spacingx)
            tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
            segments_to_displayy = prep_segments_to_display(segments_to_displayz, unedited2, tstamps, sensids)
        else:
            segments_to_displayy = []
    except:
        segments_to_displayy = []
    return {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace 1', 'showlegend':True, 'visible': True},
            {'x' : ats[-1][2][-1], 'y' : ats[-1][3][-1], 'type': 'line', 'name': 'trace '+ str(total_sum), 'hoverinfo': 'none', 'showlegend':True, 'visible': True},
            {'x' : ats[-1][0][0], 'y' : ats[-1][1].ravel(), 'type': 'line', 'name': 'ats ' + str(len(ats)), 'hoverinfo': 'none', 'showlegend':True, 'visible': True, 'fill' : 'tonexty'},
            *segments_to_displayy
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1},'legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}, 'hoverlabel_align' : 'right', 'margin' : {'l': 20, 'b': 30, 'r': 10, 't': 10}} }
    }

@app.callback(
    dash.dependencies.Output('line-graph2', 'figure'),
    [dash.dependencies.Input('line-graph2', 'clickData'),
    dash.dependencies.Input('scaling-factor2', 'value'),
    dash.dependencies.Input('spacing2', 'value')])

def update_line3(clickData, value, spacing2):
    try:
        if clickData:
            if len(sec_segments_to_display_same) > 0:
                for elem in sec_segments_to_display_same:
                    elem[0]['visible'] = False
            point = clickData['points'][0]
            x_val = point['x']
            sec_segments_to_display2, unedited2, indices_xval = calculate_segments_straight_up(ats, x_val, value, spacing2)
            tstamps, sensids = get_processinfo(infoinggroups, indices_xval)
            sec_segments_to_display = prep_segments_to_display(sec_segments_to_display2, unedited2, tstamps, sensids)
        else:
            sec_segments_to_display = []
    except:
        sec_segments_to_display = []
    return {
        'data': [
            {'x': first_line_x, 'y': first_line_y, 'type': 'line', 'name': 'trace 1', 'visible': True},
            {'x' : ats[-1][2][-1], 'y' : ats[-1][3][-1], 'type': 'line', 'name': 'trace ' + str(total_sum), 'hoverinfo': 'none', 'showlegend':True, 'visible': True},
            {'x' : ats[-1][0][0], 'y' : ats[-1][1].ravel(), 'type': 'line', 'name': 'ats ' + str(len(ats)), 'hoverinfo': 'none', 'showlegend':True, 'visible': True, 'fill' : 'tonexty'},
            *sec_segments_to_display
        ],
        'layout' : {'xaxis':{"title": "time in seconds", "titlefont": {"family": "Arial", "size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, 'range':[-10, 20], 'constrain' : 'domain'}, 'yaxis':{"title": "sensor value in mm","margin-left":"36.5px", "margin-bottom": "7.6px", "titlefont": {"family": "Arial","size": 12, "color": "rgb(68, 68, 68)"}, "tickfont" : {"family": "Arial","size":10, "color": "rgb(68, 68, 68)"}, "scaleanchor":"x", "scaleratio":1}, 'hoverlabel_align' : 'left','legend': {"font": {"family": "Arial","size": 10, "color": "rgb(68, 68, 68)"}} }
        }




#this is the graph with all traces
fig = go.Figure()
ctr = 0
for e in range(len(ats)):
        for i in range(len(ats[e][2])):
            ctr += 1
            namez = "trace " + str(ctr)
            fig.add_trace(go.Scatter(x=ats[e][2][i], y=ats[e][3][i],name=namez, line=dict(color="#999999")))
fig.update_layout(xaxis_title="time in seconds", yaxis_title= "sensor value in mm", font=dict( family = "Arial",size=10, color='rgb(68, 68, 68)'), legend=dict(font=dict( size= 10, color='rgb(68, 68, 68)')))
fig.update_yaxes(scaleanchor = "x", scaleratio = 1)
fig.update_xaxes(range = [-3, 33], constrain = 'domain')

#this is the graph with all ats
colors = ['lightsteelblue', 'red', 'blue', 'pink', 'orange', 'green', 'brown', 'purple']
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=ats[0][2][0], y=ats[0][3][0], name="trace 1"))
for e in range(len(ats)):
        namez = "ats " + str(e + 1)
        fig2.add_trace(go.Scatter(x=ats[e][0][0], y=ats[e][1].ravel(), name=namez, line=dict(color=colors[e])))
fig2.update_layout(xaxis_title="time in seconds", yaxis_title= "sensor value in mm",   font=dict(family = "Arial", size=10, color='rgb(68, 68, 68)'), legend=dict(font=dict( size= 10, color='rgb(68, 68, 68)')))
fig2.update_yaxes(scaleanchor = "x", scaleratio = 1)
fig2.update_xaxes(range = [-3, 33], constrain = 'domain')




app.layout = html.Div([
    html.H1(children='Drift Visualisation Method', style = {'font-weight': 'bold','textAlign': 'center', 'margin-top':'15px', 'margin-bottom': '15px'}), 
    html.Div([
        html.Div([
            html.P(children='All traces, unchanged', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px', 'margin-bottom': '-3px'}),
            dcc.Graph(
                id='line-graph5',
                figure=fig,style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='Average time sequences', style = {'font-weight': 'bold','textAlign': 'left', 'margin-left':'13px','margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Graph( 
                id='line-graph4',
                figure=fig2, style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'})]),
    html.Div([
        html.Div([
            html.P(children='Machining V2: the 90 degree angles method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factor3', type='number', min=1,  step=1, value=1),
            html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='spacing3', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='line-graph3',
                style={'width': '60vh', 'height': '95vh'}
            ),
        ],
        style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.P(children='Machining V2: the shortest distance method', style = {'font-weight': 'bold', 'textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),

            dcc.Input(id='scaling-factorx', type='number', min=1, step=1, value=1),
            html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),

            dcc.Input(id='spacingx', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='line-graphx',
                style={'width': '60vh', 'height': '95vh'}
            ), 
        ],
        style={'width': '50%', 'display': 'inline-block'})]),
        html.Div([
            html.P(children='Machining V2: the same timestamp method', style = {'font-weight': 'bold','textAlign': 'left','margin-left':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            html.Label('Scaling factor (min: 1) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='scaling-factor2', type='number', min=1, step=1, value=1),
            html.Label('Offset (min: 0) ', style = {'textAlign': 'left','margin-left':'13px', 'margin-right':'13px', 'margin-top':'10px','margin-bottom': '-3px'}),
            dcc.Input(id='spacing2', type='number', min=0, step=0.1, value=0),
            dcc.Graph(
                id='line-graph2',
                style={'width': '60vh', 'height': '95vh'}
            ),
        ])])


if __name__ == '__main__':
    app.run_server(debug=True)


