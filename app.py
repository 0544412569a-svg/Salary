import os
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Анализ и Учёт Зарплат", page_icon="💰", layout="wide"
)

FILENAME = "salaries.csv"

# --- Инициализация базовых колонок ---
COLUMNS = [
    "year",
    "month",
    "gross",
    "net",
    "tax",
    "bituach_leumi",
    "pension",
    "keren_ishtalmut",
    "other_deductions",
]


def load_data():
    if os.path.exists(FILENAME):
        try:
            df = pd.read_csv(FILENAME)
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

st.title("💰 Учёт, Анализ и Сравнение Зарплат")
st.caption(
    "Замена Excel: автоматический сбор, аналитика по годам и глобальное сравнение"
)

# --- Боковая панель: Ввод новых данных ---
with st.sidebar:
    st.header("➕ Добавить / Обновить месяц")
    with st.form("salary_form", clear_on_submit=False):
        col_y, col_m = st.columns(2)
        with col_y:
            input_year = st.number_input(
                "Год", min_value=2015, max_value=2035, value=2026, step=1
            )
        with col_m:
            input_month = st.selectbox("Месяц", options=list(range(1, 13)))

        st.subheader("Детализация (₪ / $)")
        input_gross = st.number_input(
            "Брутто (ברוטו)", min_value=0.0, step=100.0, format="%.2f"
        )
        input_net = st.number_input(
            "Нетто (נטו)", min_value=0.0, step=100.0, format="%.2f"
        )
        input_tax = st.number_input(
            "Подоходный налог (מס הכנסה)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
        )
        input_bl = st.number_input(
            "Битуах Леуми / Здоровье (ביטוח לאומי)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
        )
        input_pension = st.number_input(
            "Пенсия (פנסיה עובד)", min_value=0.0, step=50.0, format="%.2f"
        )
        input_keren = st.number_input(
            "Керен Иштальмут (קרן השתלמות)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
        )
        input_other = st.number_input(
            "Прочие вычеты/бонусы", min_value=0.0, step=50.0, format="%.2f"
        )

        submit_btn = st.form_submit_button("Сохранить запись")

