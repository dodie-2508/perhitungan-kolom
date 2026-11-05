import streamlit as st
import math

# Konfigurasi Halaman Web
st.set_page_config(page_title="Kalkulator Tulangan Kolom", layout="centered")
st.title("Perhitungan Penulangan Kolom")
st.write("Aplikasi untuk mengecek kapasitas tulangan lentur, geser, dan lebar penampang kolom berdasarkan SNI 2847.")

# --- FORM INPUT ---
with st.expander("1. Bahan Struktur", expanded=True):
    fc = st.number_input("Kuat tekan beton (fc') [MPa]", value=30.0)
    fy_lentur = st.number_input("Tegangan leleh baja lentur (fy) [MPa]", value=420.0)
    fy_geser = st.number_input("Tegangan leleh baja geser (fy) [MPa]", value=280.0)

with st.expander("2. Dimensi Kolom", expanded=True):
    b = st.number_input("Lebar kolom (b) [mm]", value=600.0)
    h = st.number_input("Panjang kolom (h) [mm]", value=600.0)
    ts = st.number_input("Tebal bersih selimut beton (ts) [mm]", value=40.0)

with st.expander("3. Momen & Gaya Geser Rencana (Output ETABS/SAP2000)", expanded=True):
    Pu = st.number_input("Gaya aksial terfaktor (Pu) [kN]", value=4785.39)
    Mu = st.number_input("Momen ultimit terfaktor (Mu) [kNm]", value=245.68)
    Vu = st.number_input("Gaya geser terfaktor (Vu) [kN]", value=125.70)

with st.expander("4. Rencana Tulangan (Input Pengguna)", expanded=True):
    st.markdown("### Tulangan Lentur Utama")
    col1, col2 = st.columns(2)
    with col1:
        n_lentur = st.number_input("Jumlah Buah Tulangan", min_value=1, value=8, step=1)
    with col2:
        D_lentur = st.number_input("Diameter Tulangan Deform (D) [mm]", min_value=6.0, value=22.0, step=1.0)

    st.markdown("### Tulangan Geser (Sengkang)")
    col3, col4, col5 = st.columns(3)
    with col3:
        n_geser = st.number_input("Jumlah Kaki Sengkang", min_value=1, value=2, step=1)
    with col4:
        D_geser = st.number_input("Diameter Sengkang (Ø) [mm]", min_value=4.0, value=10.0, step=1.0)
    with col5:
        s_geser = st.number_input("Jarak Sengkang (s) [mm]", min_value=10.0, value=200.0, step=5.0)

