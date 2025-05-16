import psycopg2
import uuid
import random
from datetime import datetime, timedelta, date
from faker import Faker
import decimal
import time

# Initialize Faker
fake = Faker()

# Database connection parameters - matches your docker-compose.yml
DB_PARAMS = {
    'dbname': 'krproject',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

# Constants for data generation
NUM_USERS = 20  # Total users (including existing ones)
NUM_CLIENTS_PER_USER = 5  # Clients per user
NUM_PROJECTS_PER_CLIENT = 4  # Projects per client
NUM_TASKS_PER_USER = 12  # Tasks per user
NUM_LOCATIONS_PER_USER = 5  # Locations per user
NUM_CONTRACTS_PER_PROJECT = 2  # Contracts per project
NUM_REPORTS_PER_CONTRACT = 8  # Reports per contract
MAX_EXPENSES_PER_REPORT = 3  # Maximum expenses per report

# Function to generate a random UUID
def generate_uuid():
    return str(uuid.uuid4())

# Function to generate a random date within a range
def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

# Connect to the database
def connect_to_db():
    # Retry mechanism for establishing connection
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            print("Database connection established successfully")
            return conn
        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count}/{max_retries}: Error connecting to database: {e}")
            if retry_count < max_retries:
                time.sleep(2)  # Wait before retrying
            else:
                print("Maximum retries reached. Could not connect to database.")
                return None

