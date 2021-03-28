#!/usr/bin/env python
# coding: utf-8

# In[1]:

from IPython import get_ipython
get_ipython().system('pip install kaggle')
get_ipython().system('pip install python-dotenv')


# In[2]:


# read in Kaggle API Credentials from .env
from dotenv import load_dotenv
import os

from pathlib import Path 
env_path = Path('../../') / '.env'
load_dotenv(dotenv_path=env_path)


# In[3]:


# download the latest COVID-19 vaccination data
get_ipython().system('kaggle datasets download -d gpreda/covid-world-vaccination-progress')


# In[4]:


#unzip into the /data folder
import zipfile as zf
files = zf.ZipFile("./covid-world-vaccination-progress.zip", 'r')
files.extractall('../../data')
files.close()


# In[ ]:




