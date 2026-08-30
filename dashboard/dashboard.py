import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "main_data.csv")
    df = pd.read_csv(csv_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

hour_df = load_data()

with st.sidebar:
    st.header("🚲 Bike Sharing")
    st.caption("Dashboard Analisis Data Peminjaman Sepeda")
    st.markdown("---")

    min_date = hour_df['dteday'].min().date()
    max_date = hour_df['dteday'].max().date()
    start_date, end_date = st.date_input(
        "📅 Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    season_options = hour_df['season'].unique().tolist()
    season_filter = st.multiselect(
        "🍂 Musim",
        options=season_options,
        default=season_options
    )

    weather_options = hour_df['weathersit'].unique().tolist()
    weather_filter = st.multiselect(
        "🌤️ Kondisi Cuaca",
        options=weather_options,
        default=weather_options
    )

    st.markdown("---")
    st.caption("Data: Capital Bikeshare, Washington D.C. (2011–2012)")

filtered_df = hour_df[
    (hour_df['dteday'].dt.date >= start_date) &
    (hour_df['dteday'].dt.date <= end_date) &
    (hour_df['season'].isin(season_filter)) &
    (hour_df['weathersit'].isin(weather_filter))
]

st.title("🚲 Bike Sharing Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis pola peminjaman sepeda di **Washington D.C.** berdasarkan data Capital Bikeshare (2011–2012).")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rentals = int(filtered_df['cnt'].sum())
    st.metric("🚲 Total Peminjaman", f"{total_rentals:,}")

with col2:
    total_casual = int(filtered_df['casual'].sum())
    st.metric("👤 Pengguna Casual", f"{total_casual:,}")

with col3:
    total_registered = int(filtered_df['registered'].sum())
    st.metric("🪪 Pengguna Registered", f"{total_registered:,}")

with col4:
    daily_avg = int(filtered_df.groupby('dteday')['cnt'].sum().mean())
    st.metric("📊 Rata-rata Harian", f"{daily_avg:,}")

st.markdown("---")

st.subheader("📈 Tren Peminjaman Sepeda Harian")

daily_df = filtered_df.groupby('dteday').agg(
    cnt=('cnt', 'sum'),
    casual=('casual', 'sum'),
    registered=('registered', 'sum')
).reset_index()

fig1, ax1 = plt.subplots(figsize=(14, 4))
ax1.plot(daily_df['dteday'], daily_df['cnt'], color='#1565C0', linewidth=1.5, alpha=0.9)
ax1.fill_between(daily_df['dteday'], daily_df['cnt'], alpha=0.15, color='#1565C0')
ax1.set_xlabel("")
ax1.set_ylabel("Jumlah Peminjaman", fontsize=11)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='y', alpha=0.3)
plt.tight_layout()
st.pyplot(fig1)

st.markdown("---")

st.subheader("🍂 Pengaruh Musim & Cuaca terhadap Peminjaman")

col_left, col_right = st.columns(2)

with col_left:
    season_df = filtered_df.groupby('season')['cnt'].mean().reset_index()
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    season_df['season'] = pd.Categorical(season_df['season'], categories=season_order, ordered=True)
    season_df = season_df.sort_values('season')

    colors_s = ['#66BB6A', '#FFA726', '#EF5350', '#42A5F5']
    fig2, ax2 = plt.subplots(figsize=(7, 5))
    bars = ax2.bar(season_df['season'], season_df['cnt'], color=colors_s, edgecolor='white', linewidth=1.5)

    max_idx = season_df['cnt'].values.argmax()
    bars[max_idx].set_edgecolor('#333')
    bars[max_idx].set_linewidth(2.5)

    ax2.set_title('Rata-rata Peminjaman per Musim', fontsize=13, fontweight='bold', pad=10)
    ax2.set_ylabel('Rata-rata Peminjaman/Jam', fontsize=11)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 2,
                 f'{int(h):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_ylim(0, season_df['cnt'].max() * 1.18)
    plt.tight_layout()
    st.pyplot(fig2)

with col_right:
    weather_df = filtered_df.groupby('weathersit')['cnt'].mean().reset_index()
    weather_order = ['Clear', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow']
    weather_df['weathersit'] = pd.Categorical(weather_df['weathersit'], categories=weather_order, ordered=True)
    weather_df = weather_df.sort_values('weathersit').dropna(subset=['weathersit'])

    colors_w = ['#26A69A', '#FFCA28', '#EF5350', '#8E24AA']
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    bars_w = ax3.bar(weather_df['weathersit'], weather_df['cnt'],
                     color=colors_w[:len(weather_df)], edgecolor='white', linewidth=1.5)

    max_idx_w = weather_df['cnt'].values.argmax()
    bars_w[max_idx_w].set_edgecolor('#333')
    bars_w[max_idx_w].set_linewidth(2.5)

    ax3.set_title('Rata-rata Peminjaman per Kondisi Cuaca', fontsize=13, fontweight='bold', pad=10)
    ax3.set_ylabel('Rata-rata Peminjaman/Jam', fontsize=11)
    ax3.tick_params(axis='x', rotation=12)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    for bar in bars_w:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., h + 2,
                 f'{int(h):,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax3.set_ylim(0, weather_df['cnt'].max() * 1.18)
    plt.tight_layout()
    st.pyplot(fig3)

st.markdown("---")

st.subheader("🕐 Pola Peminjaman Sepeda per Jam")

hourly_data = filtered_df.groupby(['hr', 'workingday']).agg(
    avg_cnt=('cnt', 'mean'),
    avg_casual=('casual', 'mean'),
    avg_registered=('registered', 'mean')
).reset_index()

col_h1, col_h2 = st.columns(2)

with col_h1:
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    colors_day = {'Working Day': '#1565C0', 'Holiday/Weekend': '#E65100'}
    for label, group in hourly_data.groupby('workingday'):
        ax4.plot(group['hr'], group['avg_cnt'], marker='o', markersize=4,
                 linewidth=2.5, label=label, color=colors_day.get(label, '#999'))
        ax4.fill_between(group['hr'], group['avg_cnt'], alpha=0.07,
                         color=colors_day.get(label, '#999'))
    ax4.set_title('Hari Kerja vs Hari Libur/Akhir Pekan', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xlabel('Jam (0–23)', fontsize=11)
    ax4.set_ylabel('Rata-rata Peminjaman', fontsize=11)
    ax4.set_xticks(range(0, 24))
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig4)

with col_h2:
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    working = hourly_data[hourly_data['workingday'] == 'Working Day']
    holiday = hourly_data[hourly_data['workingday'] == 'Holiday/Weekend']

    if not working.empty:
        ax5.plot(working['hr'], working['avg_registered'], '-o', markersize=3,
                 linewidth=2, label='Registered (Kerja)', color='#2E7D32')
        ax5.plot(working['hr'], working['avg_casual'], '--s', markersize=3,
                 linewidth=2, label='Casual (Kerja)', color='#C62828')
    if not holiday.empty:
        ax5.plot(holiday['hr'], holiday['avg_registered'], '-o', markersize=3,
                 linewidth=2, label='Registered (Libur)', color='#1565C0', alpha=0.7)
        ax5.plot(holiday['hr'], holiday['avg_casual'], '--s', markersize=3,
                 linewidth=2, label='Casual (Libur)', color='#E65100', alpha=0.7)

    ax5.set_title('Casual vs Registered per Jam', fontsize=13, fontweight='bold', pad=10)
    ax5.set_xlabel('Jam (0–23)', fontsize=11)
    ax5.set_ylabel('Rata-rata Peminjaman', fontsize=11)
    ax5.set_xticks(range(0, 24))
    ax5.legend(fontsize=9, loc='upper left', ncol=2)
    ax5.grid(True, alpha=0.3)
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig5)

st.markdown("---")

st.subheader("👥 Proporsi Tipe Pengguna")

col_p1, col_p2 = st.columns(2)

with col_p1:
    user_totals = filtered_df[['casual', 'registered']].sum()
    fig6, ax6 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax6.pie(
        user_totals,
        labels=['Casual', 'Registered'],
        autopct='%1.1f%%',
        colors=['#EF5350', '#26A69A'],
        startangle=90,
        explode=(0.03, 0),
        textprops={'fontsize': 12}
    )
    for autotext in autotexts:
        autotext.set_fontweight('bold')
    ax6.set_title('Distribusi Tipe Pengguna', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    st.pyplot(fig6)

with col_p2:
    hourly_user = filtered_df.groupby('hr').agg(
        casual=('casual', 'mean'),
        registered=('registered', 'mean')
    ).reset_index()

    fig7, ax7 = plt.subplots(figsize=(8, 5))
    ax7.bar(hourly_user['hr'] - 0.2, hourly_user['registered'], width=0.4,
            label='Registered', color='#26A69A', alpha=0.85)
    ax7.bar(hourly_user['hr'] + 0.2, hourly_user['casual'], width=0.4,
            label='Casual', color='#EF5350', alpha=0.85)
    ax7.set_title('Perbandingan Casual vs Registered per Jam', fontsize=13, fontweight='bold', pad=10)
    ax7.set_xlabel('Jam (0–23)', fontsize=11)
    ax7.set_ylabel('Rata-rata Peminjaman', fontsize=11)
    ax7.set_xticks(range(0, 24))
    ax7.legend(fontsize=10)
    ax7.grid(axis='y', alpha=0.3)
    ax7.spines['top'].set_visible(False)
    ax7.spines['right'].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig7)

st.markdown("---")
st.caption("© 2024 Bike Sharing Dashboard | Sumber Data: Capital Bikeshare, Washington D.C. | Proyek Akhir Dicoding")
