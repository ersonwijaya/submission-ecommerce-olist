"""
Dashboard Analisis E-Commerce Olist
Brazilian E-Commerce Public Dataset (2017-2018)
Erson Gaby Wijaya | CDCC180D6Y2298
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings('ignore')

# =====================================================
# KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Dashboard E-Commerce Olist",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
    .judul-utama { font-size:1.9rem; font-weight:700; color:#1E3A8A; margin-bottom:0.1rem; }
    .subjudul    { font-size:0.95rem; color:#6B7280; margin-bottom:1.2rem; }
    .kartu-biru  { background:linear-gradient(135deg,#EFF6FF,#DBEAFE);
                   border-left:4px solid #2563EB; border-radius:10px; padding:0.9rem 1.1rem; }
    .kartu-hijau { background:linear-gradient(135deg,#F0FDF4,#DCFCE7);
                   border-left:4px solid #10B981; border-radius:10px; padding:0.9rem 1.1rem; }
    .kartu-merah { background:linear-gradient(135deg,#FEF2F2,#FEE2E2);
                   border-left:4px solid #EF4444; border-radius:10px; padding:0.9rem 1.1rem; }
    .kartu-ungu  { background:linear-gradient(135deg,#F5F3FF,#EDE9FE);
                   border-left:4px solid #8B5CF6; border-radius:10px; padding:0.9rem 1.1rem; }
    .label-m { font-size:0.75rem; color:#6B7280; font-weight:600;
               text-transform:uppercase; letter-spacing:0.05em; }
    .nilai-m { font-size:1.5rem; font-weight:700; color:#1F2937; line-height:1.2; }
    .sub-m   { font-size:0.82rem; color:#4B5563; }
    .info-box { background:#F0F9FF; border:1px solid #BAE6FD; border-radius:8px;
                padding:0.75rem 1rem; font-size:0.88rem; color:#0C4A6E; margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)


# =====================================================
# FUNGSI LOAD & PROSES DATA DARI CSV INDIVIDUAL
# =====================================================
@st.cache_data
def muat_semua_data():
    """
    Memuat semua CSV dari folder data/ dan membangun
    dataframe gabungan yang dibutuhkan oleh dashboard.
    """
    # Deteksi path secara otomatis (lokal vs Streamlit Cloud)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Coba path relatif ke root repo terlebih dahulu
    kandidat = [
        os.path.join(base_dir, '..', 'data'),   # lokal: dashboard/../data
        os.path.join(base_dir, 'data'),          # fallback: dashboard/data
        'data',                                  # Streamlit Cloud: root/data
    ]
    PATH_DATA = None
    for p in kandidat:
        if os.path.isdir(p) and os.path.exists(os.path.join(p, 'orders_dataset.csv')):
            PATH_DATA = p
            break
    if PATH_DATA is None:
        st.error("❌ Folder 'data/' tidak ditemukan. Pastikan struktur folder sudah benar.")
        st.stop()

    # Load semua tabel
    df_pelanggan  = pd.read_csv(os.path.join(PATH_DATA, 'customers_dataset.csv'))
    df_pesanan    = pd.read_csv(
        os.path.join(PATH_DATA, 'orders_dataset.csv'),
        parse_dates=['order_purchase_timestamp', 'order_approved_at',
                     'order_delivered_carrier_date', 'order_delivered_customer_date',
                     'order_estimated_delivery_date']
    )
    df_item       = pd.read_csv(os.path.join(PATH_DATA, 'order_items_dataset.csv'))
    df_pembayaran = pd.read_csv(os.path.join(PATH_DATA, 'order_payments_dataset.csv'))
    df_ulasan     = pd.read_csv(
        os.path.join(PATH_DATA, 'order_reviews_dataset.csv'),
        parse_dates=['review_creation_date']
    )
    df_produk     = pd.read_csv(os.path.join(PATH_DATA, 'products_dataset.csv'))
    df_kategori   = pd.read_csv(os.path.join(PATH_DATA, 'product_category_name_translation.csv'))

    # --- Cleaning ---
    df_produk['product_category_name'] = df_produk['product_category_name'].fillna('outros')
    df_pembayaran = df_pembayaran[df_pembayaran['payment_type'] != 'not_defined'].copy()
    df_produk = df_produk.merge(df_kategori, on='product_category_name', how='left')
    df_produk['product_category_name_english'] = (
        df_produk['product_category_name_english'].fillna('others')
    )

    # --- Filter delivered 2017-2018 ---
    df_terkirim = df_pesanan[
        (df_pesanan['order_status'] == 'delivered') &
        (df_pesanan['order_purchase_timestamp'].dt.year.between(2017, 2018))
    ].copy()

    # --- Pembayaran dominan per pesanan ---
    df_bayar = (
        df_pembayaran
        .sort_values('payment_value', ascending=False)
        .drop_duplicates(subset='order_id', keep='first')
        [['order_id', 'payment_type', 'payment_installments', 'payment_value']]
    )

    # --- Ulasan per pesanan ---
    df_ulasan_1 = (
        df_ulasan[['order_id', 'review_score']]
        .dropna(subset=['review_score'])
        .drop_duplicates(subset='order_id', keep='first')
    )

    # --- Hitung selisih pengiriman ---
    df_terkirim['selisih_hari'] = (
        df_terkirim['order_delivered_customer_date'] -
        df_terkirim['order_estimated_delivery_date']
    ).dt.days
    df_terkirim['status_pengiriman'] = df_terkirim['selisih_hari'].apply(
        lambda x: 'Terlambat' if pd.notna(x) and x > 0 else 'Tepat/Lebih Cepat'
    )

    # --- Master dataframe ---
    df_main = (
        df_terkirim
        .merge(df_pelanggan[['customer_id', 'customer_unique_id', 'customer_state',
                              'customer_city', 'customer_zip_code_prefix']],
               on='customer_id', how='left')
        .merge(df_item[['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']],
               on='order_id', how='left')
        .merge(df_produk[['product_id', 'product_category_name_english']],
               on='product_id', how='left')
        .merge(df_bayar, on='order_id', how='left')
        .merge(df_ulasan_1, on='order_id', how='left')
    )
    df_main['tahun']     = df_main['order_purchase_timestamp'].dt.year
    df_main['bulan_str'] = df_main['order_purchase_timestamp'].dt.strftime('%Y-%m')

    # --- RFM ---
    tgl_ref = df_terkirim['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_raw = (
        df_terkirim
        .merge(df_pelanggan[['customer_id', 'customer_unique_id']], on='customer_id', how='left')
        .merge(df_item[['order_id', 'price']], on='order_id', how='left')
    )
    df_rfm = (
        rfm_raw.groupby('customer_unique_id')
        .agg(
            recency  =('order_purchase_timestamp', lambda x: (tgl_ref - x.max()).days),
            frequency=('order_id', 'nunique'),
            monetary =('price', 'sum')
        )
        .reset_index()
    )
    df_rfm['skor_r'] = pd.qcut(df_rfm['recency'], q=4, labels=[4, 3, 2, 1]).astype(int)
    df_rfm['skor_f'] = pd.qcut(
        df_rfm['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4]
    ).astype(int)
    df_rfm['skor_m'] = pd.qcut(
        df_rfm['monetary'].rank(method='first'), q=4, labels=[1, 2, 3, 4]
    ).astype(int)

    def tentukan_segmen(baris):
        r, f, m = baris['skor_r'], baris['skor_f'], baris['skor_m']
        if r >= 3 and f >= 3 and m >= 3:
            return 'Champions'
        elif r >= 3 and f >= 2:
            return 'Loyal Customers'
        elif r >= 3 and f == 1:
            return 'Recent Customers'
        elif r == 2 and f >= 2:
            return 'Potential Loyalists'
        elif r == 2 and f == 1:
            return 'Needs Attention'
        elif r == 1 and f >= 2:
            return 'At Risk'
        else:
            return 'Lost'

    df_rfm['segmen'] = df_rfm.apply(tentukan_segmen, axis=1)
    bins_m  = [0, 100, 300, 600, float('inf')]
    label_m = ['Rendah\n(<R$100)', 'Menengah\n(R$100–300)',
                'Tinggi\n(R$300–600)', 'Premium\n(>R$600)']
    df_rfm['segmen_belanja'] = pd.cut(
        df_rfm['monetary'], bins=bins_m, labels=label_m, right=False
    )

    return df_main, df_rfm


# =====================================================
# LOAD DATA
# =====================================================
with st.spinner("⏳ Memuat dan memproses data, harap tunggu..."):
    df_main, df_rfm = muat_semua_data()

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    st.markdown("## 🛒 Olist Dashboard")
    st.markdown("**E-Commerce Brasil 2017–2018**")
    st.markdown("---")
    st.markdown("### 🔧 Filter Data")

    tahun_tersedia = sorted(df_main['tahun'].dropna().unique().astype(int).tolist())
    tahun_dipilih  = st.multiselect("📅 Pilih Tahun", tahun_tersedia, default=tahun_tersedia)
    top_n          = st.slider("📦 Top N Kategori", 5, 20, 10)
    min_pesanan    = st.slider("🗺️ Min. Pesanan per Negara Bagian", 50, 500, 100, 50)

    st.markdown("---")
    st.markdown("### 📋 Tentang")
    st.markdown(
        "Dataset: **Brazilian E-Commerce Public Dataset** (Olist).  \n"
        "Mencakup **99.441 pesanan** dari 2016–2018."
    )
    st.markdown("---")
    st.caption("Erson Gaby Wijaya | CDCC180D6Y2298")

# =====================================================
# FILTER
# =====================================================
df = df_main[df_main['tahun'].isin(tahun_dipilih)].copy() if tahun_dipilih else df_main.copy()
df_kirim = df.dropna(subset=['selisih_hari']).copy()

# =====================================================
# HEADER & KPI
# =====================================================
st.markdown('<p class="judul-utama">🛒 Dashboard Analisis E-Commerce Olist</p>',
            unsafe_allow_html=True)
st.markdown(
    '<p class="subjudul">Brazilian E-Commerce Public Dataset (2017–2018) &nbsp;|&nbsp; '
    'Erson Gaby Wijaya &nbsp;|&nbsp; CDCC180D6Y2298</p>',
    unsafe_allow_html=True
)

k1, k2, k3, k4 = st.columns(4)
total_pesanan   = df['order_id'].nunique()
total_revenue   = df['price'].sum()
total_pelanggan = df['customer_unique_id'].nunique()
pct_terlambat   = (df_kirim['status_pengiriman'] == 'Terlambat').mean() * 100

with k1:
    st.markdown(f"""<div class="kartu-biru"><div class="label-m">📦 Total Pesanan</div>
    <div class="nilai-m">{total_pesanan:,}</div>
    <div class="sub-m">pesanan terkirim 2017–2018</div></div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kartu-hijau"><div class="label-m">💰 Total Revenue</div>
    <div class="nilai-m">R$ {total_revenue/1e6:.2f}M</div>
    <div class="sub-m">juta Real Brasil (BRL)</div></div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kartu-ungu"><div class="label-m">👤 Pelanggan Unik</div>
    <div class="nilai-m">{total_pelanggan:,}</div>
    <div class="sub-m">customer_unique_id</div></div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kartu-merah"><div class="label-m">⚠️ Tingkat Keterlambatan</div>
    <div class="nilai-m">{pct_terlambat:.1f}%</div>
    <div class="sub-m">dari total pesanan terkirim</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================
