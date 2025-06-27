# 🧠 Karat Habit Tracker – Backend API

This is the backend for the **Karat Habit Tracker**, a gamified mobile app that helps users build and maintain positive habits. The backend provides a RESTful API for managing users, habits, rewards, analytics, and progress tracking — all in support of the frontend Flutter application.

---

## 🎯 Project Objectives

- 📈 **Support Habit Tracking**: Provide secure and flexible endpoints for habit creation, updating, and completion.
- 🏆 **Enable Gamification**: Handle XP, rewards, and progress levels to motivate consistent behavior.
- 🔐 **User Management**: Register and authenticate users securely.
- 📊 **Data for Insights**: Track daily/weekly habit data to feed progress analytics in the app.

---

## 🛠️ Tech Stack

| Layer        | Technology            |
|--------------|------------------------|
| Language     | Python                 |
| Framework    | Django REST Framework  |
| Auth         | Token-based Auth (DRF) |
| Database     | PostgreSQL or SQLite   |
| API Format   | JSON (RESTful)         |
| CORS         | django-cors-headers    |

---

## 🔑 Main Features

- **User Authentication**
  - Registration, login, logout
  - Token-based authentication (DRF)

- **Habit Management**
  - Create, update, delete habits
  - Set habit frequency and goals

- **Tracking System**
  - Mark habits as completed daily
  - Store streaks, history, and habit status

- **Gamification**
  - XP system for each habit
  - Track levels, badges, and rewards (handled server-side)

- **Analytics & Logs**
  - Weekly/monthly summaries
  - Progress over time for insights
