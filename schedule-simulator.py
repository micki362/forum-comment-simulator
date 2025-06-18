import random
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from typing import List, Dict, Any

# REFAC: Define constants at the top level for clarity and easy modification.
PATTERNS = ['bursty', 'weekly', 'monthly', 'lurker_active', 'weekend', 'random', 'daily', 'weekday_warrior']
PATTERN_WEIGHTS = [15, 20, 10, 10, 15, 10, 10, 10] # Weights for random selection

class ForumUser:
    """Represents a single forum user with a specific activity pattern."""
    def __init__(self, user_id: int, username: str, pattern: str, forum_website: str, email_address: str, password: str):
        self.user_id = user_id
        self.username = username
        self.pattern = pattern
        self.forum_website = forum_website
        self.email_address = email_address
        self.password = password
        self.calendar: Dict[datetime.date, int] = {}

    def generate_calendar(self, start_date: datetime.date, simulation_days: int, monthly_min: int, monthly_max: int):
        """
        Generates the activity calendar for the user based on their pattern.
        REFAC: This method now accepts simulation parameters instead of relying on global variables.
        """
        calendar = {}
        if self.pattern == 'bursty':
            # Bursts of high activity every 2-4 months
            for i in range(0, simulation_days, random.randint(60, 120)):
                for j in range(random.randint(3, 7)): # A burst lasts 3-7 days
                    if (i+j) < simulation_days:
                        day = start_date + timedelta(days=i+j)
                        calendar[day] = random.randint(2, 6) # Higher activity during bursts
        elif self.pattern == 'weekly':
            # Posts once a week on a random day of the week
            weekday = random.randint(0, 6)
            for i in range(simulation_days):
                day = start_date + timedelta(days=i)
                if day.weekday() == weekday:
                    calendar[day] = random.randint(1, 2)
        elif self.pattern == 'monthly':
            # Posts once a month on a random day
            for i in range(0, simulation_days, 30):
                day_offset = random.randint(0, 29)
                if (i + day_offset) < simulation_days:
                    day = start_date + timedelta(days=i + day_offset)
                    calendar[day] = random.randint(1, 3)
        elif self.pattern == 'lurker_active':
            # Becomes active in the latter half of the simulation period
            activation_start = random.randint(simulation_days // 2, max(simulation_days // 2, simulation_days - 30))
            for i in range(activation_start, min(activation_start + random.randint(14, 30), simulation_days)):
                day = start_date + timedelta(days=i)
                calendar[day] = random.randint(2, 5)
        elif self.pattern == 'weekend':
            for i in range(simulation_days):
                day = start_date + timedelta(days=i)
                if day.weekday() >= 5: # Saturday or Sunday
                    calendar[day] = random.randint(1, 3)
                elif random.random() < 0.05: # 5% chance of a random weekday post
                    calendar[day] = 1
        elif self.pattern == 'weekday_warrior':
            for i in range(simulation_days):
                day = start_date + timedelta(days=i)
                if day.weekday() < 5: # Monday to Friday
                    calendar[day] = random.randint(1, 2)
        elif self.pattern == 'random':
            # REFAC: Correctly calculate total actions based on monthly rate and simulation duration.
            total_months = simulation_days / 30.44  # Average days in a month
            min_total_actions = int(monthly_min * total_months)
            max_total_actions = int(monthly_max * total_months)
            num_actions = random.randint(min_total_actions, max_total_actions)

            for _ in range(num_actions):
                day_offset = random.randint(0, simulation_days - 1)
                day = start_date + timedelta(days=day_offset)
                calendar[day] = calendar.get(day, 0) + 1 # Increment action count for the day
        elif self.pattern == 'daily':
            for i in range(simulation_days):
                if random.random() < 0.8:  # 80% chance to post each day
                    day = start_date + timedelta(days=i)
                    calendar[day] = random.randint(1, 2)
        
        self.calendar = calendar

def generate_simulation_data(users: List[ForumUser]) -> pd.DataFrame:
    """
    Converts the list of ForumUser objects into a structured DataFrame with specific timestamps.
    REFAC: This function now also generates specific timestamps for each action.
    """
    data = []
    for user in users:
        for date, action_count in user.calendar.items():
            for _ in range(action_count): # Create one row per action
                # Generate a random timestamp for that day
                random_hour = random.randint(0, 23)
                random_minute = random.randint(0, 59)
                random_second = random.randint(0, 59)
                action_time = datetime.combine(date, datetime.min.time()) + \
                              timedelta(hours=random_hour, minutes=random_minute, seconds=random_second)

                data.append({
                    'timestamp': action_time,
                    'date': date,
                    'user_id': user.user_id,
                    'username': user.username,
                    'forum_website': user.forum_website,
                    'email_address': user.email_address,
                    'password': user.password,
                    'pattern': user.pattern
                })
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data).sort_values(by='timestamp')

def initialize_users(df: pd.DataFrame) -> List[ForumUser]:
    """Initializes a list of ForumUser objects from a DataFrame."""
    users = []
    for idx, row in df.iterrows():
        pattern = random.choices(PATTERNS, weights=PATTERN_WEIGHTS, k=1)[0]
        users.append(
            ForumUser(
                user_id=len(users), # Simple incrementing ID
                username=row['username'],
                pattern=pattern,
                forum_website=row['forum-website'],
                email_address=row['email address'],
                password=row['password']
            )
        )
    return users

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Forum User Activity Simulator")

