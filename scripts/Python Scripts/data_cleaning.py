#!/usr/bin/env python
# coding: utf-8

# ## Libraries

# In[1]:


import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer


# ## Read in Data and display info about the data

# In[2]:


data = pd.read_csv('../../data/country_vaccinations.csv')
data.head()


# In[3]:


data.dtypes


# ## Data Completeness

# The code below shows that almost every column in the dataframe is missing data values. 

# In[4]:


data.isnull().sum()


# ### Qualitative Variables (ISO_Code & Source_Name) Missing Values

# The ISO_code which is an abbreviation of the country name is missing, so let's see which countries are missing these values.

# In[5]:


missing_iso_countries = list(data[data['iso_code'].isna()]['country'].unique())
print(missing_iso_countries)


# For the countries that have missing values, does the dataframe contain any rows that contain the corresponding ISO values?

# In[6]:


for country in missing_iso_countries:
    print(country, data[data['country'] == country]['iso_code'].notna().sum())


# After doing some digging on the internet, I found out that England, Northern Ireland, Scotland, and Wales are collectively referred to as the United Kingdom, so we need to confirm if the current UK vaccination numbers are the proper summation of the vaccinations reported separately for England, Northern Ireland, Scotland, and wales. If yes, we can drop the England/Northern Ireland/Scotland/Wales rows as they are repetitive values. If no, we can either adjust to the United Kingdom numbers to match the true values, or drop the United Kingdom and use the separate regions' numbers. 

# In[7]:


uk_data = data[data['country'] == 'United Kingdom']
eng_data = data[data['country'] == 'England']
ni_data = data[data['country'] == 'Northern Ireland']
scot_data = data[data['country'] == 'Scotland']
wales_data = data[data['country'] == 'Wales']


# In[8]:


uk_data['daily_vaccinations'].sum() 


# In[9]:


eng_data['daily_vaccinations'].sum() + ni_data['daily_vaccinations'].sum() + scot_data['daily_vaccinations'].sum() + wales_data['daily_vaccinations'].sum()   


# The numbers are pretty close minus some missing values, so we can utilize the United Kingdom numbers. 

# In[10]:


drop_countries_indices = data[(data['country'] == 'England') | (data['country'] == 'Northern Ireland') | (data['country'] == 'Wales') | (data['country'] == 'Scotland')].index
data.drop(drop_countries_indices, inplace = True) 


# I have know resolved the missing values in the ISO_Code column. Now let's look at the other qualitative column: Source_name

# In[11]:


data.isnull().sum()


# In[12]:


data[data['source_name'].isna()]


# All the missing values for the source name are for the country Belize which reports its statistics on Facebook. However, the Facebook links are dead, so we don't know what Facebook page it is. Let's just assign the source to just Facebook then.
# 
# Note: This is a temporary fix since if we have missing sources in the future that are not from Belize Facebook pages, we will need to be more verbose in our NA fills.

# In[13]:


data['source_name'] = data['source_name'].fillna('Facebook')


# In[14]:


data.isnull().sum()


# ### Quantiative Variables Missing Values

# In the data logs, `daily_vaccinations_raw` indicates vaccination numbers stored in one format while `daily_vaccinations` indicates vaccination numbers stored in an alternative format. Since `daily vaccinations` contains more complete values, let's port values from `daily_vaccinations_raw` into `daily_vaccinations` to see if we can fill in the missing values.

# In[15]:


data.daily_vaccinations = np.where(data.daily_vaccinations_raw.notna() & data.daily_vaccinations.isna(), data.daily_vaccinations_raw, data.daily_vaccinations)


# Now that we have ported all available complete values from `daily_vaccinations_raw` to store it in `daily_vaccinations`, we can drop `daily_vaccinations_raw`.

# In[16]:


data.drop(columns = ['daily_vaccinations_raw'], inplace = True)


# It will be impossible to fill in numerical columns if we don't have any data. Let's store those rows in a separate dataframe that we could use to report on data completeness if we choose.

# In[17]:


missing_num_indices = data[(data['total_vaccinations'].isna()) & (data['people_vaccinated'].isna()) & (data['people_fully_vaccinated'].isna()) & (data['daily_vaccinations'].isna()) & (data['total_vaccinations_per_hundred'].isna()) & (data['people_vaccinated_per_hundred'].isna() & (data['people_fully_vaccinated_per_hundred'].isna()) & (data['daily_vaccinations_per_million'].isna()))].index
missing_all_num_data = data[(data['total_vaccinations'].isna()) & (data['people_vaccinated'].isna()) & (data['people_fully_vaccinated'].isna()) & (data['daily_vaccinations'].isna()) & (data['total_vaccinations_per_hundred'].isna()) & (data['people_vaccinated_per_hundred'].isna() & (data['people_fully_vaccinated_per_hundred'].isna()) & (data['daily_vaccinations_per_million'].isna()))]


# In[18]:


data.drop(missing_num_indices, inplace = True) 


# If we have any `daily vaccinations` that are NaN, we can now fill it in with a zero since we have no other to impute the data.

# In[19]:


data['daily_vaccinations'] = data['daily_vaccinations'].fillna(0)


# The remaining columns that have significant missing values are `total_vaccinations`, `total_vaccinations_per_hundred`, `people_vaccinated`, `people_vaccinated_per_hundred`, `people_fully_vaccinated`, and `people_fully_vaccinated_per_hundred`. These are columns that have missing values and subsequent columns that are proportions that rely on those missing values result in NaNs as well. So we will have to just remove these rows from the dataframe.

# In[20]:


data[data['total_vaccinations'].isna()]


# I am pulling in a separate CSV to get population numbers by country, so we can calculate the per capita columns. That should allow us to resolve the missing values in `daily_vaccinations_per_million`.

# In[21]:


population = pd.read_csv('../../data/world_population.csv')
population = population[['Country Code', '2019']]
population.rename(columns = {"2019": "population"}, inplace = True)
population.head()


# Now we can join this dataframe with the vaccination data to insert the population data.

# In[22]:


data_with_population = data.merge(population, left_on = 'iso_code', right_on = 'Country Code')
data_with_population.drop(columns = ['Country Code'], inplace = True)
data_with_population.head()


# In[23]:


data_with_population['daily_vaccinations_per_million'] = data_with_population['daily_vaccinations']/(data_with_population['population']/1000000)
data_with_population.head()


# We will fill in the rest of the NaNs with zeroes since it is data that was not reported. 

# In[24]:


data_with_population = data_with_population.fillna(0)


# In[26]:


data_with_population.to_csv('../../data//clean_data.csv')
data_with_population.to_csv('../../myapp/data/clean_data.csv')


# In[ ]:




