#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# In[4]:


#   App Interface   
    
def main():
    
    os.system("git config --global user.name 'joey-van-alphen2'")
    os.system("git config --global user.email 'joey.van.alphen@hva.nl'")

    st.title('Verwarming en warm tap water verbruik')
    df1 = pd.read_csv('df1.csv')
    
#   Data invullen door gebruiker
    st.sidebar.header('Verbruik per datum')
    with st.sidebar.form(key='df1', clear_on_submit=True):
        add_col1 = st.date_input("Datum")
        add_col2 = st.number_input('Verwarming', min_value=df1['Verwarming'].iloc[-1], step=0.050, value=df1['Verwarming'].iloc[-1], format='%3.3f')
        add_col3 = st.number_input('Water', min_value=df1['Water'].iloc[-1], step=0.1, value=df1['Water'].iloc[-1], format='%3.1f')
        add_col4 = st.number_input('Temperatuur', step=1.0, value=df1['Temperatuur'].iloc[-1], format='%2.1f')
        submit = st.form_submit_button('Submit')
        if submit:
            new_data = {'Datum': add_col1, 'Verwarming': add_col2, 'Water': add_col3, 'Temperatuur' : add_col4}
            df1 = df1.append(new_data, ignore_index=True)
            df1.to_csv('df1.csv', index=False)
            st.success('Successvol toegevoegd!', icon="✅")    
    
#   Data opslaan
    os.system("git add df1.csv")
    os.system('git commit -m "Updated CSV file"')
    os.system("git push origin main")

#   Datum bruikbaar maken
    df1['Datum'] = pd.to_datetime(df1['Datum'], format='%Y-%m-%d')
#   Verbruik uitrekenen
    df1['GJ'] = df1.Verwarming.diff()
    df1['m3'] = df1.Water.diff()
#   nul-meting verwijderen zodat gemiddelde klopt
    df1 = df1.iloc[1:]
#   Datum splitsen
    df1['Jaar'] = df1.Datum.dt.year
    df1['Maand'] = df1.Datum.dt.strftime('%B')
    df1['Dag'] = df1.Datum.dt.strftime('%A')
    df1['Week'] = df1.Datum.dt.week
    df1['Jaar'] = np.where((df1['Jaar']==2023)&(df1['Week']==52), 2022, df1['Jaar'])
#   Omzetten naar dataframe
    df_week_show = df1.tail(7)
    df_week_show_st = df_week_show[['Datum', 'Verwarming', 'Water', 'GJ', 'm3']]
    df_week_show_st.columns = ['Datum', 'Meterstand Verwarming', 'Meterstand Tap Water', 'Verbruik Stadsverwarming in GJ', 'Verbruik Warm Tap Water in m3']
    df_week = df1.groupby(['Jaar','Week'])[['GJ','m3']].sum().reset_index().tail(10).sort_values(['Jaar','Week'])
    df_month = df1.groupby('Maand')[['GJ','m3']].sum().reset_index()
    df_year = df1.groupby('Jaar')[['GJ','m3']].sum().reset_index()
#   Gemiddelde temperatuur per maand berekenen
    df_temp = df1.groupby(['Jaar','Week'])['Temperatuur'].mean().to_frame().reset_index().tail(10)
    df_temp['Temperatuur'] = df_temp['Temperatuur'].round(decimals=1)

#   plot voor verwarming

    import unicodedata

    # Get the degree symbol
    degree_symbol = unicodedata.lookup("DEGREE SIGN")
    
#   Create figure with secondary y-axis
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

#   Add Traces
    fig1.add_trace(
        go.Bar(x=df_week_show['Dag'],
                   y=df_week_show['GJ'], texttemplate="%{y}", marker={'color': 'rgb(104, 92, 148)'}, width=0.5, name='Verbruik'))
    fig1.add_trace(
        go.Scatter(x=df_week_show['Dag'],
                   y=df_week_show['Temperatuur'], text=df_week_show['Temperatuur'],
                   name=f'Temperatuur in {degree_symbol}C', mode='lines+markers+text', textposition='top center',
                   marker={'size': 8}, marker_color='rgb(124, 196, 139)'), secondary_y=True,)
    fig1.add_trace(
        go.Bar(x=df_week['Week'],
                   y=df_week['GJ'], texttemplate="%{y}", marker={'color': 'rgb(104, 92, 148)'}, width=0.5, visible=False, name='Verbruik'))
    fig1.add_trace(
        go.Scatter(x=df_temp['Week'],
                   y=df_temp['Temperatuur'], text=df_temp['Temperatuur'], 
                   name='Temperatuur', mode='lines+markers+text', textposition='top center',
                   marker={'size': 8}, marker_color='rgb(124, 196, 139)', visible=False), secondary_y=True,)
    fig1.add_trace(
        go.Bar(x=df_month['Maand'], texttemplate="%{y}", marker={'color': 'rgb(104, 92, 148)'},
                   y=df_month['GJ'],visible=False, width=0.5, name='Verbruik'))
    fig1.add_trace(
        go.Bar(x=df_year['Jaar'], texttemplate="%{y}", marker={'color': 'rgb(104, 92, 148)'},
                   y=df_year['GJ'], width=0.5, name='Verbruik', visible=False))

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
                         args=[{"visible": [True, True, False, False, False, False]}]),
                    dict(label="Week",
                         method="update",
                         args=[{"visible": [False, False, True, True, False, False]}]),
                    dict(label="Maand",
                         method="update",
                         args=[{"visible": [False, False, False, False, True, False]}]),
                    dict(label="Jaar",
                         method="update",
                         args=[{"visible": [False, False, False, False, False, True]}])

                ]))], dragmode='pan')  

    fig1.update_yaxes(showticklabels=False, showgrid=False, secondary_y=True)
    fig1.update_yaxes(title_text="Verbruik in GJ", showticklabels=True, showgrid=True, secondary_y=False)
    fig1.update_layout(height=500, width=800)
    
