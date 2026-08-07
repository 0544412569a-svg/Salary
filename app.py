import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="מעקב וניתוח משכורות", page_icon="💰", layout="wide"
)

FILENAME = "salaries.csv"

# --- Список нужных колонок ---
COLUMNS = [
    "year",
    "month",
    "gross",
    "net",
    "tax",
    "bituach_leumi",
    "bituach_briut",
    "kupat_gemel",
    "shares",
]


def load_data():
    if os.path.exists(FILENAME):
        try:
            df = pd.read_csv(FILENAME)
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = 0.0
            return df[COLUMNS]
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df[COLUMNS].to_csv(FILENAME, index=False)


if "df" not in st.session_state:
    st.session_state.df = load_data()

st.title("💰 מעקב וניתוח משכורות")
st.caption("מערכת מעקב והשוואת שכר שנתית וחודשית")

# --- Боковая панель: Ввод и редактирование данных ---
with st.sidebar:
    st.header("➕ הוספת / עדכון חודש")

    col_y, col_m = st.columns(2)
    with col_y:
        input_year = st.number_input(
            "שנה (Год)", min_value=2015, max_value=2035, value=2026, step=1
        )
    with col_m:
        input_month = st.selectbox("חודש (Месяц)", options=list(range(1, 13)))

    # Проверка существования записи за выбранный период
    df_curr = st.session_state.df.copy()
    existing_row = df_curr[
        (df_curr["year"] == input_year) & (df_curr["month"] == input_month)
    ]

    is_edit = not existing_row.empty
    if is_edit:
        st.info(f"✏️ עריכת נתונים קיימים עבור {input_month}.{input_year}")
        row_data = existing_row.iloc[0]
        def_gross = (
            float(row_data["gross"]) if pd.notnull(row_data["gross"]) else None
        )
        def_net = (
            float(row_data["net"]) if pd.notnull(row_data["net"]) else None
        )
        def_tax = (
            float(row_data["tax"]) if pd.notnull(row_data["tax"]) else None
        )
        def_bl = (
            float(row_data["bituach_leumi"])
            if pd.notnull(row_data["bituach_leumi"])
            else None
        )
        def_health = (
            float(row_data["bituach_briut"])
            if pd.notnull(row_data["bituach_briut"])
            else None
        )
        def_gemel = (
            float(row_data["kupat_gemel"])
            if pd.notnull(row_data["kupat_gemel"])
            else None
        )
        def_shares = (
            float(row_data["shares"])
            if pd.notnull(row_data["shares"])
            else None
        )
    else:
        st.caption(f"🆕 הוספת חודש חדש: {input_month}.{input_year}")
        def_gross = None
        def_net = None
        def_tax = None
        def_bl = None
        def_health = None
        def_gemel = None
        def_shares = None

    with st.form("salary_form", clear_on_submit=False):
        st.subheader("פירוט נתונים (₪)")

        input_gross = st.number_input(
            "משכורת ברוטו",
            value=def_gross,
            step=100.0,
            format="%.2f",
            placeholder="0.00",
        )
        input_net = st.number_input(
            "נטו", value=def_net, step=100.0, format="%.2f", placeholder="0.00"
        )
        input_tax = st.number_input(
            "מס הכנסה", value=def_tax, step=50.0, format="%.2f", placeholder="0.00"
        )
        input_bl = st.number_input(
            "ביטוח לאומי", value=def_bl, step=50.0, format="%.2f", placeholder="0.00"
        )
        input_health = st.number_input(
            "ביטוח בריאות",
            value=def_health,
            step=50.0,
            format="%.2f",
            placeholder="0.00",
        )
        input_gemel = st.number_input(
            "קופת גמל",
            value=def_gemel,
            step=50.0,
            format="%.2f",
            placeholder="0.00",
        )
        input_shares = st.number_input(
            "מניות", value=def_shares, step=50.0, format="%.2f", placeholder="0.00"
        )

        btn_text = (
            "עדכן נתונים (Обновить)"
            if is_edit
            else "שמור נתונים (Сохранить)"
        )
        submit_btn = st.form_submit_button(btn_text)

if submit_btn:
    df_curr = st.session_state.df.copy()
    mask = (df_curr["year"] == input_year) & (df_curr["month"] == input_month)

    new_data = {
        "year": int(input_year),
        "month": int(input_month),
        "gross": float(input_gross) if input_gross is not None else 0.0,
        "net": float(input_net) if input_net is not None else 0.0,
        "tax": float(input_tax) if input_tax is not None else 0.0,
        "bituach_leumi": float(input_bl) if input_bl is not None else 0.0,
        "bituach_briut": float(input_health) if input_health is not None else 0.0,
        "kupat_gemel": float(input_gemel) if input_gemel is not None else 0.0,
        "shares": float(input_shares) if input_shares is not None else 0.0,
    }

    if mask.any():
        for key, val in new_data.items():
            df_curr.loc[mask, key] = val
    else:
        df_curr = pd.concat(
            [df_curr, pd.DataFrame([new_data])], ignore_index=True
        )

    df_curr = df_curr.sort_values(by=["year", "month"]).reset_index(drop=True)
    st.session_state.df = df_curr
    save_data(df_curr)
    st.sidebar.success(f"נשמר בהצלחה עבור {input_month}.{input_year}!")
    st.rerun()