# KONSTANTA WARNA
# =====================================================
PALET5    = ['#1E3A8A', '#F97316', '#10B981', '#8B5CF6', '#EF4444']
PALET_PAY = {'credit_card': '#2563EB', 'boleto': '#F97316', 'voucher': '#10B981'}
PALET_SEG = ['#1E3A8A','#2563EB','#10B981','#8B5CF6','#F97316','#EF4444','#9CA3AF']

# =====================================================
# TAB NAVIGASI
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📦 Revenue & Produk", "🚚 Performa Pengiriman",
    "⭐ Review & Pembayaran", "👥 Analisis RFM", "🗺️ Geospatial"
])

# ──────────────────────────────────────────────────
# TAB 1 — REVENUE & PRODUK
# ──────────────────────────────────────────────────
with tab1:
    st.subheader("Pertanyaan 1: Kategori Produk Penghasil Revenue Tertinggi")
    st.markdown('<div class="info-box">🔍 Kategori produk apa yang menghasilkan total '
                'pendapatan tertinggi, dan bagaimana tren bulanan 5 kategori teratas '
                'sepanjang Januari 2017 – Agustus 2018?</div>', unsafe_allow_html=True)

    rev_kat = (
        df.groupby('product_category_name_english')
        .agg(total_revenue=('price','sum'), jumlah_item=('order_item_id','count'))
        .reset_index().sort_values('total_revenue', ascending=False)
    )
    rev_kat['label'] = rev_kat['product_category_name_english'].str.replace('_',' ').str.title()
    top5_kat = rev_kat.head(5)['product_category_name_english'].tolist()

    df_top5 = df[df['product_category_name_english'].isin(top5_kat)].copy()
    tren = (df_top5.groupby(['bulan_str','product_category_name_english'])['price']
            .sum().reset_index())
    pivot_t = (tren.pivot(index='bulan_str', columns='product_category_name_english', values='price')
               .fillna(0).sort_index())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#FAFAFA')

    topN = rev_kat.head(top_n).copy()
    warna_b = ['#1E3A8A' if i==0 else '#2563EB' if i<3 else '#93C5FD' for i in range(len(topN))]
    b = ax1.barh(topN['label'][::-1], topN['total_revenue'][::-1]/1e3,
                 color=warna_b[::-1], edgecolor='none', height=0.7)
    maks = topN['total_revenue'].max()/1e3
    for patch, (_, row) in zip(b, topN[::-1].iterrows()):
        ax1.text(patch.get_width()+maks*0.01, patch.get_y()+patch.get_height()/2,
                 f"R$ {row['total_revenue']/1e3:.1f}K", va='center', fontsize=8.5)
    ax1.set_xlabel('Revenue (Ribu BRL)', fontsize=10)
    ax1.set_title(f'Top {top_n} Kategori berdasarkan Total Revenue', fontweight='bold')
    ax1.set_xlim(0, maks*1.2)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.set_facecolor('#F8FAFC')

    for kat, warna in zip(top5_kat, PALET5):
        if kat in pivot_t.columns:
            ax2.plot(range(len(pivot_t)), pivot_t[kat]/1e3, marker='o', ms=3.5,
                     lw=2, color=warna, label=kat.replace('_',' ').title())
    label_x = list(pivot_t.index)
    ax2.set_xticks(range(0, len(label_x), 2))
    ax2.set_xticklabels(label_x[::2], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Revenue (Ribu BRL)', fontsize=10)
    ax2.set_title('Tren Revenue Bulanan — 5 Kategori Teratas', fontweight='bold')
    ax2.legend(fontsize=8.5, loc='upper left')
    ax2.grid(alpha=0.3, linestyle='--')
    ax2.set_facecolor('#F8FAFC')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    tbl1 = rev_kat.head(5)[['label','total_revenue','jumlah_item']].copy()
    tbl1['total_revenue'] = tbl1['total_revenue'].apply(lambda x: f"R$ {x:,.0f}")
    tbl1['jumlah_item']   = tbl1['jumlah_item'].apply(lambda x: f"{x:,}")
    tbl1.columns = ['Kategori','Total Revenue','Jumlah Item']
    st.dataframe(tbl1, use_container_width=True, hide_index=True)

    with st.expander("💡 Insight"):
        st.markdown("- **health_beauty** menjadi kategori revenue tertinggi (R$ 1,23 juta).\n"
                    "- Puncak revenue terjadi **November 2017** (Black Friday) dan **Mei 2018**.\n"
                    "- Semua kategori teratas tumbuh konsisten sepanjang 2017–2018.")

# ──────────────────────────────────────────────────
# TAB 2 — PERFORMA PENGIRIMAN
# ──────────────────────────────────────────────────
with tab2:
    st.subheader("Pertanyaan 2: Performa Keterlambatan Pengiriman per Negara Bagian")
    st.markdown('<div class="info-box">🔍 Negara bagian mana yang memiliki % keterlambatan '
                'tertinggi dan berapa rata-rata hari keterlambatannya sepanjang 2017–2018?</div>',
                unsafe_allow_html=True)

    perf_state = (
        df_kirim.groupby('customer_state')
        .agg(jumlah_pesanan=('order_id','count'),
             pct_terlambat=('status_pengiriman', lambda x: (x=='Terlambat').mean()*100),
             rata_selisih=('selisih_hari','mean'))
        .reset_index().sort_values('pct_terlambat', ascending=False)
    )
    perf_f = perf_state[perf_state['jumlah_pesanan'] >= min_pesanan].copy()

    fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig2.patch.set_facecolor('#FAFAFA')

    top15 = perf_f.head(15)
    warna_s = ['#991B1B' if p>15 else '#EF4444' if p>10 else '#FCA5A5'
               for p in top15['pct_terlambat']]
    bh = ax1.barh(top15['customer_state'][::-1], top15['pct_terlambat'][::-1],
                  color=warna_s[::-1], edgecolor='none', height=0.7)
    rata_nas = perf_f['pct_terlambat'].mean()
    ax1.axvline(rata_nas, color='#1D4ED8', lw=1.5, ls='--',
                label=f'Rata-rata: {rata_nas:.1f}%')
    for patch, (_, row) in zip(bh, top15[::-1].iterrows()):
        ax1.text(patch.get_width()+0.25, patch.get_y()+patch.get_height()/2,
                 f"{row['pct_terlambat']:.1f}%", va='center', fontsize=8.5)
    ax1.set_xlabel('% Pesanan Terlambat', fontsize=10)
    ax1.set_title('Top 15 Negara Bagian — % Keterlambatan', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.set_facecolor('#F8FAFC')

    top8 = perf_f.head(8)['customer_state'].tolist()
    data_box = [df_kirim[df_kirim['customer_state']==s]['selisih_hari'].dropna().values
                for s in top8]
    bp = ax2.boxplot(data_box, labels=top8, patch_artist=True,
                     medianprops={'color':'#1E3A8A','lw':2},
                     flierprops={'marker':'o','ms':3,'alpha':0.3})
    for patch in bp['boxes']:
        patch.set_facecolor('#BFDBFE')
        patch.set_alpha(0.8)
    ax2.axhline(0, color='#EF4444', lw=1.5, ls='--', label='Batas tepat waktu')
    ax2.set_ylabel('Selisih Hari (Aktual − Estimasi)', fontsize=10)
    ax2.set_title('Distribusi Selisih Hari — Top 8 Negara Bagian', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_facecolor('#F8FAFC')

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    kiri, kanan = st.columns(2)
    with kiri:
        status_c = df_kirim['status_pengiriman'].value_counts()
        fig_pie, ax_pie = plt.subplots(figsize=(5, 4))
        ax_pie.pie(status_c.values, labels=status_c.index, autopct='%1.1f%%',
                   colors=['#EF4444','#10B981'],
                   wedgeprops={'edgecolor':'white','lw':2}, startangle=90)
        ax_pie.set_title('Proporsi Status Pengiriman', fontweight='bold')
        st.pyplot(fig_pie)
        plt.close()
    with kanan:
        tbl2 = perf_f[['customer_state','jumlah_pesanan','pct_terlambat','rata_selisih']].copy()
        tbl2['pct_terlambat'] = tbl2['pct_terlambat'].apply(lambda x: f"{x:.1f}%")
        tbl2['rata_selisih']  = tbl2['rata_selisih'].apply(lambda x: f"{x:.1f} hari")
        tbl2.columns = ['Negara Bagian','Jumlah Pesanan','% Terlambat','Rata-rata Selisih']
        st.dataframe(tbl2, use_container_width=True, hide_index=True, height=330)

    with st.expander("💡 Insight"):
        st.markdown("- **AL (Alagoas)** tertinggi (~21%) — wilayah Timur Laut Brasil paling bermasalah.\n"
                    "- SP, RJ, MG volume besar tapi keterlambatan rendah karena dekat pusat distribusi.\n"
                    "- Rata-rata selisih negatif = Olist sering kirim lebih cepat dari estimasi.")

# ──────────────────────────────────────────────────
# TAB 3 — REVIEW & PEMBAYARAN
# ──────────────────────────────────────────────────
with tab3:
    st.subheader("Pertanyaan 3: Review Score berdasarkan Metode Pembayaran")
    st.markdown('<div class="info-box">🔍 Apakah terdapat perbedaan rata-rata review score '
                'yang signifikan antara pengguna credit card, boleto, dan voucher?</div>',
                unsafe_allow_html=True)

    df_ulbayar = df[df['payment_type'].isin(['credit_card','boleto','voucher'])
                    & df['review_score'].notna()].copy()
    stats_rev = (df_ulbayar.groupby('payment_type')['review_score']
                 .agg(['mean','median','count','std']).reset_index()
                 .sort_values('mean', ascending=False))
    dist_rv = (df_ulbayar.groupby(['payment_type','review_score']).size()
               .reset_index(name='jumlah'))
    dist_rv['pct'] = dist_rv.groupby('payment_type')['jumlah'].transform(
        lambda x: x/x.sum()*100)
    pivot_d = (dist_rv.pivot(index='review_score', columns='payment_type', values='pct')
               .fillna(0))

    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig3.patch.set_facecolor('#FAFAFA')

    x = np.arange(5)
    lebar = 0.28
    for i, (metode, warna) in enumerate(PALET_PAY.items()):
        if metode in pivot_d.columns:
            ax1.bar(x+i*lebar, pivot_d[metode], lebar,
                    label=metode.replace('_',' ').title(),
                    color=warna, alpha=0.85, edgecolor='none')
    ax1.set_xticks(x+lebar)
    ax1.set_xticklabels([f'Score {i+1}' for i in range(5)], fontsize=10)
    ax1.set_ylabel('Persentase (%)', fontsize=10)
    ax1.set_title('Distribusi Review Score\nper Metode Pembayaran', fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_facecolor('#F8FAFC')

    warna_b = [PALET_PAY.get(m,'#6B7280') for m in stats_rev['payment_type']]
    label_b = [m.replace('_',' ').title() for m in stats_rev['payment_type']]
    bars = ax2.bar(label_b, stats_rev['mean'], color=warna_b, alpha=0.85,
                   yerr=stats_rev['std'], capsize=6, edgecolor='none')
    for bar, (_, row) in zip(bars, stats_rev.iterrows()):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.12,
                 f"{row['mean']:.3f}", ha='center', fontsize=11, fontweight='bold')
    ax2.axhline(df_ulbayar['review_score'].mean(), color='gray', lw=1.2, ls='--',
                label=f"Rata-rata: {df_ulbayar['review_score'].mean():.2f}")
    ax2.set_ylim(0, 5.8)
    ax2.set_ylabel('Rata-rata Review Score', fontsize=10)
    ax2.set_title('Rata-rata Review Score (±Std Dev)\nper Metode Pembayaran', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_facecolor('#F8FAFC')

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    tbl3 = stats_rev.copy()
    tbl3.columns = ['Metode Pembayaran','Rata-rata','Median','Jumlah Ulasan','Std Dev']
    tbl3['Metode Pembayaran'] = tbl3['Metode Pembayaran'].str.replace('_',' ').str.title()
    tbl3['Rata-rata'] = tbl3['Rata-rata'].round(4)
    tbl3['Std Dev']   = tbl3['Std Dev'].round(4)
    tbl3['Jumlah Ulasan'] = tbl3['Jumlah Ulasan'].apply(lambda x: f"{int(x):,}")
    st.dataframe(tbl3, use_container_width=True, hide_index=True)

    with st.expander("💡 Insight"):
        st.markdown("- Perbedaan rata-rata sangat kecil (4.04–4.09) — metode bayar bukan faktor utama kepuasan.\n"
                    "- **Credit card** punya proporsi score 5 terbesar (~60%).\n"
                    "- **Voucher** punya distribusi lebih beragam — ada potensi kendala teknis.")

# ──────────────────────────────────────────────────
# TAB 4 — RFM ANALYSIS
# ──────────────────────────────────────────────────
with tab4:
    st.subheader("Analisis Lanjutan: RFM — Segmentasi Pelanggan")
    st.markdown('<div class="info-box">📊 Mengelompokkan pelanggan berdasarkan '
                '<b>Recency</b>, <b>Frequency</b>, dan <b>Monetary</b>.</div>',
                unsafe_allow_html=True)

    dist_seg = df_rfm['segmen'].value_counts().reset_index()
    dist_seg.columns = ['Segmen','Jumlah']
    dist_seg['Persentase'] = (dist_seg['Jumlah']/len(df_rfm)*100).round(1)

    rfm_agg = (df_rfm.groupby('segmen')
               .agg(rata_r=('recency','mean'), rata_f=('frequency','mean'),
                    rata_m=('monetary','mean'), jumlah=('customer_unique_id','count'))
               .reset_index().sort_values('rata_m', ascending=False))

    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig4.patch.set_facecolor('#FAFAFA')

    wedges, texts, autotexts = ax1.pie(
        dist_seg['Jumlah'], labels=dist_seg['Segmen'], autopct='%1.1f%%',
        colors=PALET_SEG[:len(dist_seg)], startangle=140,
        wedgeprops={'width':0.6,'edgecolor':'white','lw':2})
    for at in autotexts:
        at.set_fontsize(8)
    ax1.set_title('Distribusi Segmen Pelanggan (RFM)', fontweight='bold')

    warna_rfm = PALET_SEG[:len(rfm_agg)]
    bar_r = ax2.bar(range(len(rfm_agg)), rfm_agg['rata_m'],
                    color=warna_rfm, alpha=0.85, edgecolor='none')
    ax2.set_xticks(range(len(rfm_agg)))
    ax2.set_xticklabels(rfm_agg['segmen'], rotation=25, ha='right', fontsize=9)
    ax2.set_ylabel('Rata-rata Total Belanja (BRL)', fontsize=10)
    ax2.set_title('Rata-rata Monetary per Segmen RFM', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_facecolor('#F8FAFC')
    for bar, (_, row) in zip(bar_r, rfm_agg.iterrows()):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                 f"R$ {row['rata_m']:,.0f}", ha='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

    tbl4 = rfm_agg.copy()
    tbl4['rata_r'] = tbl4['rata_r'].apply(lambda x: f"{x:.0f} hari")
    tbl4['rata_f'] = tbl4['rata_f'].apply(lambda x: f"{x:.2f}x")
    tbl4['rata_m'] = tbl4['rata_m'].apply(lambda x: f"R$ {x:,.0f}")
    tbl4['jumlah'] = tbl4['jumlah'].apply(lambda x: f"{x:,}")
    tbl4.columns  = ['Segmen','Rata-rata Recency','Rata-rata Frequency',
                      'Rata-rata Monetary','Jumlah Pelanggan']
    st.dataframe(tbl4, use_container_width=True, hide_index=True)

    st.markdown("##### Distribusi Segmen Belanja (Binning Manual)")
    dist_b = df_rfm['segmen_belanja'].value_counts().sort_index()
    fig_bin, ax_bin = plt.subplots(figsize=(10, 4))
    fig_bin.patch.set_facecolor('#FAFAFA')
    WARNA_BIN = ['#BFDBFE','#60A5FA','#2563EB','#1E3A8A']
    b_bin = ax_bin.bar(range(len(dist_b)), dist_b.values,
                       color=WARNA_BIN[:len(dist_b)], edgecolor='none', alpha=0.9)
    ax_bin.set_xticks(range(len(dist_b)))
    ax_bin.set_xticklabels(dist_b.index, fontsize=10)
    ax_bin.set_ylabel('Jumlah Pelanggan', fontsize=10)
    ax_bin.set_title('Distribusi Segmen Nilai Belanja (Binning Manual)', fontweight='bold')
    ax_bin.grid(axis='y', alpha=0.3, linestyle='--')
    ax_bin.set_facecolor('#F8FAFC')
    for bar, val in zip(b_bin, dist_b.values):
        ax_bin.text(bar.get_x()+bar.get_width()/2, bar.get_height()+100,
                    f"{val:,}\n({val/len(df_rfm)*100:.1f}%)",
                    ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig_bin)
    plt.close()

    with st.expander("💡 Insight"):
        st.markdown("- >80% pelanggan masuk segmen **Lost** — tingginya one-time buyer.\n"
                    "- **Champions** punya monetary tertinggi — perlu program loyalitas.\n"
                    "- >60% pelanggan di segmen Rendah (<R$100) — potensi upselling besar.")

# ──────────────────────────────────────────────────
# TAB 5 — GEOSPATIAL
# ──────────────────────────────────────────────────
with tab5:
    st.subheader("Analisis Lanjutan: Geospatial — Distribusi Revenue & Keterlambatan")
    st.markdown('<div class="info-box">🗺️ Pemetaan revenue dan keterlambatan pengiriman '
                'per negara bagian Brasil.</div>', unsafe_allow_html=True)

    rev_st = (df.groupby('customer_state')
              .agg(total_revenue=('price','sum'), jumlah_pesanan=('order_id','nunique'))
              .reset_index())
    perf_st = (df_kirim.groupby('customer_state')
               .agg(pct_terlambat=('status_pengiriman',
                                   lambda x: (x=='Terlambat').mean()*100))
               .reset_index())
    geo_df = rev_st.merge(perf_st, on='customer_state', how='left')

    KOORDINAT = {
        'AC':(-9.975,-67.824),'AL':(-9.666,-35.735),'AP':(0.902,-52.003),
        'AM':(-3.119,-60.021),'BA':(-12.971,-38.501),'CE':(-3.717,-38.543),
        'DF':(-15.780,-47.929),'ES':(-20.315,-40.312),'GO':(-16.686,-49.264),
        'MA':(-2.530,-44.302),'MT':(-15.600,-56.097),'MS':(-20.469,-54.620),
        'MG':(-19.919,-43.938),'PA':(-1.456,-48.502),'PB':(-7.119,-34.845),
        'PR':(-25.428,-49.273),'PE':(-8.054,-34.881),'PI':(-5.092,-42.803),
        'RJ':(-22.906,-43.173),'RN':(-5.795,-35.209),'RS':(-30.034,-51.217),
        'RO':(-8.761,-63.900),'RR':(2.820,-60.675),'SC':(-27.595,-48.548),
        'SP':(-23.549,-46.633),'SE':(-10.947,-37.073),'TO':(-10.240,-48.325)
    }
    geo_df['lat'] = geo_df['customer_state'].map(lambda s: KOORDINAT.get(s,(None,None))[0])
    geo_df['lon'] = geo_df['customer_state'].map(lambda s: KOORDINAT.get(s,(None,None))[1])
    geo_df = geo_df.dropna(subset=['lat','lon'])

    fig5, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    fig5.patch.set_facecolor('#FAFAFA')

    ax1.set_facecolor('#EFF6FF')
    sc1 = ax1.scatter(geo_df['lon'], geo_df['lat'],
                      s=geo_df['total_revenue']/geo_df['total_revenue'].max()*2500+60,
                      c=geo_df['total_revenue'], cmap='Blues', alpha=0.85,
                      edgecolors='#1D4ED8', linewidth=0.8)
    plt.colorbar(sc1, ax=ax1, label='Total Revenue (BRL)', shrink=0.8)
    for _, row in geo_df.iterrows():
        ax1.annotate(row['customer_state'], (row['lon'], row['lat']),
                     fontsize=7.5, ha='center', fontweight='bold', color='#1e3a5f')
    ax1.set_title('Distribusi Total Revenue per Negara Bagian', fontweight='bold')
    ax1.set_xlabel('Longitude', fontsize=10)
    ax1.set_ylabel('Latitude', fontsize=10)
    ax1.grid(alpha=0.3, linestyle='--')

    geo_pct = geo_df.dropna(subset=['pct_terlambat'])
    ax2.set_facecolor('#FFF7ED')
    sc2 = ax2.scatter(geo_pct['lon'], geo_pct['lat'],
                      s=geo_pct['pct_terlambat']*35+60,
                      c=geo_pct['pct_terlambat'], cmap='Reds', alpha=0.85,
                      edgecolors='#B91C1C', linewidth=0.8)
    plt.colorbar(sc2, ax=ax2, label='% Pesanan Terlambat', shrink=0.8)
    for _, row in geo_pct.iterrows():
        ax2.annotate(row['customer_state'], (row['lon'], row['lat']),
                     fontsize=7.5, ha='center', fontweight='bold', color='#7f1d1d')
    ax2.set_title('Distribusi % Keterlambatan per Negara Bagian', fontweight='bold')
    ax2.set_xlabel('Longitude', fontsize=10)
    ax2.set_ylabel('Latitude', fontsize=10)
    ax2.grid(alpha=0.3, linestyle='--')

    plt.tight_layout()
    st.pyplot(fig5)
    plt.close()

    geo_fil = geo_df[geo_df['jumlah_pesanan'] >= min_pesanan].sort_values('total_revenue', ascending=False)
    tbl5 = geo_fil[['customer_state','total_revenue','jumlah_pesanan','pct_terlambat']].copy()
    tbl5['total_revenue']  = tbl5['total_revenue'].apply(lambda x: f"R$ {x:,.0f}")
    tbl5['jumlah_pesanan'] = tbl5['jumlah_pesanan'].apply(lambda x: f"{x:,}")
    tbl5['pct_terlambat']  = tbl5['pct_terlambat'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "-")
    tbl5.columns = ['Negara Bagian','Total Revenue','Jumlah Pesanan','% Terlambat']
    st.dataframe(tbl5, use_container_width=True, hide_index=True)

    with st.expander("💡 Insight"):
        st.markdown("- **SP** mendominasi revenue karena pusat ekonomi terbesar Brasil.\n"
                    "- Wilayah Utara (AM, RR, AP) revenue rendah + keterlambatan tinggi.\n"
                    "- Pola geografis ini konfirmasi temuan di Tab Pengiriman.")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.markdown(
    "<center><small>Dashboard Analisis E-Commerce Olist &nbsp;|&nbsp; "
    "Erson Gaby Wijaya &nbsp;|&nbsp; CDCC180D6Y2298 &nbsp;|&nbsp; "
    "Brazilian E-Commerce Public Dataset (2017–2018)</small></center>",
    unsafe_allow_html=True
)