# --- Sidebar Controls ---
st.sidebar.header("Simulation Controls")
uploaded_file = st.sidebar.file_uploader("Upload your forum_users.csv", type=["csv"])

if uploaded_file:
    # REFAC: Use session_state to prevent re-reading/re-initializing on every interaction
    # Only re-initialize if the file changes or if it's the first run
    if 'users_df' not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
        try:
            users_df = pd.read_csv(uploaded_file)
            if not all(col in users_df.columns for col in ['forum-website', 'email address', 'password', 'username']):
                st.error("CSV must contain 'forum-website', 'email address', 'password', and 'username' columns.")
                st.stop()
            if users_df.empty:
                st.error("Uploaded CSV file is empty.")
                st.stop()
            
            st.session_state.users_df = users_df
            st.session_state.uploaded_filename = uploaded_file.name
            # Initialize users and store in session_state
            st.session_state.simulated_users = initialize_users(users_df)
            st.info(f"Loaded {len(st.session_state.simulated_users)} users from '{uploaded_file.name}'. Ready to simulate.")

        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.stop()

    start_date = st.sidebar.date_input("Simulation Start Date", value=datetime.today())
    end_date = st.sidebar.date_input("Simulation End Date", value=start_date + timedelta(days=365))
    random_seed = st.sidebar.number_input("Random Seed", value=42, step=1)

    st.sidebar.subheader("Estimated Monthly Activity Range")
    activity_min = st.sidebar.slider("Minimum Posts/Comments per Month", 1, 300, 20)
    activity_max = st.sidebar.slider("Maximum Posts/Comments per Month", 10, 1000, 150)

    if end_date <= start_date:
        st.error("End date must be after start date.")
        st.stop()

    if activity_max < activity_min:
        st.warning("Max activity should be greater than or equal to min activity.")

    # REFAC: Use an expander for the "Add User" form to keep the UI clean
    with st.sidebar.expander("Add New User Dynamically"):
        with st.form("new_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Password", type="password")
            new_forum = st.text_input("Forum Website")
            submitted = st.form_submit_button("Add User")

            if submitted and all([new_username, new_email, new_password, new_forum]):
                new_user_id = len(st.session_state.simulated_users)
                pattern = random.choices(PATTERNS, weights=PATTERN_WEIGHTS, k=1)[0]
                new_user = ForumUser(
                    user_id=new_user_id,
                    username=new_username,
                    pattern=pattern,
                    forum_website=new_forum,
                    email_address=new_email,
                    password=new_password
                )
                st.session_state.simulated_users.append(new_user)
                st.toast(f"User '{new_username}' added with '{pattern}' pattern!", icon="🎉")

    st.sidebar.markdown(f"**Total Users:** {len(st.session_state.simulated_users)}")

    # --- Main App Body ---
    if st.button("▶️ Run Simulation", type="primary"):
        random.seed(random_seed)
        simulation_days = (end_date - start_date).days

        with st.spinner("Simulating user activity... This may take a moment."):
            # REFAC: Loop through users and generate their calendars
            for user in st.session_state.simulated_users:
                user.generate_calendar(start_date, simulation_days, activity_min, activity_max)

            # REFAC: Generate the final DataFrame and store it in session_state
            st.session_state.simulation_df = generate_simulation_data(st.session_state.simulated_users)

    if 'simulation_df' in st.session_state:
        df = st.session_state.simulation_df
        st.header("Simulation Results")

        if df.empty:
            st.warning("Simulation complete, but no activity was generated with the current settings.")
        else:
            st.dataframe(df)
            st.download_button(
                label="Download Simulation as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name='simulated_forum_activity.csv',
                mime='text/csv'
            )

            st.header("Visualizations")
            
            # REFAC: Renamed checkbox for clarity
            if st.checkbox("Show Activity Over Time", value=True):
                activity_by_date = df.groupby('date').size().reset_index(name='actions')
                fig, ax = plt.subplots(figsize=(12, 5))
                sns.lineplot(data=activity_by_date, x='date', y='actions', ax=ax)
                ax.set_title("Total Forum Activity Per Day")
                ax.set_ylabel("Number of Posts/Comments")
                ax.set_xlabel("Date")
                st.pyplot(fig)

            # REFAC: Added new visualization for pattern analysis
            if st.checkbox("Show Activity by Pattern", value=True):
                activity_by_pattern = df.groupby('pattern').size().reset_index(name='actions')
                fig, ax = plt.subplots(figsize=(12, 6))
                sns.barplot(data=activity_by_pattern.sort_values('actions', ascending=False), x='pattern', y='actions', ax=ax)
                ax.set_title("Total Actions Generated by Each User Pattern")
                ax.set_ylabel("Total Number of Posts/Comments")
                ax.set_xlabel("Activity Pattern")
                plt.xticks(rotation=45)
                st.pyplot(fig)
else:
    st.info("Please upload a 'forum_users.csv' file to begin.")
    st.markdown("Your CSV must contain the columns: `forum-website`, `email address`, `password`, and `username`.")