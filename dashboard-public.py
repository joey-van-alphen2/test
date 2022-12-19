#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go


# In[4]:


#   App Interface  
    
def main():
    
    os.system("git config --global user.name 'joey-van-alphen2'")
    os.system("git config --global user.email 'joey.van.alphen@hva.nl'")

    st.title('Verwarming en warm water verbruik')
    df1 = pd.read_csv('df1.csv')
    
#   Data invullen door gebruiker
    st.sidebar.header('Verbruik per datum')
    with st.sidebar.form(key='df1', clear_on_submit=True):
        add_col1 = st.date_input("Datum")
        add_col2 = st.number_input('Verwarming', min_value=0000.00, step=0000.01, value=df1['Verwarming'].iloc[-1], format='%f')
        add_col3 = st.number_input('Water', min_value=000.0, step=000.1, value=df1['Water'].iloc[-1], format='%f')
        submit = st.form_submit_button('Submit')
        if submit:
            new_data = {'Datum': add_col1, 'Verwarming': add_col2, 'Water': add_col3}

            df1 = df1.append(new_data, ignore_index=True)
            df1.to_csv('df1.csv', index=False)
            st.success('Successvol toegevoegd!', icon="✅")    
    
#   Data opslaan
    os.system("git add df1.csv")
    os.system('git commit -m "Updated CSV file"')
    os.system("git push origin master")

#   Datum bruikbaar maken
    df1['Datum'] = pd.to_datetime(df1['Datum'], format='%Y-%m-%d')
#   Verbruik uitrekenen
    df1['GJ'] = df1.Verwarming.diff().fillna(0)
    df1['m3'] = df1.Water.diff().fillna(0)
#   Datum splitsen
    df1['Jaar'] = df1.Datum.dt.year
    df1['Maand'] = df1.Datum.dt.strftime('%B')
    df1['Dag'] = df1.Datum.dt.strftime('%A')
    df1['Week'] = df1.Datum.dt.week
#   Omzetten naar datframe
    df_week_show = df1.tail(7)
    df_week_show_st = df_week_show[['Datum', 'Verwarming', 'Water', 'GJ', 'm3']]
    df_week_show_st.columns = ['Datum', 'Meterstand Verwarming', 'Meterstand Tap Water', 'Verbruik Stadsverwarming in GJ', 'Verbruik Tap Water in m3']
    df_week = df1.groupby('Week')[['GJ','m3']].sum().reset_index()
    df_month = df1.groupby('Maand')[['GJ','m3']].sum().reset_index()
    df_year = df1.groupby('Jaar')[['GJ','m3']].sum().reset_index()

#   plot voor verwarming
    fig1 = go.Figure()

    fig1.add_trace(
        go.Bar(x=df_week_show['Dag'],
                   y=df_week_show['GJ'], texttemplate="%{y}", width=0.5))
    fig1.add_trace(
        go.Bar(x=df_week['Week'],
                   y=df_week['GJ'], texttemplate="%{y}", width=0.5, visible=False))
    fig1.add_trace(
        go.Bar(x=df_month['Maand'],
                   y=df_month['GJ'], texttemplate="%{y}", width=0.5, visible=False))
    fig1.add_trace(
        go.Bar(x=df_year['Jaar'],
                   y=df_year['GJ'], texttemplate="%{y}", width=0.5, visible=False))

    fig1.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(label="Dag",
                         method="update",
                         args=[{"visible": [True, False, False, False]}]),
                    dict(label="Week",
                         method="update",
                         args=[{"visible": [False, True, False, False]}]),
                    dict(label="Maand",
                         method="update",
                         args=[{"visible": [False, False, True, False]}]),
                    dict(label="Jaar",
                         method="update",
                         args=[{"visible": [False, False, False, True]}])

                ]))])  
    
    fig1.update_yaxes(title_text="Verbruik in GJ")
    
#   Plot voor tap water
    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(x=df_week_show['Dag'],
                   y=df_week_show['m3'], texttemplate="%{y}", width=0.5))
    fig2.add_trace(
        go.Bar(x=df_week['Week'],
                   y=df_week['m3'], texttemplate="%{y}", width=0.5, visible=False))
    fig2.add_trace(
        go.Bar(x=df_month['Maand'],
                   y=df_month['m3'], texttemplate="%{y}", width=0.5, visible=False))
    fig2.add_trace(
        go.Bar(x=df_year['Jaar'],
                   y=df_year['m3'], texttemplate="%{y}", width=0.5, visible=False))

    fig2.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                active=0,
                x=0.57,
                y=1.2,
                buttons=list([
                    dict(label="Dag",
                         method="update",
                         args=[{"visible": [True, False, False, False]}]),
                    dict(label="Week",
                         method="update",
                         args=[{"visible": [False, True, False, False]}]),
                    dict(label="Maand",
                         method="update",
                         args=[{"visible": [False, False, True, False]}]),
                    dict(label="Jaar",
                         method="update",
                         args=[{"visible": [False, False, False, True]}])

                ]))])  
        
    fig2.update_yaxes(title_text="Verbruik in m3")
        
#   4 kpi's maken 
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

#   kpi's waardes meegeven
    kpi1.metric(
        label="Totaal verbruik (GJ) 🔥",
        value=f'{round(df1.GJ.sum(), 2)} GJ')

    kpi2.metric(
        label="Kosten verwarming 💰",
        value=f'€ {round((df1.GJ.sum()*47.38), 2)}')

    kpi3.metric(
        label="Totaal verbruik (m3) 💧",
        value= f'{round((df1.m3.sum()), 2)} m3')
    
    kpi4.metric(
        label="Kosten warm tap water 💰",
        value=f'€ {round((df1.m3.sum()*9.92), 2)}')

#   Plots weergeven    
    st.header('Verbruik afgelopen week')
    st.dataframe(df_week_show_st)
    st.subheader('Verbruik stadsverwarming')
    st.plotly_chart(fig1) 
    st.subheader('Verbruik warm tap water')
    st.plotly_chart(fig2)


if __name__ == '__main__':
    main()

