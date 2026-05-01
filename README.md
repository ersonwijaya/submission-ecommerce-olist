# Proyek Analisis Data: Brazilian E-Commerce Public Dataset (Olist)

**Erson Gaby Wijaya | CDCC180D6Y2298**

---

## Deskripsi Proyek

Proyek ini merupakan analisis data komprehensif terhadap **Brazilian E-Commerce Public Dataset** dari Olist — marketplace e-commerce terbesar di Brasil. Dataset mencakup lebih dari 99.000 pesanan pada periode **September 2016 hingga Oktober 2018**.

### Pertanyaan Bisnis yang Dijawab
1. Revenue & Kategori Produk — Kategori produk apa yang menghasilkan total pendapatan tertinggi, dan bagaimana tren pendapatan bulanan 5 kategori teratas sepanjang 2017–2018?
2. Performa Pengiriman — Negara bagian mana yang memiliki persentase keterlambatan pengiriman tertinggi, dan berapa rata-rata hari keterlambatannya?
3. Review Score & Metode Pembayaran — Apakah terdapat perbedaan signifikan pada rata-rata review score antara pengguna credit card, boleto, dan voucher?

### Analisis Lanjutan
- RFM Analysis — Segmentasi pelanggan (Champions, Loyal, Recent, At Risk, dll.)
- Geospatial Analysis — Pemetaan revenue dan keterlambatan per negara bagian Brasil
- Clustering Manual / Binning — Segmentasi pelanggan berdasarkan nilai dan frekuensi belanja

---

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

---

## Cara Menjalankan Dashboard

### 1. Persiapan Lingkungan

Pastikan Python 3.8+ sudah terinstal. Install seluruh library yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard Secara Lokal

Masuk ke dalam folder `dashboard`, lalu jalankan perintah berikut:

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada alamat:
```
http://localhost:8501
```

> **Catatan:** File `main_data.csv` harus berada di folder yang sama dengan `dashboard.py` agar dashboard dapat berjalan dengan benar.

### 3. Mengakses Dashboard Online

Dashboard juga tersedia secara online melalui Streamlit Cloud.  
Tautan lengkapnya dapat dilihat di file **`url.txt`**.

---

## Library yang Digunakan

| Library | Versi | Fungsi |
|---------|-------|--------|
| pandas | ≥1.5.0 | Manipulasi dan analisis data |
| numpy | ≥1.23.0 | Komputasi numerik |
| matplotlib | ≥3.6.0 | Visualisasi data |
| seaborn | ≥0.12.0 | Visualisasi statistik |
| streamlit | ≥1.28.0 | Pembuatan dashboard interaktif |

---

## Fitur Dashboard

Dashboard memiliki 5 tab interaktif:

| Tab | Konten |
|-----|--------|
| Revenue & Produk | Bar chart Top N kategori + Line chart tren bulanan |
| Performa Pengiriman | Bar horizontal % terlambat + Box plot distribusi + Pie chart status |
| Review & Pembayaran | Grouped bar distribusi score + Bar rata-rata per metode |
| Analisis RFM | Donut chart segmen + Bar monetary + Distribusi binning |
| Geospatial | Scatter map Brasil — revenue & keterlambatan per negara bagian |

**Filter yang tersedia di sidebar:**
- Filter tahun (2017 / 2018 / keduanya)
- Slider Top N kategori yang ditampilkan (5–20)
- Minimum pesanan per negara bagian untuk filter geospasial

---

## Informasi Pengembang

- **Nama**: Erson Gaby Wijaya  
- **ID Dicoding**: CDCC180D6Y2298  
- **Dataset**: [Brazilian E-Commerce Public Dataset by Olist](https://drive.google.com/file/d/1MsAjPM7oKtVfJL_wRp1qmCajtSG1mdcK/view?usp=sharing)