import numpy as np
import pandas as pd


def my_melt(df, keep_cols=[]):
    """Reshapes DataFrame so each row represents a station interaction"""
    # standardize language
    df = df.rename(columns={col: (col.replace('from_', 'start_')
                                     .replace('to_', 'end_'))
                            for col in df})

    start_cols = [col for col in df if col.startswith('start_')]
    end_cols = [col for col in df if col.startswith('end_')]

    df = pd.concat([(df.loc[:,keep_cols + start_cols]
                       .rename(columns={col: col.replace('start_','')
                                        for col in start_cols})
                       .assign(type='departure')),
                    (df.loc[:,keep_cols + end_cols]
                             .rename(columns={col: col.replace('end_','')
                                              for col in end_cols})
                       .assign(type='arrival'))],
                   sort=False, axis=0)

    return df


def add_empty_rows(df, fill_series, constants=['station_id', 'lat','lon']):
    """Add empty rows to DataFrame. Cols other than constants fill with NaN

    fill_series: pd.Series representing unique values that should be represented
                 in the returned DataFrame
    """
    if fill_series.name not in df:
        raise ValueError('fill_series name must be column of DataFrame')

    fill_df = pd.merge(pd.DataFrame(fill_series).assign(key=1),
                       df[constants].drop_duplicates().assign(key=1),
                       on='key', how='left')
    fill_df = fill_df.drop(columns=['key'])

    fill_df = fill_df.merge(df, on=([fill_series.name] +  constants),
                            how='left')

    fill_df = fill_df.sort_values((constants + [fill_series.name]))

    return fill_df
