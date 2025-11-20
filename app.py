# app.py
import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import hashlib

# SET PAGE CONFIG MUST BE FIRST
st.set_page_config(
    page_title="Property Rental System",
    page_icon="🏠",
    layout="wide"
)

# Database configuration - YOUR EXISTING DATABASE
DB_CONFIG = {
    'host': 'localhost',
    'database': 'rental_db',
    'user': 'root',
    'password': 'Abcd.12345'
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password, role):
    """Verify user credentials against your existing tables"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            
            if role == 'tenant':
                query = "SELECT TenantID as id, FullName, Username FROM Tenant WHERE Username = %s AND Password = %s"
            elif role == 'owner':
                query = "SELECT OwnerID as id, FullName, Username FROM Owner WHERE Username = %s AND Password = %s"
            elif role == 'employee':
                query = "SELECT EmployeeID as id, FullName, Username FROM Employee WHERE Username = %s AND Password = %s"
            elif role == 'admin':
                query = "SELECT OwnerID as id, FullName, Username FROM Owner WHERE Username = %s AND Password = %s AND Username = 'admin'"
            else:
                return None
                
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            return user
            
        except Error as e:
            st.error(f"Login error: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def execute_query(query, params=None, fetch=True):
    """Execute SQL query"""
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    return result
                else:
                    connection.commit()
                    return cursor.rowcount
            else:
                connection.commit()
                return True
                
        except Error as e:
            st.error(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def login_section():
    """User login section"""
    st.sidebar.title("🔐 Login")
    
    role = st.sidebar.selectbox("Select Role", ["tenant", "owner", "employee", "admin"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if role == "admin" and username == "admin" and password == "admin123":
            st.session_state['logged_in'] = True
            st.session_state['user_role'] = 'admin'
            st.session_state['username'] = 'admin'
            st.session_state['user_id'] = 0
            st.session_state['full_name'] = 'System Administrator'
            st.sidebar.success("Logged in as Admin")
        else:
            user = verify_login(username, password, role)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.session_state['username'] = user['Username']
                st.session_state['user_id'] = user['id']
                st.session_state['full_name'] = user['FullName']
                st.sidebar.success(f"Welcome {user['FullName']}!")
            else:
                st.sidebar.error("Invalid credentials")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 New User Registration")
    
    reg_role = st.sidebar.selectbox("Register as", ["tenant", "owner"], key="reg_role")
    reg_fullname = st.sidebar.text_input("Full Name")
    reg_username = st.sidebar.text_input("Choose Username")
    reg_password = st.sidebar.text_input("Choose Password", type="password")
    reg_email = st.sidebar.text_input("Email")
    reg_phone = st.sidebar.text_input("Phone")
    
    if st.sidebar.button("Register"):
        if reg_role and reg_fullname and reg_username and reg_password:
            if register_user(reg_role, reg_fullname, reg_username, reg_password, reg_email, reg_phone):
                st.sidebar.success("Registration successful! Please login.")
            else:
                st.sidebar.error("Registration failed. Username may already exist.")
        else:
            st.sidebar.warning("Please fill all required fields")
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

def register_user(role, fullname, username, password, email, phone):
    """Register new user in your existing tables"""
    hashed_password = hash_password(password)
    
    try:
        if role == 'tenant':
            query = """
                INSERT INTO Tenant (FullName, Username, Password, Email, Phone, Occupation, Address, ProofID) 
                VALUES (%s, %s, %s, %s, %s, 'Not specified', 'Not specified', 'Pending')
            """
        elif role == 'owner':
            query = """
                INSERT INTO Owner (FullName, Username, Password, Email, Phone, Address) 
                VALUES (%s, %s, %s, %s, %s, 'Not specified')
            """
        else:
            return False
            
        result = execute_query(query, (fullname, username, hashed_password, email, phone), fetch=False)
        return result is not None
        
    except Error as e:
        st.error(f"Registration error: {e}")
        return False

# DASHBOARD FUNCTIONS
def show_overview():
    """Show system overview"""
    st.header("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_houses = execute_query("SELECT COUNT(*) as count FROM House")
    if total_houses:
        col1.metric("Total Houses", total_houses[0]['count'])
    
    available_houses = execute_query("SELECT COUNT(*) as count FROM House WHERE Status = 'Available'")
    if available_houses:
        col2.metric("Available Houses", available_houses[0]['count'])
    
    active_agreements = execute_query("SELECT COUNT(*) as count FROM RentalAgreement WHERE AgreementStatus = 'Active'")
    if active_agreements:
        col3.metric("Active Agreements", active_agreements[0]['count'])
    
    pending_maintenance = execute_query("SELECT COUNT(*) as count FROM MaintenanceRequest WHERE Status IN ('Open', 'InProgress')")
    if pending_maintenance:
        col4.metric("Pending Maintenance", pending_maintenance[0]['count'])

def show_houses_management():
    """Manage houses"""
    st.header("🏘️ Houses Management")
    
    with st.expander("Add New House"):
        owners = execute_query("SELECT OwnerID, FullName FROM Owner")
        if owners:
            owner_options = {f"{owner['FullName']} (ID: {owner['OwnerID']})": owner['OwnerID'] for owner in owners}
            
            col1, col2 = st.columns(2)
            with col1:
                selected_owner = st.selectbox("Owner", options=list(owner_options.keys()))
                address = st.text_input("Address")
                city = st.text_input("City")
            with col2:
                house_type = st.selectbox("Type", ["Apartment", "Independent", "Villa"])
                rent_amount = st.number_input("Rent Amount", min_value=0.0, step=1000.0)
                furnishing = st.selectbox("Furnishing", ["Unfurnished", "Semi-Furnished", "Furnished", "Fully-Furnished"])
            
            if st.button("Add House"):
                owner_id = owner_options[selected_owner]
                query = """
                    INSERT INTO House (OwnerID, Address, City, Type, RentAmount, Furnishing, Status) 
                    VALUES (%s, %s, %s, %s, %s, %s, 'Available')
                """
                result = execute_query(query, (owner_id, address, city, house_type, rent_amount, furnishing), fetch=False)
                if result:
                    st.success("House added successfully!")
    
    houses = execute_query("SELECT h.*, o.FullName as OwnerName FROM House h JOIN Owner o ON h.OwnerID = o.OwnerID")
    if houses:
        st.dataframe(houses)

def show_tenants_management():
    """Manage tenants"""
    st.header("👥 Tenants Management")
    
    with st.expander("Add New Tenant"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", key="tenant_full_name")
            phone = st.text_input("Phone", key="tenant_phone")
            email = st.text_input("Email", key="tenant_email")
        with col2:
            occupation = st.text_input("Occupation", key="tenant_occupation")
            address = st.text_input("Address", key="tenant_address")
            proof_id = st.text_input("Proof ID", key="tenant_proof_id")
            username = st.text_input("Username", key="tenant_username")
            password = st.text_input("Password", type="password", key="tenant_password")
        
        if st.button("Add Tenant"):
            hashed_pwd = hash_password(password) if password else hash_password("default123")
            query = """
                INSERT INTO Tenant (FullName, Phone, Email, Occupation, Address, ProofID, Username, Password) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            result = execute_query(query, (full_name, phone, email, occupation, address, proof_id, username, hashed_pwd), fetch=False)
            if result:
                st.success("Tenant added successfully!")
    
    tenants = execute_query("SELECT * FROM Tenant")
    if tenants:
        st.dataframe(tenants)

