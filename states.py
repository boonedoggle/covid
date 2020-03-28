import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import data_grabber
from datetime import datetime

# Data location and variables
sort_var = 'Confirmed'
top_n_regions = 15
y_scale = 1000
data_to_plot = ['Confirmed', 'Deaths']
country = 'US'

# Get dataframe for all data files
df_all = data_grabber.get_covid_df()
date = np.sort(df_all['Date'].unique())  # x-axis for plot

# Get sub-dataframe for country of interest
df = df_all[df_all['Country_Region'] == country]

data_dict = dict()
for c in df['Province_State'].unique():
    dfc = df[df['Province_State'] == c]  # Dataframe for current region
    Confirmed = []
    Deaths = []
    Recovered = []
    for d in date:
        # Get dataframe for current country and date and sum states together
        dfd = dfc[dfc['Date'] == d]
        Confirmed.append(dfd['Confirmed'].sum())
        Deaths.append(dfd['Deaths'].sum())
        Recovered.append(dfd['Recovered'].sum())
    # Create a dictionary with this country's data
    c_dict = dict()
    c_dict['Confirmed'] = np.array(Confirmed)
    c_dict['Deaths'] = np.array(Deaths)
    c_dict['Recovered'] = np.array(Recovered)
    # Calculate the total for each category to plot the top countries ones
    c_dict['Confirmed_Total'] = np.array(Confirmed).sum()
    c_dict['Deaths_Total'] = np.array(Deaths).sum()
    c_dict['Recovered_Total'] = np.array(Recovered).sum()
    data_dict[c] = c_dict

# Convert dictionary of dictionaries into a dataframe
df = pd.DataFrame(data_dict).T
# Sort by "sort_val" total
df.sort_values('{}_Total'.format(sort_var), axis=0, ascending=False, inplace=True)

# Plot timeline data for each category
fig, axs = plt.subplots(len(data_to_plot), 1, figsize=(11, 8.5), dpi=150, sharex=True)
months = mdates.MonthLocator()
days = mdates.DayLocator()
for y_str, ax in zip(data_to_plot, axs):
    for ci, c in enumerate(df.iloc[0:top_n_regions].index.values):
        y = df.iloc[ci, :][y_str]
        ax.plot_date(date, y / y_scale, '.-', label=c)
    ax.xaxis.set_tick_params(rotation=75, labelsize=10)
    if y_scale == 1:
        ax.set_yscale('log')
        ax.set_ylabel(y_str)
    else:
        ax.set_ylabel('{} [x{}]'.format(y_str, int(y_scale)))
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_minor_locator(days)
    ax.grid()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
now = datetime.utcnow()
axs[0].set_title('Generated on {}'.format(now.strftime('%b %d %Y %H:%M:%S UTC')))
if y_scale == 1:
    fig.savefig('fig/states_log.png')
else:
    fig.savefig('fig/states_lin.png')
fig.show()
