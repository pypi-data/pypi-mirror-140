import plotly.graph_objects as go
from plotly.subplots import make_subplots

def dfpolt(title,df):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    columns = df.columns
    # Add traces
    fig.add_trace(
        go.Bar(x=df.index, y=df.iloc[:,0], name=columns[0],
               text=df.iloc[:,0],
               textposition='outside',
               textfont=dict(
                   size=13,
                   color='#1f77b4')
               ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df.iloc[:,1], name=columns[1]),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text=title
    )

    # Set x-axis title
    fig.update_xaxes(title_text="", tickformat='%Y-%m')
    fig.update_traces(texttemplate='%{text:.2f}元')
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>"+columns[0]+"</b>  ", secondary_y=False)
    fig.update_yaxes(title_text="<b>"+columns[1]+"</b>  ", secondary_y=True)

    fig.update_layout(
        autosize=False,
        width=1000,
        height=600,
        margin=dict(
            l=20,
            r=20,
            b=40,
            t=40,
            pad=4
        ),
        paper_bgcolor="LightSteelBlue",
    )
    return fig