def show_owners_management():
    """Manage owners"""
    st.header("👤 Owners Management")
    
    with st.expander("Add New Owner"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Owner Full Name")
            phone = st.text_input("Owner Phone")
        with col2:
            email = st.text_input("Owner Email")
            address = st.text_input("Owner Address")
            username = st.text_input("Owner Username")
            password = st.text_input("Owner Password", type="password")
        
        if st.button("Add Owner"):
            hashed_pwd = hash_password(password) if password else hash_password("default123")
            query = """
                INSERT INTO Owner (FullName, Phone, Email, Address, Username, Password) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = execute_query(query, (full_name, phone, email, address, username, hashed_pwd), fetch=False)
            if result:
                st.success("Owner added successfully!")
    
    owners = execute_query("SELECT * FROM Owner")
    if owners:
        st.dataframe(owners)

def show_employees_management():
    """Manage employees"""
    st.header("👷 Employees Management")
    
    with st.expander("Add New Employee"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Employee Full Name")
            role = st.selectbox("Role", ["Plumber", "Electrician", "Carpenter", "Painter", "Cleaner", "AC Technician", "Security", "Gardener"])
            username = st.text_input("Employee Username")
        with col2:
            phone = st.text_input("Employee Phone")
            email = st.text_input("Employee Email")
            password = st.text_input("Employee Password", type="password")
        
        if st.button("Add Employee"):
            hashed_pwd = hash_password(password) if password else hash_password("default123")
            query = """
                INSERT INTO Employee (FullName, Role, Phone, Email, Username, Password) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = execute_query(query, (full_name, role, phone, email, username, hashed_pwd), fetch=False)
            if result:
                st.success("Employee added successfully!")
    
    employees = execute_query("SELECT * FROM Employee")
    if employees:
        st.dataframe(employees)

def show_maintenance_management():
    """Admin maintenance management"""
    st.header("🔧 Maintenance Management")
    
    # Section 1: Maintenance Overview
    st.subheader("📊 Maintenance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total maintenance requests
    total_requests = execute_query("SELECT COUNT(*) as count FROM MaintenanceRequest")[0]['count']
    col1.metric("Total Requests", total_requests)
    
    # Open requests
    open_requests = execute_query("SELECT COUNT(*) as count FROM MaintenanceRequest WHERE Status = 'Open'")[0]['count']
    col2.metric("Open Requests", open_requests)
    
    # In Progress requests
    inprogress_requests = execute_query("SELECT COUNT(*) as count FROM MaintenanceRequest WHERE Status = 'InProgress'")[0]['count']
    col3.metric("In Progress", inprogress_requests)
    
    # Closed requests
    closed_requests = execute_query("SELECT COUNT(*) as count FROM MaintenanceRequest WHERE Status = 'Closed'")[0]['count']
    col4.metric("Closed Requests", closed_requests)
    
    st.markdown("---")
    
    # Section 2: All Maintenance Requests
    st.subheader("📋 All Maintenance Requests")
    
    # Get all maintenance requests with details
    maintenance_requests = execute_query("""
        SELECT 
            mr.RequestID,
            mr.RequestDate,
            mr.Description,
            mr.Status,
            mr.Cost,
            h.Address,
            h.City,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            o.FullName as OwnerName,
            a.AssignedDate,
            a.CompletionDate,
            e.FullName as EmployeeName,
            e.Role as EmployeeRole
        FROM MaintenanceRequest mr 
        JOIN House h ON mr.HouseID = h.HouseID 
        JOIN Tenant t ON mr.TenantID = t.TenantID 
        JOIN Owner o ON h.OwnerID = o.OwnerID 
        LEFT JOIN Assignment a ON mr.RequestID = a.RequestID 
        LEFT JOIN Employee e ON a.EmployeeID = e.EmployeeID 
        ORDER BY mr.RequestDate DESC
    """)
    
    if maintenance_requests:
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Open", "InProgress", "Closed", "Cancelled"],
                key="admin_maintenance_status"
            )
        
        with col_filter2:
            employee_filter = st.selectbox(
                "Filter by Employee",
                ["All Employees"] + list(set([r['EmployeeName'] for r in maintenance_requests if r['EmployeeName']])),
                key="admin_maintenance_employee"
            )
        
        with col_filter3:
            city_filter = st.selectbox(
                "Filter by City", 
                ["All Cities"] + list(set([r['City'] for r in maintenance_requests])),
                key="admin_maintenance_city"
            )
        
        # Apply filters
        filtered_requests = maintenance_requests.copy()
        
        if status_filter != "All":
            filtered_requests = [r for r in filtered_requests if r['Status'] == status_filter]
        
        if employee_filter != "All Employees":
            filtered_requests = [r for r in filtered_requests if r['EmployeeName'] == employee_filter]
        
        if city_filter != "All Cities":
            filtered_requests = [r for r in filtered_requests if r['City'] == city_filter]
        
        # Display requests
        for req in filtered_requests:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_color = {
                        'Open': '🔴',
                        'InProgress': '🟡',
                        'Closed': '🟢',
                        'Cancelled': '⚫'
                    }
                    
                    st.write(f"### {status_color.get(req['Status'], '⚪')} Request #{req['RequestID']}")
                    st.write(f"**Property:** {req['Address']}, {req['City']}")
                    st.write(f"**Tenant:** {req['TenantName']} ({req['TenantPhone']})")
                    st.write(f"**Owner:** {req['OwnerName']}")
                    st.write(f"**Submitted:** {req['RequestDate']}")
                    st.write(f"**Description:** {req['Description']}")
                    
                    if req['EmployeeName']:
                        st.write(f"**Assigned To:** {req['EmployeeName']} ({req['EmployeeRole']})")
                        if req['AssignedDate']:
                            st.write(f"**Assigned:** {req['AssignedDate']}")
                        if req['CompletionDate']:
                            st.write(f"**Completed:** {req['CompletionDate']}")
                
                with col2:
                    status_badge = {
                        'Open': 'warning',
                        'InProgress': 'info',
                        'Closed': 'success',
                        'Cancelled': 'secondary'
                    }
                    st.write("**Status:**")
                    st.write(f"**:{status_badge.get(req['Status'], 'secondary')}[{req['Status']}]**")
                    
                    if req['Cost']:
                        st.write(f"**Cost:** ₹{req['Cost']:,.2f}")
                
                with col3:
                    st.write("**Admin Actions:**")
                    
                    if req['Status'] == 'Open':
                        # Assign to employee
                        employees = execute_query("SELECT EmployeeID, FullName, Role FROM Employee")
                        if employees:
                            employee_options = {f"{emp['FullName']} ({emp['Role']})": emp['EmployeeID'] for emp in employees}
                            selected_employee = st.selectbox(
                                "Assign to", 
                                options=list(employee_options.keys()),
                                key=f"admin_assign_{req['RequestID']}"
                            )
                            
                            if st.button("Assign", key=f"admin_assign_btn_{req['RequestID']}"):
                                employee_id = employee_options[selected_employee]
                                
                                # Create assignment
                                assignment_query = """
                                    INSERT INTO Assignment (EmployeeID, RequestID, AssignedDate) 
                                    VALUES (%s, %s, CURDATE())
                                """
                                execute_query(assignment_query, (employee_id, req['RequestID']), fetch=False)
                                
                                # Update request status
                                update_query = "UPDATE MaintenanceRequest SET Status = 'InProgress' WHERE RequestID = %s"
                                execute_query(update_query, (req['RequestID'],), fetch=False)
                                
                                st.success(f"✅ Request assigned to {selected_employee}")
                                st.rerun()
                    
                    elif req['Status'] == 'InProgress':
                        # Reassign or complete
                        employees = execute_query("SELECT EmployeeID, FullName, Role FROM Employee")
                        if employees:
                            employee_options = {f"{emp['FullName']} ({emp['Role']})": emp['EmployeeID'] for emp in employees}
                            current_employee = f"{req['EmployeeName']} ({req['EmployeeRole']})" if req['EmployeeName'] else "Not Assigned"
                            selected_employee = st.selectbox(
                                "Reassign to", 
                                options=list(employee_options.keys()),
                                index=list(employee_options.keys()).index(current_employee) if current_employee in employee_options else 0,
                                key=f"admin_reassign_{req['RequestID']}"
                            )
                            
                            col_act1, col_act2 = st.columns(2)
                            with col_act1:
                                if st.button("Reassign", key=f"reassign_{req['RequestID']}"):
                                    employee_id = employee_options[selected_employee]
                                    update_assignment = "UPDATE Assignment SET EmployeeID = %s WHERE RequestID = %s"
                                    execute_query(update_assignment, (employee_id, req['RequestID']), fetch=False)
                                    st.success("✅ Employee reassigned!")
                                    st.rerun()
                            
                            with col_act2:
                                if st.button("Mark Complete", key=f"admin_complete_{req['RequestID']}"):
                                    # Update request status
                                    update_query = "UPDATE MaintenanceRequest SET Status = 'Closed' WHERE RequestID = %s"
                                    execute_query(update_query, (req['RequestID'],), fetch=False)
                                    
                                    # Update assignment completion date
                                    update_assignment = "UPDATE Assignment SET CompletionDate = CURDATE() WHERE RequestID = %s"
                                    execute_query(update_assignment, (req['RequestID'],), fetch=False)
                                    
                                    st.success("✅ Maintenance request completed!")
                                    st.rerun()
                    
                    elif req['Status'] == 'Closed':
                        if st.button("Reopen", key=f"reopen_{req['RequestID']}"):
                            update_query = "UPDATE MaintenanceRequest SET Status = 'InProgress' WHERE RequestID = %s"
                            execute_query(update_query, (req['RequestID'],), fetch=False)
                            
                            update_assignment = "UPDATE Assignment SET CompletionDate = NULL WHERE RequestID = %s"
                            execute_query(update_assignment, (req['RequestID'],), fetch=False)
                            
                            st.success("✅ Request reopened!")
                            st.rerun()
                    
                    # Cancel option for all statuses
                    if req['Status'] != 'Cancelled':
                        if st.button("Cancel", key=f"cancel_{req['RequestID']}"):
                            update_query = "UPDATE MaintenanceRequest SET Status = 'Cancelled' WHERE RequestID = %s"
                            execute_query(update_query, (req['RequestID'],), fetch=False)
                            st.success("✅ Request cancelled!")
                            st.rerun()
                
                st.divider()
        
        st.write(f"**Showing {len(filtered_requests)} of {len(maintenance_requests)} requests**")
    
    else:
        st.info("📭 No maintenance requests found.")
    
    # Section 3: Maintenance Analytics
    st.markdown("---")
    st.subheader("📈 Maintenance Analytics")
    
    # Cost analytics by property
    cost_analytics = execute_query("""
        SELECT 
            h.Address,
            h.City,
            o.FullName as OwnerName,
            COUNT(mr.RequestID) as TotalRequests,
            SUM(COALESCE(mr.Cost, 0)) as TotalCost,
            AVG(COALESCE(mr.Cost, 0)) as AvgCost
        FROM House h 
        JOIN Owner o ON h.OwnerID = o.OwnerID 
        LEFT JOIN MaintenanceRequest mr ON h.HouseID = mr.HouseID 
        GROUP BY h.HouseID, h.Address, h.City, o.FullName
        HAVING TotalRequests > 0
        ORDER BY TotalCost DESC
    """)
    
    if cost_analytics:
        st.write("**Maintenance Cost by Property:**")
        for analytics in cost_analytics:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{analytics['Address']}**")
                st.write(f"*{analytics['City']} - {analytics['OwnerName']}*")
            with col2:
                st.metric("Requests", analytics['TotalRequests'])
            with col3:
                st.metric("Total Cost", f"₹{analytics['TotalCost']:,.2f}")
            with col4:
                st.metric("Avg Cost", f"₹{analytics['AvgCost']:,.2f}")
            with col5:
                cost_per_request = analytics['TotalCost'] / analytics['TotalRequests'] if analytics['TotalRequests'] > 0 else 0
                st.metric("Cost/Request", f"₹{cost_per_request:,.2f}")
            
            st.divider()
    
    # Section 4: Employee Performance
    st.markdown("---")
    st.subheader("👷 Employee Performance")
    
    employee_performance = execute_query("""
        SELECT 
            e.EmployeeID,
            e.FullName,
            e.Role,
            COUNT(a.AssignmentID) as TotalAssignments,
            COUNT(CASE WHEN a.CompletionDate IS NOT NULL THEN 1 END) as CompletedAssignments,
            AVG(DATEDIFF(a.CompletionDate, a.AssignedDate)) as AvgCompletionDays,
            SUM(COALESCE(mr.Cost, 0)) as TotalRevenue
        FROM Employee e 
        LEFT JOIN Assignment a ON e.EmployeeID = a.EmployeeID 
        LEFT JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        GROUP BY e.EmployeeID, e.FullName, e.Role
        ORDER BY CompletedAssignments DESC
    """)
    
    if employee_performance:
        for emp in employee_performance:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{emp['FullName']}**")
                st.write(f"*{emp['Role']}*")
            with col2:
                st.metric("Total Tasks", emp['TotalAssignments'])
            with col3:
                st.metric("Completed", emp['CompletedAssignments'])
            with col4:
                completion_rate = (emp['CompletedAssignments'] / emp['TotalAssignments'] * 100) if emp['TotalAssignments'] > 0 else 0
                st.metric("Completion %", f"{completion_rate:.1f}%")
            with col5:
                st.metric("Revenue", f"₹{emp['TotalRevenue']:,.2f}")
            
            st.divider()

def show_payments_management():
    """Admin payments management"""
    st.header("💰 Payments Management")
    
    # Section 1: Payment Overview
    st.subheader("📊 Payment Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total payments
    total_payments = execute_query("SELECT COUNT(*) as count FROM Payment")[0]['count']
    col1.metric("Total Payments", total_payments)
    
    # Total revenue
    total_revenue = execute_query("SELECT COALESCE(SUM(Amount), 0) as total FROM Payment WHERE Status = 'Completed'")[0]['total']
    col2.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
    # Pending payments
    pending_payments = execute_query("SELECT COUNT(*) as count FROM Payment WHERE Status = 'Pending'")[0]['count']
    pending_amount = execute_query("SELECT COALESCE(SUM(Amount), 0) as total FROM Payment WHERE Status = 'Pending'")[0]['total']
    col3.metric("Pending Payments", pending_payments)
    col4.metric("Pending Amount", f"₹{pending_amount:,.2f}")
    
    st.markdown("---")
    
    # Section 2: All Payments
    st.subheader("💳 All Payments")
    
    # Get all payments with details
    payments = execute_query("""
        SELECT 
            p.*,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            o.FullName as OwnerName,
            o.Phone as OwnerPhone,
            h.Address as PropertyAddress
        FROM Payment p 
        JOIN Tenant t ON p.TenantID = t.TenantID 
        JOIN Owner o ON p.OwnerID = o.OwnerID 
        LEFT JOIN RentalAgreement ra ON t.TenantID = ra.TenantID 
        LEFT JOIN House h ON ra.HouseID = h.HouseID 
        ORDER BY p.PaymentDate DESC
    """)
    
    if payments:
        # Filter options
        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
        
        with col_filter1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Completed", "Pending", "Failed", "Refunded"],
                key="admin_payment_status"
            )
        
        with col_filter2:
            mode_filter = st.selectbox(
                "Filter by Payment Mode",
                ["All", "UPI", "Cash", "Card", "BankTransfer", "Cheque", "Other"],
                key="admin_payment_mode"
            )
        
        with col_filter3:
            owner_filter = st.selectbox(
                "Filter by Owner",
                ["All Owners"] + list(set([r['OwnerName'] for r in payments])),
                key="admin_payment_owner"
            )
        
        with col_filter4:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"],
                key="admin_payment_sort"
            )
        
        # Apply filters
        filtered_payments = payments.copy()
        
        if status_filter != "All":
            filtered_payments = [p for p in filtered_payments if p['Status'] == status_filter]
        
        if mode_filter != "All":
            filtered_payments = [p for p in filtered_payments if p['Mode'] == mode_filter]
        
        if owner_filter != "All Owners":
            filtered_payments = [p for p in filtered_payments if p['OwnerName'] == owner_filter]
        
        # Apply sorting
        if sort_by == "Newest First":
            filtered_payments.sort(key=lambda x: x['PaymentDate'], reverse=True)
        elif sort_by == "Oldest First":
            filtered_payments.sort(key=lambda x: x['PaymentDate'])
        elif sort_by == "Highest Amount":
            filtered_payments.sort(key=lambda x: x['Amount'], reverse=True)
        elif sort_by == "Lowest Amount":
            filtered_payments.sort(key=lambda x: x['Amount'])
        
        # Display payments
        for payment in filtered_payments:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_color = {
                        'Completed': '🟢',
                        'Pending': '🟡',
                        'Failed': '🔴',
                        'Refunded': '🔵'
                    }
                    
                    st.write(f"### {status_color.get(payment['Status'], '⚪')} Payment #{payment['PaymentID']}")
                    st.write(f"**Tenant:** {payment['TenantName']} ({payment['TenantPhone']})")
                    st.write(f"**Owner:** {payment['OwnerName']} ({payment['OwnerPhone']})")
                    if payment['PropertyAddress']:
                        st.write(f"**Property:** {payment['PropertyAddress']}")
                    st.write(f"**Date:** {payment['PaymentDate']} | **Mode:** {payment['Mode']}")
                    st.write(f"**Transaction ID:** {payment['PaymentID']}")
                
                with col2:
                    st.write(f"**Amount:**")
                    st.success(f"₹{payment['Amount']:,.2f}")
                
                with col3:
                    status_badge = {
                        'Completed': 'success',
                        'Pending': 'warning',
                        'Failed': 'error',
                        'Refunded': 'info'
                    }
                    st.write("**Status:**")
                    st.write(f"**:{status_badge.get(payment['Status'], 'secondary')}[{payment['Status']}]**")
                    
                    # Admin actions
                    st.write("**Admin Actions:**")
                    
                    if payment['Status'] == 'Pending':
                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if st.button("✅ Complete", key=f"admin_complete_{payment['PaymentID']}"):
                                update_query = "UPDATE Payment SET Status = 'Completed' WHERE PaymentID = %s"
                                execute_query(update_query, (payment['PaymentID'],), fetch=False)
                                st.success("Payment marked as completed!")
                                st.rerun()
                        with col_act2:
                            if st.button("❌ Fail", key=f"admin_fail_{payment['PaymentID']}"):
                                update_query = "UPDATE Payment SET Status = 'Failed' WHERE PaymentID = %s"
                                execute_query(update_query, (payment['PaymentID'],), fetch=False)
                                st.success("Payment marked as failed!")
                                st.rerun()
                    
                    elif payment['Status'] == 'Completed':
                        if st.button("↩️ Refund", key=f"admin_refund_{payment['PaymentID']}"):
                            update_query = "UPDATE Payment SET Status = 'Refunded' WHERE PaymentID = %s"
                            execute_query(update_query, (payment['PaymentID'],), fetch=False)
                            st.success("Payment refunded!")
                            st.rerun()
                    
                    elif payment['Status'] in ['Failed', 'Refunded']:
                        if st.button("🔄 Reset", key=f"admin_reset_{payment['PaymentID']}"):
                            update_query = "UPDATE Payment SET Status = 'Pending' WHERE PaymentID = %s"
                            execute_query(update_query, (payment['PaymentID'],), fetch=False)
                            st.success("Payment status reset to pending!")
                            st.rerun()
                
                st.divider()
        
        st.write(f"**Showing {len(filtered_payments)} of {len(payments)} payments**")
    
    else:
        st.info("📭 No payment records found.")
    
    # Section 3: Payment Analytics
    st.markdown("---")
    st.subheader("📈 Payment Analytics")
    
    # Monthly revenue
    monthly_revenue = execute_query("""
        SELECT 
            YEAR(PaymentDate) as Year,
            MONTH(PaymentDate) as Month,
            COUNT(*) as PaymentCount,
            SUM(Amount) as TotalRevenue
        FROM Payment 
        WHERE Status = 'Completed'
        GROUP BY YEAR(PaymentDate), MONTH(PaymentDate)
        ORDER BY Year DESC, Month DESC
        LIMIT 12
    """)
    
    if monthly_revenue:
        st.write("**Monthly Revenue (Last 12 Months):**")
        for month in monthly_revenue:
            month_name = f"{month['Year']}-{month['Month']:02d}"
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{month_name}**")
            with col2:
                st.metric("Payments", month['PaymentCount'])
            with col3:
                st.metric("Revenue", f"₹{month['TotalRevenue']:,.2f}")
            
            st.divider()
    
    # Payment mode distribution
    payment_modes = execute_query("""
        SELECT 
            Mode,
            COUNT(*) as Count,
            SUM(Amount) as TotalAmount
        FROM Payment 
        WHERE Status = 'Completed'
        GROUP BY Mode
        ORDER BY TotalAmount DESC
    """)
    
    if payment_modes:
        st.write("**Payment Mode Distribution:**")
        for mode in payment_modes:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{mode['Mode']}**")
            with col2:
                st.metric("Transactions", mode['Count'])
            with col3:
                st.metric("Amount", f"₹{mode['TotalAmount']:,.2f}")
            
            st.divider()
    
    # Owner revenue ranking
    owner_revenue = execute_query("""
        SELECT 
            o.FullName as OwnerName,
            COUNT(p.PaymentID) as PaymentCount,
            SUM(p.Amount) as TotalRevenue
        FROM Owner o 
        LEFT JOIN Payment p ON o.OwnerID = p.OwnerID AND p.Status = 'Completed'
        GROUP BY o.OwnerID, o.FullName
        ORDER BY TotalRevenue DESC
    """)
    
    if owner_revenue:
        st.write("**Owner Revenue Ranking:**")
        for owner in owner_revenue:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{owner['OwnerName']}**")
            with col2:
                st.metric("Payments", owner['PaymentCount'])
            with col3:
                st.metric("Revenue", f"₹{owner['TotalRevenue'] or 0:,.2f}")
            
            st.divider()
    
    # Section 4: Create Manual Payment
    st.markdown("---")
    st.subheader("➕ Create Manual Payment")
    
    with st.expander("Add Payment Record", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Get tenants
            tenants = execute_query("SELECT TenantID, FullName FROM Tenant")
            tenant_options = {tenant['FullName']: tenant['TenantID'] for tenant in tenants}
            selected_tenant = st.selectbox("Tenant", options=list(tenant_options.keys()), key="admin_manual_tenant")
            
            # Get owners
            owners = execute_query("SELECT OwnerID, FullName FROM Owner")
            owner_options = {owner['FullName']: owner['OwnerID'] for owner in owners}
            selected_owner = st.selectbox("Owner", options=list(owner_options.keys()), key="admin_manual_owner")
            
            payment_date = st.date_input("Payment Date", key="admin_manual_date")
            amount = st.number_input("Amount", min_value=0.0, step=1000.0, key="admin_manual_amount")
        
        with col2:
            payment_mode = st.selectbox(
                "Payment Mode", 
                ["UPI", "Cash", "Card", "BankTransfer", "Cheque", "Other"],
                key="admin_manual_mode"
            )
            payment_status = st.selectbox(
                "Status", 
                ["Completed", "Pending", "Failed"],
                key="admin_manual_status"
            )
            notes = st.text_area("Notes", key="admin_manual_notes")
        
        if st.button("💾 Create Payment", key="admin_create_payment"):
            tenant_id = tenant_options[selected_tenant]
            owner_id = owner_options[selected_owner]
            
            query = """
                INSERT INTO Payment (TenantID, OwnerID, PaymentDate, Amount, Mode, Status) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = execute_query(query, (tenant_id, owner_id, payment_date, amount, payment_mode, payment_status), fetch=False)
            if result:
                st.success("✅ Payment created successfully!")
                st.rerun()

def show_crud_operations():
    """CRUD operations"""
    st.header("⚙️ CRUD Operations")
    query = st.text_area("Enter SQL Query", height=100)
    if st.button("Execute Query"):
        if query:
            result = execute_query(query)
            if result is not None:
                if isinstance(result, list):
                    st.dataframe(result)
                else:
                    st.success(f"Query executed. Rows affected: {result}")

# TENANT FUNCTIONS
def show_available_houses():
    """Show available houses with booking feature"""
    st.header("🔍 Available Houses")
    
    tenant_id = st.session_state.get('user_id')
    
    houses = execute_query("""
        SELECT h.*, o.FullName as OwnerName, o.Phone as OwnerPhone 
        FROM House h 
        JOIN Owner o ON h.OwnerID = o.OwnerID 
        WHERE h.Status = 'Available'
    """)
    
    if houses:
        for house in houses:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(f"🏠 {house['Address']}")
                    st.write(f"**City:** {house['City']} | **Type:** {house['Type']}")
                    st.write(f"**Rent:** ₹{house['RentAmount']:,.2f} | **Furnishing:** {house['Furnishing']}")
                    st.write(f"**Owner:** {house['OwnerName']} | **Phone:** {house['OwnerPhone']}")
                
                with col2:
                    # Calculate security deposit (2 months rent)
                    security_deposit = house['RentAmount'] * 2
                    st.write(f"**Security Deposit:** ₹{security_deposit:,.2f}")
                
                with col3:
                    # Book Now button with expandable form
                    with st.expander("📝 Book Now"):
                        with st.form(f"book_form_{house['HouseID']}"):
                            st.write("**Rental Agreement Details**")
                            
                            start_date = st.date_input("Start Date", key=f"start_{house['HouseID']}")
                            end_date = st.date_input("End Date", 
                                                   value=start_date + pd.DateOffset(years=1) if start_date else None,
                                                   key=f"end_{house['HouseID']}")
                            
                            st.write(f"**Monthly Rent:** ₹{house['RentAmount']:,.2f}")
                            st.write(f"**Security Deposit:** ₹{security_deposit:,.2f}")
                            st.write(f"**Total Initial Payment:** ₹{house['RentAmount'] + security_deposit:,.2f}")
                            
                            agreed = st.checkbox("I agree to the terms and conditions", key=f"agree_{house['HouseID']}")
                            
                            if st.form_submit_button("✅ Confirm Booking", type="primary"):
                                if not agreed:
                                    st.error("Please agree to the terms and conditions")
                                elif not start_date or not end_date:
                                    st.error("Please select start and end dates")
                                elif start_date >= end_date:
                                    st.error("End date must be after start date")
                                else:
                                    # Check if tenant already has active agreement
                                    existing_agreement = execute_query("""
                                        SELECT COUNT(*) as count FROM RentalAgreement 
                                        WHERE TenantID = %s AND AgreementStatus = 'Active'
                                    """, (tenant_id,))[0]['count']
                                    
                                    if existing_agreement > 0:
                                        st.error("You already have an active rental agreement. Please terminate it before booking a new property.")
                                    else:
                                        # Create rental agreement
                                        agreement_query = """
                                            INSERT INTO RentalAgreement 
                                            (HouseID, TenantID, StartDate, EndDate, MonthlyRent, SecurityDeposit, AgreementStatus) 
                                            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
                                        """
                                        agreement_result = execute_query(
                                            agreement_query, 
                                            (house['HouseID'], tenant_id, start_date, end_date, house['RentAmount'], security_deposit),
                                            fetch=False
                                        )
                                        
                                        if agreement_result:
                                            # Update house status to Reserved
                                            update_house_query = "UPDATE House SET Status = 'Reserved' WHERE HouseID = %s"
                                            execute_query(update_house_query, (house['HouseID'],), fetch=False)
                                            
                                            st.success("🎉 Booking request submitted successfully!")
                                            st.balloons()
                                            st.info("The owner will review your request and contact you soon.")
                                            st.rerun()
                
                st.divider()
    else:
        st.info("No available houses at the moment.")
        
    # Show tenant's current booking status
    st.header("📋 My Booking Status")
    current_agreements = execute_query("""
        SELECT ra.*, h.Address, h.City, o.FullName as OwnerName
        FROM RentalAgreement ra
        JOIN House h ON ra.HouseID = h.HouseID
        JOIN Owner o ON h.OwnerID = o.OwnerID
        WHERE ra.TenantID = %s
        ORDER BY ra.StartDate DESC
    """, (tenant_id,))
    
    if current_agreements:
        for agreement in current_agreements:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Status with color coding
                    status_colors = {
                        'Pending': '🟡',
                        'Active': '🟢',
                        'Terminated': '🔴'
                    }
                    
                    st.write(f"### {status_colors.get(agreement['AgreementStatus'], '⚪')} {agreement['Address']}")
                    st.write(f"**Period:** {agreement['StartDate']} to {agreement['EndDate']}")
                    st.write(f"**Rent:** ₹{agreement['MonthlyRent']:,.2f} | **Deposit:** ₹{agreement['SecurityDeposit']:,.2f}")
                    st.write(f"**Owner:** {agreement['OwnerName']}")
                
                with col2:
                    status_badges = {
                        'Pending': 'warning',
                        'Active': 'success',
                        'Terminated': 'error'
                    }
                    st.write(f"**Status:**")
                    st.write(f"**:{status_badges.get(agreement['AgreementStatus'], 'secondary')}[{agreement['AgreementStatus']}]**")
                    
                    # Show days remaining for active agreements
                    if agreement['AgreementStatus'] == 'Active':
                        days_remaining = (agreement['EndDate'] - pd.Timestamp.now().date()).days
                        if days_remaining > 0:
                            st.write(f"**{days_remaining} days remaining**")
                        else:
                            st.write("**Agreement expired**")
                
                st.divider()
    else:
        st.info("You don't have any rental agreements yet. Book a house above! 🏠")
def show_tenant_agreements():
    st.header("📄 My Agreements")
    tenant_id = st.session_state.get('user_id')
    agreements = execute_query("SELECT ra.*, h.Address, h.City FROM RentalAgreement ra JOIN House h ON ra.HouseID = h.HouseID WHERE ra.TenantID = %s", (tenant_id,))
    if agreements:
        st.dataframe(agreements)
    else:
        st.info("No agreements found")

def show_tenant_maintenance():
    """Tenant maintenance requests with form and nice table"""
    st.header("🔧 Maintenance Requests")
    
    tenant_id = st.session_state.get('user_id')
    
    # Section 1: Submit New Maintenance Request
    with st.expander("➕ Submit New Maintenance Request", expanded=True):
        # Get tenant's currently rented houses
        houses = execute_query("""
            SELECT h.HouseID, h.Address 
            FROM House h 
            JOIN RentalAgreement ra ON h.HouseID = ra.HouseID 
            WHERE ra.TenantID = %s AND ra.AgreementStatus = 'Active'
        """, (tenant_id,))
        
        if houses:
            house_options = {f"{house['Address']} (ID: {house['HouseID']})": house['HouseID'] for house in houses}
            selected_house = st.selectbox("Select Property", options=list(house_options.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                request_date = st.date_input("Request Date")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
            with col2:
                issue_type = st.selectbox("Issue Type", [
                    "Plumbing", "Electrical", "HVAC", "Appliances", 
                    "Structural", "Pest Control", "Cleaning", "Other"
                ])
            
            description = st.text_area("Detailed Description of the Issue", 
                                     placeholder="Please describe the issue in detail...")
            
            if st.button("Submit Maintenance Request", type="primary"):
                if 'last_submission' not in st.session_state:
                    st.session_state.last_submission = None

                # Prevent rapid multiple submissions
                if st.session_state.last_submission != description:
                    house_id = house_options[selected_house]
                    query = """
                        INSERT INTO MaintenanceRequest (HouseID, TenantID, RequestDate, Description, Status) 
                        VALUES (%s, %s, %s, %s, 'Open')
                    """
                    result = execute_query(query, (house_id, tenant_id, request_date, description), fetch=False)
                    if result:
                        st.session_state.last_submission = description
                        st.success("✅ Maintenance request submitted successfully!")
                        st.rerun()
        else:
            st.warning("You don't have any active rental agreements.")
    
    st.markdown("---")
    
    # Section 2: Existing Maintenance Requests
    st.subheader("📋 My Maintenance Requests")
    
    # Fetch maintenance requests with employee assignment info
    requests = execute_query("""
        SELECT 
            mr.RequestID,
            mr.RequestDate,
            mr.Description,
            mr.Status,
            mr.Cost,
            h.Address,
            a.AssignedDate,
            a.CompletionDate,
            e.FullName as EmployeeName,
            e.Role as EmployeeRole,
            e.Phone as EmployeePhone
        FROM MaintenanceRequest mr 
        JOIN House h ON mr.HouseID = h.HouseID 
        LEFT JOIN Assignment a ON mr.RequestID = a.RequestID 
        LEFT JOIN Employee e ON a.EmployeeID = e.EmployeeID 
        WHERE mr.TenantID = %s 
        ORDER BY mr.RequestDate DESC
    """, (tenant_id,))
    
    if requests:
        for req in requests:
            # Create a nice card for each request
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Status with color coding
                    status_color = {
                        'Open': '🔵',
                        'InProgress': '🟡', 
                        'Closed': '🟢',
                        'Cancelled': '🔴'
                    }
                    
                    st.write(f"### {status_color.get(req['Status'], '⚪')} Request #{req['RequestID']}")
                    st.write(f"**Property:** {req['Address']}")
                    st.write(f"**Submitted:** {req['RequestDate']}")
                    st.write(f"**Description:** {req['Description']}")
                    
                    # Show assigned employee info if available
                    if req['EmployeeName']:
                        st.write(f"**Assigned To:** {req['EmployeeName']} ({req['EmployeeRole']})")
                        st.write(f"**Employee Contact:** {req['EmployeePhone']}")
                        if req['AssignedDate']:
                            st.write(f"**Assigned Date:** {req['AssignedDate']}")
                
                with col2:
                    # Status badge
                    status_badge = {
                        'Open': 'primary',
                        'InProgress': 'warning',
                        'Closed': 'success', 
                        'Cancelled': 'error'
                    }
                    
                    st.write(f"**Status:**")
                    st.write(f"**:{status_badge.get(req['Status'], 'secondary')}[{req['Status']}]**")
                    
                    if req['Cost']:
                        st.write(f"**Cost:** ₹{req['Cost']:,.2f}")
                    
                    if req['CompletionDate']:
                        st.write(f"**Completed:** {req['CompletionDate']}")
                
                st.divider()
    else:
        st.info("📭 No maintenance requests found. Submit your first request above!")
    
    # Quick stats
    if requests:
        st.subheader("📊 Request Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        total_requests = len(requests)
        open_requests = len([r for r in requests if r['Status'] == 'Open'])
        inprogress_requests = len([r for r in requests if r['Status'] == 'InProgress'])
        closed_requests = len([r for r in requests if r['Status'] == 'Closed'])
        
        col1.metric("Total Requests", total_requests)
        col2.metric("Open", open_requests)
        col3.metric("In Progress", inprogress_requests)
        col4.metric("Closed", closed_requests)

def show_tenant_payments():
    st.header("💰 My Payments")
    tenant_id = st.session_state.get('user_id')
    payments = execute_query("SELECT * FROM Payment WHERE TenantID = %s", (tenant_id,))
    if payments:
        st.dataframe(payments)
    else:
        st.info("No payments found")

def show_tenant_profile():
    """Show and update tenant profile in a beautiful layout"""
    st.header("👤 My Profile")
    
    tenant_id = st.session_state.get('user_id')
    tenant = execute_query("SELECT * FROM Tenant WHERE TenantID = %s", (tenant_id,))[0]
    
    # Profile in a nice card layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📊 Quick Stats")
        
        # Count agreements
        agreements_count = execute_query(
            "SELECT COUNT(*) as count FROM RentalAgreement WHERE TenantID = %s", 
            (tenant_id,)
        )[0]['count']
        
        # Count maintenance requests
        maintenance_count = execute_query(
            "SELECT COUNT(*) as count FROM MaintenanceRequest WHERE TenantID = %s", 
            (tenant_id,)
        )[0]['count']
        
        # Count payments
        payments_count = execute_query(
            "SELECT COUNT(*) as count FROM Payment WHERE TenantID = %s", 
            (tenant_id,)
        )[0]['count']
        
        st.metric("Rental Agreements", agreements_count)
        st.metric("Maintenance Requests", maintenance_count)
        st.metric("Payments Made", payments_count)
    
    with col2:
        st.subheader("Personal Information")
        
        # Display current info in a nice format
        with st.container():
            st.markdown("---")
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write("**👤 Full Name:**")
                st.info(tenant['FullName'])
                
                st.write("**📧 Email:**")
                st.info(tenant['Email'])
                
                st.write("**🏠 Address:**")
                st.info(tenant['Address'])
                
            with col_info2:
                st.write("**📞 Phone:**")
                st.info(tenant['Phone'])
                
                st.write("**💼 Occupation:**")
                st.info(tenant['Occupation'])
                
                st.write("**🆔 Proof ID:**")
                st.info(tenant['ProofID'])
        
        st.markdown("---")
    
    # Update Profile Section
    st.subheader("✏️ Update Profile")
    
    with st.form("update_profile_form"):
        st.write("Edit your profile information:")
        
        col_up1, col_up2 = st.columns(2)
        
        with col_up1:
            new_email = st.text_input("Email Address", value=tenant['Email'])
            new_phone = st.text_input("Phone Number", value=tenant['Phone'])
            new_occupation = st.text_input("Occupation", value=tenant['Occupation'])
            
        with col_up2:
            new_address = st.text_area("Address", value=tenant['Address'])
            new_proof_id = st.text_input("Proof ID", value=tenant['ProofID'])
        
        # Password update section
        st.subheader("🔒 Change Password")
        change_password = st.checkbox("I want to change my password")
        
        if change_password:
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                current_password = st.text_input("Current Password", type="password")
            with col_pass2:
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("💾 Update Profile", type="primary")
        
        if submitted:
            updates = []
            params = []
            
            # Basic info updates
            if new_email != tenant['Email']:
                updates.append("Email = %s")
                params.append(new_email)
            if new_phone != tenant['Phone']:
                updates.append("Phone = %s")
                params.append(new_phone)
            if new_occupation != tenant['Occupation']:
                updates.append("Occupation = %s")
                params.append(new_occupation)
            if new_address != tenant['Address']:
                updates.append("Address = %s")
                params.append(new_address)
            if new_proof_id != tenant['ProofID']:
                updates.append("ProofID = %s")
                params.append(new_proof_id)
            
            # Password update
            if change_password:
                if not current_password or not new_password or not confirm_password:
                    st.error("Please fill all password fields")
                elif new_password != confirm_password:
                    st.error("New passwords don't match")
                else:
                    # Verify current password
                    current_check = execute_query(
                        "SELECT Password FROM Tenant WHERE TenantID = %s AND Password = %s",
                        (tenant_id, current_password)
                    )
                    if current_check:
                        updates.append("Password = %s")
                        params.append(new_password)
                    else:
                        st.error("Current password is incorrect")
            
            if updates:
                query = f"UPDATE Tenant SET {', '.join(updates)} WHERE TenantID = %s"
                params.append(tenant_id)
                result = execute_query(query, params, fetch=False)
                if result:
                    st.success("🎉 Profile updated successfully!")
                    st.rerun()
            else:
                st.info("No changes made to your profile.")

# OWNER FUNCTIONS
def show_owner_properties():
    st.header("📈 My Properties")
    owner_id = st.session_state.get('user_id')
    properties = execute_query("SELECT * FROM House WHERE OwnerID = %s", (owner_id,))
    if properties:
        st.dataframe(properties)
    else:
        st.info("No properties found")

def show_owner_analytics():
    """Show owner analytics using functions"""
    st.header("📊 Property Analytics")
    
    owner_id = st.session_state.get('user_id')
    
    # Revenue and Property Stats
    col1, col2, col3 = st.columns(3)
    
    total_revenue = execute_query("SELECT CalculateOwnerRevenue(%s) as revenue", (owner_id,))[0]['revenue']
    col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
    active_agreements = execute_query("SELECT CountOwnerActiveAgreements(%s) as count", (owner_id,))[0]['count']
    col2.metric("Active Agreements", active_agreements)
    
    total_properties = execute_query("SELECT COUNT(*) as count FROM House WHERE OwnerID = %s", (owner_id,))[0]['count']
    col3.metric("Total Properties", total_properties)
    
    # Property Performance
    st.subheader("🏠 Property Performance")
    properties = execute_query("SELECT HouseID, Address, RentAmount FROM House WHERE OwnerID = %s", (owner_id,))
    
    if properties:
        for prop in properties:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            avg_maintenance = execute_query("SELECT GetAverageMaintenanceCost(%s) as cost", (prop['HouseID'],))[0]['cost']
            total_maintenance = execute_query("SELECT GetTotalMaintenanceCost(%s) as total", (prop['HouseID'],))[0]['total']
            is_available = execute_query("SELECT IsHouseAvailable(%s) as available", (prop['HouseID'],))[0]['available']
            
            with col1:
                st.write(f"**{prop['Address']}**")
            with col2:
                st.metric("Rent", f"₹{prop['RentAmount']:,.2f}")
            with col3:
                st.metric("Avg Maintenance", f"₹{avg_maintenance:,.2f}")
            with col4:
                st.metric("Status", "Available" if is_available else "Occupied")
            
            st.divider()
    else:
        st.info("No properties found for analytics.")

def show_owner_maintenance():
    """Owner maintenance management"""
    st.header("🔧 Maintenance Management")
    
    owner_id = st.session_state.get('user_id')
    
    # Section 1: Maintenance Requests for Owner's Properties
    st.subheader("📋 Maintenance Requests for My Properties")
    
    maintenance_requests = execute_query("""
        SELECT 
            mr.RequestID,
            mr.RequestDate,
            mr.Description,
            mr.Status,
            mr.Cost,
            h.Address,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            a.AssignedDate,
            a.CompletionDate,
            e.FullName as EmployeeName,
            e.Role as EmployeeRole
        FROM MaintenanceRequest mr 
        JOIN House h ON mr.HouseID = h.HouseID 
        JOIN Tenant t ON mr.TenantID = t.TenantID 
        LEFT JOIN Assignment a ON mr.RequestID = a.RequestID 
        LEFT JOIN Employee e ON a.EmployeeID = e.EmployeeID 
        WHERE h.OwnerID = %s 
        ORDER BY mr.RequestDate DESC
    """, (owner_id,))
    
    if maintenance_requests:
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        total_requests = len(maintenance_requests)
        open_requests = len([r for r in maintenance_requests if r['Status'] == 'Open'])
        inprogress_requests = len([r for r in maintenance_requests if r['Status'] == 'InProgress'])
        closed_requests = len([r for r in maintenance_requests if r['Status'] == 'Closed'])
        
        col1.metric("Total Requests", total_requests)
        col2.metric("Open", open_requests)
        col3.metric("In Progress", inprogress_requests)
        col4.metric("Closed", closed_requests)
        
        st.markdown("---")
        
        # Display requests
        for req in maintenance_requests:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_color = {
                        'Open': '🔴',
                        'InProgress': '🟡', 
                        'Closed': '🟢'
                    }
                    
                    st.write(f"### {status_color.get(req['Status'], '⚪')} Request #{req['RequestID']}")
                    st.write(f"**Property:** {req['Address']}")
                    st.write(f"**Tenant:** {req['TenantName']} ({req['TenantPhone']})")
                    st.write(f"**Submitted:** {req['RequestDate']}")
                    st.write(f"**Description:** {req['Description']}")
                    
                    if req['EmployeeName']:
                        st.write(f"**Assigned To:** {req['EmployeeName']} ({req['EmployeeRole']})")
                        if req['AssignedDate']:
                            st.write(f"**Assigned:** {req['AssignedDate']}")
                        if req['CompletionDate']:
                            st.write(f"**Completed:** {req['CompletionDate']}")
                
                with col2:
                    st.write("**Status:**")
                    status_badge = {
                        'Open': 'warning',
                        'InProgress': 'info',
                        'Closed': 'success'
                    }
                    st.write(f"**:{status_badge.get(req['Status'], 'secondary')}[{req['Status']}]**")
                    
                    if req['Cost']:
                        st.write(f"**Cost:** ₹{req['Cost']:,.2f}")
                
                with col3:
                    # Action buttons based on status
                    if req['Status'] == 'Open':
                        st.write("**Actions:**")
                        
                        # Get available employees
                        employees = execute_query("SELECT EmployeeID, FullName, Role FROM Employee")
                        if employees:
                            employee_options = {f"{emp['FullName']} ({emp['Role']})": emp['EmployeeID'] for emp in employees}
                            selected_employee = st.selectbox(
                                "Assign to", 
                                options=list(employee_options.keys()),
                                key=f"assign_{req['RequestID']}"
                            )
                            
                            if st.button("Assign", key=f"assign_btn_{req['RequestID']}"):
                                employee_id = employee_options[selected_employee]
                                
                                # Create assignment
                                assignment_query = """
                                    INSERT INTO Assignment (EmployeeID, RequestID, AssignedDate) 
                                    VALUES (%s, %s, CURDATE())
                                """
                                execute_query(assignment_query, (employee_id, req['RequestID']), fetch=False)
                                
                                # Update request status
                                update_query = "UPDATE MaintenanceRequest SET Status = 'InProgress' WHERE RequestID = %s"
                                execute_query(update_query, (req['RequestID'],), fetch=False)
                                
                                st.success(f"✅ Request assigned to {selected_employee}")
                                st.rerun()
                    
                    elif req['Status'] == 'InProgress':
                        st.write("**Actions:**")
                        if st.button("Mark Complete", key=f"complete_{req['RequestID']}"):
                            # Update request status to Closed
                            update_query = "UPDATE MaintenanceRequest SET Status = 'Closed' WHERE RequestID = %s"
                            execute_query(update_query, (req['RequestID'],), fetch=False)
                            
                            # Update assignment completion date
                            update_assignment = "UPDATE Assignment SET CompletionDate = CURDATE() WHERE RequestID = %s"
                            execute_query(update_assignment, (req['RequestID'],), fetch=False)
                            
                            st.success("✅ Maintenance request completed!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("📭 No maintenance requests for your properties.")
    
    # Section 2: Maintenance Cost Analytics
    st.markdown("---")
    st.subheader("💰 Maintenance Cost Analytics")
    
    cost_analytics = execute_query("""
        SELECT 
            h.HouseID,
            h.Address,
            COUNT(mr.RequestID) as TotalRequests,
            SUM(COALESCE(mr.Cost, 0)) as TotalCost,
            AVG(COALESCE(mr.Cost, 0)) as AvgCost
        FROM House h 
        LEFT JOIN MaintenanceRequest mr ON h.HouseID = mr.HouseID 
        WHERE h.OwnerID = %s 
        GROUP BY h.HouseID, h.Address
        ORDER BY TotalCost DESC
    """, (owner_id,))
    
    if cost_analytics:
        for analytics in cost_analytics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{analytics['Address']}**")
            with col2:
                st.metric("Total Requests", analytics['TotalRequests'])
            with col3:
                st.metric("Total Cost", f"₹{analytics['TotalCost']:,.2f}")
            with col4:
                st.metric("Avg Cost", f"₹{analytics['AvgCost']:,.2f}")
            
            st.divider()
    else:
        st.info("No maintenance cost data available.")

def show_owner_payments():
    """Owner payments management"""
    st.header("💰 Payments Management")
    
    owner_id = st.session_state.get('user_id')
    
    # Section 1: Payment Statistics
    st.subheader("📊 Payment Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total revenue
    total_revenue = execute_query("SELECT CalculateOwnerRevenue(%s) as revenue", (owner_id,))[0]['revenue']
    col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    
    # Payment counts by status
    payments = execute_query("""
        SELECT 
            p.*,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            h.Address as PropertyAddress
        FROM Payment p 
        JOIN Tenant t ON p.TenantID = t.TenantID 
        JOIN RentalAgreement ra ON t.TenantID = ra.TenantID 
        JOIN House h ON ra.HouseID = h.HouseID 
        WHERE p.OwnerID = %s 
        AND ra.AgreementStatus = 'Active'
        ORDER BY p.PaymentDate DESC
    """, (owner_id,))

    # Calculate payment stats correctly
    completed_count = len([p for p in payments if p['Status'] == 'Completed'])
    completed_total = sum(p['Amount'] for p in payments if p['Status'] == 'Completed')
    pending_count = len([p for p in payments if p['Status'] == 'Pending']) 
    pending_total = sum(p['Amount'] for p in payments if p['Status'] == 'Pending')
    
    col2.metric("Completed Payments", completed_count)
    col3.metric("Pending Payments", pending_count)
    col4.metric("Pending Amount", f"₹{pending_total:,.2f}")
    
    
    
    st.markdown("---")
    
    # Section 2: Recent Payments
    st.subheader("💳 Recent Payments")
    
    payments = execute_query("""
        SELECT 
            p.*,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            h.Address as PropertyAddress
        FROM Payment p 
        JOIN Tenant t ON p.TenantID = t.TenantID 
        JOIN RentalAgreement ra ON t.TenantID = ra.TenantID 
        JOIN House h ON ra.HouseID = h.HouseID 
        WHERE p.OwnerID = %s 
        AND ra.AgreementStatus = 'Active'
        ORDER BY p.PaymentDate DESC
    """, (owner_id,))
    
    if payments:
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            status_filter = st.selectbox("Filter by Status", 
                                       ["All", "Completed", "Pending", "Failed", "Refunded"],
                                       key="payment_status_filter")
        
        with col_filter2:
            mode_filter = st.selectbox("Filter by Payment Mode",
                                     ["All", "UPI", "Cash", "Card", "BankTransfer", "Cheque"],
                                     key="payment_mode_filter")
        
        with col_filter3:
            date_filter = st.selectbox("Sort by",
                                     ["Newest First", "Oldest First", "Highest Amount", "Lowest Amount"],
                                     key="payment_sort")
        
        # Apply filters
        filtered_payments = payments.copy()
        
        if status_filter != "All":
            filtered_payments = [p for p in filtered_payments if p['Status'] == status_filter]
        
        if mode_filter != "All":
            filtered_payments = [p for p in filtered_payments if p['Mode'] == mode_filter]
        
        # Apply sorting
        if date_filter == "Newest First":
            filtered_payments.sort(key=lambda x: x['PaymentDate'], reverse=True)
        elif date_filter == "Oldest First":
            filtered_payments.sort(key=lambda x: x['PaymentDate'])
        elif date_filter == "Highest Amount":
            filtered_payments.sort(key=lambda x: x['Amount'], reverse=True)
        elif date_filter == "Lowest Amount":
            filtered_payments.sort(key=lambda x: x['Amount'])
        
        # Display payments
        for payment in filtered_payments:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status_color = {
                        'Completed': '🟢',
                        'Pending': '🟡',
                        'Failed': '🔴',
                        'Refunded': '🔵'
                    }
                    
                    st.write(f"### {status_color.get(payment['Status'], '⚪')} Payment #{payment['PaymentID']}")
                    st.write(f"**Tenant:** {payment['TenantName']} ({payment['TenantPhone']})")
                    st.write(f"**Property:** {payment['PropertyAddress']}")
                    st.write(f"**Date:** {payment['PaymentDate']} | **Mode:** {payment['Mode']}")
                
                with col2:
                    st.write(f"**Amount:**")
                    st.success(f"₹{payment['Amount']:,.2f}")
                
                with col3:
                    status_badge = {
                        'Completed': 'success',
                        'Pending': 'warning',
                        'Failed': 'error',
                        'Refunded': 'info'
                    }
                    st.write(f"**Status:**")
                    st.write(f"**:{status_badge.get(payment['Status'], 'secondary')}[{payment['Status']}]**")
                    
                    import uuid
                    if payment['Status'] == 'Pending':
                        if st.button("✅ Mark Completed", key=f"complete_{uuid.uuid4()}"):
                            update_query = "UPDATE Payment SET Status = 'Completed' WHERE PaymentID = %s"
                            execute_query(update_query, (payment['PaymentID'],), fetch=False)
                            st.success("Payment marked as completed!")
                            st.rerun()
                    elif payment['Status'] == 'Completed':
                        if st.button("↩️ Refund", key=f"refund_{uuid.uuid4()}"):
                            update_query = "UPDATE Payment SET Status = 'Refunded' WHERE PaymentID = %s"
                            execute_query(update_query, (payment['PaymentID'],), fetch=False)
                            st.success("Payment refunded!")
                            st.rerun()
                
                st.divider()
        
        st.write(f"**Showing {len(filtered_payments)} of {len(payments)} payments**")
        
    else:
        st.info("📭 No payment records found.")
    
    # Section 3: Monthly Revenue Chart
    st.markdown("---")
    st.subheader("📈 Monthly Revenue")
    
    monthly_revenue = execute_query("""
        SELECT 
            YEAR(PaymentDate) as Year,
            MONTH(PaymentDate) as Month,
            COUNT(*) as PaymentCount,
            SUM(Amount) as TotalRevenue
        FROM Payment 
        WHERE OwnerID = %s AND Status = 'Completed'
        GROUP BY YEAR(PaymentDate), MONTH(PaymentDate)
        ORDER BY Year DESC, Month DESC
        LIMIT 12
    """, (owner_id,))
    
    if monthly_revenue:
        # Create a simple bar chart using st.metric
        st.write("**Last 12 Months Revenue:**")
        
        for month_data in monthly_revenue:
            month_name = f"{month_data['Year']}-{month_data['Month']:02d}"
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**{month_name}**")
            with col2:
                st.metric("Payments", month_data['PaymentCount'])
            with col3:
                st.metric("Revenue", f"₹{month_data['TotalRevenue']:,.2f}")
            
            st.divider()
    else:
        st.info("No revenue data available for chart.")
    
    # Section 4: Record Manual Payment
    st.markdown("---")
    st.subheader("➕ Record Manual Payment")
    
    with st.expander("Add Payment Record", expanded=False):
        # Get tenants who have active agreements with this owner
        active_tenants = execute_query("""
            SELECT DISTINCT t.TenantID, t.FullName, h.Address
            FROM Tenant t
            JOIN RentalAgreement ra ON t.TenantID = ra.TenantID
            JOIN House h ON ra.HouseID = h.HouseID
            WHERE h.OwnerID = %s AND ra.AgreementStatus = 'Active'
        """, (owner_id,))
        
        if active_tenants:
            col1, col2 = st.columns(2)
            
            with col1:
                tenant_options = {f"{tenant['FullName']} - {tenant['Address']}": tenant['TenantID'] for tenant in active_tenants}
                selected_tenant = st.selectbox("Tenant", options=list(tenant_options.keys()), key="manual_payment_tenant")
                payment_date = st.date_input("Payment Date", key="manual_payment_date")
                amount = st.number_input("Amount", min_value=0.0, step=1000.0, key="manual_payment_amount")
            
            with col2:
                payment_mode = st.selectbox("Payment Mode", 
                                          ["UPI", "Cash", "Card", "BankTransfer", "Cheque", "Other"],
                                          key="manual_payment_mode")
                payment_status = st.selectbox("Status", 
                                           ["Completed", "Pending", "Failed"],
                                           key="manual_payment_status")
                notes = st.text_input("Notes (Optional)", key="manual_payment_notes")
            
            if st.button("💾 Record Payment", key="record_manual_payment"):
                # Get tenant_id FIRST
                tenant_id = tenant_options[selected_tenant]

                # Then check for duplicates
                if 'last_payment_record' not in st.session_state:
                    st.session_state.last_payment_record = None

                current_payment = f"{tenant_id}_{amount}_{payment_date}"

                if st.session_state.last_payment_record != current_payment:
                    query = """
                        INSERT INTO Payment (TenantID, OwnerID, PaymentDate, Amount, Mode, Status) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    result = execute_query(query, (tenant_id, owner_id, payment_date, amount, payment_mode, payment_status), fetch=False)
                    if result:
                        st.session_state.last_payment_record = current_payment
                        st.success("✅ Payment recorded successfully!")
                        st.rerun()
                else:
                    st.warning("Payment already recorded!")
        else:
            st.warning("No active tenants found for manual payment recording.")

def show_owner_profile():
    st.header("👤 My Profile")
    owner_id = st.session_state.get('user_id')
    owner = execute_query("SELECT * FROM Owner WHERE OwnerID = %s", (owner_id,))
    if owner:
        st.json(owner[0])

# EMPLOYEE FUNCTIONS
def show_assigned_tasks():
    """Show employee's assigned maintenance tasks"""
    st.header("📋 My Assigned Tasks")
    
    employee_id = st.session_state.get('user_id')
    
    # Get assigned tasks
    tasks = execute_query("""
        SELECT 
            a.AssignmentID,
            a.AssignedDate,
            a.CompletionDate,
            mr.RequestID,
            mr.RequestDate,
            mr.Description,
            mr.Status as RequestStatus,
            mr.Cost,
            h.Address,
            h.City,
            t.FullName as TenantName,
            t.Phone as TenantPhone,
            t.Email as TenantEmail
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        JOIN House h ON mr.HouseID = h.HouseID 
        JOIN Tenant t ON mr.TenantID = t.TenantID 
        WHERE a.EmployeeID = %s 
        ORDER BY 
            CASE WHEN a.CompletionDate IS NULL THEN 0 ELSE 1 END,
            a.AssignedDate DESC
    """, (employee_id,))
    
    if tasks:
        # Quick stats
        col1, col2, col3 = st.columns(3)
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t['CompletionDate'] is None])
        completed_tasks = len([t for t in tasks if t['CompletionDate'] is not None])
        
        col1.metric("Total Tasks", total_tasks)
        col2.metric("Pending", pending_tasks)
        col3.metric("Completed", completed_tasks)
        
        st.markdown("---")
        
        # Display tasks
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    # Status indicator
                    if task['CompletionDate']:
                        status_icon = "✅"
                        status_text = "Completed"
                        status_color = "success"
                    else:
                        status_icon = "🟡"
                        status_text = "In Progress"
                        status_color = "warning"
                    
                    st.write(f"### {status_icon} Task #{task['AssignmentID']}")
                    st.write(f"**Property:** {task['Address']}, {task['City']}")
                    st.write(f"**Tenant:** {task['TenantName']}")
                    st.write(f"**Tenant Contact:** {task['TenantPhone']} | {task['TenantEmail']}")
                    st.write(f"**Request Date:** {task['RequestDate']}")
                    st.write(f"**Assigned Date:** {task['AssignedDate']}")
                    st.write(f"**Issue Description:** {task['Description']}")
                    
                    if task['CompletionDate']:
                        st.write(f"**Completed Date:** {task['CompletionDate']}")
                    if task['Cost']:
                        st.write(f"**Cost:** ₹{task['Cost']:,.2f}")
                
                with col2:
                    st.write("**Status:**")
                    st.write(f"**:{status_color}[{status_text}]**")
                    
                    # Days since assignment
                    if task['AssignedDate']:
                        days_assigned = (pd.Timestamp.now().date() - task['AssignedDate']).days
                        st.write(f"**{days_assigned} days assigned**")
                
                with col3:
                    st.write("**Actions:**")
                    
                    if not task['CompletionDate']:
                        # Mark as complete form
                        with st.form(f"complete_form_{task['AssignmentID']}"):
                            st.write("Mark as Complete")
                            actual_cost = st.number_input(
                                "Actual Cost (₹)", 
                                min_value=0.0, 
                                value=task['Cost'] or 0.0,
                                step=100.0,
                                key=f"cost_{task['AssignmentID']}"
                            )
                            notes = st.text_area(
                                "Completion Notes", 
                                placeholder="Any notes about the work done...",
                                key=f"notes_{task['AssignmentID']}"
                            )
                            
                            if st.form_submit_button("✅ Mark Complete", type="primary"):
                                # Update maintenance request
                                update_request = """
                                    UPDATE MaintenanceRequest 
                                    SET Status = 'Closed', Cost = %s 
                                    WHERE RequestID = %s
                                """
                                execute_query(update_request, (actual_cost, task['RequestID']), fetch=False)
                                
                                # Update assignment
                                update_assignment = """
                                    UPDATE Assignment 
                                    SET CompletionDate = CURDATE() 
                                    WHERE AssignmentID = %s
                                """
                                execute_query(update_assignment, (task['AssignmentID'],), fetch=False)
                                
                                st.success("🎉 Task marked as complete!")
                                st.balloons()
                                st.rerun()
                    
                    else:
                        st.info("Task completed")
                        if task['Cost']:
                            st.write(f"Final cost: ₹{task['Cost']:,.2f}")
                
                st.divider()
        
        # Show completion rate
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            st.subheader("📊 Performance")
            col_perf1, col_perf2 = st.columns(2)
            col_perf1.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            # Average completion time for completed tasks
            completed_with_dates = [t for t in tasks if t['CompletionDate'] and t['AssignedDate']]
            if completed_with_dates:
                avg_days = sum([(t['CompletionDate'] - t['AssignedDate']).days for t in completed_with_dates]) / len(completed_with_dates)
                col_perf2.metric("Avg Completion Time", f"{avg_days:.1f} days")
    
    else:
        st.info("📭 No tasks assigned to you yet.")
        st.write("Tasks will appear here when the admin assigns maintenance requests to you.")
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("🚀 Quick Actions")
    
    col_act1, col_act2 = st.columns(2)
    
    with col_act1:
        if st.button("🔄 Refresh Tasks", key="refresh_tasks"):
            st.rerun()
    
    with col_act2:
        pending_count = len([t for t in tasks if t['CompletionDate'] is None])
        if pending_count > 0:
            st.write(f"**{pending_count} tasks pending completion**")

