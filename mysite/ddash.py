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

    app = app_name

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
        html.Div([
        html.H2('APP1'),
        html.H4("說明",style={'color':'#e2598b'}),
        dcc.Markdown(dedent('''
        ### 選單區
        這裡有四個選單前兩者可以直接由microbio這份excel檔中的欄位獲取，我使用多重選擇的形式
        讓使用者決定要面四個圖要有哪些資料，另外兩個欄位是我從你們的病人資料中簡單撈出的兩個變數
        ，性別和年齡（從出生日期換算），性別使用單選（男、女、不拘），年齡使用range slider的
        選擇方式,我在app2、3中，年齡的選單是使用另一種方式，看那一種比較喜歡。
        選取完後要按下更新圖表，上面的設定才後開始更新，在更新中你會看到這個網站在瀏覽器的title變成Updating...
        表示更新中

        ### 繪圖區
        1. 這四個多樣性指標資料是我寫程式自己在算的
        2. 當你將滑鼠移到任意圖表上面時，你可以看到modebar,你可以點選看看玩玩各自的功能，
        3. 如果你不喜歡某些modebar，我可以把他完全hide和disable掉
        4. 你可以拖動圖表，按住左鍵然後移動滑鼠，我設置默認的dragmode為pan，也可以改成別的
        4. 你將滑鼠移到boxplot上的點上面時，可以立刻看到病人的ID和數值，這個資訊是可以改寫的，我目前就是放病人ID而已，要的話我還可以放很多你想放的資訊。
        5. 每個圖右側的legend是可以點選的，可以將各自對應的資料hide起來,當然，也是可以把legend關掉，這樣就沒有hide的功能。app2、3、4的legend就是被我關掉的

        #### 全部的圖表配置，版型、配色、間距、大小等，如有需要都可以在細部修改

        ''')),],className='container'),
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
        html.Br(),
        dcc.Markdown(dedent('''
            ### click event test
            你有提到可不可以讓使用者點選一些點位，然後就呈現那些點位的圖表或相關資訊，因此我在這裡做了簡單的功能prototype
            你可以在**左上圖的任一個點**點下去，然後下方文字就會出現那個點的資訊，目前只是prototype,所以我只讓ID跑出來，如果需要
            可以呈現出任意可以對應的到的資料，如果不要文字，要畫圖也可以，例如 將血液資料show出來

            ##### 如果有需要，我也可以改採用多重選擇的功能,讓使用者能夠點選很多個點,然後漂亮的呈現出他們的資訊 
              
        '''),className='container'),
        html.Div(html.H3(id='display_clicked_data',children='You did not click any data yet!'),style={'border': 'thin lightgrey solid'}),
        html.Hr(),
        # link region
        html.Div([
            html.Div(html.A('home', href='/home', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app4', href='/app3', className = 'btn btn-primary'),className='col-3'),
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
        html.Div([
        html.H2('APP2'),
        html.H4("說明",style={'color':'#e2598b'}),
        dcc.Markdown(dedent('''
        ### 效能問題
        這個app是全部裡面最需要計算量的一個,挑選病患資料後，後台必須重頭重新計算，abundant > 0.3% 且**顯著**的species
        產出plot需要的資料,然後一次將20圖更新,因此當你按下更新圖表後,需要等一陣子, 也因此,如果你們之後想用computer intensive
        的方式來計算p值,如bootstrap、 bayesian等方式,會等很久很久才更新,建議還是只使用比較簡單的統計算法就好（如現在在用的t test）

        因為你現在給我的example data幾乎沒有物種符合abundant > 0.3% 且**顯著**的,所以我目前是把**p value的門檻拉高到0.5**, 
        而之後也要處理如果篩選完後物種數量不到20,這些圖要怎麼放上去,版型要怎麼樣才不會跑掉的太誇張

        ### 選單區
        我使用性別（單選）及年齡(兩個整數input)來做為選單,我嘗試使用另一種方式來，讓使用者選擇年齡的上限和下限，再來更新選單
        當然,這個選單區的排版也還醜醜的,正式做的時候再修。

        ### 圖表
        我關掉legend，太花了

        我額外加上默認的滾輪反應，你在任意一張圖表上滾滑鼠滾輪即可放大縮小,

        modebar的選單區被我hide掉幾個,測試我能不能關掉一些不太會用到的modebar

        圖還醜醜的,p值的呈現也醜醜的,之後再修

        您的資料中物種名稱有些沒有種名，因此你會看到有些的種名為nan，之後可能要改成sp.或spp.

        '''))],className='container'),
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
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-3'),
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
        html.H4("說明",style={'color':'#e2598b'}),
        dcc.Markdown(dedent('''
        你的說明只有提到Genus level top 15,所以我假設是將同個Genus底下的物種百分比加總，然後再以這個百分比來挑選> 0.3%、
        且計算 one way anova 的p值，一樣我暫時將p值得門檻上限拉到0.5，再將前15丟上來畫圖

        其餘選單區和圖表本身的說明如app2，我程式碼幾乎是照搬過來的
        ''')),
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
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-3'),
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


def microbio_app4(all_pid):

    pid_options = [{'label':i, 'value':i} for i in all_pid]

    external_stylesheets = [
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
        "https://freelancerlife.info/static/apps/css/dash_apps.css",
        ]
    app = dash.Dash(csrf_protect=False,external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        # main title
        html.H1(children='Microbiota Community Visualization',style={ 'text-align': 'center' }),
        html.P(children='author of this app: Even',style={ 'text-align': 'right' }),
        html.Div([
        html.H2('APP4'),
        html.H4("說明",style={'color':'#e2598b'}),
        dcc.Markdown(dedent('''
        你提到要做血液資料視覺化,但是之後有可能會有很多很多的病人都要show這個圖，我不知道到底要一口氣畫多少張圖上去,
        所以我目前是只放四個圖,做個下拉式選單，讓使用者能選這個圖要呈現誰的資料

        ### 圖表
        我目前使用3個y來呈現這個圖，一些排版還要再修（如：y3的axis label會擋到），總之，只是demo
        legend可以點喔

        ### 資料庫連動
        這是唯一有和資料庫做連動的圖表，其他我的app都只是拿你給我的excel檔，計算產出plot_data的excel檔，從load這些plot_data再畫圖
        ,之後在世做全部都要連進資料庫里

        你可以去後台更新,新增病人基本資料,再新增該病人的血液資料,然後這個app的下拉式選單中就會直接多出一個選項

        我目前還沒編寫一些例外處理的的程式，因此你資料庫動一動這個app只要狀況不對就會掛掉(例如：新增了病人資料卻沒有新增血液資料)，
        正式要做的時候在幫你們設想這些一大堆的例外狀況怎麼處理吧
        ''')),
        html.A('後台入口', href='/admin', className = 'btn btn-primary'),
        ],className='container'),
        html.Hr(),
        # plot 4 section
        html.Div(children=[
            html.P('圖1',className='col-6'),
            html.P('圖2',className='col-6'),
        ],className='row'),
        html.Div(children=[
            html.Div(dcc.Dropdown(id='f1 dropdown',options=pid_options,value=all_pid[0],placeholder="Select a patient"),className='col-6'),
            html.Div(dcc.Dropdown(id='f2 dropdown',options=pid_options,value=all_pid[1],placeholder="Select a patient"),className='col-6'),
        ],className='row'),
        # plot 4 draw region
        html.Div([
            html.Div(id='f1', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[0])),className='col-6'),
            html.Div(id='f2', children=dcc.Graph(figure=utils.draw_blood_data(all_pid[1])),className='col-6'),
        ],className='row'),
        html.Br(),
        html.Div(children=[
            html.P('圖3',className='col-6'),
            html.P('圖4',className='col-6'),
        ],className='row'),
        html.Div(children=[
            html.Div(dcc.Dropdown(id='f3 dropdown',options=pid_options,value=all_pid[2],placeholder="Select a patient"),className='col-6'),
            html.Div(dcc.Dropdown(id='f4 dropdown',options=pid_options,value=all_pid[3],placeholder="Select a patient"),className='col-6'),
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
        **this the prototype demo app for your project**,
        
        ## 這是說明文件

        我目前就你們需求，研究出一套能夠走下去的開發路線，目前只是很簡單的將之後整個project會用到的元件呈現出來，
        還沒有好好的規劃整體的結構與版型，所以你目前看起來會很亂，還很丑。但這只是demo而已，請見諒。

        你們需要**互動性的資料視覺化呈現**（我簡稱儀表板），並且建構在**動態網站框架**(具有資料庫連動的網站)底下，亦即，前台的使用者可以對
        圖表鉤拉點選，並依需求更新所呈現的圖表。而在管理者端要能進入後台更新資料，而一但更新完資料後立刻會和前台連動，例如
        儀表板中的選單又多了幾個不同的病人可以選擇，諸如此類。

        因此，我使用python的dash套件進行儀表板分析，使用django套件來開發這個後台框架。我花了點時間才研究出一套最妥當的方式將這兩者整合起來。
        目前考慮到執行效率優化的問題，先將整個app分成4個小的各自呈現，除了執行效率外，我也覺得一次放超多圖表在同個app底下會很亂,
        使用者會很難使用。
        執行效率緩慢是指按下更新圖表後，要等個超過30秒才會更新，但這個問題在我大幅度的修改程式運行流程後好了很多，所以我猜現在將多個
        app放回去在同個頁面下應該不會太卡。

        #### 各app使用說明，以及一些建議與問題，會放在各app底下，請再各自前往看看
        ''')),
        html.Br(),
        # link region        
        html.Div([
            html.Div(html.A('Go to app1', href='/app1', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app2', href='/app2', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app3', href='/app3', className = 'btn btn-primary'),className='col-3'),
            html.Div(html.A('Go to app4', href='/app4', className = 'btn btn-primary'),className='col-3'),
        ],className='row d-flex justify-content-between'),
        html.Br(),
        dcc.Markdown(dedent('''
        #### 資料庫與前台連動
        1. 我選用最簡單的資料庫sqlite,顧名思義lite版的資料庫，但處理你們最多可能會有的資料應該也還是綽綽有餘，但如果你們希望這個資料庫
        要當成server，讓非這個project的其他程式能夠讀到裡面的資料的話，就必須改用別的資料庫，如：postgresql等，總之這只是demo,所以
        我也只用最簡單的sqlite。

        2. 關聯式資料庫規劃，簡而言之，一個關聯式資料庫就是由彼此就有關系的多個資料表構成，依你們的案子，就是以病人編號來串接起所有資料表，
        如問卷資料表、微生物相資料表、病人基本資料、病人血液檢測資料等，各資料表彼此的關係是需要妥善設計規劃的，我目前就只有在資料庫中建立兩個資料表，
        病人基本資料、血液檢測資料，並以病人編號為primary Key，設計成一對一的關係，所以一個病人只會對應到一組血液檢測結果，不同次的血液檢測用不同欄位呈現，
        而你必須要先新增一位病人基本資料，才能在病人檢測資料表中新增他的血液資料。
        
        3. 我目前只有將app4，與後台資料庫做連結，因此你在後台做一些事情，會立刻反應到前台，例如你將病人血液資料砍到4個以下，app4會整個掛掉，因為
        我程式碼是寫要至少4個病人資料來呈現，而如果你新增的話，下拉是選單中就會立刻多出你所新增的病人血液資料。

        4. 後台我會先再開一組使用者及密碼給你，這個後台就是能夠讓你們直接輸入資料的地方

        ''')),
        html.Br(),
        html.A('後台入口', href='/admin', className = 'btn btn-primary'),
        html.Br(),
        html.Br(),
        dcc.Markdown(dedent(
        '''
        #### 網站部屬

        我在嘗試使用免費的網站部屬平台（heroku）部屬這個demo網站時失敗了，因此目前是放在要付費的平台底下(digital ocean)，選用最簡單的方案，一個月5美金，約150台幣，先給你們看看
        ，如果案子沒要給我接，或者是之後打算找別的地方部屬的話，**我最多2個禮拜內會把這個伺服器關掉，當然你們願意提供這個些微的伺服器運作費用的話就繼續讓他開著，
        不然沒有理由要繼續花我的荷包**。

        目前就只有接nginx和gunicorn來將這個demo網站接出去，如果要正式給我來部屬的話，還會幫你們選購網址，進行https加密，以及基本的伺服器設定與維護。


        #### 報價

        我會額外寫個報價檔案給你們，願意接受的話就開工吧。
        如果需要的話，這兩個禮拜內可以開個視訊會議，跟你們進行報價說明。


        #### 程式原始碼

        我的程式碼一律公開，這裡面沒有你們的資料，放心：
        https://github.com/even311379/microbio_demo


        #### 我的聯絡方式
        * email: even311379@hotmail.com
        * phone: 0989914039
        * 個人網站： https://freelancerlife.info
        ''')),
        
    ], className="container bg-light")

    return app

def app_test():
    app = dash.Dash(csrf_protect=False)
    app.layout = html.Div([
        html.H1('test'),
        html.P('I should try multiple apps to boost load time for each app')
    ])

    return app
