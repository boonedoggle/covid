import os, tempfile, git, datetime
import pandas as pd


def _get_data_folder(git_url, git_dir, data_sub_dir):
    if not os.path.isdir(git_dir):  # Clone repo if it does not exist
        print('Cloning Repository: {}'.format(git_url))
        git.Repo.clone_from(git_url, git_dir)
    else:  # Pull the latest if repo has already been cloned
        print('Updating data repo')
        git.cmd.Git(git_dir).pull()
    print('Done getting data')
    return os.path.join(git_dir, data_sub_dir)


def get_covid_df(git_url=None, git_dir=None, data_sub_dir=None):
    # Get data from repo and get list of the csv data files
    if git_url is None:
        git_url = 'https://github.com/CSSEGISandData/COVID-19.git'
    if git_dir is None: # Save to temporary location
        git_dir = os.path.join(tempfile.gettempdir(), os.path.basename(git_url).split('.')[0])
    if data_sub_dir is None:
        data_sub_dir = 'csse_covid_19_data/csse_covid_19_daily_reports'
    data_folder = _get_data_folder(git_url, git_dir, data_sub_dir)
    data_file_names = [p for p in os.listdir(data_folder) if p.endswith('.csv')]
    
    # Combine each csv data file into a common dataframe
    list_of_df = []
    for filename in data_file_names:
        df = pd.read_csv(os.path.join(data_folder, filename), index_col=None, header=0)
        df['Date'] = datetime.datetime.strptime(filename.split('.')[0], '%m-%d-%Y')
        list_of_df.append(df)
    df0 = pd.concat(list_of_df, axis=0, ignore_index=True)
    
    # Some files have "Country_Region" and Some have "Country/Region". Combine them
    df0['Country_Region'].update(df0['Country/Region'])
    df0.drop('Country/Region', axis=1, inplace=True)  # Remove redundant column

    # Some files have "Province_State" and Some have "Province/State". Combine them
    df0['Province_State'].update(df0['Province/State'])
    df0.drop('Province/State', axis=1, inplace=True)  # Remove redundant column
    
    # Some files have "Mainland China" & some have "China". Rename "Mainland China"
    df0.loc[df0.Country_Region == 'Mainland China', 'Country_Region'] = 'China'
    
    return df0


