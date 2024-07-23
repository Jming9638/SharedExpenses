import pandas as pd
import streamlit as st
import dataframe_image as dfi
import plotly.graph_objects as go

color_palette = [
    "#001219",
    "#005f73",
    "#0a9396",
    "#94d2bd",
    "#e9d8a6",
    "#ee9b00",
    "#ca6702",
    "#bb3e03",
    "#ae2012",
    "#9b2226"
]


def cross_calculation(data):
    results = []
    for i in data.index:
        row_result = []
        for j in data.columns:
            if i == j:
                row_result.append(0)
            else:
                try:
                    num = data.loc[i, j] - data.loc[j, i]
                    row_result.append(num)
                except:
                    row_result.append(data.loc[i, j])
        results.append(row_result)

    return results


def pie_plot(data, l, v, title=None):
    labels = data[l]
    values = data[v]

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            hoverinfo='label+value+percent',
            hovertemplate='Item: %{label} <br> RM %{value:.2f} <extra></extra>'
        )
    )

    fig.update_traces(
        marker=dict(colors=color_palette)
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        font=dict(size=16),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14)),
        hoverlabel=dict(font_size=14),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        margin=dict(t=50, b=20, l=50, r=20),
        width=1000
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={'displayModeBar': False}
    )


def run():
    st.set_page_config(
        page_title='Shared Expenses',
        page_icon=':moneybag:',
        layout='wide',  # centered, wide
        initial_sidebar_state='auto'  # auto, expanded, collapsed
    )

    st.title('Shared Expenses Calculator')
    file_cols = st.columns((1, 3))

    with file_cols[0]:
        uploaded_file = st.file_uploader(
            label='Upload your .csv file.',
            type=['csv'],
            accept_multiple_files=False
        )

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        data = data.dropna(subset=['paid'])
        data = data.sort_values(by=['paid', 'category', 'item'])

        with file_cols[1]:
            st.dataframe(
                data=data,
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        default_cols = ['paid', 'amount', 'category', 'item']
        members = [member for member in data.columns.tolist() if member not in default_cols]

        def get_names(row):
            return [col for col in members if row[col] == 1]

        data['owed'] = data.apply(get_names, axis=1)
        data['member_count'] = data['owed'].apply(len)
        data['divided_amount'] = data['amount'] / data['member_count']
        data_exploded = data.explode('owed', ignore_index=True)
        pivot_data = data_exploded.pivot_table(
            index='paid',
            columns='owed',
            values='divided_amount',
            aggfunc='sum',
            fill_value=0
        )
        result = pd.DataFrame(data=cross_calculation(pivot_data), index=pivot_data.index, columns=pivot_data.columns)

        display_table = []
        for paid in result.index:
            for owed in result.columns:
                amount = result.loc[paid, owed]
                if amount > 0:
                    display_table.append([owed, '=' * 10, f'RM{amount:.2f}', '=' * 9 + '>', paid])

        display_table = pd.DataFrame(
            data=display_table,
            columns=['Check', 'how much', 'you', 'need to', 'pay']
        ).sort_values('Check')
        dfi.export(
            display_table.style.hide(),
            filename='./result.png',
            table_conversion='matplotlib',
            dpi=150,
        )
        image_cols = st.columns((2, 3))
        with (image_cols[0]):
            total_spend = data['amount'].sum()
            st.header(f'Total Spend: RM{total_spend:.2f}')

            item_spend = data.groupby(['category'])['amount'].sum().reset_index()
            item_spend = item_spend.sort_values(by=['amount'], ascending=False)
            pie_plot(item_spend, 'category', 'amount', 'Category Distribution')
        with image_cols[1]:
            st.image(
                image='./result.png',
                use_column_width=True
            )


if __name__ == "__main__":
    run()
