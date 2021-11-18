import pandas as pd
from collections import deque

def form_last_n_games(df: pd.DataFrame, n:int, cols_to_grab=['Class'], lookup_cols=['Team Code']):
    """
    Requires that the input df is sorted such that old elements are at the top,
    e.g. `df = df.sort_values(by='Date', ascending=True)`
    """
    progress = widgets.IntProgress(
        value=0,
        min=0,
        max=len(df) + 1,
        description='Processing:',
        bar_style='',  # 'success', 'info', 'warning', 'danger' or ''
        style={'bar_color': 'green'},
        orientation='horizontal'
    )

    display(progress)

    result = df.copy()

    new_columns = [lookup + '_' + ''.join(['p']*(prev+1)) + '_' +
                   col for col in cols_to_grab for prev in range(n) for lookup in lookup_cols]
    new_df = pd.DataFrame(columns=new_columns)

    lookup_dict = {}
    progress.value += 1
    for index, row in df.iterrows():
        to_drop = False
        append_row = pd.Series(index=new_columns, name=index)
        for lookup in lookup_cols:
            lkup_key = row[lookup]
            last_n = lookup_dict.get(lkup_key, deque(maxlen=n))

            if len(last_n) < n:
                to_drop = True
            else:
                append_cols = [
                    lookup + '_' + ''.join(['p']*(prev+1)) + '_' + col for col in cols_to_grab for prev in range(n)]
                append_row[append_cols] = [elem for r in last_n for elem in r]

            last_n.appendleft(row[cols_to_grab])
            lookup_dict[lkup_key] = last_n

        if to_drop:
            result.drop(index, inplace=True)
        else:
            new_df = new_df.append(append_row)
        progress.value += 1

    return pd.concat([result, new_df], axis=1), new_columns