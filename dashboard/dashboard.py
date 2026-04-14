import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# ==============================
# CONFIGURATION & SETUP
# ==============================
st.set_page_config(page_title="Bike Sharing Analytics", page_icon="🚲", layout="wide")
sns.set_theme(style='whitegrid')

# ==============================
# LOAD DATA (ANTI-ERROR PATH)
# ==============================
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "main_data.csv")

try:
    day_df = pd.read_csv(csv_path)
    # Pastikan format datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
except FileNotFoundError:
    st.error("🚨 File main_data.csv tidak ditemukan. Pastikan file berada di folder yang sama dengan dashboard.py")
    st.stop()

# ==============================
# SIDEBAR: FILTER DETAIL 
# ==============================
min_date = day_df["dteday"].min().date()
max_date = day_df["dteday"].max().date()

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485965120184-e220f721d03e?q=80&w=1000&auto=format&fit=crop", use_column_width=True)
    st.title("🚲 Bike Analytics")
    st.markdown("Sesuaikan filter untuk analisis mendalam:")
    
    st.markdown("---")
    
    # FILTER 1: Rentang Tanggal (THE ULTIMATE TIME-BOUND FILTER)
    st.markdown("**📅 1. Rentang Waktu (Time-Bound)**")
    date_range = st.date_input(
        label="Pilih rentang tanggal (Bulan/Hari/Tahun):",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Validasi input tanggal (mencegah error jika user baru klik 1 tanggal)
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.warning("⚠️ Silakan klik tanggal akhir untuk memuat data.")
        st.stop()
    
    # FILTER 2: Tipe Hari
    st.markdown("**📆 2. Tipe Hari**")
    hari_filter = st.selectbox(
        label="Pilih tipe hari untuk dibandingkan:",
        options=("Semua Hari", "Khusus Hari Kerja", "Khusus Hari Libur / Akhir Pekan")
    )

# ==============================
# LOGIKA PENERAPAN FILTER
# ==============================
# 1. Terapkan Filter Tanggal
main_df = day_df[(day_df["dteday"].dt.date >= start_date) & 
                 (day_df["dteday"].dt.date <= end_date)].copy()

# 2. Terapkan Filter Tipe Hari
if hari_filter == "Khusus Hari Kerja":
    main_df = main_df[main_df["workingday"] == 1]
elif hari_filter == "Khusus Hari Libur / Akhir Pekan":
    main_df = main_df[main_df["workingday"] == 0]

# ==============================
# HEADER DASHBOARD & METRIK UTAMA
# ==============================
st.title("Data Penumpang Sepeda (Bike Sharing) 📊")
st.markdown(f"Menampilkan data dari **{start_date.strftime('%d %B %Y')}** hingga **{end_date.strftime('%d %B %Y')}**.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="🚴 Total Penyewaan", value=f"{main_df['cnt'].sum():,}")
with col2:
    st.metric(label="👥 Pelanggan Terdaftar (Registered)", value=f"{main_df['registered'].sum():,}")
with col3:
    st.metric(label="🚶 Pelanggan Kasual (Casual)", value=f"{main_df['casual'].sum():,}")

st.markdown("---")

# ==============================
# KONTEN UTAMA: TABS
# ==============================
tab1, tab2, tab3 = st.tabs(["📈 Tren Penyewaan", "👥 Pola Pengguna (Casual vs Registered)", "🚀 Analisis Lanjutan"])

# --- TAB 1: TREN WAKTU ---
with tab1:
    st.subheader("Fluktuasi Total Penyewaan Sepeda")
    if not main_df.empty:
        # Jika rentang hari kurang dari 60 hari, tampilkan tren harian agar lebih detail
        if (end_date - start_date).days <= 60:
            trend_df = main_df.groupby(main_df['dteday'].dt.date)['cnt'].sum().reset_index()
            x_col = 'dteday'
            xlabel = "Tanggal"
        else:
            # Jika lebih dari 60 hari, tampilkan tren bulanan (Tahun-Bulan)
            main_df['year_month'] = main_df['dteday'].dt.to_period('M').astype(str)
            trend_df = main_df.groupby('year_month')['cnt'].sum().reset_index()
            x_col = 'year_month'
            xlabel = "Bulan"

        fig_tren, ax_tren = plt.subplots(figsize=(12, 5))
        sns.lineplot(x=x_col, y='cnt', data=trend_df, marker='o', 
                     linewidth=3, color='#2E86C1', markersize=8, ax=ax_tren)
        
        ax_tren.set_xlabel(xlabel, fontsize=12)
        ax_tren.set_ylabel("Total Penyewaan", fontsize=12)
        plt.xticks(rotation=45) # Memiringkan teks agar tidak bertumpuk
        st.pyplot(fig_tren)
    else:
        st.warning("Data tidak ditemukan untuk rentang tanggal ini.")

# --- TAB 2: POLA PENGGUNA (MENJAWAB PERTANYAAN 2) ---
with tab2:
    st.header("Analisis Perilaku Pengguna (Casual vs Registered)")
    st.markdown("**Fokus Analisis:** Membandingkan proporsi penyewaan pada hari kerja vs hari libur untuk strategi diskon.")

    if hari_filter != "Semua Hari":
        st.warning("⚠️ **Perhatian:** Untuk melihat perbandingan antara Hari Kerja dan Libur, ubah filter Tipe Hari menjadi **'Semua Hari'**.")

    if not main_df.empty:
        col_pie, col_bar = st.columns([1, 2])

        with col_pie:
            st.subheader("Proporsi Total")
            total_casual = main_df['casual'].sum()
            total_registered = main_df['registered'].sum()

            if total_casual > 0 or total_registered > 0:
                fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
                ax_pie.pie([total_casual, total_registered], labels=['Casual', 'Registered'],
                           autopct='%1.1f%%', colors=['#FFA07A', '#5DADE2'],
                           startangle=90, explode=(0.1, 0), shadow=True)
                ax_pie.axis('equal')
                st.pyplot(fig_pie)
            else:
                st.info("Belum ada data penyewaan di rentang ini.")

        with col_bar:
            st.subheader("Perbandingan Berdasarkan Tipe Hari")
            
            user_pattern = main_df.groupby('workingday').agg({
                'casual': 'sum',
                'registered': 'sum'
            }).reset_index()

            user_pattern['total_rentals'] = user_pattern['casual'] + user_pattern['registered']
            user_pattern['Casual (%)'] = (user_pattern['casual'] / user_pattern['total_rentals']) * 100
            user_pattern['Registered (%)'] = (user_pattern['registered'] / user_pattern['total_rentals']) * 100
            user_pattern['workingday'] = user_pattern['workingday'].map({0: 'Hari Libur', 1: 'Hari Kerja'})

            user_pattern_melted = user_pattern.melt(
                id_vars='workingday', 
                value_vars=['Casual (%)', 'Registered (%)'], 
                var_name='Tipe Pengguna', 
                value_name='Persentase'
            )

            fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
            sns.barplot(x='workingday', y='Persentase', hue='Tipe Pengguna', 
                        data=user_pattern_melted, palette=['#FFA07A', '#5DADE2'], ax=ax_bar)
            
            ax_bar.set_xlabel("Tipe Hari", fontsize=12)
            ax_bar.set_ylabel("Persentase Penyewaan (%)", fontsize=12)
            ax_bar.set_ylim(0, 100)
            
            for p in ax_bar.patches:
                height = p.get_height()
                if height > 0:
                    ax_bar.annotate(f'{height:.2f}%', 
                                    (p.get_x() + p.get_width() / 2., height), 
                                    ha='center', va='bottom', 
                                    fontsize=11, fontweight='bold', color='black', xytext=(0, 5), 
                                    textcoords='offset points')

            plt.legend(title='Tipe Pengguna')
            st.pyplot(fig_bar)

        if len(user_pattern) == 2:
            casual_libur = user_pattern.loc[user_pattern['workingday'] == 'Hari Libur', 'Casual (%)'].values[0]
            casual_kerja = user_pattern.loc[user_pattern['workingday'] == 'Hari Kerja', 'Casual (%)'].values[0]
            selisih = casual_libur - casual_kerja

            st.success(f"💡 **Kesimpulan & Action Plan:**\n\nDalam rentang waktu yang Anda pilih, terdapat lonjakan persentase pelanggan **Casual** pada **Hari Libur ({casual_libur:.2f}%)** dibandingkan **Hari Kerja ({casual_kerja:.2f}%)**. Selisih persentase ini mencapai **{selisih:.2f}%**.\n\n**Rekomendasi:** Fokuskan promosi konversi *membership* pada akhir pekan untuk memaksimalkan ROI pemasaran.")

    else:
        st.warning("Data tidak ditemukan untuk rentang filter ini.")

# --- TAB 3: ANALISIS LANJUTAN ---
with tab3:
    st.subheader("Analisis Mendalam (Clustering, RFM, & Time Series)")
    col_c, col_r = st.columns(2)
    
    with col_c:
        st.markdown("**1. Clustering: Profil Permintaan**")
        if 'demand_cluster' in main_df.columns and not main_df.empty:
            cluster_counts = main_df['demand_cluster'].value_counts().reset_index()
            cluster_counts.columns = ['Kategori', 'Jumlah Hari']
            fig_clust, ax_clust = plt.subplots(figsize=(6, 4))
            sns.barplot(y='Kategori', x='Jumlah Hari', data=cluster_counts, palette='viridis', ax=ax_clust)
            st.pyplot(fig_clust)
        else:
            st.info("Data Clustering tidak tersedia di rentang ini.")

    with col_r:
        st.markdown("**2. Hari Berkinerja Tertinggi**")
        if not main_df.empty:
            top_days = main_df.groupby('weekday')['cnt'].sum().sort_values(ascending=False).reset_index()
            day_map = {0:'Minggu', 1:'Senin', 2:'Selasa', 3:'Rabu', 4:'Kamis', 5:'Jumat', 6:'Sabtu'}
            top_days['weekday'] = top_days['weekday'].map(day_map)
            st.dataframe(top_days, use_container_width=True)

    st.markdown("---")
    st.markdown("**3. Time Series Analysis (Moving Average)**")
    if '7_day_MA' in main_df.columns and '30_day_MA' in main_df.columns and not main_df.empty:
        fig_ma, ax_ma = plt.subplots(figsize=(14, 5))
        sns.lineplot(x='dteday', y='cnt', data=main_df, label='Data Harian', color='lightgrey', alpha=0.5, ax=ax_ma)
        sns.lineplot(x='dteday', y='7_day_MA', data=main_df, label='7-Hari MA', color='#F39C12', linewidth=2, ax=ax_ma)
        sns.lineplot(x='dteday', y='30_day_MA', data=main_df, label='30-Hari MA', color='#E74C3C', linewidth=3, ax=ax_ma)
        st.pyplot(fig_ma)
    else:
         st.info("Data Moving Average (Time Series) tidak tersedia di rentang ini.")

st.markdown("---")
st.caption("Copyright © 2026 - Bike Sharing Data Analysis")