def show_complete_tasks():
    """Show employee's completed maintenance tasks"""
    st.header("✅ Completed Tasks")
    
    employee_id = st.session_state.get('user_id')
    
    # Get completed tasks
    completed_tasks = execute_query("""
        SELECT 
            a.AssignmentID,
            a.AssignedDate,
            a.CompletionDate,
            mr.RequestID,
            mr.RequestDate,
            mr.Description,
            mr.Status as RequestStatus,
            mr.Cost,
            h.Address,
            h.City,
            h.Type as PropertyType,
            t.FullName as TenantName,
            t.Phone as TenantPhone
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        JOIN House h ON mr.HouseID = h.HouseID 
        JOIN Tenant t ON mr.TenantID = t.TenantID 
        WHERE a.EmployeeID = %s 
        AND a.CompletionDate IS NOT NULL
        ORDER BY a.CompletionDate DESC
    """, (employee_id,))
    
    if completed_tasks:
        # Completion statistics
        st.subheader("📈 Completion Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_completed = len(completed_tasks)
        
        # Calculate completion time statistics
        completion_times = []
        total_cost = 0
        
        for task in completed_tasks:
            if task['AssignedDate'] and task['CompletionDate']:
                days_taken = (task['CompletionDate'] - task['AssignedDate']).days
                completion_times.append(days_taken)
            if task['Cost']:
                total_cost += task['Cost']
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        fastest_completion = min(completion_times) if completion_times else 0
        slowest_completion = max(completion_times) if completion_times else 0
        
        col1.metric("Total Completed", total_completed)
        col2.metric("Avg Completion Time", f"{avg_completion_time:.1f} days")
        col3.metric("Fastest Completion", f"{fastest_completion} days")
        col4.metric("Total Revenue", f"₹{total_cost:,.2f}")
        
        st.markdown("---")
        
        # Filter options
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            time_filter = st.selectbox(
                "Filter by Time", 
                ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                key="time_filter"
            )
        
        with col_filter2:
            property_filter = st.selectbox(
                "Filter by Property Type",
                ["All Types", "Apartment", "Independent", "Villa"],
                key="property_filter"
            )
        
        with col_filter3:
            sort_by = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First", "Highest Cost", "Lowest Cost", "Quickest", "Slowest"],
                key="sort_completed"
            )
        
        # Apply filters
        filtered_tasks = completed_tasks.copy()
        
        # Time filter
        if time_filter != "All Time":
            cutoff_date = pd.Timestamp.now().date()
            if time_filter == "Last 7 Days":
                cutoff_date -= pd.Timedelta(days=7)
            elif time_filter == "Last 30 Days":
                cutoff_date -= pd.Timedelta(days=30)
            elif time_filter == "Last 90 Days":
                cutoff_date -= pd.Timedelta(days=90)
            
            filtered_tasks = [t for t in filtered_tasks if t['CompletionDate'] >= cutoff_date]
        
        # Property type filter
        if property_filter != "All Types":
            filtered_tasks = [t for t in filtered_tasks if t['PropertyType'] == property_filter]
        
        # Apply sorting
        if sort_by == "Newest First":
            filtered_tasks.sort(key=lambda x: x['CompletionDate'], reverse=True)
        elif sort_by == "Oldest First":
            filtered_tasks.sort(key=lambda x: x['CompletionDate'])
        elif sort_by == "Highest Cost":
            filtered_tasks.sort(key=lambda x: x['Cost'] or 0, reverse=True)
        elif sort_by == "Lowest Cost":
            filtered_tasks.sort(key=lambda x: x['Cost'] or 0)
        elif sort_by == "Quickest":
            filtered_tasks.sort(key=lambda x: (x['CompletionDate'] - x['AssignedDate']).days if x['AssignedDate'] and x['CompletionDate'] else 999)
        elif sort_by == "Slowest":
            filtered_tasks.sort(key=lambda x: (x['CompletionDate'] - x['AssignedDate']).days if x['AssignedDate'] and x['CompletionDate'] else -999, reverse=True)
        
        # Display completed tasks
        st.subheader(f"🎯 Completed Tasks ({len(filtered_tasks)})")
        
        for task in filtered_tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"### ✅ Task #{task['AssignmentID']}")
                    st.write(f"**Property:** {task['Address']}, {task['City']}")
                    st.write(f"**Type:** {task['PropertyType']}")
                    st.write(f"**Tenant:** {task['TenantName']} ({task['TenantPhone']})")
                    st.write(f"**Issue:** {task['Description']}")
                    
                    # Timeline
                    if task['AssignedDate'] and task['CompletionDate']:
                        days_taken = (task['CompletionDate'] - task['AssignedDate']).days
                        st.write(f"**Timeline:** {task['AssignedDate']} → {task['CompletionDate']} ({days_taken} days)")
                
                with col2:
                    if task['Cost']:
                        st.write(f"**Cost:**")
                        st.success(f"₹{task['Cost']:,.2f}")
                    else:
                        st.write(f"**Cost:**")
                        st.info("No cost recorded")
                    
                    # Efficiency rating
                    if task['AssignedDate'] and task['CompletionDate']:
                        days_taken = (task['CompletionDate'] - task['AssignedDate']).days
                        if days_taken <= 1:
                            efficiency = "⚡ Excellent"
                            color = "success"
                        elif days_taken <= 3:
                            efficiency = "👍 Good"
                            color = "info"
                        elif days_taken <= 7:
                            efficiency = "⚠️ Average"
                            color = "warning"
                        else:
                            efficiency = "🐌 Slow"
                            color = "error"
                        
                        st.write(f"**Efficiency:**")
                        st.write(f"**:{color}[{efficiency}]**")
                
                with col3:
                    st.write("**Completion Details**")
                    st.write(f"**Completed:** {task['CompletionDate']}")
                    
                    # Reopen option (if needed)
                    if st.button("🔄 Reopen Task", key=f"reopen_{task['AssignmentID']}"):
                        # Reopen the task
                        update_request = "UPDATE MaintenanceRequest SET Status = 'InProgress', Cost = NULL WHERE RequestID = %s"
                        execute_query(update_request, (task['RequestID'],), fetch=False)
                        
                        update_assignment = "UPDATE Assignment SET CompletionDate = NULL WHERE AssignmentID = %s"
                        execute_query(update_assignment, (task['AssignmentID'],), fetch=False)
                        
                        st.success("Task reopened and moved back to assigned tasks!")
                        st.rerun()
                
                st.divider()
        
        # Export option
        st.markdown("---")
        st.subheader("📤 Export Data")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            if st.button("📊 Generate Completion Report", key="generate_report"):
                # Create a simple report
                report_data = []
                for task in filtered_tasks:
                    days_taken = (task['CompletionDate'] - task['AssignedDate']).days if task['AssignedDate'] and task['CompletionDate'] else 0
                    report_data.append({
                        'Task ID': task['AssignmentID'],
                        'Property': task['Address'],
                        'Issue': task['Description'],
                        'Assigned Date': task['AssignedDate'],
                        'Completed Date': task['CompletionDate'],
                        'Days Taken': days_taken,
                        'Cost': task['Cost'] or 0
                    })
                
                df_report = pd.DataFrame(report_data)
                st.dataframe(df_report)
                
                # Download button
                csv = df_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Report",
                    data=csv,
                    file_name=f"completed_tasks_report_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_report"
                )
        
        with col_exp2:
            st.write("**Quick Summary**")
            st.write(f"**Total Tasks:** {len(filtered_tasks)}")
            st.write(f"**Total Revenue:** ₹{sum(t['Cost'] or 0 for t in filtered_tasks):,.2f}")
            st.write(f"**Avg Completion Time:** {avg_completion_time:.1f} days")
    
    else:
        st.info("📭 No completed tasks found.")
        st.write("Complete some tasks from the 'Assigned Tasks' tab to see them here!")
        
        # Quick navigation
        if st.button("🚀 Go to Assigned Tasks", key="go_to_assigned"):
            # This would need proper tab navigation
            st.info("Navigate to the 'Assigned Tasks' tab to start working!")

