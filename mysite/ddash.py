import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import json
from . import utils
import pandas as pd
from . import models
from textwrap import dedent

min_age = pd.read_excel('doc/PatientX.xlsx').Age.min()
max_age = pd.read_excel('doc/PatientX.xlsx').Age.max()
min_marker = int(min_age*0.1)*10+10
max_marker = int(max_age*0.1)*10

# need to make it dynamic later:
age_marker =  {30:'30',40:'40',50:'50',60:'60',70:'70'}

toolbar_cof = {
    'modeBarButtonsToRemove': ['sendDataToCloud', 'lasso2d','zoom2d','select2d','autoScale2d','hoverCompareCartesian'],
    'scrollZoom':True}

def create_plot2_row_layout(s = 0, e = 5):
    divs = []
    for i in range(s,e):
        divs.append(
            dcc.Graph(figure=utils.draw_plot2(i),className='col col-md-2dot4',style={ 'height': '300px', }, config=toolbar_cof)
        )
    return divs

def create_plot3_row_layout(s = 0, e = 5):
    divs = []
    for i in range(s,e):
        divs.append(
            dcc.Graph(figure=utils.draw_plot3(i),className='col col-md-2dot4',style={ 'height': '300px', }, config=toolbar_cof)
        )
    return divs

def dispatcher(request,app_name):

    app = app_name()

    params = {
        'data': request.body,
        'method': request.method,
        'content_type': request.content_type
    }

    with app.server.test_request_context(request.path, **params):
        app.server.preprocess_request()
        try:
            response = app.server.full_dispatch_request()
        except Exception as e:
            response = app.server.make_response(app.server.handle_exception(e))
        
        return response.get_data()