# Generate user data
def generate_users(conn, num_users):
    users = []
    existing_users = []

    cursor = conn.cursor()
    cursor.execute('SELECT id, "firstName", "lastName", email FROM "user"')
    existing_users = cursor.fetchall()

    # Include existing users
    for user in existing_users:
        users.append({
            'id': user[0],
            'firstName': user[1],
            'lastName': user[2],
            'email': user[3],
        })

    print(f"Found {len(existing_users)} existing users")

    # If there are no existing users, create initial users with specific IDs
    if len(existing_users) == 0:
        # Initial users with fixed IDs for consistency
        initial_users = [
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'firstName': 'John',
                'lastName': 'Doe',
                'email': 'john@example.com',
                'password': 'password123'
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'firstName': 'Sarah',
                'lastName': 'Johnson',
                'email': 'sarah@example.com',
                'password': 'securepass456'
            }
        ]

        for user_data in initial_users:
            cursor.execute(
                'INSERT INTO "user" (id, "firstName", "lastName", email, password) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (user_data['id'], user_data['firstName'], user_data['lastName'], user_data['email'], user_data['password'])
            )

            users.append({
                'id': user_data['id'],
                'firstName': user_data['firstName'],
                'lastName': user_data['lastName'],
                'email': user_data['email'],
            })

        print(f"Created {len(initial_users)} initial users")

    # Add additional users
    for i in range(len(users), num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{i}@{fake.domain_name()}"

        # Generate a unique user ID
        user_id = generate_uuid()

        cursor.execute(
            'INSERT INTO "user" (id, "firstName", "lastName", email, password) VALUES (%s, %s, %s, %s, %s) RETURNING id',
            (user_id, first_name, last_name, email, fake.password(length=10))
        )

        new_id = cursor.fetchone()[0]
        users.append({
            'id': new_id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
        })

        if i % 5 == 0:
            conn.commit()

    conn.commit()
    print(f"Total users: {len(users)}")
    return users

# Generate client data
def generate_clients(conn, users, clients_per_user):
    clients = []

    # First, fetch existing clients
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", name FROM client')
    existing_clients = cursor.fetchall()

    # Include existing clients
    for client in existing_clients:
        clients.append({
            'id': client[0],
            'idUser': client[1],
            'name': client[2],
        })

    print(f"Found {len(existing_clients)} existing clients")

    # Add new clients
    for user in users:
        # Count existing clients for this user
        existing_count = sum(1 for client in clients if client['idUser'] == user['id'])

        for i in range(existing_count, clients_per_user):
            company_name = fake.company()
            note = fake.text(max_nb_chars=100) if random.random() > 0.3 else None
            contact_name = fake.name() if random.random() > 0.2 else None
            contact_phone = fake.phone_number() if random.random() > 0.2 else None
            contact_email = fake.email() if random.random() > 0.2 else None

            # Generate a unique client ID
            client_id = generate_uuid()

            cursor.execute(
                'INSERT INTO client (id, "idUser", name, note, "contactName", "contactPhone", "contactEmail") ' +
                'VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (client_id, user['id'], company_name, note, contact_name, contact_phone, contact_email)
            )

            new_id = cursor.fetchone()[0]
            clients.append({
                'id': new_id,
                'idUser': user['id'],
                'name': company_name,
            })

    conn.commit()
    print(f"Total clients: {len(clients)}")
    return clients

# Generate project data
def generate_projects(conn, users, clients, projects_per_client):
    projects = []

    # First, fetch existing projects
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", "idClient", name FROM project')
    existing_projects = cursor.fetchall()

    # Include existing projects
    for project in existing_projects:
        projects.append({
            'id': project[0],
            'idUser': project[1],
            'idClient': project[2],
            'name': project[3],
        })

    print(f"Found {len(existing_projects)} existing projects")

    # Dictionary to track projects per client
    client_project_count = {}
    for project in projects:
        client_id = project['idClient']
        client_project_count[client_id] = client_project_count.get(client_id, 0) + 1

    # Add new projects
    for client in clients:
        # Find user for this client
        user_id = client['idUser']

        # Count existing projects for this client
        existing_count = client_project_count.get(client['id'], 0)

        for i in range(existing_count, projects_per_client):
            project_types = ["Website", "Mobile App", "Desktop Application", "API", "Database",
                            "Migration", "Integration", "Implementation", "Development", "Automation",
                            "Dashboard", "Reporting", "Analysis", "Research", "Support", "Maintenance"]

            project_adjectives = ["New", "Legacy", "Modern", "Innovative", "Custom", "Enterprise",
                                "Internal", "External", "Client-facing", "Backend", "Frontend"]

            project_name = f"{random.choice(project_adjectives)} {random.choice(project_types)}"
            note = fake.text(max_nb_chars=100) if random.random() > 0.3 else None

            # Generate a unique project ID
            project_id = generate_uuid()

            cursor.execute(
                'INSERT INTO project (id, "idUser", "idClient", name, note) ' +
                'VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (project_id, user_id, client['id'], project_name, note)
            )

            new_id = cursor.fetchone()[0]
            projects.append({
                'id': new_id,
                'idUser': user_id,
                'idClient': client['id'],
                'name': project_name,
            })

    conn.commit()
    print(f"Total projects: {len(projects)}")
    return projects

# Generate task data
def generate_tasks(conn, users, tasks_per_user):
    tasks = []

    # First, fetch existing tasks
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", title FROM task')
    existing_tasks = cursor.fetchall()

    # Include existing tasks
    for task in existing_tasks:
        tasks.append({
            'id': task[0],
            'idUser': task[1],
            'title': task[2],
        })

    print(f"Found {len(existing_tasks)} existing tasks")

    # Dictionary to track tasks per user
    user_task_count = {}
    for task in tasks:
        user_id = task['idUser']
        user_task_count[user_id] = user_task_count.get(user_id, 0) + 1

    # Task categories and actions for more realistic task titles
    task_categories = [
        "Frontend", "Backend", "Database", "UI/UX", "Design", "Testing", "Documentation",
        "Research", "Planning", "Deployment", "Maintenance", "Support", "Security",
        "Performance", "Optimization", "Integration", "API", "Authentication", "Reporting",
        "Analytics", "Infrastructure", "DevOps", "Architecture", "Mobile", "Desktop"
    ]

    task_actions = [
        "Development", "Implementation", "Design", "Testing", "Verification", "Review",
        "Analysis", "Research", "Documentation", "Troubleshooting", "Debugging", "Configuration",
        "Setup", "Integration", "Migration", "Refactoring", "Optimization", "Enhancement",
        "Improvement", "Extension", "Management", "Coordination", "Planning", "Assessment"
    ]

    # Add new tasks
    for user in users:
        # Count existing tasks for this user
        existing_count = user_task_count.get(user['id'], 0)

        # Generate more task titles for this user
        for i in range(existing_count, tasks_per_user):
            task_title = f"{random.choice(task_categories)} {random.choice(task_actions)}"

            # Generate a unique task ID
            task_id = generate_uuid()

            cursor.execute(
                'INSERT INTO task (id, "idUser", title) VALUES (%s, %s, %s) RETURNING id',
                (task_id, user['id'], task_title)
            )

            new_id = cursor.fetchone()[0]
            tasks.append({
                'id': new_id,
                'idUser': user['id'],
                'title': task_title,
            })

    conn.commit()
    print(f"Total tasks: {len(tasks)}")
    return tasks

# Generate location data
def generate_locations(conn, users, locations_per_user):
    locations = []

    # First, fetch existing locations
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", title FROM location')
    existing_locations = cursor.fetchall()

    # Include existing locations
    for location in existing_locations:
        locations.append({
            'id': location[0],
            'idUser': location[1],
            'title': location[2],
        })

    print(f"Found {len(existing_locations)} existing locations")

    # Dictionary to track locations per user and their titles
    user_locations = {}
    for location in locations:
        user_id = location['idUser']
        if user_id not in user_locations:
            user_locations[user_id] = []
        user_locations[user_id].append(location['title'])

    # Extended location types
    location_types = [
        "Home Office", "Client Site", "Main Office", "Satellite Office", "Coworking Space",
        "Coffee Shop", "Remote", "Field Location", "Conference Center", "Training Facility",
        "Airport Lounge", "Hotel", "Library", "Public Space", "Branch Office", "Partner Office",
        "Customer Premises", "Mobile Office", "Home", "Virtual Office"
    ]

    # Add new locations
    for user in users:
        # Get existing location titles for this user
        existing_titles = user_locations.get(user['id'], [])

        # Generate more locations for this user
        for _ in range(len(existing_titles), locations_per_user):
            # Try to find a location type that hasn't been used yet
            available_types = [loc for loc in location_types if loc not in existing_titles]

            if not available_types:
                # If we've used all types, add a numbered variant
                location_title = f"{random.choice(location_types)} {len(existing_titles) + 1}"
            else:
                location_title = random.choice(available_types)

            existing_titles.append(location_title)

            # Generate a unique location ID
            location_id = generate_uuid()

            cursor.execute(
                'INSERT INTO location (id, "idUser", title) VALUES (%s, %s, %s) RETURNING id',
                (location_id, user['id'], location_title)
            )

            new_id = cursor.fetchone()[0]
            locations.append({
                'id': new_id,
                'idUser': user['id'],
                'title': location_title,
            })

    conn.commit()
    print(f"Total locations: {len(locations)}")
    return locations

# Generate contract data
def generate_contracts(conn, projects, contracts_per_project):
    contracts = []

    # First, fetch existing contracts
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", "idProject", name, "startDate", "endDate", rate, "rateUnit" FROM contract')
    existing_contracts = cursor.fetchall()

    # Include existing contracts
    for contract in existing_contracts:
        contracts.append({
            'id': contract[0],
            'idUser': contract[1],
            'idProject': contract[2],
            'name': contract[3],
            'startDate': contract[4],
            'endDate': contract[5],
            'rate': contract[6],
            'rateUnit': contract[7],
        })

    print(f"Found {len(existing_contracts)} existing contracts")

    # Dictionary to track contracts per project
    project_contract_count = {}
    for contract in contracts:
        project_id = contract['idProject']
        project_contract_count[project_id] = project_contract_count.get(project_id, 0) + 1

    # Contract phase names
    contract_phases = [
        "Initial Phase", "Planning Phase", "Development Phase", "Implementation Phase",
        "Testing Phase", "Deployment Phase", "Support Phase", "Maintenance Phase",
        "Extension Phase", "Revision Phase", "Enhancement Phase", "Optimization Phase",
        "Training Phase", "Consultation Phase", "Migration Phase", "Integration Phase"
    ]

    # Additional descriptive terms
    descriptive_terms = [
        "Short-term", "Long-term", "Fixed-price", "Time-based", "Milestone-based",
        "Agile", "Sprint-based", "Project-based", "Retainer", "Maintenance",
        "Support", "Development", "Implementation", "Enhancement", "Customization"
    ]

    # Add new contracts
    for project in projects:
        user_id = project['idUser']

        # Count existing contracts for this project
        existing_count = project_contract_count.get(project['id'], 0)

        # Time range for project contracts (2024-2026)
        start_year = 2024
        end_year = 2026

        # Generate sequential contracts
        for i in range(existing_count, contracts_per_project):
            # Determine contract timeframe
            if i == 0:  # First contract starts in early 2024
                start_date = date(start_year, random.randint(1, 4), random.randint(1, 28))
                duration_months = random.randint(3, 8)
            else:  # Subsequent contracts follow the previous one
                prev_end = contracts[-1]['endDate']
                start_date = prev_end + timedelta(days=random.randint(7, 30))  # Gap between contracts
                duration_months = random.randint(2, 6)

            end_date = start_date + timedelta(days=30*duration_months)

            # Make sure end date is not beyond 2026
            if end_date > date(end_year, 12, 31):
                end_date = date(end_year, 12, 31)

            # Generate contract details
            if i == 0:
                contract_name = f"{random.choice(descriptive_terms)} {random.choice(contract_phases)}"
            else:
                contract_name = f"{project['name']} {random.choice(contract_phases)} {i+1}"

            note = fake.text(max_nb_chars=100) if random.random() > 0.3 else None

            # Rate varies by type of work and experience
            rate_base = random.randint(50, 150)
            rate_decimals = random.randint(0, 99)
            rate = decimal.Decimal(f"{rate_base}.{rate_decimals:02d}")

            rate_unit = random.choice(["hour", "day", "week", "month", "project"])

            # Generate a unique contract ID
            contract_id = generate_uuid()

            cursor.execute(
                'INSERT INTO contract (id, "idUser", "idProject", name, note, rate, "rateUnit", "startDate", "endDate") ' +
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (contract_id, user_id, project['id'], contract_name, note, rate, rate_unit, start_date, end_date)
            )

            new_id = cursor.fetchone()[0]
            contracts.append({
                'id': new_id,
                'idUser': user_id,
                'idProject': project['id'],
                'name': contract_name,
                'startDate': start_date,
                'endDate': end_date,
                'rate': rate,
                'rateUnit': rate_unit,
            })

    conn.commit()
    print(f"Total contracts: {len(contracts)}")
    return contracts

# Generate report data
def generate_reports(conn, contracts, reports_per_contract):
    reports = []

    # First, fetch existing reports
    cursor = conn.cursor()
    cursor.execute('SELECT id, "idUser", "idContract", note, billable, "startTimestamp", "endTimestamp" FROM report')
    existing_reports = cursor.fetchall()

    # Include existing reports
    for report in existing_reports:
        reports.append({
            'id': report[0],
            'idUser': report[1],
            'idContract': report[2],
            'note': report[3],
            'billable': report[4],
            'startTimestamp': report[5],
            'endTimestamp': report[6],
        })

    print(f"Found {len(existing_reports)} existing reports")

    # Dictionary to track reports per contract
    contract_report_count = {}
    for report in reports:
        contract_id = report['idContract']
        contract_report_count[contract_id] = contract_report_count.get(contract_id, 0) + 1

    # Activity descriptions for more realistic report notes
    activities = [
        "Client meeting", "Internal review", "Development sprint", "Testing session",
        "Documentation update", "Research", "Design session", "Planning", "Implementation",
        "Bug fixing", "Feature development", "Performance optimization", "Security audit",
        "Code review", "Database work", "API integration", "UI/UX improvements",
        "Deployment preparation", "Infrastructure setup", "Training preparation",
        "Requirements gathering", "Stakeholder communication", "Status report preparation",
        "Data migration", "System configuration", "Troubleshooting", "Client support"
    ]

    # Add new reports
    for contract in contracts:
        user_id = contract['idUser']

        # Count existing reports for this contract
        existing_count = contract_report_count.get(contract['id'], 0)

        # Generate reports within contract date range
        start_date = contract['startDate']
        end_date = contract['endDate']

        # Don't generate too many reports for short contracts
        contract_days = (end_date - start_date).days
        actual_reports = min(reports_per_contract, max(1, contract_days // 4))

        # Generate reports with a good distribution across the contract period
        for i in range(existing_count, actual_reports):
            # Determine report date - distribute evenly through contract period
            segment_size = max(1, contract_days // actual_reports)
            segment_start = start_date + timedelta(days=i * segment_size)
            segment_end = min(end_date, segment_start + timedelta(days=segment_size - 1))
            report_date = random_date(segment_start, segment_end)

            # Generate work schedule - most work happens during business hours
            start_hour = random.randint(7, 10)  # Start between 7am and 10am
            duration_hours = random.randint(3, 9)  # Work between 3 and 9 hours

            # Breaks are typically 15-60 minutes
            break_minutes = random.choice([0, 15, 30, 45, 60, 90])

            start_timestamp = datetime.combine(report_date, datetime.min.time()) + timedelta(hours=start_hour)
            end_timestamp = start_timestamp + timedelta(hours=duration_hours)
            break_time = f"{break_minutes} minutes"

            # Generate report details with more realistic notes
            activity = random.choice(activities)
            details = fake.sentence(nb_words=random.randint(3, 8))
            note = f"{activity}: {details}"

            # Most work is billable, but some isn't
            billable = random.random() > 0.1

            # Generate a unique report ID
            report_id = generate_uuid()

            cursor.execute(
                'INSERT INTO report (id, "idUser", "idContract", note, billable, "startTimestamp", "endTimestamp", "breakTime") ' +
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id',
                (report_id, user_id, contract['id'], note, billable, start_timestamp, end_timestamp, break_time)
            )

            new_id = cursor.fetchone()[0]
            reports.append({
                'id': new_id,
                'idUser': user_id,
                'idContract': contract['id'],
                'note': note,
                'billable': billable,
                'startTimestamp': start_timestamp,
                'endTimestamp': end_timestamp,
            })

            if i % 20 == 0:
                conn.commit()

    conn.commit()
    print(f"Total reports: {len(reports)}")
    return reports

# Generate assign data (link tasks to projects)
def generate_assignments(conn, projects, tasks):
    # Keep track of existing assignments to avoid duplicates
    cursor = conn.cursor()
    cursor.execute('SELECT "idProject", "idTask" FROM assign')
    existing_assignments = set((row[0], row[1]) for row in cursor.fetchall())

    print(f"Found {len(existing_assignments)} existing task assignments")

    # Group tasks by user for faster access
    user_tasks = {}
    for task in tasks:
        user_id = task['idUser']
        if user_id not in user_tasks:
            user_tasks[user_id] = []
        user_tasks[user_id].append(task)

    # Create task assignments (projects to tasks)
    assignments_added = 0
    for project in projects:
        user_id = project['idUser']

        # Find tasks belonging to the same user
        project_user_tasks = user_tasks.get(user_id, [])

        if not project_user_tasks:
            continue

        # Assign 2-5 random tasks to this project
        num_tasks = min(len(project_user_tasks), random.randint(2, 5))
        assigned_tasks = random.sample(project_user_tasks, num_tasks)

        for task in assigned_tasks:
            # Skip if this assignment already exists
            if (project['id'], task['id']) in existing_assignments:
                continue

            try:
                cursor.execute(
                    'INSERT INTO assign ("idProject", "idTask") VALUES (%s, %s)',
                    (project['id'], task['id'])
                )
                existing_assignments.add((project['id'], task['id']))
                assignments_added += 1
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                continue

            if assignments_added % 50 == 0:
                conn.commit()

    conn.commit()
    print(f"Added {assignments_added} new task assignments")

# Generate locatedAt data (link reports to locations)
def generate_report_locations(conn, reports, locations):
    # Keep track of existing location assignments
    cursor = conn.cursor()
    cursor.execute('SELECT "idReport", "idLocation" FROM "locatedAt"')
    existing_assignments = set((row[0], row[1]) for row in cursor.fetchall())

    print(f"Found {len(existing_assignments)} existing report locations")

    # Group locations by user for faster access
    user_locations = {}
    for location in locations:
        user_id = location['idUser']
        if user_id not in user_locations:
            user_locations[user_id] = []
        user_locations[user_id].append(location)

    # Associate reports with locations
    locations_added = 0
    for report in reports:
        user_id = report['idUser']

        # Find locations belonging to the same user
        report_user_locations = user_locations.get(user_id, [])

        if not report_user_locations:
            continue

        # Randomly select one location for this report
        location = random.choice(report_user_locations)

        # Skip if this assignment already exists
        if (report['id'], location['id']) in existing_assignments:
            continue

        try:
            cursor.execute(
                'INSERT INTO "locatedAt" ("idReport", "idLocation") VALUES (%s, %s)',
                (report['id'], location['id'])
            )
            existing_assignments.add((report['id'], location['id']))
            locations_added += 1
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            continue

        if locations_added % 50 == 0:
            conn.commit()

    conn.commit()
    print(f"Added {locations_added} new report locations")

# Generate expenses data
def generate_expenses(conn, reports):
    # Keep track of existing expenses
    cursor = conn.cursor()
    cursor.execute('SELECT "idReport", price, note FROM expenses')
    existing_expenses = set((row[0], float(row[1]), row[2]) for row in cursor.fetchall())

    print(f"Found {len(existing_expenses)} existing expenses")

    # More detailed expense categories for realistic expense notes
    expense_categories = {
        "Transportation": ["Taxi fare", "Uber ride", "Public transit", "Parking fee", "Mileage reimbursement", "Car rental", "Fuel"],
        "Meals": ["Client lunch", "Team dinner", "Business breakfast", "Catering", "Coffee meeting", "Snacks for meeting"],
        "Technology": ["Software subscription", "Cloud services", "Domain registration", "Hosting fees", "Dev tools", "API access"],
        "Hardware": ["Monitor", "Keyboard", "Mouse", "Laptop accessories", "Cables", "Storage devices", "Memory upgrade"],
        "Office": ["Paper", "Printer ink", "Stationery", "Notebooks", "Pens", "Office furniture", "Ergonomic equipment"],
        "Communication": ["Mobile data", "Internet service", "Phone charges", "Conference call service", "Virtual meeting software"],
        "Professional": ["Books", "Technical publications", "Online courses", "Training materials", "Certification fees", "Conference registration"],
        "Travel": ["Flight", "Hotel", "Train ticket", "Airport transfer", "Baggage fees", "Travel insurance", "Visa fees"]
    }

    # Add new expenses
    expenses_added = 0
    for report in reports:
        # Generate 0 to MAX_EXPENSES_PER_REPORT expenses
        num_expenses = random.randint(0, MAX_EXPENSES_PER_REPORT)

        for _ in range(num_expenses):
            # Select a random expense category and item
            category = random.choice(list(expense_categories.keys()))
            item = random.choice(expense_categories[category])

            # Generate expense details with realistic pricing based on category
            if category == "Transportation":
                price = decimal.Decimal(random.randint(10, 100) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Meals":
                price = decimal.Decimal(random.randint(8, 75) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Technology":
                price = decimal.Decimal(random.randint(5, 200) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Hardware":
                price = decimal.Decimal(random.randint(20, 500) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Office":
                price = decimal.Decimal(random.randint(5, 150) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Communication":
                price = decimal.Decimal(random.randint(10, 100) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Professional":
                price = decimal.Decimal(random.randint(15, 300) + random.random()).quantize(decimal.Decimal('0.01'))
            elif category == "Travel":
                price = decimal.Decimal(random.randint(50, 1000) + random.random()).quantize(decimal.Decimal('0.01'))
            else:
                price = decimal.Decimal(random.randint(5, 200) + random.random()).quantize(decimal.Decimal('0.01'))

            note = f"{category} - {item}"

            # Skip if this expense already exists
            if (report['id'], float(price), note) in existing_expenses:
                continue

            try:
                cursor.execute(
                    'INSERT INTO expenses ("idReport", price, note) VALUES (%s, %s, %s)',
                    (report['id'], price, note)
                )
                existing_expenses.add((report['id'], float(price), note))
                expenses_added += 1
            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                continue

            if expenses_added % 50 == 0:
                conn.commit()

    conn.commit()
    print(f"Added {expenses_added} new expenses")

# Main function to run the data generation
def generate_data():
    print("Starting data generation process...")
    conn = connect_to_db()
    if not conn:
        return

    try:
        print("Generating users...")
        users = generate_users(conn, NUM_USERS)

        print("Generating clients...")
        clients = generate_clients(conn, users, NUM_CLIENTS_PER_USER)

        print("Generating projects...")
        projects = generate_projects(conn, users, clients, NUM_PROJECTS_PER_CLIENT)

        print("Generating tasks...")
        tasks = generate_tasks(conn, users, NUM_TASKS_PER_USER)

        print("Generating locations...")
        locations = generate_locations(conn, users, NUM_LOCATIONS_PER_USER)

        print("Generating contracts...")
        contracts = generate_contracts(conn, projects, NUM_CONTRACTS_PER_PROJECT)

        print("Generating reports...")
        reports = generate_reports(conn, contracts, NUM_REPORTS_PER_CONTRACT)

        print("Assigning tasks to projects...")
        generate_assignments(conn, projects, tasks)

        print("Assigning locations to reports...")
        generate_report_locations(conn, reports, locations)

        print("Generating expenses...")
        generate_expenses(conn, reports)

        print("Data generation complete!")

        # Print statistics for verification
        cursor = conn.cursor()

        tables = ["user", "client", "project", "task", "location", "contract", "report", "assign", "locatedAt", "expenses"]
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            print(f"Total records in {table}: {count}")

    except Exception as e:
        print(f"Error during data generation: {e}")
    finally:
        conn.close()

# Run the data generation
if __name__ == "__main__":
    generate_data()