# --- TOMBOL RUN & EVALUASI ---
if st.button("Run / Evaluasi Keamanan"):
    try:
        st.markdown("---")
        st.subheader("Hasil Evaluasi")

        # ---------------- PERHITUNGAN DASAR ----------------
        Agr = b * h
        ds = ts + D_geser + (D_lentur / 2)
        d = h - ds
        
        # ---------------- 1. PENGECEKAN TULANGAN LENTUR ----------------
        st.markdown("### 🔹 Tulangan Lentur (Aksial)")
        As = n_lentur * (0.25 * math.pi * (D_lentur**2))
        
        rho_akt = As / Agr
        rho_min = 0.01  # Syarat minimum SNI untuk kolom (1%)
        phi_aksial = 0.65 
        
        phi_Pn = 0.80 * phi_aksial * ((0.85 * fc * (Agr - As)) + (fy_lentur * As)) / 1000 # kN
        
        st.write(f"Rencana Tulangan Lentur Terpasang: **{n_lentur}D{int(D_lentur)}**")
        st.write(f"Luas Tulangan Terpasang (As): **{As:.2f} mm²**")
        st.write(f"Rasio Penulangan (rho): **{rho_akt:.4f}** (Minimum syarat: **{rho_min:.2f}**)")
        st.write(f"Kapasitas Aksial Nominal (phi Pn): **{phi_Pn:.2f} kN**")
        st.write(f"Gaya Aksial Rencana (Pu): **{Pu:.2f} kN**")

        if rho_akt < rho_min:
            st.error(f"❌ TULANGAN LENTUR ({n_lentur}D{int(D_lentur)}) TIDAK OKE: Rasio penulangan ({rho_akt*100:.2f}%) kurang dari syarat minimum 1% (Ast < 0.01 Agr).")
        elif phi_Pn < Pu:
            st.error(f"❌ TULANGAN LENTUR ({n_lentur}D{int(D_lentur)}) TIDAK OKE: Kapasitas phi Pn ({phi_Pn:.2f} kN) lebih kecil dari beban aksial rencana Pu ({Pu:.2f} kN).")
        else:
            st.success(f"✅ TULANGAN LENTUR ({n_lentur}D{int(D_lentur)}) SUDAH AMAN (Memenuhi syarat kapasitas & rasio minimum).")

        # ---------------- 2. PEMERIKSAAN LEBAR KOLOM (SPASI TULANGAN) ----------------
        st.markdown("### 🔹 Pemeriksaan Lebar Kolom (Spasi Tulangan)")
        tebal_selimut_total = 2 * ts
        sengkang_total = 2 * D_geser
        n_sisi_lebar = max(2, math.ceil(n_lentur / 2))
        lebar_tulangan_pakai = n_sisi_lebar * D_lentur
        spasi_bersih = max(25.0, D_lentur)
        jumlah_spasi = max(0, n_sisi_lebar - 1)
        total_spasi_bersih = jumlah_spasi * spasi_bersih
        
        total_lebar_fisik = tebal_selimut_total + sengkang_total + lebar_tulangan_pakai + total_spasi_bersih

        st.write(f"- Tebal selimut beton (2 sisi): 2 x {ts} = {tebal_selimut_total} mm")
        st.write(f"- Sengkang (2 sisi): 2 x {D_geser} = {sengkang_total} mm")
        st.write(f"- Tulangan terpakai pada sisi lebar ({n_sisi_lebar} buah D{int(D_lentur)}): {n_sisi_lebar} x {D_lentur} = {lebar_tulangan_pakai} mm")
        st.write(f"- Jarak bersih antar tulangan ({jumlah_spasi} celah): {jumlah_spasi} x {spasi_bersih} = {total_spasi_bersih} mm")
        st.write(f"- **Total Kebutuhan Lebar:** **{total_lebar_fisik:.1f} mm** (Lebar Kolom b = {b} mm)")

        if total_lebar_fisik <= b:
            st.success(f"✅ PEMERIKSAAN LEBAR KOLOM SUDAH AMAN (Total kebutuhan {total_lebar_fisik:.1f} mm < Lebar Kolom {b} mm)")
        else:
            st.error(f"❌ PEMERIKSAAN LEBAR KOLOM TIDAK OKE: Tulangan terlalu padat/lebar ({total_lebar_fisik:.1f} mm) melebihi lebar kolom b = {b} mm!")

        # ---------------- 3. PENGECEKAN TULANGAN GESER ----------------
        st.markdown("### 🔹 Tulangan Geser (Sengkang)")
        phi_v = 0.75
        
        Vc = (math.sqrt(fc) / 6) * b * d / 1000 # kN
        phi_Vc = phi_v * Vc
        
        st.write(f"Gaya Geser Rencana (Vu): **{Vu:.2f} kN**")
        st.write(f"Kapasitas Geser Beton (phi Vc): **{phi_Vc:.2f} kN**")

        if Vu > (0.5 * phi_Vc):
            if Vu > phi_Vc:
                st.warning("⚠️ Perlu tulangan geser struktural (Vu > phi Vc).")
            else:
                st.info("ℹ️ Perlu tulangan geser minimum (0.5 phi Vc < Vu <= phi Vc).")
                
            Av_pakai = n_geser * (0.25 * math.pi * (D_geser**2))
            Av_s_pakai = Av_pakai / s_geser
            Av_s_min = b / (3 * fy_geser)
            
            if Vu > phi_Vc:
                Vs_perlu = ((Vu - phi_Vc) / phi_v) * 1000 
                Av_s_struktur = Vs_perlu / (fy_geser * d)
            else:
                Av_s_struktur = 0
                
            Av_s_perlu = max(Av_s_min, Av_s_struktur)
            s_max = d / 2 

            st.write(f"Kebutuhan Luas Geser (Av/s perlu): **{Av_s_perlu:.3f} mm²/mm**")
            st.write(f"Kapasitas Terpasang (Av/s pakai): **{Av_s_pakai:.3f} mm²/mm**")
            
            aman_geser = True
            if Av_s_pakai < Av_s_perlu:
                st.error(f"❌ TULANGAN GESER ({n_geser}D{int(D_geser)}-{int(s_geser)}) TIDAK OKE: Kapasitas sengkang kurang dari kebutuhan rasio geser.")
                aman_geser = False
            
            if s_geser > s_max:
                st.error(f"❌ JARAK SENGKANG ({n_geser}D{int(D_geser)}-{int(s_geser)}) TIDAK OKE: Jarak spasi {s_geser} mm melebihi batas maksimum d/2 ({s_max:.1f} mm).")
                aman_geser = False
                
            if aman_geser:
                st.success(f"✅ TULANGAN GESER ({n_geser}D{int(D_geser)}-{int(s_geser)}) SUDAH AMAN.")
        else:
            st.success(f"✅ TULANGAN GESER ({n_geser}D{int(D_geser)}-{int(s_geser)}) SUDAH AMAN (Vu <= 0.5 phi Vc, cukup sengkang minimum).")

    except Exception as e:
        st.error(f"Terjadi kesalahan dalam perhitungan: {e}")