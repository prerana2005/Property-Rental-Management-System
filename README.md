# Property Rental Management System

## 📌 Overview
The **Property Rental Management System** is a complete database-driven web application built using **Python (Streamlit)** and **MySQL**.  
It allows **owners, tenants, employees, and admins** to manage rental properties, agreements, payments, maintenance workflows, and analytics through a clean, interactive interface.

This application demonstrates:
- Full CRUD operations
- Complex SQL queries (joins, aggregates, nested queries)
- Stored procedures & functions
- Triggers
- Normalized database (3NF)
- Multi-user dashboards with role-based access

---

# 📂 Key Features

### ✔ Admin Features
- Manage Houses, Tenants, Owners, Employees
- Approve/monitor maintenance requests
- Oversee system-wide payments
- Execute CRUD SQL from GUI

### ✔ Owner Features
- View/manage properties
- Track earnings (Revenue Dashboard)
- Check tenant agreements
- Handle maintenance requests
- View analytics based on SQL functions

### ✔ Tenant Features
- Browse available houses
- Book rental agreements
- Submit maintenance issues
- View payments & agreements
- Manage profile

### ✔ Employee Features
- View assigned maintenance tasks
- Update completion details
- Track workload & performance analytics

### ✔ Database Features
- Stored procedures
- User-defined functions
- Triggers
- Normalization (3NF)
- Joins, nested queries, aggregates

---

# 🛠️ Tech Stack

### **Frontend**
- Streamlit (Python)

### **Backend**
- MySQL Database  
- SQL Functions, Triggers & Procedures

### **Programming Languages**
- Python  
- SQL  

### **Tools**
- MySQL Workbench
- VS Code  
- Git / GitHub  

---

# 🚀 How to Run the Project

## 🔹 1. Clone the Repository
```

git clone [https://github.com/prerana2005/Property-Rental-Management-System.git](https://github.com/Vidyu8/Property-Rental-Management-System.git)
cd Property-Rental-Management-System

```

## 🔹 2. Install Required Python Libraries
```

pip install -r requirements.txt

```

## 🔹 3. Set Up the MySQL Database

### Step 1 — Create the database
```

CREATE DATABASE rental_db;

```

### Step 2 — Import the SQL script
Import **Mini_Project.sql** via:
- MySQL Workbench → File → Run SQL Script  
OR
```

mysql -u root -p rental_db < Mini_Project.sql

```

This creates:
- Tables with constraints  
- Functions & Procedures  
- Triggers  
- Sample data  

---

## 🔹 4. Update Database Credentials (if needed)
Inside `app.py`, modify:
```

host="localhost"
user="root"
password="yourpassword"
database="rental_db"

```

---

## 🔹 5. Run the Application
```

streamlit run app.py

```

The app will start at:  
http://localhost:8501/

---

# 🔐 Default Login Credentials (Sample)

### Admin
- Username: admin  
- Password: admin123  

### Tenant
- Username: tenant_user  
- Password: tenant123  

### Owner
- Username: owner_user  
- Password: owner123  

### Employee
- Username: employee_user  
- Password: employee123  

---

# 📁 Project Structure

```

Property-Rental-Management-System/
│── app.py                     # Streamlit frontend
│── Mini_Project.sql           # SQL schema + data + functions
│── requirements.txt           # Python dependencies
│── Mini_Project_report.pdf    # Project report
│── README.md                  # Documentation

```