def show_workload_analytics():
    """Show employee workload analytics and performance metrics"""
    st.header("📊 Workload Analytics")
    
    employee_id = st.session_state.get('user_id')
    
    # Get employee details
    employee = execute_query("SELECT * FROM Employee WHERE EmployeeID = %s", (employee_id,))[0]
    
    st.subheader(f"👤 Performance Dashboard - {employee['FullName']} ({employee['Role']})")
    
    # Section 1: Key Performance Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Total assignments
    total_assignments = execute_query("""
        SELECT COUNT(*) as count FROM Assignment WHERE EmployeeID = %s
    """, (employee_id,))[0]['count']
    
    # Completed assignments
    completed_assignments = execute_query("""
        SELECT COUNT(*) as count FROM Assignment 
        WHERE EmployeeID = %s AND CompletionDate IS NOT NULL
    """, (employee_id,))[0]['count']
    
    # Pending assignments
    pending_assignments = execute_query("""
        SELECT COUNT(*) as count FROM Assignment 
        WHERE EmployeeID = %s AND CompletionDate IS NULL
    """, (employee_id,))[0]['count']
    
    # Total revenue generated
    total_revenue = execute_query("""
        SELECT COALESCE(SUM(mr.Cost), 0) as total 
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        WHERE a.EmployeeID = %s AND mr.Cost IS NOT NULL
    """, (employee_id,))[0]['total']
    
    col1.metric("Total Tasks", total_assignments)
    col2.metric("Completed", completed_assignments)
    col3.metric("Pending", pending_assignments)
    col4.metric("Revenue Generated", f"₹{total_revenue:,.2f}")
    
    # Completion rate
    if total_assignments > 0:
        completion_rate = (completed_assignments / total_assignments) * 100
        st.metric("Task Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Section 2: Monthly Performance
    st.subheader("📈 Monthly Performance")
    
    monthly_performance = execute_query("""
        SELECT 
            YEAR(a.CompletionDate) as Year,
            MONTH(a.CompletionDate) as Month,
            COUNT(*) as CompletedTasks,
            AVG(DATEDIFF(a.CompletionDate, a.AssignedDate)) as AvgCompletionDays,
            SUM(mr.Cost) as TotalRevenue
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        WHERE a.EmployeeID = %s 
        AND a.CompletionDate IS NOT NULL
        GROUP BY YEAR(a.CompletionDate), MONTH(a.CompletionDate)
        ORDER BY Year DESC, Month DESC
        LIMIT 6
    """, (employee_id,))
    
    if monthly_performance:
        for month in monthly_performance:
            month_name = f"{month['Year']}-{month['Month']:02d}"
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{month_name}**")
            with col2:
                st.metric("Tasks Completed", month['CompletedTasks'])
            with col3:
                st.metric("Avg Days", f"{month['AvgCompletionDays']:.1f}")
            with col4:
                st.metric("Revenue", f"₹{month['TotalRevenue'] or 0:,.2f}")
            
            st.divider()
    else:
        st.info("No monthly performance data available yet.")
    
    # Section 3: Task Type Analysis
    st.markdown("---")
    st.subheader("🔧 Task Type Analysis")
    
    task_analysis = execute_query("""
        SELECT 
            h.Type as PropertyType,
            COUNT(*) as TaskCount,
            AVG(DATEDIFF(a.CompletionDate, a.AssignedDate)) as AvgDays,
            SUM(mr.Cost) as TotalCost
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        JOIN House h ON mr.HouseID = h.HouseID 
        WHERE a.EmployeeID = %s 
        AND a.CompletionDate IS NOT NULL
        GROUP BY h.Type
        ORDER BY TaskCount DESC
    """, (employee_id,))
    
    if task_analysis:
        for analysis in task_analysis:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{analysis['PropertyType']}**")
            with col2:
                st.metric("Tasks", analysis['TaskCount'])
            with col3:
                st.metric("Avg Days", f"{analysis['AvgDays']:.1f}")
            with col4:
                st.metric("Total Cost", f"₹{analysis['TotalCost'] or 0:,.2f}")
            
            st.divider()
    else:
        st.info("No task type analysis data available.")
    
    # Section 4: Efficiency Metrics
    st.markdown("---")
    st.subheader("⚡ Efficiency Metrics")
    
    efficiency_data = execute_query("""
        SELECT 
            COUNT(*) as TotalCompleted,
            AVG(DATEDIFF(a.CompletionDate, a.AssignedDate)) as OverallAvgDays,
            MIN(DATEDIFF(a.CompletionDate, a.AssignedDate)) as FastestCompletion,
            MAX(DATEDIFF(a.CompletionDate, a.AssignedDate)) as SlowestCompletion,
            SUM(mr.Cost) as TotalRevenue,
            AVG(mr.Cost) as AvgTaskCost
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        WHERE a.EmployeeID = %s 
        AND a.CompletionDate IS NOT NULL
    """, (employee_id,))[0]
    
    if efficiency_data['TotalCompleted'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Overall Avg Time", f"{efficiency_data['OverallAvgDays']:.1f} days")
        col2.metric("Fastest Task", f"{efficiency_data['FastestCompletion']} days")
        col3.metric("Slowest Task", f"{efficiency_data['SlowestCompletion']} days")
        col4.metric("Avg Task Cost", f"₹{efficiency_data['AvgTaskCost'] or 0:,.2f}")
        
        # Performance rating
        avg_days = efficiency_data['OverallAvgDays'] or 0
        if avg_days <= 2:
            rating = "🏆 Excellent"
            color = "success"
        elif avg_days <= 4:
            rating = "👍 Good"
            color = "info"
        elif avg_days <= 7:
            rating = "⚠️ Average"
            color = "warning"
        else:
            rating = "🐌 Needs Improvement"
            color = "error"
        
        st.write(f"**Performance Rating:** :{color}[{rating}]")
    
    # Section 5: Recent Activity Timeline
    st.markdown("---")
    st.subheader("🕒 Recent Activity Timeline")
    
    recent_activity = execute_query("""
        SELECT 
            a.AssignmentID,
            a.AssignedDate,
            a.CompletionDate,
            mr.Description,
            h.Address,
            CASE 
                WHEN a.CompletionDate IS NULL THEN 'Pending'
                ELSE 'Completed'
            END as Status
        FROM Assignment a 
        JOIN MaintenanceRequest mr ON a.RequestID = mr.RequestID 
        JOIN House h ON mr.HouseID = h.HouseID 
        WHERE a.EmployeeID = %s 
        ORDER BY a.AssignedDate DESC
        LIMIT 10
    """, (employee_id,))
    
    if recent_activity:
        for activity in recent_activity:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                status_icon = "✅" if activity['Status'] == 'Completed' else "🟡"
                st.write(f"{status_icon} **Task #{activity['AssignmentID']}** - {activity['Description'][:50]}...")
                st.write(f"📍 {activity['Address']}")
            
            with col2:
                st.write(f"**Assigned:** {activity['AssignedDate']}")
                if activity['CompletionDate']:
                    st.write(f"**Completed:** {activity['CompletionDate']}")
            
            with col3:
                status_badge = "success" if activity['Status'] == 'Completed' else "warning"
                st.write(f"**:{status_badge}[{activity['Status']}]**")
            
            st.divider()
    else:
        st.info("No recent activity to display.")
    
    # Section 6: Workload Recommendations
    st.markdown("---")
    st.subheader("💡 Performance Insights")
    
    if total_assignments > 0:
        insights = []
        
        # Completion rate insight
        if completion_rate >= 90:
            insights.append("🎯 **Excellent completion rate!** Keep up the great work!")
        elif completion_rate >= 70:
            insights.append("👍 **Good completion rate.** You're maintaining steady performance.")
        else:
            insights.append("📈 **Consider improving completion rate.** Focus on completing pending tasks.")
        
        # Efficiency insight
        if efficiency_data['OverallAvgDays'] and efficiency_data['OverallAvgDays'] <= 3:
            insights.append("⚡ **Outstanding efficiency!** You complete tasks quickly.")
        elif efficiency_data['OverallAvgDays'] and efficiency_data['OverallAvgDays'] <= 5:
            insights.append("📅 **Good efficiency.** You maintain a steady pace.")
        else:
            insights.append("⏰ **Work on efficiency.** Try to reduce task completion time.")
        
        # Revenue insight
        if total_revenue > 50000:
            insights.append("💰 **High revenue contributor!** Your work generates significant value.")
        elif total_revenue > 20000:
            insights.append("💵 **Solid revenue generation.** Your work is financially valuable.")
        
        # Display insights
        for insight in insights:
            st.write(insight)
    
    else:
        st.info("Start completing tasks to see personalized insights and analytics!")

def show_employee_profile():
    st.header("👤 My Profile")
    employee_id = st.session_state.get('user_id')
    employee = execute_query("SELECT * FROM Employee WHERE EmployeeID = %s", (employee_id,))
    if employee:
        st.json(employee[0])

# DASHBOARDS
def admin_dashboard():
    st.title("🏠 Property Rental System - Admin Dashboard")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Overview", "🏘️ Houses", "👥 Tenants", "👤 Owners", "👷 Employees",
        "🔧 Maintenance", "💰 Payments", "⚙️ CRUD Operations"
    ])
    
    with tab1:
        show_overview()
    with tab2:
        show_houses_management()
    with tab3:
        show_tenants_management()
    with tab4:
        show_owners_management()
    with tab5:
        show_employees_management()
    with tab6:
        show_maintenance_management()
    with tab7:
        show_payments_management()
    with tab8:
        show_crud_operations()