def microbio_app1():
    print('Am I here?')
    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # main title
        html.H1(children='Microbiota Community Visualization',style={ 'text-align': 'center' }),
        html.P(children='author of this app: Even',style={ 'text-align': 'right' }),
        html.H2('APP1'),
        html.H4("Put these info here?",style={'color':'#e2598b'}),
        html.Hr(),
        # plot1 section
        html.H3(children='Microbio Community Diversity Indice',style={ 'text-align': 'center' }),
        # menus for plot1
        html.Div([
            html.Div(
                [html.P(children='Select CRC time (default: ALL)'),
                dcc.Dropdown(
                    id = 'CRC dropdown',
                    options=[
                        {'label': 'Time1', 'value': 'Time1'},
                        {'label': 'Time2', 'value': 'Time2'},
                        {'label': 'Time3', 'value': 'Time3'},
                        {'label': 'Time4', 'value': 'Time4'},
                    ],
                    value=['Time1','Time2','Time3','Time4'],
                    multi=True,
                    placeholder="Select CRC Time:",
                ),],className='col col-sm-4'
            ),
            html.Div(
                [html.P(children='Select CSP time (default: ALL)'),
                dcc.Dropdown(
                    id = 'CSP dropdown',
                    options=[
                        {'label': 'Time1', 'value': 'Time1'},
                        {'label': 'Time2', 'value': 'Time2'},
                        {'label': 'Time3', 'value': 'Time3'},
                        {'label': 'Time4', 'value': 'Time4'},
                    ],
                    value=['Time1','Time2','Time3','Time4'],
                    multi=True,
                    placeholder="Select CRC Time:",
                ),],className='col col-sm-4'
            ),
            html.Div(
                [html.P(children='Select Gender (default: ALL)'),
                dcc.Dropdown(
                    id = 'Gender dropdown',
                    options=[
                        {'label': '女', 'value': 0},
                        {'label': '男', 'value': 1},
                        {'label': '不拘', 'value': 2},
                    ],
                    value=2,
                    multi=False,
                    placeholder="選擇性別")
                ,],className="col col-sm-4")
        ],className="row mt-2 d-flex justify-content-between"),
        html.P('選擇年齡範圍：'),
        html.Div([
            html.Div(dcc.RangeSlider(id='age-slider1',min=min_age,max=max_age,marks=age_marker,step=1,value=[min_age, max_age]),className='col col-md-6'),
            html.Div(html.Button(id='MCDI_Button',children='更新圖表',className='btn btn-primary'),className="col col-md-6")]
            ,className="row"),
        html.Div(id='age-slider1-output'),
        # plot1 draw region
        html.Div(id='MCDI',children=
            [html.Div(
            [dcc.Graph(id='ffg1',figure=utils.draw_plot1('Richness'),className='col col-6',style={ 'height': '40vh' }),
                dcc.Graph(figure=utils.draw_plot1('Chao1'),className='col col-6',style={ 'height': '40vh' }),],
                className='row mt-2 d-flex justify-content-between'),
            html.Div(
            [dcc.Graph(figure=utils.draw_plot1('Shannon'),className='col col-6',style={ 'height': '40vh' }),
                dcc.Graph(figure=utils.draw_plot1('Simpson'),className='col col-6',style={ 'height': '40vh' }),],
                className='row mt-2 d-flex justify-content-between'),]),
        html.H4("Test Click events, try to click any data in the upper left fig~",style={'color':'#e2598b'}),
        html.Div(html.P(id='display_clicked_data',children='You did not click any data yet!'),style={'border': 'thin lightgrey solid'}),
        html.Hr(),
        # link region
        html.Div([
            html.Div(html.A('home', href='/home', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app4', href='/app3', className = 'btn btn-primary'),className='col-4'),
        ],className='row d-flex justify-content-between'),
    ])

    @app.callback(
    Output('age-slider1-output', 'children'),
    [Input('age-slider1', 'value')])
    def update_age_slider_text(value):
        return f'您目前選取了{value[0]}到{value[1]}歲之間的病人'

    @app.callback(
        Output('MCDI','children'),
        [Input('MCDI_Button','n_clicks')],
        [State('CRC dropdown','value'),
         State('CSP dropdown','value'),
         State('Gender dropdown','value'),
         State('age-slider1','value'),
         ]
        )
    def update_MCDI(n_clicks,CRC_filter, CSP_filter, Gender_filter, age_range):
        
        stages = ['NC'] + ['CSP-' + i for i in CSP_filter] + ['CRC-' + i for i in CRC_filter]
        out =   [html.Div(
                    [dcc.Graph(id='ffg1',figure=utils.draw_plot1('Richness',age_range, stages, Gender_filter),className='col col-6',style={ 'height': '40vh' }),
                    dcc.Graph(figure=utils.draw_plot1('Chao1',age_range, stages, Gender_filter),className='col col-6',style={ 'height': '40vh' }),],
                    className='row mt-2 d-flex justify-content-between'),
                html.Div(
                    [dcc.Graph(figure=utils.draw_plot1('Richness',age_range, stages, Gender_filter),className='col col-6',style={ 'height': '40vh' }),
                    dcc.Graph(figure=utils.draw_plot1('Richness',age_range, stages, Gender_filter),className='col col-6',style={ 'height': '40vh' }),],
                    className='row mt-2 d-flex justify-content-between')]
        return  out


    @app.callback(
        Output('display_clicked_data', 'children'),
        [Input('ffg1', 'clickData')])
    def display_click_data(clickData):
        print(clickData)
        try:
            return 'You clicked ' + clickData['points'][0]['text'] +'!'
        except:
            return 'something wrong in the click info return logic!!'

    return app


