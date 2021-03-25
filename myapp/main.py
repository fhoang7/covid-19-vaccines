#!/usr/bin/env python
# coding: utf-8

# ## Preprocessing: Clean data into JSON 
# Inspired by: https://towardsdatascience.com/a-complete-guide-to-an-interactive-geographical-map-using-python-f4c5197e23e0#_=_

# In[1]:


import pandas as pd
import geopandas as gpd
import json


# In[2]:


data = pd.read_csv('../data/clean_data.csv', index_col = 0)
data.head()


# In[3]:


fully_vaccinations = data[['country', 'iso_code', 'date', 'people_fully_vaccinated', 'population']]


# In[4]:


fully_vaccinations.loc[:, 'fully_vac_per_capita'] = fully_vaccinations.loc[:, 'people_fully_vaccinated']/fully_vaccinations.loc[:, 'population']
fully_vaccinations.loc[:, 'date'] = pd.to_datetime(fully_vaccinations.loc[:, 'date'], format='%Y-%m-%d')
fully_vaccinations = fully_vaccinations[['country', 'iso_code', 'date', 'fully_vac_per_capita']]


# In[5]:


fully_vaccinations.head()


# Import geo-location data for world map drawing

# In[6]:


shape = '../data/world_shape/ne_110m_admin_0_countries.shp'
gdf = gpd.read_file(shape)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['geo_country', 'country_code', 'geometry']
gdf = gdf[gdf['geo_country']!= 'Antarctica']


# To prep for `Bokeh`, we need to have a final data format of GeoJSON

# We have countries that do not have reported data but we still want to use their geometry to shade in their countries on a world map. We also have countries that (for a particular date) did not report so we want to use the data last published.

# In[7]:


date = '2021-02-22'

#Filter taking any observations on that date or before
filtered_vaccinations = fully_vaccinations[fully_vaccinations['date'] <= date]

#Group by country and take max and drop duplicate entries
a = filtered_vaccinations.groupby('country').transform(max).drop_duplicates()


# In[8]:


def filtered_data(selectedDate):
    filtered_vaccinations = fully_vaccinations[fully_vaccinations['date'] <= selectedDate]
    a = filtered_vaccinations.groupby('country').transform(max).drop_duplicates()
    b = gdf.merge(a, left_on = 'country_code', right_on = 'iso_code', how = 'left')
    return b


# ## Plotting using Bokeh 

# ### Fully Vaccinated World Map (Heat Map)

# In[12]:


from bokeh.io import output_notebook, show, output_file, save, curdoc
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, ColorBar, Title, DateSlider, Column
from bokeh.palettes import RdYlGn
from bokeh.transform import linear_cmap
from datetime import datetime

current_date = datetime.today().strftime('%Y-%m-%d')
sample = filtered_data(current_date)
sample['date'] = sample['date'].to_string()
sample_json = sample.to_json()

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = sample_json)

#Define a continuous multi-hue color palette. Reverse color order so that we go from red to green.
palette = RdYlGn[11]

palette = palette[::-1]
mapper = linear_cmap(field_name='fully_vac_per_capita', palette=palette ,low=0 ,high=0.5)
#Create color bar. 
color_bar = ColorBar(color_mapper=mapper['transform'], label_standoff=8,width = 500, height = 20,
border_line_color=None,location = "bottom_center", orientation = 'horizontal')

#Define hover tool display
TOOLTIPS = [
    ("country", "@geo_country"),
    ("value", "@fully_vac_per_capita{0,0.0000}")
]


#Create figure object.
p = figure(title = 'Road to COVID-19 Immunity through Vaccination', plot_height = 700 , plot_width = 1100, tools = 'hover',
          tooltips = TOOLTIPS)

#Style Grid/Axes/Title
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.outline_line_color = None
p.axis.visible = False
p.title.align = "center"
p.title.text_font_size = '20pt'

#Add map to figure 
p.patches('xs','ys', source = geosource,fill_color = mapper,
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify figure layout.
p.add_layout(color_bar, 'below')

#Add notes below graph
p.add_layout(Title(text="This world map shows the proportion of the population of countries around the world that has been fully vaccinated", 
                   align="center", text_font_size = '10pt'), "above")
p.add_layout(Title(text="Source: Our World in Data, Kaggle", align="center", text_alpha = 0.5), "below")


def update_plot(attr, old, new):
    selectedDate = str(datepicker.value_as_date)
    new_data = filtered_data(selectedDate)
    new_data['date'] = new_data['date'].to_string()
    new_json = new_data.to_json()
    geosource.geojson = new_json

    
#Datepicker 

datepicker = DateSlider(start = "2020-12-13", end = current_date, step = 1, value = current_date, 
                        width = 200, align = "center", title = "Currently Displaying")
datepicker.on_change('value', update_plot)

# Last Updated on Current Date Text
update_text = "Last Updated on " + str(current_date)
p.add_layout(Title(text=update_text, align="center", text_alpha = 0.5), "below")

#Authorship
p.add_layout(Title(text="Made by Frank Hoang", align="center", text_alpha = 0.5), "below")

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = Column(datepicker,p)
curdoc().add_root(layout)
show(layout)


# In[ ]:




