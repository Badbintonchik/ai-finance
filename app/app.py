import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# --- 1. SETTINGS & THEME ---
st.set_page_config(page_title="Nexus AI Finance", layout="wide", page_icon="📈")

# Custom CSS for a modern "Fintech" look
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #1E88E5; }
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #1E88E5; color: white; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE (DATABASE) ---
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame([
        {"ID": 1, "Date": (datetime.now() - timedelta(days=5)).date(), "Category": "Income", "Amount": 50000.0, "Type": "Income", "Note": "Monthly Salary"},
        {"ID": 2, "Date": (datetime.now() - timedelta(days=3)).date(), "Category": "Rent", "Amount": 15000.0, "Type": "Expense", "Note": "Apartment"},
        {"ID": 3, "Date": (datetime.now() - timedelta(days=1)).date(), "Category": "Food", "Amount": 1200.0, "Type": "Expense", "Note": "Dinner out"},
    ])

# --- 3. AI LOGIC ENGINE ---
class FinanceAI:
    def __init__(self, df):
        self.df = df

    def parse_natural_language(self, text):
        """Simulates NLP to extract data from text"""
        text = text.lower()
        amount = 0.0
        found_amt = re.findall(r'\d+', text)
        if found_amt: amount = float(found_amt[0])
        
        category = "Other"
        for cat in ["Food", "Rent", "Transport", "Shopping", "Health"]:
            if cat.lower() in text: category = cat
            
        return {"ID": len(self.df)+1, "Date": datetime.now().date(), "Category": category, "Amount": amount, "Type": "Expense", "Note": text}

    def get_forecast(self):
        """Simple Moving Average Forecast for next month"""
        expenses = self.df[self.df['Type'] == 'Expense']['Amount']
        if len(expenses) < 2: return 0
        return expenses.mean() * 1.1 # Predicting a 10% increase

# ai = FinanceAI(st.session_state.transactions)

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6081/6081440.png", width=100)
    st.title("Nexus AI")
    menu = st.radio("Navigation", ["Dashboard", "Transaction Manager", "AI Forecast", "Settings"])
    st.divider()
    st.info("AI Model: Finance-GPT v2.0")

# --- 5. MAIN INTERFACE ---

if menu == "Dashboard":
    st.title("🚀 Financial Insights")
    
    # Global Calculations
    df = st.session_state.transactions
    income = df[df['Type'] == 'Income']['Amount'].sum()
    expense = df[df['Type'] == 'Expense']['Amount'].sum()
    balance = income - expense
    
    # KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wallet Balance", f"${balance:,.2f}")
    c2.metric("Monthly Income", f"${income:,.2f}")
    c3.metric("Total Expenses", f"${expense:,.2f}", delta=f"-{expense/income:.1%}" if income > 0 else None)
    c4.metric("Savings Rate", f"{(balance/income*100) if income > 0 else 0:.1f}%")

    st.divider()

    # Visuals Row
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Spending Trends")
        # Ensure dates are datetime for plotting
        plot_df = df.copy()
        plot_df['Date'] = pd.to_datetime(plot_df['Date'])
        line_fig = px.area(plot_df.sort_values("Date"), x="Date", y="Amount", color="Type", template="plotly_white")
        st.plotly_chart(line_fig, use_container_width=True)

    with col_right:
        st.subheader("🎯 Budget Gauge")
        # Gauge Chart for Budget
        usage = (expense / income) * 100 if income > 0 else 0
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = usage,
            title = {'text': "Budget Used %"},
            gauge = {'axis': {'range': [0, 100]},
                     'bar': {'color': "#1E88E5"},
                     'steps': [
                         {'range': [0, 50], 'color': "#e8f5e9"},
                         {'range': [50, 80], 'color': "#fff3e0"},
                         {'range': [80, 100], 'color': "#ffebee"}]}))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # AI Chat Interface (Functional Fun)
    st.subheader("💬 Ask your AI Assistant")
    with st.container(border=True):
        user_msg = st.chat_input("How much did I spend on food?")
        if user_msg:
            with st.chat_message("user"): st.write(user_msg)
            with st.chat_message("assistant"):
                if "food" in user_msg.lower():
                    food_total = df[df['Category'] == 'Food']['Amount'].sum()
                    st.write(f"You've spent **${food_total:,.2f}** on food this month. That's about {food_total/expense:.1%} of your total expenses.")
                else:
                    st.write("I'm analyzing your data... You are currently in good standing, but watch your 'Rent' costs!")

elif menu == "Transaction Manager":
    st.title("📑 Transaction Manager")
    
    # 1. AI Quick Entry
    st.info("Try typing: 'I spent 50 dollars on Shopping'")
    quick_note = st.text_input("AI Quick Entry", placeholder="Describe your expense...")
    if st.button("Magic Add ✨"):
        ai = FinanceAI(st.session_state.transactions)
        new_row = ai.parse_natural_language(quick_note)
        st.session_state.transactions = pd.concat([st.session_state.transactions, pd.DataFrame([new_row])], ignore_index=True)
        st.success("AI parsed and added the transaction!")

    st.divider()

    # 2. Interactive Data Editor
    st.subheader("Edit History")
    edited_df = st.data_editor(
        st.session_state.transactions, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Amount": st.column_config.NumberColumn(format="$ %d"),
            "Type": st.column_config.SelectboxColumn(options=["Income", "Expense"]),
            "Category": st.column_config.SelectboxColumn(options=["Income", "Rent", "Food", "Transport", "Shopping", "Other"])
        }
    )
    if st.button("Save Changes"):
        st.session_state.transactions = edited_df
        st.toast("Data Saved Successfully!")

elif menu == "AI Forecast":
    st.title("🔮 Spending Forecast")
    ai = FinanceAI(st.session_state.transactions)
    prediction = ai.get_forecast()
    
    st.write("Based on your historical spending habits, here is your AI-generated prediction for next month:")
    st.metric("Predicted Expenses", f"${prediction:,.2f}", delta="10% increase", delta_color="inverse")
    
    st.warning("Action Plan: Based on this trend, you should reduce your 'Food' spending by $200 to meet your savings goal.")