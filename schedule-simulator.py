import random
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

# --- Streamlit UI ---
st.title("Forum User Activity Simulator")

st.sidebar.header("Simulation Controls")

# Upload CSV file
uploaded_file = st.sidebar.file_uploader("Upload your forum_users.csv", type=["csv"])

if uploaded_file is not None:
    users_df = pd.read_csv(uploaded_file)

    if not all(col in users_df.columns for col in ['forum-website', 'email address', 'password', 'username']):
        st.error("CSV must contain 'forum-website', 'email address', 'password', and 'username' columns.")
    else:
        start_date = st.sidebar.date_input("Simulation Start Date", value=datetime.today())
        end_date = st.sidebar.date_input("Simulation End Date", value=start_date + timedelta(days=365))
        random_seed = st.sidebar.number_input("Random Seed (optional)", value=42, step=1)

        st.sidebar.subheader("Estimated Monthly Activity Range")
        activity_min = st.sidebar.slider("Minimum Posts/Comments per Month", 10, 300, 50)
        activity_max = st.sidebar.slider("Maximum Posts/Comments per Month", 100, 1000, 200)

        if end_date <= start_date:
            st.error("End date must be after start date.")
            st.stop()

        simulation_days = (end_date - start_date).days
        random.seed(random_seed)

        PATTERNS = ['bursty', 'weekly', 'monthly', 'lurker_active', 'weekend', 'random', 'daily']

        class ForumUser:
            def __init__(self, user_id, username, pattern, forum_website, email_address, password):
                self.user_id = user_id
                self.username = username
                self.pattern = pattern
                self.forum_website = forum_website
                self.email_address = email_address
                self.password = password
                self.calendar = self.generate_calendar()

            def generate_calendar(self):
                calendar = {}
                if self.pattern == 'bursty':
                    for i in range(0, simulation_days, random.randint(60, 120)):
                        for j in range(random.randint(2, 4)):
                            if (i+j) < simulation_days:
                                day = start_date + timedelta(days=i+j)
                                calendar[day] = random.randint(1, 5)
                elif self.pattern == 'weekly':
                    for i in range(0, simulation_days, 7):
                        day = start_date + timedelta(days=i)
                        calendar[day] = random.randint(1, 2)
                elif self.pattern == 'monthly':
                    for i in range(0, simulation_days, 30):
                        day = start_date + timedelta(days=i)
                        calendar[day] = random.randint(1, 2)
                elif self.pattern == 'lurker_active':
                    if simulation_days > 250:
                        activation_start = random.randint(150, 250)
                    else:
                        activation_start = random.randint(0, max(0, simulation_days - 14))
                    for i in range(activation_start, min(activation_start + 14, simulation_days)):
                        day = start_date + timedelta(days=i)
                        calendar[day] = random.randint(2, 5)
                elif self.pattern == 'weekend':
                    for i in range(0, simulation_days):
                        day = start_date + timedelta(days=i)
                        if day.weekday() >= 5:
                            calendar[day] = random.randint(1, 3)
                elif self.pattern == 'random':
                    num_actions = random.randint(activity_min//12, activity_max//12)
                    for _ in range(num_actions):
                        day = start_date + timedelta(days=random.randint(0, simulation_days-1))
                        calendar[day] = random.randint(1, 3)
                elif self.pattern == 'daily':
                    for i in range(simulation_days):
                        day = start_date + timedelta(days=i)
                        calendar[day] = random.randint(1, 2)  # Light daily activity
                return calendar

        simulated_users = []
        for idx, row in users_df.iterrows():
            pattern = random.choices(PATTERNS, weights=[20, 25, 10, 10, 10, 10, 15])[0]
            simulated_users.append(
                ForumUser(
                    user_id=idx,
                    username=row['username'],
                    pattern=pattern,
                    forum_website=row['forum-website'],
                    email_address=row['email address'],
                    password=row['password']
                )
            )

        st.sidebar.subheader("Add New User Dynamically")
        new_username = st.sidebar.text_input("Username")
        new_email = st.sidebar.text_input("Email Address")
        new_password = st.sidebar.text_input("Password")
        new_forum = st.sidebar.text_input("Forum Website")
        add_user = st.sidebar.button("Add User")

        if add_user and new_username and new_email and new_password and new_forum:
            new_user_id = max([u.user_id for u in simulated_users], default=0) + 1
            pattern = random.choices(PATTERNS, weights=[20, 25, 10, 10, 10, 10, 15])[0]
            new_user = ForumUser(
                user_id=new_user_id,
                username=new_username,
                pattern=pattern,
                forum_website=new_forum,
                email_address=new_email,
                password=new_password
            )
            simulated_users.append(new_user)
            st.success(f"User {new_username} added successfully!")

        st.sidebar.markdown(f"**Total Users:** {len(simulated_users)}")

        data = []
        for user in simulated_users:
            for date, actions in user.calendar.items():
                data.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'forum_website': user.forum_website,
                    'email_address': user.email_address,
                    'password': user.password,
                    'date': date,
                    'posts_or_comments': actions,
                    'pattern': user.pattern
                })

        simulation_df = pd.DataFrame(data)

        st.dataframe(simulation_df.sort_values(by=['date', 'user_id']))

        st.download_button(
            label="Download Simulation as CSV",
            data=simulation_df.to_csv(index=False).encode('utf-8'),
            file_name='simulated_forum_activity.csv',
            mime='text/csv'
        )

        if st.checkbox("Show Activity Heatmap"):
            import seaborn as sns
            import matplotlib.pyplot as plt

            heatmap_data = simulation_df.groupby(['date']).agg({'posts_or_comments':'sum'}).reset_index()
            heatmap_data['date'] = pd.to_datetime(heatmap_data['date'])

            fig, ax = plt.subplots(figsize=(10,5))
            sns.lineplot(data=heatmap_data, x='date', y='posts_or_comments', ax=ax)
            st.pyplot(fig)

else:
    st.info("Please upload a 'forum_users.csv' file with 'forum-website', 'email address', 'password', and 'username' columns.")
