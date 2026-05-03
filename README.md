# Proyek Analisis Data: Brazilian E-Commerce Public Dataset (Olist)

## Deskripsi Proyek
Proyek ini merupakan analisis data komprehensif terhadap **Brazilian E-Commerce Public Dataset** dari Olist. Dataset mencakup lebih dari 99.000 pesanan pada periode September 2016 hingga Oktober 2018. Analisis mencakup eksplorasi revenue per kategori produk, performa pengiriman per negara bagian, serta perbandingan review score berdasarkan metode pembayaran.

## Struktur Direktori
```
submission/
├── dashboard/
│   └── dashboard.py
├── data/
│   ├── customers_dataset.csv
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

## Cara Menjalankan Dashboard

### 1. Persiapan Lingkungan (Setting Environment)

Disarankan menggunakan virtual environment agar tidak terjadi konflik library antar proyek.

**Menggunakan `venv` (Python bawaan):**
```bash
python -m venv venv
```

Aktifkan virtual environment:
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Mac / Linux:**
  ```bash
  source venv/bin/activate
  ```

**Atau menggunakan `conda`:**
```bash
conda create --name olist-env python=3.9
conda activate olist-env
```

### 2. Instalasi Dependensi

Setelah virtual environment aktif, install seluruh library yang dibutuhkan:

```bash
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard Secara Lokal

Masuk ke dalam folder `dashboard`, lalu jalankan perintah berikut:

```bash
cd dashboard
streamlit run dashboard.py
```

Dashboard akan terbuka otomatis di browser pada alamat:
```
http://localhost:8501
```

> **Catatan:** Pastikan folder `data/` yang berisi semua file CSV berada satu level di atas folder `dashboard/` (sesuai struktur direktori di atas), karena `dashboard.py` membaca data secara otomatis dari folder tersebut.

### 4. Mengakses Dashboard Online

Dashboard juga tersedia secara online melalui Streamlit Cloud.  
Tautan lengkapnya dapat dilihat di file **`url.txt`**.

---

## Library yang Digunakan

| Library | Fungsi |
|---------|--------|
| pandas | Manipulasi dan analisis data |
| numpy | Komputasi numerik |
| matplotlib | Visualisasi data |
| seaborn | Visualisasi statistik |
| streamlit | Pembuatan dashboard interaktif |

---

## Informasi Pengembang
- **Nama**: Erson Gaby Wijaya
- **Username Dicoding**: ersongabywijaya
- **Dataset**: Brazilian E-Commerce Public Dataset by Olist
