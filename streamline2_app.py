import streamlit as st
import pandas as pd
import numpy as np
import datetime

# Function to generate nurse shift schedule
def generate_schedule(nurses, unavailable_days, shift_preferences, month, year):
    days_in_month = (datetime.date(year, month, 1).replace(day=28) + datetime.timedelta(days=4)).day
    shifts = ["Morning", "Afternoon", "Night"]
    schedule = {f"Day {i+1}": {shift: [] for shift in shifts} for i in range(days_in_month)}
    
    for day in range(1, days_in_month + 1):
        available_nurses = [n for n in nurses if day not in unavailable_days.get(n, [])]
        
        for shift in shifts:
            preferred_nurses = [n for n in available_nurses if (day, shift) in shift_preferences.get(n, [])]
            
            if len(preferred_nurses) >= 2:
                assigned = preferred_nurses[:2]
            elif len(preferred_nurses) == 1:
                other_nurses = [n for n in available_nurses if n not in preferred_nurses]
                assigned = preferred_nurses + (other_nurses[:1] if other_nurses else [])
            else:
                assigned = available_nurses[:2]
            
            schedule[f"Day {day}"][shift] = assigned
    
    # Fill empty slots with available nurses
    for day in range(1, days_in_month + 1):
        available_nurses = [n for n in nurses if day not in unavailable_days.get(n, [])]
        
        for shift in shifts:
            if len(schedule[f"Day {day}"][shift]) < 2:
                remaining_nurses = [n for n in available_nurses if n not in schedule[f"Day {day}"][shift]]
                schedule[f"Day {day}"][shift] += remaining_nurses[:(2 - len(schedule[f"Day {day}"][shift]))]
    
    return pd.DataFrame(schedule).T

# Main function for Streamlit UI
def main():
    st.set_page_config(page_title="Nurse Shift Scheduler", layout="wide")
    st.title("Nurse Shift Assignment Scheduler")
    st.markdown("Assign shifts based on nurse preferences and availability for each month.")
    
    # Select month and year
    today = datetime.date.today()
    month = st.sidebar.selectbox("Select Month", list(range(1, 13)), index=today.month - 1)
    year = st.sidebar.selectbox("Select Year", list(range(today.year, today.year + 2)), index=0)
    
    # Input fields
    nurses = [f"Nurse {i+1}" for i in range(20)]
    unavailable_days = {
        nurse: st.sidebar.multiselect(f"{nurse} Unavailable Days in {month}/{year}", list(range(1, 32))) 
        for nurse in nurses
    }
    shift_preferences = {
        nurse: st.sidebar.multiselect(f"{nurse} Preferred Days & Shifts", 
                                      [(d, s) for d in range(1, 32) for s in ["Morning", "Afternoon", "Night"]]) 
        for nurse in nurses
    }
    
    if st.sidebar.button("Generate Schedule"):
        schedule = generate_schedule(nurses, unavailable_days, shift_preferences, month, year)
        st.success(f"Shift schedule for {month}/{year} generated successfully!")
        st.dataframe(schedule)
    
    # Footer
    st.markdown("---")
    st.markdown("Developed for optimized nurse scheduling.")

if __name__ == "__main__":
    main()
