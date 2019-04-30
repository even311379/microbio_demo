# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 07:29:51 2019

@author: DB
"""
import os
import pandas as pd
import numpy as np
import re
from scipy import stats
import plotly.graph_objs as go
from plotly import tools
from . import models
from django.db import connection
import dash_core_components as dcc
import dash_html_components as html

def parse_X_data(filename):
    temp = pd.read_excel(filename)
    ID = temp.個案編號
    gender = temp.性別
    
    age = [2019 - i.year for i in temp.生日]
    if 'CRC' in filename:
        ID = [i[:-2] for i in ID]
        group = ['CRC'] * len(temp)
    elif 'CN' in filename:
        group = ['CN'] * len(temp)
    else:
        group = ['N'] * len(temp)
    
    return pd.DataFrame(dict(Group=group,ID=ID,Gender=gender,Age=age))

def create_patenitX():
    X = []
    data_files = ['doc/正常人組問卷.xlsx','doc/腸鏡組問卷 CN.xlsx','doc/CRC-T3問卷.xlsx']
    for file in data_files:
        X.append(parse_X_data(file))
    
    Patient_X = pd.concat(X,axis=0).reset_index(drop=True)
    
    return Patient_X

def create_plot1_data(Patient_X):
    microbio_data = pd.read_excel('doc/microbio.xlsx')
    IDS = [j+'-'+i for j in Patient_X[Patient_X.Group == 'CRC'].ID for i in ['1','2','3','4']] + Patient_X[Patient_X.Group == 'N'].ID.tolist() + \
    [j+'-'+i for j in Patient_X[Patient_X.Group == 'CN'].ID for i in ['1','2','3','4']]
    Group = []
    Stage = []
    Richness = []
    Chao1 = []
    Shannon = []
    Simpson = []
    Age = []
    Gender = []
    
    for ID in IDS:
        Richness.append(sum(microbio_data[ID]>0))
        P_only_one = microbio_data[ID][microbio_data[ID] > 0].min()
        P_only_two = microbio_data[ID][microbio_data[ID] > P_only_one].min()
        F1 = sum(microbio_data[ID] == P_only_one)
        F2 = sum(microbio_data[ID] == P_only_two)
        Chao1.append(sum(microbio_data[ID]>0) + F1**2/(2*F2))
        Shannon.append(-sum([pi*np.log(pi) for pi in microbio_data[ID] if pi > 0 ]))
        N = int(1/P_only_one)
        Simpson.append( 1- (sum([int(pi*N)*(int(pi*N) - 1) for pi in microbio_data[ID] if pi > 0 ])/(N*N-1)))
        
        if 'P' in ID:
            Stage.append(f'CRC-Time{ID[-1]}')
            Group.append('CRC')
        elif 'CN' in ID:
            Stage.append(f'CSP-Time{ID[-1]}')
            Group.append('CN')
        else:
            Stage.append('NC')
            Group.append('N')
        
        if '-' in ID:
            Age.append(Patient_X[Patient_X.ID==ID[:-2]].Age.iloc[0])
            Gender.append(Patient_X[Patient_X.ID==ID[:-2]].Gender.iloc[0])
        else:
            Age.append(Patient_X[Patient_X.ID==ID].Age.iloc[0])
            Gender.append(Patient_X[Patient_X.ID==ID].Gender.iloc[0])
    
    return pd.DataFrame(dict(ID = IDS, Group = Group, Stage = Stage,Gender=Gender,Age=Age, Richness = Richness, Chao1 = Chao1, Shannon = Shannon, Simpson = Simpson))
    


def draw_plot1(DI, age_range = [0,100],stages = ['NC', 'CSP-Time1','CSP-Time2', 'CSP-Time3', 'CSP-Time4', 'CRC-Time1','CRC-Time2', 'CRC-Time3', 'CRC-Time4'], Genders = 2):

    x_data = stages
    # plot_data = pd.read_excel('plot1_data.xlsx')
    plot_data = pd.read_excel('doc/plot1_data.xlsx')
    plot_data = plot_data[(plot_data.Age >= age_range[0]) & (plot_data.Age <= age_range[1])]
    if Genders == 0:
        plot_data = plot_data[plot_data.Gender == '女']
    elif Genders == 1:
        plot_data = plot_data[plot_data.Gender == '男']
    else:
        pass
    y_data = [plot_data[plot_data.Stage == i][DI] for i in x_data]
    hover_data = [plot_data[plot_data.Stage == i].ID for i in x_data]
    colors = ['rgba(87,169,23,0.8)','rgba(255,248,182,0.8)', 'rgba(255,189,145, 0.8)', 'rgba(255,141,113, 0.8)', 'rgba(255,112,126, 0.8)', 'rgba(202,25,25, 0.8)', 'rgba(163,21,37, 0.8)', 'rgba(127,20,37, 0.8)', 'rgba(77,6,28, 0.8)']

    traces = []

    for xd, yd, cls, ht in zip(x_data, y_data, colors, hover_data):
            traces.append(go.Box(
                y=yd,
                name=xd,
                text=ht,
                boxpoints='all',
                jitter=0.5,
                pointpos = 0,
                whiskerwidth=0.2,
                fillcolor=cls,
                marker=dict(
                    size=4,
                ),
                line=dict(width=1),
            ))

    layout = go.Layout(
        title=DI,
        yaxis=dict(
            autorange=True,
        ),
        hovermode="closest",
        dragmode="pan",
        clickmode='event+select',
        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
        showlegend=True
    )
    
    return go.Figure(data=traces, layout=layout)

def parse_fig2_data(Genders=2, min_age = 10, max_age = 100):
    microbio_data = pd.read_excel('doc/microbio.xlsx')
    plot1_data = pd.read_excel('doc/plot1_data.xlsx')
    plot1_data = plot1_data[(plot1_data.Age >= min_age) & (plot1_data.Age <= max_age)]

    if Genders == 0:
        plot1_data = plot1_data[plot1_data.Gender == '女']
    elif Genders == 1:
        plot1_data = plot1_data[plot1_data.Gender == '男']
    else:
        pass

    print(plot1_data.columns)
    BOOL_col = [(i == 'CRC-Time1') or (i == 'NC')  for i in plot1_data.Stage]
    tt = plot1_data[BOOL_col].ID
    tt1 = microbio_data[tt].mean(axis=1)
    BOOL_row = (tt1 > 0.003).tolist()
    temp = microbio_data.iloc[BOOL_row,:]
    temp_NC = temp[plot1_data[plot1_data.Stage == 'NC'].ID]
    temp_CRC_time1 = temp[plot1_data[plot1_data.Stage == 'CRC-Time1'].ID]
    t_p_values = []
    
    for i in range(len(temp)):
        t_p_values.append(stats.ttest_ind(temp_NC.iloc[i,:],temp_CRC_time1.iloc[i,:])[1])
        
    p_threshold = .5
    temp2 = temp.iloc[np.array(t_p_values) <= p_threshold,:]
    
    if len(temp2) < 20:
        microbio_names = [f'{g} {s}' for g, s in zip(temp2['Genus'],temp2['Species'])]
        plot2_data = temp2[plot1_data[BOOL_col].ID.tolist()]
        plot2_data.insert(0,'species_name',microbio_names)
    else:
        M = temp2[plot1_data[BOOL_col].ID.tolist()].mean(axis=1)
        top20threshold = M.sort_values(ascending=False).iloc[19]
        temp3 = temp2.iloc[np.array(M) >= top20threshold]
        microbio_names = [f'{g} {s}' for g, s in zip(temp3['Genus'],temp3['Species'])]
        plot2_data = temp3[plot1_data[BOOL_col].ID.tolist()]
        plot2_data.insert(0,'species_name',microbio_names)
    
    plot2_data.reset_index(False)
    plot2_data.to_excel('doc/plot2_data.xlsx',index=False)
    return plot2_data


def draw_plot2(I):
    x_data = ['NC', 'CRC-Time1']
    plot2_data = pd.read_excel('doc/plot2_data.xlsx')
    NC_cols = [i for i in plot2_data.columns[1:] if 'N' in i]
    CRC_cols = [i for i in plot2_data.columns[1:] if 'P' in i]
    try:
        y_data = [plot2_data[NC_cols].iloc[I,:], plot2_data[CRC_cols].iloc[I,:]]
        p_value = round(stats.ttest_ind(y_data[0],y_data[1])[1],3)
        colors = ['rgba(87,169,23,0.8)','rgba(202,25,25, 0.8)']
        hover_text = [NC_cols, CRC_cols]
        traces = []
        for xd, yd, cls, ht in zip(x_data, y_data, colors, hover_text):
                traces.append(go.Box(
                    y=yd,
                    name=xd,
                    text=ht,
                    boxpoints='all',
                    jitter=0.8,
                    pointpos = 0,
                    whiskerwidth=0.2,
                    fillcolor=cls,
                    marker=dict(
                        size=5,
                    ),
                    line=dict(width=1),
                ))
        
        layout = go.Layout(
            title=f'<b>{plot2_data.species_name[I]}</b>',
            font=dict(size=12),
            hovermode="closest",
            dragmode="pan",
            yaxis=dict(
                autorange=True,
            ),
            xaxis = dict(
                showticklabels=True
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
            showlegend=False,
            margin=dict(
                l=100,
                r=15,
                b=15,
                t=100,
                pad=0
            ),
            annotations=[
                dict(
                    x=0.8,
                    y=1.1,
                    showarrow=False,
                    text=f'p-value: {p_value}',
                    xref='paper',
                    yref='paper',
                    font=dict(size=10),
                    bordercolor='#c7c7c7',
                    borderwidth=2,
                    borderpad=2,
                    bgcolor='#ff7f0e',
                    opacity=0.8
                ),]
        )
            
        return go.Figure(data=traces, layout=layout)
    except:
        return 'no graph!'

def parse_fig3_data(Genders=2, min_age = 10, max_age = 100):
    microbio_data = pd.read_excel('doc/microbio.xlsx')
    genus_data = microbio_data.groupby(['Genus']).sum()
    plot1_data = pd.read_excel('doc/plot1_data.xlsx')
    plot1_data = plot1_data[(plot1_data.Age >= min_age) & (plot1_data.Age <= max_age)]

    if Genders == 0:
        plot1_data = plot1_data[plot1_data.Gender == '女']
    elif Genders == 1:
        plot1_data = plot1_data[plot1_data.Gender == '男']
    else:
        pass

    BOOL_col = [i in ['CRC-Time1', 'CRC-Time2', 'CRC-Time3', 'CRC-Time4']  for i in plot1_data.Stage]
    
    BOOL_row = (genus_data[plot1_data[BOOL_col].ID.tolist()].mean(axis=1) > 0.003).tolist()
    temp = genus_data.iloc[BOOL_row,:]
    temp_CRC_time1 = temp[plot1_data[plot1_data.Stage == 'CRC-Time1'].ID]
    temp_CRC_time2 = temp[plot1_data[plot1_data.Stage == 'CRC-Time2'].ID]
    temp_CRC_time3 = temp[plot1_data[plot1_data.Stage == 'CRC-Time3'].ID]
    temp_CRC_time4 = temp[plot1_data[plot1_data.Stage == 'CRC-Time4'].ID]
    aov_p_values = []
    for i in range(len(temp)):
        aov_p_values.append(stats.f_oneway(temp_CRC_time1.iloc[i],temp_CRC_time2.iloc[i],temp_CRC_time3.iloc[i],temp_CRC_time4.iloc[i])[1])
        
    p_threshold = .5 # set p threshold
    temp2 = temp.iloc[np.array(aov_p_values) <= p_threshold,:]
    if len(temp2) < 15: # set Top N
        plot3_data = temp2[plot1_data[BOOL_col].ID.tolist()]
    else:
        M = temp2[plot1_data[BOOL_col].ID.tolist()].mean(axis=1)
        top15threshold = M.sort_values(ascending=False).iloc[14] # set Top N
        temp3 = temp2.iloc[np.array(M) >= top15threshold]
        plot3_data = temp3[plot1_data[BOOL_col].ID.tolist()]

    plot3_data.reset_index(False)
    plot3_data.to_excel('doc/plot3_data.xlsx')

    return plot3_data


def draw_plot3(I):
    x_data = ['CRC-T1', 'CRC-T2', 'CRC-T3', 'CRC-T4']
    plot3_data = pd.read_excel('doc/plot3_data.xlsx')

    T1_cols = [i for i in plot3_data.columns[1:] if '-1' in i]
    T2_cols = [i for i in plot3_data.columns[1:] if '-2' in i]
    T3_cols = [i for i in plot3_data.columns[1:] if '-3' in i]
    T4_cols = [i for i in plot3_data.columns[1:] if '-4' in i]

    y_data = [plot3_data[T1_cols].iloc[I,:], plot3_data[T2_cols].iloc[I,:],plot3_data[T3_cols].iloc[I,:], plot3_data[T4_cols].iloc[I,:]]

    p_value = round(stats.f_oneway(y_data[0],y_data[1],y_data[2],y_data[3])[1],3)

    colors = ['rgba(202,25,25, 0.8)', 'rgba(163,21,37, 0.8)', 'rgba(127,20,37, 0.8)', 'rgba(77,6,28, 0.8)']

    traces = []

    for xd, yd, cls in zip(x_data, y_data, colors):
            traces.append(go.Box(
                y=yd,
                name=xd,
                boxpoints='all',
                jitter=0.8,
                pointpos = 0,
                whiskerwidth=0.2,
                fillcolor=cls,
                marker=dict(
                    size=5,
                ),
                line=dict(width=1),
            ))

    layout = go.Layout(
        title=f'<b>{plot3_data.Genus[I]}</b>',
        font=dict(size=14),
        yaxis=dict(
            autorange=True,
        ),
        xaxis = dict(
            showticklabels=True
        ),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
        showlegend=False,
        annotations=[
            dict(
                x=0.8,
                y=1.1,
                showarrow=False,
                text=f'p-value: {p_value}',
                xref='paper',
                yref='paper',
                font=dict(size=16),
                bordercolor='#c7c7c7',
                borderwidth=2,
                borderpad=2,
                bgcolor='#ff7f0e',
                opacity=0.8
            ),]
    )

    return go.Figure(data=traces, layout=layout)


def draw_blood_data(pID):
    patient_info = models.patient_data.objects.get(PatientID = pID)
    tt = models.blood_test_data.objects.filter(PatientID = patient_info).values()[0]
    blood_data = [tt[k] for k in tt][1:]
    
    y_data = []
    for i in range(3):
        y_data.append(blood_data[i+1:i+5])
    
    x_data = ['Treg', 'CEC', 'CEA']
    colors = ['#f77754', '#018790', '#0a516d']
    traces = []
    for xd, yd, cls, ya in zip(x_data, y_data, colors, ['y','y2','y3']):
        trace = go.Scatter(x=[0,1,2,3],y = yd,marker=dict(color=cls),mode = 'lines+markers',name = xd,yaxis=ya)
        traces.append(trace)
    
    layout = go.Layout(title=pID,
        yaxis=dict(title=x_data[0],titlefont=dict(color=colors[0]),tickfont=dict(color=colors[0]),),
        yaxis2=dict(title=x_data[1],titlefont=dict(color=colors[1]),tickfont=dict(color=colors[1]),side='right',anchor='x',overlaying='y'),
        yaxis3=dict(title=x_data[2],titlefont=dict(color=colors[2]),tickfont=dict(color=colors[2]),side='right',anchor='free',overlaying='y',position=0.85),
        xaxis=go.layout.XAxis(ticktext=['Before','1M','3M','6M'],tickvals=[0,1,2,3],domain=[0, 0.8],showgrid=False),
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)',
        )

    return go.Figure(data=traces, layout=layout)

    