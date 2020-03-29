import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import data_grabber
from datetime import datetime

# Data location and variables
sort_var = 'Confirmed'
top_n_regions = 5
y_scale = 1000
data_to_plot = ['Confirmed', 'Deaths']
country = 'US'
dpi = 150
figsize = (1200 / dpi, 675 / dpi)
date_start = np.datetime64('2020-03-01')  # None for min
date_final = np.datetime64('2020-04-01')  # None for max

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
    c_dict['Confirmed_Total'] = np.array(Confirmed)[-1]
    c_dict['Deaths_Total'] = np.array(Deaths)[-1]
    c_dict['Recovered_Total'] = np.array(Recovered)[-1]
    data_dict[c] = c_dict

# Convert dictionary of dictionaries into a dataframe
df = pd.DataFrame(data_dict).T
# Sort by "sort_val" total
df.sort_values('{}_Total'.format(sort_var), axis=0, ascending=False, inplace=True)

# Plot timeline data for each category
plt.style.use('dark_background')
fig, axs = plt.subplots(2, len(data_to_plot), figsize=figsize, dpi=dpi, sharex='all')
months = mdates.MonthLocator()
days = mdates.DayLocator()
for y_str, ax in zip(data_to_plot, axs.T):
    ax0 = ax[0]
    ax1 = ax[1]
    for ci, c in enumerate(df.iloc[0:top_n_regions].index.values):
        y = df.iloc[ci, :][y_str]
        ax0.plot_date(date, y / y_scale, '-', label=c)
        dy = np.diff(y)
        ax1.plot_date(date[1:], dy / y_scale, '-', label=c)
    ax0.xaxis.set_tick_params(labelsize=10)
    ax0.set_title('{} [x{}]'.format(y_str, int(y_scale)))
    ax1.set_title('Daily Change {} [x{}]'.format(y_str, int(y_scale)))
    dst = date[0] if date_start is None else date_start
    den = ax0.get_xlim()[1] if date_final is None else date_final
    ax0.set_xlim((dst, den))
    formatter = mdates.ConciseDateFormatter('%b')
    ax0.xaxis.set_major_locator(months)
    ax0.xaxis.set_major_formatter(formatter)
    ax0.xaxis.set_minor_locator(days)
    ax0.grid(alpha=0.2)
    ax1.grid(alpha=0.2)
now = datetime.utcnow()
axs[1, 0].legend(loc=2, fontsize=8, ncol=int(np.ceil(top_n_regions / 8)))  # 8 rows max
fig.savefig('fig/states.png', bbox_inches='tight')
fig.show()
