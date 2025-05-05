# 🧠 Forum Comment Simulator

A Streamlit-based simulation tool that generates realistic forum user activity patterns. This app helps developers, prompt engineers, and social researchers model user posting behavior across various types of forums — useful for training data generation, testing forum moderation systems, or studying interaction patterns.

---

## 📦 Features

- Upload your own `forum_users.csv` containing user data
- Simulate different user activity patterns: bursty, weekly, monthly, lurker, weekend-only, random, and daily casuals
- Adjust simulation date range and monthly activity intensity
- Dynamically add new users during simulation
- View real-time post/comment simulation and export as CSV
- Visualize activity trends with built-in heatmap

---

## 📁 CSV Format Required

Your uploaded `forum_users.csv` must contain the following columns:

forum-website,email address,password,username

Example:
https://forum.example.com,john@example.com,pass1234,john_doe

---

## 🚀 Run Locally

```bash

# Install dependencies
pip install streamlit pandas seaborn matplotlib

# Run the app
streamlit run schedule-simulator.py
