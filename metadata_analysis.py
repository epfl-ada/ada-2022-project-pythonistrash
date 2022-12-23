from base_imports import *
from plotly.graph_objs import Figure

import plotly.express as px


def extract_release_year(df):
    """
    Extracts the release year from the release date as a new column
    :param df: the dataframe
    :return: The extended dataframe
    """
    df['Movie release year'] = df['Movie release date'].astype(str).str[:4]
    df = df[df["Movie release year"].str.contains("nan") == False].copy()
    df['Movie release year'] = df['Movie release year'].apply(lambda x: int(x))
    return df


def plot_by_year(df, prefix: str, metric: str, col: str, log_yscale=True):
    """
    Plot a year grouped column
    :param df: said column
    :param prefix: str
    :param metric: what is being plotted
    :param log_yscale: bool
    :param col: where to find data in df
    """
    fig, ax = plt.subplots()

    fig.set_size_inches(16, 8)
    ax.set_xlabel('Release year', fontsize=18)
    ax.set_ylabel(f'{prefix} {metric}', fontsize=16)
    ax.set_title(f'{prefix} {metric} by year', fontsize=16)
    ax.set_label("Floats")
    if prefix == "Mean":
        l = sns.lineplot(data=df, x="startYear", y=col, legend="brief")
    else:
        l = sns.lineplot(data=df, legend="brief")
    if log_yscale:
        l.set_yscale("log")
    plt.xticks(rotation=90)

    plt.show()


def remove_first_and_last_chars(input_str: str) -> str:
    """
    Remove the first and last char of a string.
    :param input_str
    :return: processed string
    """
    if len(input_str) < 2:
        return ""
    return input_str[1:-1]


def separate_id_from_data(paired_string: str, remove_brackets=True) -> (str, str):
    """
    Separates "{"FreebaseID": "some string"}" strings into ("FreebaseID", "some string") tuples.
    :param paired_string: input paired string
    :param remove_brackets: if True, remove the leading and trailing curly brackets
    :return: said tuple of strings
    """
    if remove_brackets:
        paired_string = remove_first_and_last_chars(paired_string)

    ls = paired_string.split(":")
    for i, s in enumerate(ls):
        ls[i] = remove_first_and_last_chars(s.strip())

    if len(ls) < 2:
        return None, None
    return ls[0], ls[1]


def separate_ids_from_list_data(list_paired_string: str) -> (list, list):
    """
    Separates "{"FreebaseID1": "some string 1", "FreebaseID2": "some string 2", etc.}" strings
    into two lists: (["FreebaseID1", "FreebaseID2", ...], ["some string 1", "some string 2", ...]).
    :param list_paired_string: input list of pairs as string
    :return: said tuple of lists
    """
    list_paired_string = remove_first_and_last_chars(list_paired_string)
    split_pairs = list_paired_string.split(",")
    tupled_pairs = [separate_id_from_data(pair, remove_brackets=False) for pair in split_pairs]
    return [p[0] for p in tupled_pairs], [p[1] for p in tupled_pairs]


def col_to_col_values(column_name: str) -> str:
    """
    String formatting for value column names
    :param column_name: original column name
    :return: said formatted string
    """
    return f"{column_name}: values"


def append_processed_columns(df: pd.DataFrame, column_name: str):
    """
    Separate Freebase IDs from values
    :param df: data, modified in place
    :param column_name: name of column where to separate {Freebase ID: value} pairs
    """
    vals = df[column_name].apply(separate_ids_from_list_data).values.copy()
    df[f"{column_name}: Freebase IDs"] = [vals[i][0] for i in range(len(vals))]
    df[col_to_col_values(column_name)] = [vals[i][1] for i in range(len(vals))]


def distinct_values(df: pd.DataFrame, column_name: str, raw_name: bool = False) -> set:
    """
    Get all values from a column
    :param column_name: said column
    :return: set of values
    """
    col_name = column_name if raw_name else col_to_col_values(column_name)
    return set.union(*df[col_name].apply(set).values)


def name_appended_column(prefix: str, val: str) -> str:
    """
    Format column name
    :param prefix: str
    :param val: str
    :return: str
    """
    return f"{prefix}: {val}"


def append_indicator_columns(df: pd.DataFrame, all_values: set, column_name: str, prefix: str) -> pd.DataFrame:
    """
    Add columns to the right of a dataframe indicating whether a particular value is present or not
    in some initial column listing values of the same family
    :param df: data (not modified)
    :param all_values: all possible values
    :param column_name: column to inspect
    :param prefix: str
    :return: Dataframe with added columns
    """
    cols = [df[col_to_col_values(column_name)]
            .apply(lambda x: 1 if val in x else 0)
            .rename(name_appended_column(prefix, val))
            for val in all_values]
    cols.insert(0, df)
    return pd.concat(cols, axis=1)


