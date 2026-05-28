import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💸",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================
st.markdown("""
<style>
.main {
    background-color: #F8FAFC;
}

.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

h1, h2, h3 {
    color: #1E293B;
}

.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# LOAD DATA
# =========================================
@st.cache_data
def load_data():
    df = pd.read_csv('Personal_Finance_Dataset.csv')

    df['Date'] = pd.to_datetime(df['Date'])

    df['Month'] = df['Date'].dt.month
    df['MonthName'] = df['Date'].dt.strftime('%B')
    df['Year'] = df['Date'].dt.year
    df['DayName'] = df['Date'].dt.day_name()

    return df


df = load_data()

# =========================================
# SIDEBAR
# =========================================
st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/2489/2489756.png",
    width=120
)

st.sidebar.title("📌 Dashboard Filter")

selected_year = st.sidebar.multiselect(
    "Pilih Tahun",
    options=sorted(df['Year'].unique()),
    default=sorted(df['Year'].unique())
)

selected_type = st.sidebar.multiselect(
    "Pilih Tipe Transaksi",
    options=df['Type'].unique(),
    default=df['Type'].unique()
)

selected_category = st.sidebar.multiselect(
    "Pilih Kategori",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# FILTER DATA
filtered_df = df[
    (df['Year'].isin(selected_year)) &
    (df['Type'].isin(selected_type)) &
    (df['Category'].isin(selected_category))
]

income_df = filtered_df[filtered_df['Type'] == 'Income']
expense_df = filtered_df[filtered_df['Type'] == 'Expense']

# =========================================
# HEADER
# =========================================
st.title("💸 Personal Finance Dashboard")

st.markdown(
    """
Dashboard interaktif untuk menganalisis pola pemasukan dan pengeluaran pribadi.  
Dataset menggunakan mata uang **Dollar ($)**.
"""
)

# =========================================
# KPI SECTION
# =========================================
total_income = income_df['Amount'].sum()
total_expense = expense_df['Amount'].sum()
balance = total_income - total_expense

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="💰 Total Income",
        value=f"$ {total_income:,.2f}"
    )

with col2:
    st.metric(
        label="💳 Total Expense",
        value=f"$ {total_expense:,.2f}"
    )

with col3:
    st.metric(
        label="🏦 Balance",
        value=f"$ {balance:,.2f}"
    )

st.divider()

# =========================================
# CHART ROW 1
# =========================================
col4, col5 = st.columns(2)

with col4:
    st.subheader("📊 Expense by Category")

    category_expense = (
        expense_df.groupby('Category')['Amount']
        .sum()
        .reset_index()
        .sort_values(by='Amount', ascending=False)
    )

    fig1 = px.bar(
        category_expense,
        x='Category',
        y='Amount',
        color='Amount',
        text_auto='.2s',
        template='plotly_white'
    )

    fig1.update_layout(
        xaxis_title='Category',
        yaxis_title='Total Expense ($)',
        height=450
    )

    st.plotly_chart(fig1, use_container_width=True)

with col5:
    st.subheader("🥧 Expense Proportion")

    fig2 = px.pie(
        category_expense,
        names='Category',
        values='Amount',
        hole=0.5,
        template='plotly_white'
    )

    fig2.update_layout(height=450)

    st.plotly_chart(fig2, use_container_width=True)

# =========================================
# CHART ROW 2
# =========================================
col6, col7 = st.columns(2)

with col6:
    st.subheader("📈 Monthly Expense Trend")

    monthly_expense = (
        expense_df.groupby(['Year', 'MonthName'])['Amount']
        .sum()
        .reset_index()
    )

    month_order = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]

    monthly_expense['MonthName'] = pd.Categorical(
        monthly_expense['MonthName'],
        categories=month_order,
        ordered=True
    )

    monthly_expense = monthly_expense.sort_values('MonthName')

    fig3 = px.line(
        monthly_expense,
        x='MonthName',
        y='Amount',
        markers=True,
        template='plotly_white'
    )

    fig3.update_layout(
        xaxis_title='Month',
        yaxis_title='Expense ($)',
        height=450
    )

    st.plotly_chart(fig3, use_container_width=True)

with col7:
    st.subheader("📅 Spending by Day")

    ordered_days = [
        'Monday', 'Tuesday', 'Wednesday',
        'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]

    expense_day = (
        expense_df.groupby('DayName')['Amount']
        .sum()
        .reindex(ordered_days)
        .reset_index()
    )

    fig4 = px.bar(
        expense_day,
        x='DayName',
        y='Amount',
        color='Amount',
        text_auto='.2s',
        template='plotly_white'
    )

    fig4.update_layout(
        xaxis_title='Day',
        yaxis_title='Expense ($)',
        height=450
    )

    st.plotly_chart(fig4, use_container_width=True)

# =========================================
# ADDITIONAL INSIGHT
# =========================================
st.divider()

st.header("📌 Financial Insights")

highest_category = category_expense.iloc[0]['Category']
highest_amount = category_expense.iloc[0]['Amount']

avg_expense = expense_df['Amount'].mean()

col8, col9 = st.columns(2)

with col8:
    st.info(
        f"Kategori pengeluaran terbesar adalah **{highest_category}** "
        f"dengan total pengeluaran sebesar **$ {highest_amount:,.2f}**."
    )

with col9:
    st.warning(
        f"Rata-rata pengeluaran transaksi adalah sekitar "
        f"**$ {avg_expense:,.2f}** per transaksi."
    )

# =========================================
# CONCLUSION
# =========================================
st.divider()

st.header("✅ Conclusion")

st.success(
    "Dashboard menunjukkan bahwa pengeluaran pengguna masih didominasi "
    "oleh kategori tertentu. Melalui visualisasi interaktif, pengguna "
    "dapat memantau pola keuangan, mengontrol pengeluaran, dan membantu "
    "pengambilan keputusan finansial dengan lebih efektif."
)

# =========================================
# DATA PREVIEW
# =========================================
st.divider()

st.subheader("📄 Dataset Preview")

st.caption(
    "Keterangan: Kolom Amount pada dataset menggunakan mata uang Dollar ($)."
)

st.dataframe(filtered_df, use_container_width=True)