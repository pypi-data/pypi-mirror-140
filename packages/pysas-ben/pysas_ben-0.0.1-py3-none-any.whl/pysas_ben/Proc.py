import pandas as pd
import numpy as np


def sort(df,by,ascending=True,nodupkey=False,keep=None):
    """
    Sorting the Datasets with given columns
    :df: Dataframe name
    :by: Columns by which want to be sorted as space separated string
    :ascending: order in which columns have to be sorted,can be
    passed as list eg: [True,False,True]
    :nodupkey: True to eliminate duplicate rows
    :keep: to return df with required columns passed as string separated
    """
    cols = by.split()
    df = df.sort_values(by=cols,ascending=ascending)
    if nodupkey == True:
        df.drop_duplicates(inplace=True)
    if keep != None:
        cols = keep.split()
        df = df[cols]

    return df