def retrieve_n_most_frequent(df: pd.DataFrame, n: int, all_vals: list[str], prefix: str) -> list:
    """
    Retrieve the n most frequent genres, languages or countries, sorted in descending order
    of frequency
    :param df: data
    :param n: integer, max number of values to retrieve
    :param all_vals: all possible values
    :param prefix: str
    :return: said list
    """

    def comparator(val1, val2):
        mean_val1 = df[name_appended_column(prefix, val1)].mean()
        mean_val2 = df[name_appended_column(prefix, val2)].mean()
        return mean_val1 - mean_val2

    return sorted(all_vals, key=cmp_to_key(comparator), reverse=True)[:n]


def retrieve_frequent(df: pd.DataFrame, all_vals: list, prefix: str, freq_threshold=0.05) -> list:
    """
    Filter the values with a sufficiently high frequency
    :param df: data
    :param all_vals: all possible values
    :param prefix: str
    :param freq_threshold: float
    :return: list of sufficiently frequent values
    """
    return list(
        filter(
            lambda val: df[name_appended_column(prefix, val)].mean() > freq_threshold,
            all_vals
        )
    )


def map_to_col_names(data_names: list, prefix: str) -> list:
    """
    Convert data values into column names
    :param data_names: list of  data values
    :param prefix: str
    :return: list of formatted column names
    """
    f = lambda x: name_appended_column(prefix, x)
    return list(map(f, data_names))


def find_correlated_metadata(df: pd.DataFrame, freq_data: list, success_metric: str, prefix: str, sig_level=0.05) \
        -> list:
    """
    Among a list of sufficiently frequent data taken from the metadata dataframe,
    find the values such that they are correlated to a movie's success metric with
    a p-value less than sig-level.
    :param df: input dataframe
    :param freq_data: column names to search in
    :param success_metric: str, name of column in df
    :param prefix: str
    :param sig_level: significance level, defaults to 5%
    :return: described list
    """
    correlated_data = []

    for value in freq_data:
        res = stats.spearmanr(df[success_metric], df[name_appended_column(prefix, value)])
        if res.pvalue < sig_level:
            correlated_data.append(value)
    return correlated_data


def plot_metadata_frequency_against_metric(df: pd.DataFrame, prefix: str, titled_data: list, success_metric: str,
                                           title: str, log_scale=True):
    """
    Generating a grid of histograms
    :param df: data
    :param prefix: str
    :param titled_data: titles of data, to be converted to column names
    :param success_metric: measured column name
    :param title: str, figure title
    :param log_scale: determines the scale of the axes
    """

    # Making the data fit into a square grid...
    squares = np.arange(8) ** 2
    shifted_squares = squares - len(titled_data)
    smallest_big_enough_square = squares[np.argmax(shifted_squares > 0) - 1]

    tested_data = map_to_col_names(titled_data, prefix)[:smallest_big_enough_square]
    size = int(np.sqrt(smallest_big_enough_square))

    fig, ax = plt.subplots(size, size, figsize=(11, 11), sharex=True)
    for i in range(smallest_big_enough_square):
        sbplt = ax[i % size, math.floor(i / size)]
        sns.histplot(ax=sbplt, data=df[df[tested_data[i]] == 1][success_metric], log_scale=log_scale)
        sbplt.set_title(titled_data[i])

    fig.suptitle(title, fontsize=18)
    fig.tight_layout()


def mapmaker(df: pd.DataFrame, target_col: str, color_continuous_scale="Greens", width=800, height=500) -> Figure:
    """
    Create map representation of a feature.
    :param df: data
    :param target_col: feature to represent as colors
    :param color_continuous_scale: color palette
    :param width: int
    :param height: int
    :return: Map as a Figure plotly object
    """
    cntries_map = px.choropleth(
        data_frame=df,
        locationmode="country names",
        locations=df.index,
        color=target_col,
        color_continuous_scale=color_continuous_scale,
        range_color=(df[target_col].quantile(0.1), df[target_col].quantile(0.9))
    )
    cntries_map.update_layout(width=width, height=height)
    return cntries_map


def savemap(fig: Figure, path: str) -> None:
    """
    Save given map to memory
    :param fig: map as Figure plotly object
    :param path: str
    """
    with open(path, "w") as f:
        f.write(fig.to_html())


def linear_reg(df, success_metric, prefix_var, list_vars):
    """
    Perform linear regression over the given list of features and response variable.
    :param df: data
    :param success_metric: response variable
    :param prefix_var: str
    :param list_vars: str
    :return:
    """
    def formula_rhs_string(prefix, list_all_vars):
        return " + ".join(list(map(lambda x: f'C(pat.Q("{name_appended_column(prefix, x)}"))', list_all_vars)))

    return smf.ols(formula=success_metric + ' ~ ' + formula_rhs_string(prefix_var, list_vars), data=df).fit()


def add_mean_to_series(ser: pd.Series, idx_name="Mean") -> pd.Series:
    """
    Find the mean val in a series and add it to all other values
    :param ser: Series
    :param idx_name: label of mean
    :return: new series with mean summed to all other values then dropped
    """
    val = ser[ser.index == idx_name].values[0]
    ser = ser + val
    ser = ser.drop(idx_name)
    return ser
