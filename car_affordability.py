import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime

def format_number(number):
    """
    Format numbers using international number system (e.g., 1,234,567.89)
    """
    if isinstance(number, (int, float)):
        # Format with thousand separators and 2 decimal places
        formatted_num = f"{number:,.2f}"
        # Remove .00 if the number is whole
        if formatted_num.endswith('.00'):
            formatted_num = formatted_num[:-3]
        return f"₹{formatted_num}"
    return "₹0"

def calculate_loan_details(car_price, down_payment_percentage, loan_term_years, loan_interest_rate):
    """Calculate loan related details"""
    loan_amount = car_price * (1 - down_payment_percentage)
    annual_interest = loan_interest_rate / 12
    months = loan_term_years * 12
    
    # EMI calculation
    emi = (loan_amount * annual_interest * (1 + annual_interest)**months) / ((1 + annual_interest)**months - 1)
    
    # Generate amortization schedule
    remaining_balance = loan_amount
    amortization = []
    total_interest = 0
    
    for month in range(1, months + 1):
        interest_payment = remaining_balance * annual_interest
        principal_payment = emi - interest_payment
        remaining_balance -= principal_payment
        total_interest += interest_payment
        
        amortization.append({
            'Month': month,
            'EMI': emi,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': max(0, remaining_balance)
        })
    
    return emi, loan_amount, total_interest, amortization

def main():
    st.set_page_config(page_title="Car Affordability Calculator", layout="wide")
    
    # Custom CSS for better number readability
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stAlert {
            padding: 1rem;
            margin: 1rem 0;
        }
        .metric-value {
            font-family: 'Courier New', monospace;
            font-size: 1.2rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🚗 Car Loan Affordability Calculator")
    st.markdown("---")
    
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Car Details")
        car_price = st.number_input("Car Price",
                                  min_value=100000, 
                                  max_value=10000000, 
                                  value=500000,
                                  step=50000,
                                  format="%d",
                                  help="Enter the total price of the car")
        st.write(f"Selected price: {format_number(car_price)}")
        
        down_payment_percentage = st.slider("Down Payment (%)", 
                                         min_value=10, 
                                         max_value=50, 
                                         value=20) / 100
        st.write(f"Down payment amount: {format_number(car_price * down_payment_percentage)}")
        
        monthly_fuel_cost = st.number_input("Expected Monthly Fuel Cost",
                                          min_value=1000,
                                          max_value=50000,
                                          value=5000,
                                          step=500,
                                          format="%d")
        st.write(f"Fuel cost: {format_number(monthly_fuel_cost)}")
    
    with col2:
        st.subheader("Loan Details")
        monthly_income = st.number_input("Monthly Income",
                                       min_value=20000,
                                       max_value=1000000,
                                       value=50000,
                                       step=5000,
                                       format="%d")
        st.write(f"Your income: {format_number(monthly_income)}")
        
        loan_term_years = st.selectbox("Loan Term (Years)", 
                                     options=[3, 4, 5, 7],
                                     index=1)
        
        loan_interest_rate = st.slider("Annual Interest Rate (%)",
                                     min_value=7.0,
                                     max_value=15.0,
                                     value=8.0) / 100
    
    # Calculate loan details
    emi, loan_amount, total_interest, amortization = calculate_loan_details(
        car_price, down_payment_percentage, loan_term_years, loan_interest_rate
    )
    
    # Calculate affordability metrics
    down_payment = car_price * down_payment_percentage
    total_monthly_cost = emi + monthly_fuel_cost
    income_percentage = (total_monthly_cost / monthly_income) * 100
    can_afford = income_percentage <= 10
    
    # Display Summary
    st.markdown("---")
    st.subheader("Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Down Payment", format_number(down_payment))
    with col2:
        st.metric("Monthly EMI", format_number(emi))
    with col3:
        st.metric("Total Monthly Cost", format_number(total_monthly_cost))
    with col4:
        st.metric("% of Income", f"{income_percentage:.1f}%")
    
    # Affordability Status
    if can_afford:
        st.success(f"✅ This car appears to be within your budget! Monthly cost is {format_number(total_monthly_cost)}")
    else:
        st.warning(f"⚠️ This car might stretch your budget. The total monthly cost of {format_number(total_monthly_cost)} exceeds 10% of your income.")
    
    # Additional cost insights
    st.info(f"""
    📊 Cost Breakdown:
    • Loan Amount: {format_number(loan_amount)}
    • Total Interest: {format_number(total_interest)}
    • Total Cost of Ownership: {format_number(car_price + total_interest + (monthly_fuel_cost * loan_term_years * 12))}
    """)
    
    # Visualization Section
    st.markdown("---")
    st.subheader("Loan Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Cost Breakdown", "EMI Schedule", "Loan Amortization"])
    
    with tab1:
        # Create pie chart for cost breakdown
        labels = ['Down Payment', 'Loan Amount', 'Total Interest', 'Fuel Cost (Total)']
        values = [
            down_payment,
            loan_amount,
            total_interest,
            monthly_fuel_cost * loan_term_years * 12
        ]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=['#2ecc71', '#3498db', '#e74c3c', '#f1c40f'],
            text=[format_number(val) for val in values],
            textposition='inside'
        )])
        
        fig.update_layout(
            title="Total Cost Breakdown",
            annotations=[dict(text='Cost<br>Analysis', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Create EMI schedule visualization
        df = pd.DataFrame(amortization)
        fig = px.line(df, x='Month', y=['Principal', 'Interest'],
                     title='Monthly EMI Breakdown',
                     labels={'value': 'Amount (₹)', 'variable': 'Component'})
        fig.update_layout(
            yaxis_tickformat=',',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Display amortization table with formatted numbers
        df_display = df.copy()
        df_display['EMI'] = df_display['EMI'].apply(format_number)
        df_display['Principal'] = df_display['Principal'].apply(format_number)
        df_display['Interest'] = df_display['Interest'].apply(format_number)
        df_display['Balance'] = df_display['Balance'].apply(format_number)
        st.dataframe(df_display, use_container_width=True)

if __name__ == "__main__":
    main()
