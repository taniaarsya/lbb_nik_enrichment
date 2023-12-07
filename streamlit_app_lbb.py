import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(layout='wide')

# --- READ DATA ---
customer_merge = pd.read_pickle('data_lbb/customer_merge.pkl')
coord = pd.read_csv('data_lbb/coordinate.csv')

# --- ROW 1 ---
st.write('# Customer Performance Dashboard')
st.write("""This customer performance dashboard provides an in-depth understanding of customer profiles based on several key criteria, including province, gender, profession and income level. The province analysis provides insights into the distribution of customers across regions, while the gender breakdown provides a balanced picture of male and female customers. In addition, it provides information related to the profession of customers, which can provide an in-depth view of market segmentation. 
         Income level analysis provides additional insights into customer purchasing power and spending patterns. 
         This dashboard aims to provide a comprehensive understanding of customer performance, enabling more informed and strategic decision-making.""")

# --- ROW 2 ---
col1, col2 = st.columns(2)

## --- LINE PLOT ---

# data: line plot
df_join = pd.crosstab(index=customer_merge['Profession'], columns='Profession_count', colnames=[None])
df_join = df_join.reset_index()

# Membuat line plot interaktif
fig = go.Figure()

# Menambahkan line plot untuk frekuensi bergabung
fig.add_trace(go.Scatter(x=df_join['Profession'], y=df_join['Profession_count'],
                         mode='lines+markers', name='Mumber of Customer',
                         line=dict(color='red')))

# Menambahkan secondary y-axis untuk Annual Income
fig.update_layout(yaxis=dict(title='Number of Customer', side='left', rangemode='tozero'),
                  yaxis2=dict(title='Annual Income', overlaying='y', side='right'))

# Menambahkan bar plot untuk rata-rata Annual Income
avg_income = customer_merge.groupby('Profession')['Annual_Income'].sum().reset_index()
fig.add_trace(go.Bar(x=avg_income['Profession'], y=avg_income['Annual_Income'],
                     name='Average Annual Income', marker=dict(color='skyblue'),
                     yaxis='y2'))

# Menambahkan informasi hover
fig.update_traces(hovertemplate='Profession: %{x}<br>Count: %{y}',
                  selector=dict(type='scatter'))

# Menampilkan visualisasi
fig.update_layout(title='Number of customer and Average Annual Income by Profession',
                  xaxis=dict(title='Profession'),
                  legend=dict(x=0.7, y=1),
                  width=800, 
                  height=500,
                  showlegend=True)

col1.write('### Average Annual Income Based on Profession')
col1.plotly_chart(fig, use_container_width=True)


# --- MAP PLOT ---
data: map
prov_gender = pd.crosstab(index=customer_merge['province'],
                        columns=customer_merge['gender'], colnames=[None])
prov_gender['Total'] = prov_gender['Female'] + prov_gender['Male']
df_map = prov_gender.merge(coord, on='province')

# plot: map
plot_map = px.scatter_mapbox(data_frame=df_map, lat='latitude', lon='longitude',
                             mapbox_style='carto-positron', zoom=3,
                             size='Total',
                             hover_name='province',
                             hover_data={'Male': True,
                                         'Female': True,
                                         'latitude': False,
                                         'longitude': False})

col2.write('### Number of Customer across Indonesia')
col2.plotly_chart(plot_map, use_container_width=True)

# --- ROW 3 ---
st.divider()
col3, col4 = st.columns(2)

## --- INPUT SELECT ---
input_select = col3.selectbox(
    label='Select Profession',
    options=customer_merge['Profession'].unique().sort_values()
)

## --- INPUT SLIDER ---
input_slider = col4.slider(
    label='Select age range',
    min_value=customer_merge['age'].min(),
    max_value=customer_merge['age'].max(),
    value=[25,55]
)

min_slider = input_slider[0]
max_slider = input_slider[1]

# --- ROW 4 ---
col5, col6 = st.columns(2)

## --- BARPLOT ---
# input_select = "Engineer"  # Ganti dengan nilai sebenarnya dari input

# Filter berdasarkan departemen yang dipilih
employ_cs = customer_merge[customer_merge['Profession'] == input_select]

# Membuat tabel frekuensi generasi
df_gen = pd.crosstab(index=employ_cs['generation'], columns='num_people', colnames=[None])
df_gen = df_gen.reset_index()

# Plot Pie Chart
pie_chart = px.pie(df_gen, names='generation', values='num_people',
                   title=f'Customer Count per Generation in {input_select} Profession.',
                   labels={'num_people': 'Customer Count', 'generation': 'Generation'},
                   hole=0.3)  # Parameter hole menambahkan cincin tengah untuk mempercantik


col5.write(f'### Customer Count per Generation in {input_select} Profession.') # f-string
col5.plotly_chart(pie_chart, use_container_width=True)

## --- MULTIVARIATE ---

min_slider = 20  # Ganti dengan nilai slider sesuai kebutuhan
max_slider = 40  # Ganti dengan nilai slider sesuai kebutuhan
employ_age = customer_merge[customer_merge['age'].between(left=min_slider, right=max_slider)]

# Menyusun data berdasarkan profesi dan jenis kelamin
dept_gender = pd.crosstab(index=customer_merge['Profession'],
                          columns=customer_merge['gender'],
                          colnames=[None])
dept_gender_melt = dept_gender.melt(ignore_index=False, var_name='gender', value_name='num_people')
dept_gender_melt = dept_gender_melt.reset_index()

# Plot Grouped Bar Chart
bar_chart = px.bar(dept_gender_melt,
                   x='Profession',
                   y='num_people',
                   color='gender',
                   labels={'num_people': 'Customer Count', 'Profession': 'Profession'},
                   title='Customer Count by Profession and Gender',
                   barmode='group')

col6.write(f'### Gender by Profession')
col6.plotly_chart(bar_chart, use_container_width=True)

scatter_plot = px.scatter(customer_merge, x='Work_Experience', y='Annual_Income',
                         title='Annual Income vs Work Experience',
                         labels={'Work_Experience': 'Work Experience', 'Annual_Income': 'Annual Income'},
                         hover_data={'Profession': True})

# Menambahkan regresi linier
scatter_plot.update_traces(
    line=dict(dash='solid', color='darkgray'),
    selector=dict(mode='markers')
)

# Menampilkan visualisasi di Streamlit
st.plotly_chart(scatter_plot, use_container_width=True)
