import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import data_grabber
from datetime import datetime

# Data location and variables
sort_var = 'Confirmed'
top_n_regions = 10
y_scale = 1000
data_to_plot = ['Confirmed', 'Deaths']
dpi = 150
figsize = (1200 / dpi, 675 / dpi)
date_start = np.datetime64('2020-02-01')  # Data starts at 2020-01-22
date_final = np.datetime64('2020-04-01')  # None for max

# Get dataframe for all data files
df_all = data_grabber.get_covid_df()
date = np.sort(df_all['Date'].unique())  # x-axis for plot

# Combine each country's data into a single row by summing the "Province/State"
data_dict = dict()
for c in df_all['Country_Region'].unique():
    dfc = df_all[df_all['Country_Region'] == c]  # Dataframe for current region
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
fig, axs = plt.subplots(len(data_to_plot), 1, figsize=figsize, dpi=150, sharex=True)
months = mdates.MonthLocator()
days = mdates.DayLocator()
for y_str, ax in zip(data_to_plot, axs):
    for ci, c in enumerate(df.iloc[0:top_n_regions].index.values):
        y = df.iloc[ci, :][y_str]
        ax.plot_date(date, y / y_scale, '.-', label=c)
    ax.xaxis.set_tick_params(labelsize=10)
    if y_scale == 1:
        ax.set_yscale('log')
        ax.set_ylabel(y_str)
    else:
        ax.set_ylabel('{} [x{}]'.format(y_str, int(y_scale)))
    dst = date[0] if date_start is None else date_start
    den = ax.get_xlim()[1] if date_final is None else date_final
    ax.set_xlim((dst, den))
    formatter = mdates.ConciseDateFormatter('%b')
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(days)
    ax.grid()
now = datetime.utcnow()
axs[0].set_title('Generated on {}'.format(now.strftime('%b %d %Y %H:%M:%S UTC')))
axs[0].legend(loc=2, fontsize=8, ncol=int(np.ceil(top_n_regions / 8)))  # 8 rows max
if y_scale == 1:
    fig.savefig('fig/countries_log.png', bbox_inches='tight')
else:
    fig.savefig('fig/countries_lin.png', bbox_inches='tight')
fig.show()