def microbio_app2():
    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # main title
        html.H1(children='Microbiota Community Visualization',style={ 'text-align': 'center' }),
        html.P(children='author of this app: Even',style={ 'text-align': 'right' }),
        html.H2('APP2'),
        html.H4("Put these info here?",style={'color':'#e2598b'}),
        html.Hr(),
         # plot 2 section
        html.H3(children='NC VS CRC-Time1 for top 20 microbial species',style={ 'text-align': 'center' }),
        # plot 2 menu region
        html.Div([html.P('選擇性別',className='col-3'),html.P('選擇年齡範圍：',className='col-2')],className='row'),
        html.Div([html.Div(dcc.Dropdown(
            id='Gender dropdown1',
            options=[{'label': '女', 'value': 0},{'label': '男', 'value': 1},{'label': '不拘', 'value': 2},],
            value=2,
            placeholder="選擇性別"
            ),className='col-3'),
            html.Div(dcc.Input(id='min_age1',type='number',value=0,placeholder='最小年齡'),className='col col-2'),
            html.P('到',className='col-2'),
            html.Div(dcc.Input(id='max_age1',type='number',value=100,placeholder='最大年齡'),className='col col-2'),
            html.Div(html.Button(id='N_VS_CRCT1_button',children='更新圖表',className='btn btn-primary'),className='col-3')
        ],className='row'),
        # plot 2 draw region
        html.Div(id='N_VS_CRCT1',children=[
            html.Div(create_plot2_row_layout(s = 0, e = 5),className='row'),
            html.Div(create_plot2_row_layout(s = 5, e = 10),className='row'),
            html.Div(create_plot2_row_layout(s = 10, e = 15),className='row'),
            html.Div(create_plot2_row_layout(s = 15, e = 20),className='row'),]
            ),
        html.Hr(),
        html.Div([
            html.Div(html.A('home', href='/home', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-4'),
        ],className='row d-flex justify-content-between'),
    ])

    @app.callback(
    Output('N_VS_CRCT1','children'),
    [Input('N_VS_CRCT1_button','n_clicks')],
    [State('Gender dropdown1','value'),
    State('min_age1','value'),
    State('max_age1','value'),],
    )
    def update_Top20_N_VS_CRCT1(n_clicks,gender,min_age,max_age):
        '''
        need to just recreate the whole data set, since it requires so many conditions
        '''
        utils.parse_fig2_data(gender, min_age, max_age)

        try:
            divs = [
            html.Div(create_plot2_row_layout(s = 0, e = 5),className='row'),
            html.Div(create_plot2_row_layout(s = 5, e = 10),className='row'),
            html.Div(create_plot2_row_layout(s = 10, e = 15),className='row'),
            html.Div(create_plot2_row_layout(s = 15, e = 20),className='row'),]
            return divs
        except:
            return "ERROR!"
    
    return app


def microbio_app3():
    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # main title
        html.H1(children='Microbiota Community Visualization',style={ 'text-align': 'center' }),
        html.P(children='author of this app: Even',style={ 'text-align': 'right' }),
        html.H2('APP3'),
        html.H4("Put these info here?",style={'color':'#e2598b'}),
        html.Hr(),
        # plot 3 section
        html.H3(children='Top 15 significant microbial Genus CRC-Time1 to 4',style={ 'text-align': 'center' }),
        # plot 3 menu
        html.Div([html.P('選擇性別',className='col-6'),html.P('選擇年齡範圍：',className='col-6')],className='row'),
        html.Div([html.Div(dcc.Dropdown(
            id='Gender dropdown2',
            options=[{'label': '女', 'value': 0},{'label': '男', 'value': 1},{'label': '不拘', 'value': 2},],
            value=2,
            placeholder="選擇性別"
            ),className='col-3'),
            html.Div(dcc.Input(id='min_age2',type='number',value=0,placeholder='最小年齡'),className='col col-2'),
            html.P('到',className='col-2'),
            html.Div(dcc.Input(id='max_age2',type='number',value=100,placeholder='最大年齡'),className='col col-2'),
            html.Div(html.Button(id='CRCT1234_button',children='更新圖表',className='btn btn-primary'),className='col-3')
        ],className='row'),
        # plot 3 draw region
        html.Div(id='CRCT1234',children=[
            html.Div(create_plot3_row_layout(s = 0, e = 5),className='row'),
            html.Div(create_plot3_row_layout(s = 5, e = 10),className='row'),
            html.Div(create_plot3_row_layout(s = 10, e = 15),className='row'),
        ]),
        html.Hr(),
        # link region        
        html.Div([
            html.Div(html.A('home', href='/home', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-4'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-4'),
        ],className='row d-flex justify-content-between'),
    ])

    @app.callback(
    Output('CRCT1234','children'),
    [Input('CRCT1234_button','n_clicks')],
    [State('Gender dropdown2','value'),
    State('min_age2','value'),
    State('max_age2','value'),],
    )
    def update_Top15_CRCT1234(n_clicks,gender,min_age,max_age):
        '''
        need to just recreate the whole data set, since it requires so many conditions
        '''
        utils.parse_fig3_data(gender, min_age, max_age)

        try:
            divs = [
            html.Div(create_plot3_row_layout(s = 0, e = 5),className='row'),
            html.Div(create_plot3_row_layout(s = 5, e = 10),className='row'),
            html.Div(create_plot3_row_layout(s = 10, e = 15),className='row'),]
            return divs
        except:
            # pd.read_excel('plot2_data.xlsx')
            return "ERROR! "
    
    return app


