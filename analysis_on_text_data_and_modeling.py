# -*- coding: utf-8 -*-
"""Analysis-on-text-data-and-Modeling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NHtUNqMdkIRHGi5zsAlrQRWIn8o111YL
"""

pip install pycaret



"""# Internship Assesment

**`Problem Statement`**:

We have a list of trades of different simulations (eash is numbered and based on different settings). Each simulation represents a different permutation of settings used to run them. These are results of a trading algorithm which decides when and how to buy or sell different assets. We want to know what permutation will work for Wednesday 15:00 (for example) and we assume that each day of the week and hour of the day has a different profile as certain activities are based on news which are the same hours of the days. etc. 

Selecting the best permutation (best by aggregated profit & loss) for a future period is needed by selecting day of the week and time of the day. You can take any feature you want, and you can use anything which will make the prediction better (you can even download Gold prices and use it's value and volatility if you think this might help) so long as your prediction is the profit/loss. The different ML method / model is upon your selection.

**`Target Variable`** : 

**Profit/Loss**

**Importing Libraries**
"""

# to deal with dataframes
import pandas as pd
pd.set_option('display.max_columns',None)  
pd.set_option('display.expand_frame_repr',False)
pd.set_option('display.max_colwidth',100)
import os
import glob2

# for mathematical operations
import numpy as np

# for visualization
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import matplotlib.pyplot as plt # matplot

import seaborn as sns # seaborn
sns.set_style('whitegrid')

# for ml in pycaret
from pycaret.regression import *


import warnings
warnings.filterwarnings('ignore')

from google.colab import drive
drive.mount('/content/drive')

"""**Reading Datasets**"""

# giving the path where all files are saved
files=glob2.glob('//content//drive//MyDrive//Colab Notebooks//mayuri//*.txt')

# reading each file from folder and saving them into a list (it will also remove the last row from each dataframe)
dfs=[pd.read_csv(f,sep="\t",skipfooter=1) for f in files]

# concatenating all dataframes
df=pd.concat(dfs,ignore_index=True)
df

df.to_csv('Data.csv',index=False)

"""**Taking a look through Dataset**"""

# checking for stats
df.describe(include='all').T

# checking for unique levels in each attribute (especially in categorical attributes)
df.nunique()

df=df.drop(columns=['Note'])

# checking for missing values
df.isnull().sum()/len(df)*100

"""# **Preprocessing**

1. We will **remove entries** which have **time difference/duration of more than 24 hours**
"""

# removing BP and EP
df['Entry DateTime']=df['Entry DateTime'].str.replace('BP','')
df['Exit DateTime']=df['Exit DateTime'].str.replace('EP','')

# converting into datetime
df['Entry DateTime']=pd.to_datetime(df['Entry DateTime'])
df['Exit DateTime']=pd.to_datetime(df['Exit DateTime'])

df['Difference']=df['Exit DateTime'] - df['Entry DateTime']
df['Difference']=df['Difference'] / np.timedelta64(1,'h')

# subsetting
df[df['Difference']>=24.00]

"""We have 110 entries, where the difference is more than 24 hours, we will remove them from our data set"""

df=df[df['Difference']<24.00]

"""2. We will convert **Exit Efficiency**, **Entry Efficiency**, **Total Efficiency** and  **FlatToFlat Profit/Loss (C)**  to numerical attributes."""

# removing % and F
df['Exit Efficiency']=df['Exit Efficiency'].str.replace('%','')
df['Entry Efficiency']=df['Entry Efficiency'].str.replace('%','')
df['Total Efficiency']=df['Total Efficiency'].str.replace('%','')

df['FlatToFlat Profit/Loss (C)']=df['FlatToFlat Profit/Loss (C)'].str.replace('F','')

# converting datatype
df[['Exit Efficiency',
    'Entry Efficiency',
    'Total Efficiency',
    'FlatToFlat Profit/Loss (C)']]=df[['Exit Efficiency',
                                       'Entry Efficiency',
                                       'Total Efficiency',
                                       'FlatToFlat Profit/Loss (C)']].astype('float64')

"""## Feature Engineering
We will create some features from our existing features to reduce dimension of our dataset
"""

df['Price Diff.']=df['Exit Price'] - df['Entry Price']
df['Open Quantity Diff.']=df['Max Closed Quantity'] - df['Max Open Quantity']
df['Price While Open Diff.']=df['High Price While Open'] - df['Low Price While Open']
df['Efficiency Diff.']=df['Exit Efficiency'] - df['Entry Efficiency']
df['FTF Max Open P/L Diff.']=df['FlatToFlat Max Open Profit (C)'] - df['FlatToFlat Max Open Loss (C)']
df['Max Open P/L Diff.']=df['Max Open Profit (C)'] - df['Max Open Loss (C)']
df['Position Quantity Diff.']=df['Close Position Quantity'] - df['Open Position Quantity']

df=df.drop(columns=['Exit Price','Entry Price',
                    'Max Closed Quantity','Max Open Quantity',
                    'High Price While Open','Low Price While Open',
                    'Exit Efficiency','Entry Efficiency',
                    'FlatToFlat Max Open Profit (C)','FlatToFlat Max Open Loss (C)',
                    'Max Open Profit (C)','Max Open Loss (C)',
                    'Close Position Quantity','Open Position Quantity',
                    'Symbol','Entry DateTime','Exit DateTime','Duration'])

"""## EDA

**Profit/Loss**
"""

# box plot
fig=px.box(df,
           y='Profit/Loss (C)',
           labels={'Profit/Loss (C)':'Profit/Loss'},
           title='Distribution of Profit Loss')
fig.show()

"""We will remove the entry from **Profit/Loss** attribute whose value is less than -4k."""

df_final=df[df['Profit/Loss (C)']> -4000.00]

"""**Corelation Plot**"""

f,ax=plt.subplots(figsize=(10,9.5))
sns.heatmap(df_final.corr(),
            cmap='coolwarm',
            annot=True);

"""We see a *Perfect Corelation* between **Commission** & **Trade Quantity** so we will remove one of the attribute from our dataset.

## PyCaret
"""

# preprocessing
preprocessing_parameters=setup(df,
                               ignore_features=['Commission (C)'],
                               target='Profit/Loss (C)',
                               categorical_features=['Trade Type'],
                               numeric_features=['Trade Quantity','Commission (C)',
                                                 'Open Quantity Diff.','Position Quantity Diff.'], # because pycaret is considering them as categorical variables
                               session_id=1212,
                               n_jobs=-1,
                               normalize=True,
                               normalize_method='minmax',
                               transform_target=True,
                               transform_target_method='yeo-johnson')

# compare all models
best_model=compare_models(round=10,
                          include=['lightgbm'],
                          sort='RMSE')

# hyperparameter tuning
tuned_best_model=tune_model(best_model,
                            round=10,
                            n_iter=10,
                            optimize='RMSE')

# important features
plot_model(tuned_best_model,plot='feature_all')