#   Plot voor tap water
    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(x=df_week_show['Dag'], marker={'color': 'rgb(104, 92, 148)'},
                   y=df_week_show['m3'], texttemplate="%{y}", width=0.5, visible=True))
    fig2.add_trace(
        go.Bar(x=df_week['Week'], marker={'color': 'rgb(104, 92, 148)'}, 
                   y=df_week['m3'], texttemplate="%{y}", width=0.5, visible=False))
    fig2.add_trace(
        go.Bar(x=df_month['Maand'], marker={'color': 'rgb(104, 92, 148)'}, 
                   y=df_month['m3'], texttemplate="%{y}", width=0.5, visible=False))
    fig2.add_trace(
        go.Bar(x=df_year['Jaar'], marker={'color': 'rgb(104, 92, 148)'},
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

                ]))], dragmode='pan')  
        
    fig2.update_yaxes(title_text="Verbruik in m3")
    fig2.update_layout(height=500, width=730)
        
#   4 kpi's maken 
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

#   kpi's waardes meegeven
    kpi1.metric(
        label="Totaal verbruik 🔥",
        value=f'{round(df1.GJ.sum(), 2)} GJ')

    kpi2.metric(
        label="Kosten verwarming 💰",
        value=f'€ {round((df1.GJ.sum()*47.38), 2)}')

    kpi3.metric(
        label="Totaal verbruik 💧",
        value= f'{round((df1.m3.sum()), 2)} m3')
    
    kpi4.metric(
        label="Kosten warm tap water 💰",
        value=f'€ {round((df1.m3.sum()*9.92), 2)}')

#   Plots met kpi's weergeven    
    st.header('Verbruik afgelopen week')
    st.dataframe(df_week_show_st)
    
    st.subheader('Verbruik stadsverwarming')
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        label="Gemiddeld verbruik per dag",
        value= f'{round((df1.GJ.mean()), 3)} GJ')

    kpi2.metric(
        label="Gemiddelde kosten per dag",
        value=f'€ {round(((df1.GJ.mean())*47.38), 2)}')

    kpi3.metric(
        label=f"Verbruik op {(df1['Datum'].iloc[-1]).strftime('%d-%m-%Y')}",
        value=f'{round((df1.GJ.iloc[-1]), 3)} GJ',
        delta=round((df1['GJ'].iloc[-1])-(df1.GJ.mean()),3),
        delta_color='inverse')

    kpi4.metric(
        label=f"Kosten op {(df1['Datum'].iloc[-1]).strftime('%d-%m-%Y')}",
        value=f'€ {round(((df1.GJ.iloc[-1])*47.38), 2)}',
        delta=round(((df1['GJ'].iloc[-1])*47.38)-((df1.GJ.mean())*47.38),2),
        delta_color='inverse')
    
    st.plotly_chart(fig1) 
    
    st.subheader('Verbruik warm tap water')
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        label="Gemiddeld verbruik per dag",
        value= f'{round((df1.m3.mean()), 2)} m3')

    kpi2.metric(
        label="Gemiddelde kosten per dag",
        value=f'€ {round(((df1.m3.mean())*9.92), 2)}')

    kpi3.metric(
        label=f"Verbruik op {(df1['Datum'].iloc[-1]).strftime('%d-%m-%Y')}",
        value=f'{round((df1.m3.iloc[-1]), 2)} m3',
        delta=round((df1['m3'].iloc[-1])-(df1.m3.mean()),2),
        delta_color='inverse')

    kpi4.metric(
        label=f"Kosten op {(df1['Datum'].iloc[-1]).strftime('%d-%m-%Y')}",
        value=f'€ {round(((df1.m3.iloc[-1])*9.92), 2)}',
        delta=round(((df1['m3'].iloc[-1])*9.92)-((df1.m3.mean())*9.92),2),
        delta_color='inverse')

    st.plotly_chart(fig2)
    
    st.subheader('Statistieken per datum test')

    # Vraag om datum input
    selected_date = st.date_input("Selecteer een datum:")

    # Zoek index van geselecteerde datum in df1
    selected_row = df1[df1['Datum'].dt.strftime('%d-%m-%Y') == selected_date]

    if selected_row.empty:
        st.error("Geen gegevens gevonden voor de geselecteerde datum.")
    else:
        selected_index = selected_row.index[0]
        # Maak gebruik van de geselecteerde index om de metrics voor die datum te tonen
        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            label=f"Verbruik op {selected_date}",
            value=f'{round((df1.GJ.loc[selected_index]), 3)} GJ',
            delta=round((df1['GJ'].loc[selected_index])-(df1.GJ.mean()),3),
            delta_color='inverse')

        kpi2.metric(
            label=f"Kosten op {selected_date}",
            value=f'€ {round(((df1.GJ.loc[selected_index])*47.38), 2)}',
            delta=round(((df1['GJ'].loc[selected_index])*47.38)-((df1.GJ.mean())*47.38),2),
            delta_color='inverse')

        kpi3.metric(
            label=f"Temperatuur op {selected_date}",
            value=f'{df1.Temperatuur.loc[selected_index]} {degree_symbol}C')

    
    st.subheader('Statistieken per datum')

    # Voeg dropdown toe met datums uit de 'Datum' kolom van df1
    date_options = df1['Datum'].dt.strftime('%d-%m-%Y').tolist()
    selected_date = st.date_input("Selecteer een datum:")

    # Zoek index van geselecteerde datum in df1
    selected_index = df1[df1['Datum'] == selected_date].index[0]
