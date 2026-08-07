import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="מעקב וניתוח משכורות", page_icon="💰", layout="wide"
)

FILENAME = "salaries.csv"

# --- Полный список колонок ---
COLUMNS = [
    "year",
    "month",
    "gross",
    "net",
    "tax",
    "bituach_leumi",
    "bituach_briut",
    "pension",
    "kupat_gemel",
    "shares",
    "other_deductions",
]


def load_data():
    if os.path.exists(FILENAME):
        try:
            df = pd.read_csv(FILENAME)
            # Автоматически добавляем отсутствующие столбцы со значением 0.0
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = 0.0
            return df
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_csv(FILENAME, index=False)


if "df" not in st.session_state:
    st.session_state.df = load_data()

st.title("💰 מעקב וניתוח משכורות (Учёт и анализ зарплат)")
st.caption("מערכת מעקב והשוואת שכר שנתית וחודשית")

# --- Боковая панель: Ввод данных ---
with st.sidebar:
    st.header("➕ הוספת / עדכון חודש")
    with st.form("salary_form", clear_on_submit=False):
        col_y, col_m = st.columns(2)
        with col_y:
            input_year = st.number_input(
                "שנה (Год)", min_value=2015, max_value=2035, value=2026, step=1
            )
        with col_m:
            input_month = st.selectbox(
                "חודש (Месяц)", options=list(range(1, 13))
            )

        st.subheader("פירוט נתונים (₪)")
        input_gross = st.number_input(
            "משכורת ברוטו", min_value=0.0, step=100.0, format="%.2f"
        )
        input_net = st.number_input(
            "נטו", min_value=0.0, step=100.0, format="%.2f"
        )
        input_tax = st.number_input(
            "מס הכנסה", min_value=0.0, step=50.0, format="%.2f"
        )
        input_bl = st.number_input(
            "ביטוח לאומי", min_value=0.0, step=50.0, format="%.2f"
        )
        input_health = st.number_input(
            "ביטוח בריאות", min_value=0.0, step=50.0, format="%.2f"
        )
        input_pension = st.number_input(
            "פנסיה", min_value=0.0, step=50.0, format="%.2f"
        )
        input_gemel = st.number_input(
            "קופת גמל", min_value=0.0, step=50.0, format="%.2f"
        )
        input_shares = st.number_input(
            "מניות", min_value=0.0, step=50.0, format="%.2f"
        )
        input_other = st.number_input(
            "שעות/תוספות/ניכויים", min_value=0.0, step=50.0, format="%.2f"
        )

        submit_btn = st.form_submit_button("שמור נתונים (Сохранить)")

if submit_btn:
    df_curr = st.session_state.df.copy()
    mask = (df_curr["year"] == input_year) & (df_curr["month"] == input_month)

    new_data = {
        "year": int(input_year),
        "month": int(input_month),
        "gross": float(input_gross),
        "net": float(input_net),
        "tax": float(input_tax),
        "bituach_leumi": float(input_bl),
        "bituach_briut": float(input_health),
        "pension": float(input_pension),
        "kupat_gemel": float(input_gemel),
        "shares": float(input_shares),
        "other_deductions": float(input_other),
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

# --- Главная аналитика ---
if not st.session_state.df.empty:
    df = st.session_state.df.copy()

    # Проверяем наличие всех нужных колонок
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0.0

    tab_all, tab_year, tab_manage = st.tabs(
        [
            "📊 השוואה כללית (Все годы)",
            "📅 ניתוח לפי שנה (По годам)",
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

        # Главный график всех лет
        fig_all, ax_all = plt.subplots(figsize=(12, 5))
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

        for i in x:
            g_val = yearly_summary["total_gross"].iloc[i]
            n_val = yearly_summary["total_net"].iloc[i]
            ax_all.text(
                i - width / 2,
                g_val,
                f"₪{g_val:,.0f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
            ax_all.text(
                i + width / 2,
                n_val,
                f"₪{n_val:,.0f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        st.pyplot(fig_all)

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

    # ==================== ВКЛАДКА 2: Конкретный год ====================
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

        # Безопасное формирование строки Итого (סה"כ)
        st.write(f"### טבלת נתונים לשנת {selected_year}")

        df_year_disp = df_year.copy()
        df_year_disp["month"] = df_year_disp["month"].apply(
            lambda m: f"{m:02d}.{selected_year}"
        )

        sum_row = {
            "month": 'סה"כ',
            "gross": df_year["gross"].sum(),
            "net": df_year["net"].sum(),
            "tax": df_year.get("tax", pd.Series([0])).sum(),
            "bituach_leumi": df_year.get("bituach_leumi", pd.Series([0])).sum(),
            "bituach_briut": df_year.get("bituach_briut", pd.Series([0])).sum(),
            "pension": df_year.get("pension", pd.Series([0])).sum(),
            "kupat_gemel": df_year.get("kupat_gemel", pd.Series([0])).sum(),
            "shares": df_year.get("shares", pd.Series([0])).sum(),
            "other_deductions": df_year.get(
                "other_deductions", pd.Series([0])
            ).sum(),
        }
        df_year_disp = pd.concat(
            [df_year_disp, pd.DataFrame([sum_row])], ignore_index=True
        )

        # Переименование колонок
        df_year_disp.rename(
            columns={
                "month": "חודש",
                "gross": "משכורת ברוטו",
                "net": "נטו",
                "tax": "מס הכנסה",
                "bituach_leumi": "ביטוח לאומי",
                "bituach_briut": "ביטוח בריאות",
                "pension": "פנסיה",
                "kupat_gemel": "קופת גמל",
                "shares": "מניות",
                "other_deductions": "שעות/תוספות",
            },
            inplace=True,
        )

        cols_to_format = [
            "משכורת ברוטו",
            "נטו",
            "מס הכנסה",
            "ביטוח לאומי",
            "ביטוח בריאות",
            "פנסיה",
            "קופת גמל",
            "מניות",
            "שעות/תוספות",
        ]
        fmt_dict = {
            c: "₪{:,.2f}" for c in cols_to_format if c in df_year_disp.columns
        }

        st.dataframe(
            df_year_disp.drop(columns=["year"], errors="ignore").style.format(
                fmt_dict
            ),
            use_container_width=True,
        )

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