if submit_btn:
    df_curr = st.session_state.df.copy()
    # Проверяем, есть ли уже запись за этот год и месяц
    mask = (df_curr["year"] == input_year) & (df_curr["month"] == input_month)

    new_data = {
        "year": int(input_year),
        "month": int(input_month),
        "gross": float(input_gross),
        "net": float(input_net),
        "tax": float(input_tax),
        "bituach_leumi": float(input_bl),
        "pension": float(input_pension),
        "keren_ishtalmut": float(input_keren),
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
    st.sidebar.success(f"Сохранено за {input_month}.{input_year}!")
    st.rerun()

# --- Главная страница с графиками и аналитикой ---
if not st.session_state.df.empty:
    df = st.session_state.df.copy()

    # Вкладки
    tab_all, tab_year, tab_manage = st.tabs(
        [
            "📊 Глобальное сравнение всех лет",
            "📅 Анализ конкретного года",
            "⚙️ Управление данными и Экспорт",
        ]
    )

    # ==================== ВКЛАДКА 1: Все годы ====================
    with tab_all:
        st.subheader("📈 Сравнение годовых и месячных показателей за все годы")

        # Агрегация по годам
        yearly_summary = (
            df.groupby("year")
            .agg(
                total_gross=("gross", "sum"),
                total_net=("net", "sum"),
                avg_monthly_net=("net", "mean"),
            )
            .reset_index()
        )

        # Вывод ключевых метрик
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Всего лет в базе", len(yearly_summary))
        col_m2.metric(
            "Рекордный Брутто за год",
            f"₪{yearly_summary['total_gross'].max():,.2f}",
        )
        col_m3.metric(
            "Рекордный Нетто за год",
            f"₪{yearly_summary['total_net'].max():,.2f}",
        )

        # Главный график сравнения всех лет
        fig_all, ax_all = plt.subplots(figsize=(12, 5))
        years = yearly_summary["year"].astype(str)
        x = range(len(years))
        width = 0.35

        ax_all.bar(
            [i - width / 2 for i in x],
            yearly_summary["total_gross"],
            width,
            label="Сумма Брутто (ברוטו)",
            color="#2b5c8f",
        )
        ax_all.bar(
            [i + width / 2 for i in x],
            yearly_summary["total_net"],
            width,
            label="Сумма Нетто (נטו)",
            color="#27ae60",
        )

        ax_all.set_xticks(list(x))
        ax_all.set_xticklabels(years)
        ax_all.set_ylabel("Сумма за год (₪ / $)")
        ax_all.set_title("Сравнение общих доходов по годам")
        ax_all.legend()
        ax_all.grid(True, linestyle="--", alpha=0.5)

        # Подписи значений над столбцами
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

        # Сводная таблица по годам
        st.write("### Сводная таблица по годам")
        yearly_disp = yearly_summary.copy()
        yearly_disp.columns = [
            "Год",
            "Итого Брутто",
            "Итого Нетто",
            "Средний Нетто в месяц",
        ]
        st.dataframe(
            yearly_disp.style.format(
                {
                    "Итого Брутто": "₪{:,.2f}",
                    "Итого Нетто": "₪{:,.2f}",
                    "Средний Нетто в месяц": "₪{:,.2f}",
                }
            ),
            use_container_width=True,
        )

    # ==================== ВКЛАДКА 2: Конкретный год ====================
    with tab_year:
        available_years = sorted(df["year"].unique(), reverse=True)
        selected_year = st.selectbox(
            "Выберите год для детального просмотра:", options=available_years
        )

        df_year = (
            df[df["year"] == selected_year]
            .sort_values(by="month")
            .reset_index(drop=True)
        )

        st.subheader(f"📊 Динамика зарплаты за {selected_year} год")

        # Метрики года
        y_gross_sum = df_year["gross"].sum()
        y_net_sum = df_year["net"].sum()
        y_net_avg = df_year["net"].mean()

        c1, c2, c3 = st.columns(3)
        c1.metric(f"Итого Брутто {selected_year}", f"₪{y_gross_sum:,.2f}")
        c2.metric(f"Итого Нетто {selected_year}", f"₪{y_net_sum:,.2f}")
        c3.metric(f"Средний Нетто/мес", f"₪{y_net_avg:,.2f}")

        # График по 12 месяца выбранного года (как в Excel)
        fig_y, ax_y = plt.subplots(figsize=(11, 4.5))
        m_labels = [f"{m:02d}.{selected_year}" for m in df_year["month"]]

        ax_y.bar(
            m_labels,
            df_year["net"],
            color="#3498db",
            alpha=0.85,
            label="Нетто (נטו)",
        )
        ax_y.axhline(
            y_net_avg,
            color="#e74c3c",
            linestyle="--",
            label=f"Среднее Нетто: ₪{y_net_avg:,.2f}",
        )

        ax_y.set_ylabel("Сумма (₪)")
        ax_y.set_title(f"Ежемесячный доход (Нетто) за {selected_year} год")
        ax_y.legend()
        ax_y.grid(True, linestyle="--", alpha=0.5)

        for i, val in enumerate(df_year["net"]):
            ax_y.text(
                i, val, f"₪{val:,.0f}", ha="center", va="bottom", fontsize=8
            )

        st.pyplot(fig_y)

        # Таблица Excel-формата за этот год
        st.write(f"### Детальная таблица за {selected_year} год")

        df_year_disp = df_year.copy()
        df_year_disp["month"] = df_year_disp["month"].apply(
            lambda m: f"{m:02d}.{selected_year}"
        )

        # Добавляем строку СУММА (סה"כ)
        sum_row = {
            "month": "סה\"כ (Итого)",
            "gross": df_year["gross"].sum(),
            "net": df_year["net"].sum(),
            "tax": df_year["tax"].sum(),
            "bituach_leumi": df_year["bituach_leumi"].sum(),
            "pension": df_year["pension"].sum(),
            "keren_ishtalmut": df_year["keren_ishtalmut"].sum(),
            "other_deductions": df_year["other_deductions"].sum(),
        }
        df_year_disp = pd.concat(
            [df_year_disp, pd.DataFrame([sum_row])], ignore_index=True
        )

        # Переименование колонок как в Excel
        df_year_disp.rename(
            columns={
                "month": "Месяц",
                "gross": "Брутто (ברוטו)",
                "net": "Нетто (נטו)",
                "tax": "Налог (מס)",
                "bituach_leumi": "Бит.Леуми",
                "pension": "Пенсия",
                "keren_ishtalmut": "Керен Ишт.",
                "other_deductions": "Прочее",
            },
            inplace=True,
        )

        # Форматирование в валюту
        cols_to_format = [
            "Брутто (ברוטו)",
            "Нетто (נטו)",
            "Налог (מס)",
            "Бит.Леуми",
            "Пенсия",
            "Керен Ишт.",
            "Прочее",
        ]
        fmt_dict = {c: "₪{:,.2f}" for c in cols_to_format}

        st.dataframe(
            df_year_disp.drop(columns=["year"], errors="ignore").style.format(
                fmt_dict
            ),
            use_container_width=True,
        )

    # ==================== ВКЛАДКА 3: Управление ====================
    with tab_manage:
        st.subheader("📥 Выгрузка и Удаление")

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Скачать всю базу в CSV (для Excel)",
            data=csv_bytes,
            file_name="salaries_data.csv",
            mime="text/csv",
        )

        st.markdown("---")
        st.write("### Удалить запись")
        del_options = [
            f"{row['year']} — Месяц {int(row['month']):02d} (Нетто: ₪{row['net']:,.2f})"
            for _, row in df.iterrows()
        ]
        selected_del = st.selectbox("Выберите запись:", options=del_options)

        if st.button("❌ Удалить выбранную запись"):
            idx = del_options.index(selected_del)
            df_updated = df.drop(df.index[idx]).reset_index(drop=True)
            st.session_state.df = df_updated
            save_data(df_updated)
            st.success("Запись удалена!")
            st.rerun()
else:
    st.info(
        "База данных пока пуста. Добавьте вашу первую зарплату через меню слева!"
    )