# --- Главный блок аналитики ---
if not st.session_state.df.empty:
    df = st.session_state.df.copy()

    tab_all, tab_year, tab_manage = st.tabs(
        [
            "📊 השוואה כללית (Все годы)",
            "📅 ניתוח לפי שנה (По годаם)",
            "⚙️ ניהול נתונים (Управление)",
        ]
    )

    # ==================== ВКЛАДКА 1: Все годы ====================
    with tab_all:
        st.subheader("📈 השוואת הכנסות לפי שנים")

        yearly_summary = (
            df.groupby("year")
            .agg(
                total_gross=("gross", "sum"),
                total_net=("net", "sum"),
                avg_monthly_net=("net", "mean"),
            )
            .reset_index()
        )

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("שנים במערכת", len(yearly_summary))
        col_m2.metric(
            "שיא ברוטו שנתי", f"₪{yearly_summary['total_gross'].max():,.2f}"
        )
        col_m3.metric(
            "שיא נטו שנתי", f"₪{yearly_summary['total_net'].max():,.2f}"
        )

        # График 1: Столбчатый график сравнения сумм по годам
        fig_all, ax_all = plt.subplots(figsize=(12, 4.5))
        years = yearly_summary["year"].astype(str)
        x = range(len(years))
        width = 0.35

        ax_all.bar(
            [i - width / 2 for i in x],
            yearly_summary["total_gross"],
            width,
            label="משכורת ברוטו",
            color="#2b5c8f",
        )
        ax_all.bar(
            [i + width / 2 for i in x],
            yearly_summary["total_net"],
            width,
            label="נטו",
            color="#27ae60",
        )

        ax_all.set_xticks(list(x))
        ax_all.set_xticklabels(years)
        ax_all.set_ylabel("סכום (₪)")
        ax_all.set_title("השוואת הכנסות שנתית (ברוטו מול נטו)")
        ax_all.legend()
        ax_all.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig_all)

        # --- График 2: Волновой график сравнения נטו по месяцам от года к году ---
        st.markdown("---")
        st.subheader("🌊 השוואת נטו חודשי בין השנים (משנה לשנה)")

        fig_wave, ax_wave = plt.subplots(figsize=(12, 5))

        months_list = list(range(1, 13))
        months_labels = [f"{m:02d}" for m in months_list]

        # Уникальные годы для отрисовки разных линий
        unique_years = sorted(df["year"].unique())

        for y in unique_years:
            df_y = df[df["year"] == y]
            # Заполняем пропущенные месяцы значением None, чтобы линия не прерывалась или корректно строилась
            net_by_month = []
            for m in months_list:
                val = df_y[df_y["month"] == m]["net"]
                net_by_month.append(val.values[0] if not val.empty else None)

            ax_wave.plot(
                months_labels,
                net_by_month,
                marker="o",
                linewidth=2.5,
                markersize=6,
                label=f"שנת {y}",
            )

        ax_wave.set_xlabel("חודש (Месяц)")
        ax_wave.set_ylabel("נטו (₪)")
        ax_wave.set_title("מגמת נטו חודשית - השוואה לפי שנים")
        ax_wave.legend(title="שנה")
        ax_wave.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig_wave)

        st.markdown("---")
        st.write("### טבלת סיכום שנתית")
        yearly_disp = yearly_summary.copy()
        yearly_disp.columns = [
            "שנה",
            "סה\"כ ברוטו",
            "סה\"כ נטו",
            "ממוצע נטו חודשי",
        ]
        st.dataframe(
            yearly_disp.style.format(
                {
                    "סה\"כ ברוטו": "₪{:,.2f}",
                    "סה\"כ נטו": "₪{:,.2f}",
                    "ממוצע נטו חודשי": "₪{:,.2f}",
                }
            ),
            use_container_width=True,
        )

    # ==================== ВКЛАДКА 2: Выбранный год ====================
    with tab_year:
        available_years = sorted(df["year"].unique(), reverse=True)
        selected_year = st.selectbox(
            "בחר שנה להצגה (Выберите год):", options=available_years
        )

        df_year = (
            df[df["year"] == selected_year]
            .sort_values(by="month")
            .reset_index(drop=True)
        )

        st.subheader(f"📊 פירוט נתוני שכר לשנת {selected_year}")

        y_gross_sum = df_year["gross"].sum()
        y_net_sum = df_year["net"].sum()
        y_net_avg = df_year["net"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric(f"סה\"כ ברוטו {selected_year}", f"₪{y_gross_sum:,.2f}")
        c2.metric(f"סה\"כ נטו {selected_year}", f"₪{y_net_sum:,.2f}")
        c3.metric(f"ממוצע נטו לחודש", f"₪{y_net_avg:,.2f}")

        # График за выбранный год
        fig_y, ax_y = plt.subplots(figsize=(11, 4.5))
        m_labels = [f"{m:02d}.{selected_year}" for m in df_year["month"]]

        ax_y.bar(
            m_labels, df_year["net"], color="#3498db", alpha=0.85, label="נטו"
        )
        ax_y.axhline(
            y_net_avg,
            color="#e74c3c",
            linestyle="--",
            label=f"ממוצע נטו: ₪{y_net_avg:,.2f}",
        )

        ax_y.set_ylabel("סכום (₪)")
        ax_y.set_title(f"הכנסה חודשית (נטו) לשנת {selected_year}")
        ax_y.legend()
        ax_y.grid(True, linestyle="--", alpha=0.5)

        for i, val in enumerate(df_year["net"]):
            ax_y.text(
                i, val, f"₪{val:,.0f}", ha="center", va="bottom", fontsize=8
            )

        st.pyplot(fig_y)

        # --- Формирование и стилизация таблицы ---
        st.write(f"### טבלת נתונים לשנת {selected_year}")

        df_year_disp = df_year[COLUMNS].copy()
        df_year_disp["month"] = df_year_disp["month"].apply(
            lambda m: f"{m:02d}.{selected_year}"
        )

        numeric_cols = [
            "gross",
            "net",
            "tax",
            "bituach_leumi",
            "bituach_briut",
            "kupat_gemel",
            "shares",
        ]

        # Строка 1: Итого (סה"כ)
        sum_row = {"month": 'סה"כ'}
        for col in numeric_cols:
            sum_row[col] = df_year[col].sum()

        # Строка 2: Среднее (ממוצע)
        avg_row = {"month": "ממוצע"}
        for col in numeric_cols:
            avg_row[col] = df_year[col].mean()

        df_final = pd.concat(
            [df_year_disp, pd.DataFrame([sum_row, avg_row])], ignore_index=True
        )

        # Переименование колонок
        df_final.rename(
            columns={
                "month": "חודש",
                "gross": "משכורת ברוטו",
                "net": "נטו",
                "tax": "מס הכנסה",
                "bituach_leumi": "ביטוח לאומי",
                "bituach_briut": "ביטוח בריאות",
                "kupat_gemel": "קופת גמל",
                "shares": "מניות",
            },
            inplace=True,
        )

        # --- Функция стилизации таблицы ---
        def style_dataframe(df_to_style):
            def highlight_summary_rows(row):
                if row["חודש"] == 'סה"כ':
                    return [
                        "background-color: #d0e1f9; font-weight: bold; color: #000000;"
                    ] * len(row)
                elif row["חודש"] == "ממוצע":
                    return [
                        "background-color: #e6e6e6; font-weight: bold; color: #000000;"
                    ] * len(row)
                return [""] * len(row)

            def color_negative_red(val):
                if isinstance(val, (int, float)) and val < 0:
                    return "color: #e74c3c; font-weight: bold;"
                return ""

            cols_to_format = [
                "משכורת ברוטו",
                "נטו",
                "מס הכנסה",
                "ביטוח לאומי",
                "ביטוח בריאות",
                "קופת גמל",
                "מניות",
            ]
            fmt_dict = {
                c: "₪{:,.2f}"
                for c in cols_to_format
                if c in df_to_style.columns
            }

            styler = df_to_style.drop(columns=["year"], errors="ignore").style

            styler = styler.apply(highlight_summary_rows, axis=1)

            if hasattr(styler, "map"):
                styler = styler.map(color_negative_red, subset=cols_to_format)
            else:
                styler = styler.applymap(color_negative_red, subset=cols_to_format)

            styler = styler.format(fmt_dict)

            return styler

        st.dataframe(style_dataframe(df_final), use_container_width=True)

    # ==================== ВКЛАДКА 3: Управление ====================
    with tab_manage:
        st.subheader("📥 הורדת נתונים ומחיקה")

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 הורד את כל הנתונים בקובץ CSV (Скачать CSV)",
            data=csv_bytes,
            file_name="salaries_data.csv",
            mime="text/csv",
        )

        st.markdown("---")
        st.write("### מחיקת רשומה (Удаление записи)")
        del_options = [
            f"שנה: {row['year']} — חודש: {int(row['month']):02d} (נטו: ₪{row['net']:,.2f})"
            for _, row in df.iterrows()
        ]
        selected_del = st.selectbox(
            "בחר רשומה למחיקה (Выберите запись):", options=del_options
        )

        if st.button("❌ מחק רשומה (Удалить)"):
            idx = del_options.index(selected_del)
            df_updated = df.drop(df.index[idx]).reset_index(drop=True)
            st.session_state.df = df_updated
            save_data(df_updated)
            st.success("הרשומה נמחקה בהצלחה!")
            st.rerun()
else:
    st.info(
        "אין נתונים במערכת. אנא הוסף את המשכורת הראשונה שלך בסרגל הצד! (Добавьте данные в левой панели)"
    )
