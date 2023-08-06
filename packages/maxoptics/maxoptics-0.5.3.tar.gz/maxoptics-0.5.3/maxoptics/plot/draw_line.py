def draw_line(x_axis, title, y_name, x_name, field, y_axis=[], data=[], type="polyline"):
    """
    ---
    inputs:
        title:  str
        x_axis: list[float]
        x_name: str
        y_axis: list[list[float]]
        y_name: str
        field:  list[str]
    output:
        type: pandas.Dataframe
        description: A list with dataframes with labels and data as values
        and Title as keys. Like:
    ---
    """
    if len(field) == 0:
        field.append(y_name)
    print(field)
    data = data or y_axis
    if len(data) == len(field):
        df = pd.DataFrame(data=data, index=x_axis, columns=field)
    else:
        df = pd.DataFrame(data=data, index=x_axis, columns=field)
    setattr(df, "title", title)
    setattr(df, "ylabel", y_name)
    setattr(df, "xlabel", x_name)
    setattr(df, "fields", field)
    return df
