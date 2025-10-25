import streamlit as st
from .models import init_db
from .database import get_conn
import pandas as pd
from .analytics import read_operations, summary_by_month, by_category
from .export import export_excel, export_pdf
from datetime import date

def run_app():
    st.set_page_config(page_title="BudgetWise", layout="wide")
    init_db()

    st.title("💡 BudgetWise — умный финансовый помощник")
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("Добавить операцию")
        op_date = st.date_input("Дата", value=date.today())
        amount = st.number_input("Сумма (положительная — доход, отрицательная — расход)", value=0.0, format="%.2f")
        # categories from DB
        conn = get_conn()
        cats = pd.read_sql_query("SELECT id, name, type FROM categories ORDER BY name", conn)
        conn.close()
        cat_options = {f"{row['name']} ({row['type']})": row['id'] for _, row in cats.iterrows()}
        if cat_options:
            sel = st.selectbox("Категория", options=list(cat_options.keys()))
            cat_id = cat_options[sel]
        else:
            st.info("Нет категорий. Добавьте категорию справа.")
            cat_id = None
        note = st.text_input("Примечание")
        if st.button("Добавить операцию"):
            if amount == 0:
                st.error("Сумма не может быть нулевой.")
            else:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("INSERT INTO operations (date, amount, category_id, note) VALUES (?,?,?,?)", (op_date.isoformat(), amount, cat_id, note))
                conn.commit()
                conn.close()
                st.success("Операция добавлена.")
                st.experimental_rerun()

        st.markdown("---")
        st.subheader("Операции")
        df = read_operations()
        if df.empty:
            st.info("Операции отсутствуют.")
        else:
            # filters
            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                start = st.date_input("С", value=df["date"].min().date() if not df.empty else date.today())
            with c2:
                end = st.date_input("По", value=df["date"].max().date() if not df.empty else date.today())
            with c3:
                txt = st.text_input("Поиск в примечании или категории")
            mask = (df["date"].dt.date >= start) & (df["date"].dt.date <= end)
            if txt:
                mask = mask & (df["note"].str.contains(txt, case=False, na=False) | df["category"].str.contains(txt, case=False, na=False))
            df_filtered = df.loc[mask].copy()
            st.dataframe(df_filtered[["date","amount","category","note"]], use_container_width=True)

            # export buttons
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                if st.button("Экспорт в Excel"):
                    fname = export_excel(df_filtered, None)
                    st.success(f"Excel сохранён: {fname}")
            with col_e2:
                if st.button("Экспорт в PDF"):
                    fname = export_pdf(df_filtered, None)
                    st.success(f"PDF сохранён: {fname}")

    with col2:
        st.subheader("Управление категориями")
        with st.form("cat_form", clear_on_submit=True):
            name = st.text_input("Название")
            typ = st.selectbox("Тип", ["expense","income"])
            submitted = st.form_submit_button("Добавить категорию")
            if submitted:
                if not name:
                    st.error("Введите название.")
                else:
                    conn = get_conn()
                    try:
                        conn.execute("INSERT INTO categories (name, type) VALUES (?,?)", (name, typ))
                        conn.commit()
                        st.success("Категория добавлена.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Ошибка: возможно, категория уже существует.")
                    finally:
                        conn.close()
        st.markdown("---")
        st.subheader("Аналитика")
        df_all = read_operations()
        if not df_all.empty:
            agg = summary_by_month(df_all)
            st.markdown("**Помесячная сводка**")
            st.line_chart(agg.set_index("month")[["income","expense","net"]])
            st.markdown("**По категориям (топ)**")
            cat = by_category(df_all)
            st.bar_chart(cat.set_index("category")["amount"])
            st.markdown("---")
            st.write("Баланс за период:", f"{df_all['amount'].sum():.2f}")
        else:
            st.info("Нет данных для аналитики. Добавьте операции.")