all_pid = models.patient_data.objects.all().values_list('PatientID',flat=True)
pid_options = [{'label':i, 'value':i} for i in all_pid]

def microbio_app4():
    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # main title
        html.H1(children='Microbiota Community Visualization',style={ 'text-align': 'center' }),
        html.P(children='author of this app: Even',style={ 'text-align': 'right' }),
        html.H2('APP4'),
        html.H4("Put these info here?",style={'color':'#e2598b'}),
        html.Hr(),
        # plot 4 section
        html.Div(children=[
            html.Div(dcc.Dropdown(id='f1 dropdown',options=pid_options,value=all_pid[0],placeholder="Select a patient"),className='col-3'),
            html.Div(dcc.Dropdown(id='f2 dropdown',options=pid_options,value=all_pid[1],placeholder="Select a patient"),className='col-3'),
            html.Div(dcc.Dropdown(id='f3 dropdown',options=pid_options,value=all_pid[2],placeholder="Select a patient"),className='col-3'),
            html.Div(dcc.Dropdown(id='f4 dropdown',options=pid_options,value=all_pid[3],placeholder="Select a patient"),className='col-3'),
        ],className='row'),
        # plot 4 menu
        html.H4("I guess there is no need to add interaction menus??"),
        html.P("Since there are so many patient, why not let the users to pick four? they what to see"),
        # plot 4 draw region
        html.Div([
            html.Div(id='f1', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[0])),className='col-6'),
            html.Div(id='f2', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[1])),className='col-6'),
        ],className='row'),
        html.Div([
            html.Div(id='f3', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[2])),className='col-6'),
            html.Div(id='f4', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[3])),className='col-6'),
        ],className='row'),
        # link region        
        html.Div([
            html.Div(html.A('home', href='/home', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-3'),
        ],className='row d-flex justify-content-between'),
    ])

    @app.callback(
        Output('f1','children'),
        [Input('f1 dropdown','value')])
    def update_f1(PID):
        return dcc.Graph(figure=utils.draw_blood_data(PID))
    
    @app.callback(
    Output('f2','children'),
    [Input('f2 dropdown','value')])
    def update_f2(PID):
        return dcc.Graph(figure=utils.draw_blood_data(PID))

    @app.callback(
    Output('f3','children'),
    [Input('f3 dropdown','value')])
    def update_f3(PID):
        return dcc.Graph(figure=utils.draw_blood_data(PID))

    @app.callback(
    Output('f4','children'),
    [Input('f4 dropdown','value')])
    def update_f4(PID):
        return dcc.Graph(figure=utils.draw_blood_data(PID))

    return app


def home():
    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)
    app.layout= html.Div([
        dcc.Markdown(dedent('''
        # So, dear customer,
        **this a prototype demo app for your project**,

        It's a little difficult than my expect, so I'll charge a little higher that I thought,

        I seperate your apps into smaller piece, in order to make it clearer to see the content and save the loading time.

        That's why I spent sometime to handle optimization.

        Anyways, it does not look good now, there are still bunch of issues to fix, but almost all the functionality you asked is in it.
        
        Let me explain:

        1. you can update all figure once you click 更新圖表, all the figure in that app will update, 
        calculate everything from raw data and draw the result to the users. As as consequence, for app2 and app3,
        you have to wait maybe more than 30 seconds to finish the updates.

        2. click event is tested in app1, which you can click any point in the upper left figure, and it will should what that point is.
        I can easily take this info to backend to and then present more interesting info about this point, that's easy. But I am run out 
        of time to do it.

        3. I set up a platform to key in data, and will update everything in frontend. I use django framework and its backend.
        you can enter admin to key data. So far I only set up one data table for you, and everything in app4 is based on this model.
        So, you can enter the admin, change some value, and then the figures in app4 will change with it.

        ...... <br>
        ## the is just a draft for the explanation documents, it's very hard to read now. I'll update it a few days later. ##
        
        ** Just let me try if I can deploy the whole project on heroku now. **
        ''')),
        # link region        
        html.Div([
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-3'),
        ],className='row d-flex justify-content-between'),
        html.A('後台入口', href='/admin', className = 'btn btn-primary'),
    ])

    return app

def app_test():
    app = dash.Dash(csrf_protect=False)
    app.layout = html.Div([
        html.H1('test'),
        html.P('I should try multiple apps to boost load time for each app')
    ])

    return app