def tenant_dashboard():
    st.title(f"🏠 Welcome {st.session_state.get('full_name', 'Tenant')}!")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Browse Houses", "📄 My Agreements", "🔧 Maintenance", "💰 My Payments", "👤 My Profile"
    ])
    
    with tab1:
        show_available_houses()
    with tab2:
        show_tenant_agreements()
    with tab3:
        show_tenant_maintenance()
    with tab4:
        show_tenant_payments()
    with tab5:
        show_tenant_profile()

def owner_dashboard():
    st.title(f"🏠 Welcome {st.session_state.get('full_name', 'Owner')}!")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 My Properties", "📊 Analytics", "🔧 Maintenance", "💰 Payments", "👤 My Profile"
    ])
    
    with tab1:
        show_owner_properties()
    with tab2:
        show_owner_analytics()
    with tab3:
        show_owner_maintenance()
    with tab4:
        show_owner_payments()
    with tab5:
        show_owner_profile()

def employee_dashboard():
    st.title(f"🏠 Welcome {st.session_state.get('full_name', 'Employee')}!")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Assigned Tasks", "✅ Complete Tasks", "📊 Workload", "👤 My Profile"
    ])
    
    with tab1:
        show_assigned_tasks()
    with tab2:
        show_complete_tasks()
    with tab3:
        show_workload_analytics()
    with tab4:
        show_employee_profile()

# MAIN APP
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_section()
        st.title("🏠 Welcome to Property Rental System")
        st.write("Please login or register from the sidebar to access the system.")
    else:
        login_section()
        user_role = st.session_state.get('user_role', 'admin')
        
        if user_role == 'admin':
            admin_dashboard()
        elif user_role == 'tenant':
            tenant_dashboard()
        elif user_role == 'owner':
            owner_dashboard()
        elif user_role == 'employee':
            employee_dashboard()

if __name__ == "__main__":
    main()