#.dt.strftime('%d-%m-%Y')
    # Maak gebruik van de geselecteerde index om de metrics voor die datum te tonen
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        label=f"Verbruik op {selected_date}",
        value=f'{round((df1.GJ.loc[selected_index]), 3)} GJ',
        delta=round((df1['GJ'].loc[selected_index])-(df1.GJ.mean()),3),
        delta_color='inverse')

    kpi2.metric(
        label=f"Kosten op {selected_date}",
        value=f'€ {round(((df1.GJ.loc[selected_index])*47.38), 2)}',
        delta=round(((df1['GJ'].loc[selected_index])*47.38)-((df1.GJ.mean())*47.38),2),
        delta_color='inverse')
    
    kpi3.metric(
        label=f"Temperatuur op {selected_date}",
        value=f'{df1.Temperatuur.loc[selected_index]} {degree_symbol}C')

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader('Records')
    
    # Haal de datum op uit de kolom met behulp van de bepaalde index
    max_index_gj = df1['GJ'].idxmax()
    max_date_gj = df1.loc[max_index_gj, 'Datum'].strftime('%d-%m-%Y')
    max_temperatuur_gj = df1.loc[max_index_gj, 'Temperatuur']
    
    if (df1.GJ.iloc[-1]) == (df1.GJ.max()):
        st.error('Oei, een nieuw record... Het hoogste verbruik tot nu toe:')
        
    st.markdown(f'Het record met het meeste verbruik in GJ was op {max_date_gj}')

    kpi1, kpi2, kpi3 = st.columns(3) 

    kpi1.metric(
        label="Verbruik op die dag",
        value= f'{round((df1.GJ.max()), 3)} GJ')

    kpi2.metric(
        label="Kosten op die dag",
        value=f'€ {round((df1.GJ.max()*47.38), 2)}')

    kpi3.metric(
        label="Temperatuur op die dag",
        value=f'{max_temperatuur_gj} {degree_symbol}C')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    min_index_gj = df1['GJ'].idxmin()
    min_date_gj = df1.loc[min_index_gj, 'Datum'].strftime('%d-%m-%Y')
    min_temperatuur_gj = df1.loc[min_index_gj, 'Temperatuur']    
  
    if (df1.GJ.iloc[-1]) == (df1.GJ.min()):
        st.balloons()
        st.success('Hoera, een nieuw record! Het laagste verbruik tot nu toe:')
        
    st.markdown(f'Het record met het minste verbruik in GJ was op {min_date_gj}')
    
    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        label="Verbruik op die dag",
        value= f'{round((df1.GJ.min()), 3)} GJ')

    kpi2.metric(
        label="Kosten op die dag",
        value=f'€ {round((df1.GJ.min()*47.38), 2)}')

    kpi3.metric(
        label="Temperatuur op die dag",
        value=f'{min_temperatuur_gj} {degree_symbol}C')
  
    
    toon_data = st.checkbox('Toon alle data')
    
    if toon_data:
        st.dataframe(df1)
            
if __name__ == '__main__':
    main()

