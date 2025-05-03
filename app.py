from flask import Flask, render_template,Response, request, redirect, url_for, flash,abort, session, jsonify,send_from_directory, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime, timedelta,date
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
import os,shutil
import io,zipfile
from waitress import serve
from sqlalchemy import exists, text,func, extract
from sqlalchemy.dialects.postgresql import ARRAY
import traceback,calendar
from datetime import date, timedelta
import psycopg2
from psycopg2 import OperationalError
from collections import defaultdict
import re 
from psycopg2.extras import RealDictCursor


app = Flask(__name__)
app.secret_key = "your_secret_key"

#Exclusively calls database
def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="media2",
            user="postgres",
            password="user123"
        )
        return conn
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None
    
# PostgreSQL Database Configuration
DATABASE_URL = "postgresql://postgres:user123@127.0.0.1:5432/media2"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Pagination Config
JOBS_PER_PAGE = 10

# Define User Model 
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Define Job Model 
class JobDetail(db.Model):
    __tablename__ = 'job_detail'
    photoid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    eventcode = db.Column(db.String(50), nullable=False)
    r_type = db.Column(db.String(50), nullable=False)
    photographer_selection = db.Column(db.Text, nullable=True)
    event_title = db.Column(db.String(255), nullable=False)
    event_venue = db.Column(db.String(255), nullable=False)
    event_dt_fm = db.Column(db.Date, nullable=True)
    event_dt_to = db.Column(db.Date, nullable=True)
    event_ti_fm = db.Column(db.Time, nullable=True)
    event_ti_to = db.Column(db.Time, nullable=True)
    requester_name = db.Column(db.String(255), nullable=False)
    request_phone = db.Column(db.String(20), nullable=False)
    request_email = db.Column(db.String(255), nullable=False)
    request_div = db.Column(db.String(255), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    jobcode = db.Column(db.String(255), nullable=False, unique=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime)  

class JobPhotographers(db.Model):
    __tablename__ = 'job_photographers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photoid = db.Column(db.Integer, db.ForeignKey('job_detail.photoid'), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    photographer_name = db.Column(db.String(255), nullable=False)
    
    job = db.relationship('JobDetail', backref=db.backref('photographers', lazy=True))

class EventCode(db.Model):
    __tablename__ = 'event_code'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=True)
    examples = db.Column(db.Text, nullable=True)

class EventVenue(db.Model):
    __tablename__ = 'event_venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class Keyword(db.Model):
    __tablename__ = 'keywords'  # Ensure this matches your table name in PostgreSQL
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(100), unique=True, nullable=False)  # Ensure this column matches the database

class KeywordEntry(db.Model):
    __tablename__ = 'keyword_entry'
    keyno = db.Column(db.Integer, primary_key=True)
    jobcode = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    keyword_id = db.Column(ARRAY(db.Integer), nullable=True)  # Array column
    keywords = db.Column(ARRAY(db.String(100)), nullable=True)  # Store keyword texts
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    mody_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.Column(db.String(50), nullable=False)
    path = db.Column(db.Text, nullable=False)

def __repr__(self):
        return f'<KeywordEntry {self.filename} Path: {self.path}>'
        
# Create tables
with app.app_context():
    db.create_all()


# =========================================
#          JOB CODE GENERATION
# =========================================
def generate_job_code(eventcode):
    """Generates a unique job code in the format: eventcode/year/photoid."""
    if not eventcode:
        eventcode = "UNKNOWN"

    current_year = datetime.now().year

    # ✅ Get the highest photoid for the current year only
    last_photoid = db.session.execute(
        text("SELECT COALESCE(MAX(photoid), 0) FROM job_detail WHERE EXTRACT(YEAR FROM created_at) = :current_year"),
        {"current_year": current_year}
    ).fetchone()[0]

    next_photoid = last_photoid + 1  # Ensure unique ID

    return f"{eventcode}/{current_year}/{next_photoid}"

#==========================================================
#                   LOGIN PAGE (login.html)
#==========================================================
@app.route('/', methods=['GET', 'POST'])
def login():
    # Fetch announcements
    announcements = db.session.execute(text("SELECT message FROM announcements ORDER BY created_at DESC")).fetchall()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Fetch user securely
        user = db.session.execute(
            text("SELECT * FROM users WHERE username = :username AND password = :password"),
            {"username": username, "password": password}
        ).fetchone()

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', announcements=announcements)

#==========================================================
#                   HOME PAGE (index.html)
#==========================================================
@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#==========================================================
#                   JOB MANAGEMENT PAGE (job.html)
#==========================================================
# app.py

# Import necessary modules if not already present at the top
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, or_, exists # Make sure 'or_' and 'exists' are imported if used elsewhere
from datetime import datetime, timedelta
import traceback # Useful for debugging errors

# --- Assume your Flask app (app), SQLAlchemy (db), and models (JobDetail, JobPhotographers) are defined here ---
# Example:
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri'
# app.config['SECRET_KEY'] = 'your_secret_key'
# db = SQLAlchemy(app)
#
# class JobDetail(db.Model):
#     # ... your model definition ...
#     photoid = db.Column(db.Integer, primary_key=True)
#     jobcode = db.Column(db.String)
#     event_title = db.Column(db.String)
#     event_dt_fm = db.Column(db.Date)
#     event_dt_to = db.Column(db.Date)
#     requester_name = db.Column(db.String)
#     is_deleted = db.Column(db.Boolean, default=False, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow) # Example created_at
#     # ... other columns ...
#
# class JobPhotographers(db.Model):
#      # ... your model definition ...
#      id = db.Column(db.Integer, primary_key=True) # Example primary key
#      photoid = db.Column(db.Integer, db.ForeignKey('job_detail.photoid')) # Example foreign key
#      event_date = db.Column(db.Date)
#      photographer_name = db.Column(db.String)
#      # ... other columns ...
#
# def generate_job_code(eventcode):
#     # Your implementation for generating job codes
#     return f"JOB-{eventcode}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
# --- End Example Setup ---


#==========================================================
#                JOB MANAGEMENT PAGE (job.html)
#==========================================================
@app.route('/job', methods=['GET'])
def job():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    # ***** MODIFICATION START *****
    # Start the query by filtering out deleted jobs FIRST
    query = JobDetail.query.filter_by(is_deleted=False)
    # ***** MODIFICATION END *****

    # Then apply search filters if needed
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_( # Make sure 'or_' is imported from sqlalchemy
                JobDetail.jobcode.ilike(search_term),
                JobDetail.event_title.ilike(search_term),
                JobDetail.requester_name.ilike(search_term)
                # Add other fields to search if desired
            )
        )

    # Finally, order the results and paginate
    # Order by created_at AFTER filtering
    query = query.order_by(JobDetail.created_at.desc())
    jobs = query.paginate(page=page, per_page=10, error_out=False)

    return render_template('job.html', jobs=jobs, search_query=search_query)


#==========================================================
#                   ADDING NEW JOB(add_job.html)
#==========================================================

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        try:
            print("✅ Form submitted!")  
            print("📌 Received form data:", request.form)  

            # Capture form data
            eventcode = request.form.get('eventcode')
            r_type = request.form.get('r_type')
            photographer_selection = ', '.join(request.form.getlist('photographer_selection'))
            event_title = request.form.get('event_title')
            event_venue = request.form.get('event_venue')
            event_dt_fm = request.form.get('event_dt_fm')
            event_dt_to = request.form.get('event_dt_to')
            event_ti_fm = request.form.get('event_ti_fm')
            event_ti_to = request.form.get('event_ti_to')
            requester_name = request.form.get('requester_name')
            request_phone = request.form.get('request_phone')
            request_email = request.form.get('request_email')
            request_div = request.form.get('request_div')
            remarks = request.form.get('remarks')

            print("📌 Extracted event_dt_fm:", event_dt_fm)  
            print("📌 Extracted event_dt_to:", event_dt_to)  

            # Convert date & time safely
            event_dt_fm = datetime.strptime(event_dt_fm, '%Y-%m-%d').date() if event_dt_fm else None
            event_dt_to = datetime.strptime(event_dt_to, '%Y-%m-%d').date() if event_dt_to else None
            event_ti_fm = datetime.strptime(event_ti_fm, '%H:%M').time() if event_ti_fm else None
            event_ti_to = datetime.strptime(event_ti_to, '%H:%M').time() if event_ti_to else None

            print("📌 Converted event_dt_fm:", event_dt_fm)  
            print("📌 Converted event_dt_to:", event_dt_to)  

            # ✅ Generate job code
            jobcode = generate_job_code(eventcode)
            print("📌 Generated jobcode:", jobcode)  

            # ✅ Create new job entry
            new_job = JobDetail(
                jobcode=jobcode,
                eventcode=eventcode,
                r_type=r_type,
                event_title=event_title,
                event_venue=event_venue,
                event_dt_fm=event_dt_fm,
                event_dt_to=event_dt_to,
                event_ti_fm=event_ti_fm,
                event_ti_to=event_ti_to,
                requester_name=requester_name,
                request_phone=request_phone,
                request_email=request_email,
                request_div=request_div,
                remarks=remarks,
                photographer_selection=photographer_selection,  # ✅ Correctly storing photographers
                is_deleted=False
            )

            db.session.add(new_job)
            db.session.flush()  # Ensures new_job.photoid is generated
            print("📌 New job added to session, photoid:", new_job.photoid)  

            # ✅ Save Photographer Assignments Per Day
            if new_job.photoid and event_dt_fm and event_dt_to:
                current_date = event_dt_fm
                while current_date <= event_dt_to:
                    key = f'day_photographers_{current_date}'
                    selected_photographers = request.form.getlist(key)  # ✅ Correct form key

                    for photographer in selected_photographers:
                        # ✅ Check if the photographer is already assigned for this date
                        exists_query = db.session.query(
                            exists().where(
                                (JobPhotographers.photoid == new_job.photoid) &
                                (JobPhotographers.event_date == current_date) &
                                (JobPhotographers.photographer_name == photographer)
                            )
                        ).scalar()

                        if not exists_query:  # ✅ Only insert if NOT already in DB
                            db.session.add(JobPhotographers(photoid=new_job.photoid, event_date=current_date, photographer_name=photographer))

                    current_date += timedelta(days=1)  # ✅ Increment date properly

            db.session.commit()
            print("✅ Database commit successful!")  

            flash("Job successfully added!", "success")
            return redirect(url_for('job'))  # ✅ Ensure this matches your route

        except Exception as e:
            db.session.rollback()
            print("❌ Database Error:", str(e))  
            flash(f"Database Error: {str(e)}", "danger")

    # Fetch required dropdown data
    event_codes = db.session.execute(text("SELECT code, description FROM event_code")).fetchall()
    event_venues = db.session.execute(text("SELECT name FROM event_venue")).mappings().all()
    photographers = db.session.execute(text("SELECT name FROM photographers WHERE status='active'")).mappings().all()

    return render_template('add_job.html', job=None, event_codes=event_codes, event_venues=event_venues, photographers=photographers)

#==========================================================
#           UPDATE EXISTING JOB (update_job.html)
#==========================================================
# --- Your update_job Route ---
@app.route('/update_job/<int:photoid>', methods=['GET', 'POST'])
def update_job(photoid):
    # Use get_or_404 to automatically handle cases where the job ID doesn't exist
    job = JobDetail.query.get_or_404(photoid)

    if request.method == 'POST':
        try:
            print("\n✅ Update Form submitted!")
            print("📌 Received form data:", request.form)

            # --- Capture form data ---
            eventcode = request.form.get('eventcode')
            r_type = request.form.get('r_type')
            event_title = request.form.get('event_title')
            event_venue = request.form.get('event_venue')
            event_dt_fm_str = request.form.get('event_dt_fm') # Keep as string initially for validation
            event_dt_to_str = request.form.get('event_dt_to') # Keep as string initially for validation
            event_ti_fm = request.form.get('event_ti_fm') # Store as string or Time object based on DB
            event_ti_to = request.form.get('event_ti_to') # Store as string or Time object based on DB
            requester_name = request.form.get('requester_name')
            request_phone = request.form.get('request_phone')
            request_email = request.form.get('request_email')
            request_div = request.form.get('request_div')
            remarks = request.form.get('remarks')
            photographer_selection = request.form.get('photographer_selection') # Initial list string from hidden input

            # --- Basic Server-Side Validation (Example) ---
            # Check for missing required fields
            required_fields = {
                'Event Code': eventcode, 'Requirement Type': r_type, 'Event Title': event_title,
                'Event Venue': event_venue, 'Event Date From': event_dt_fm_str, 'Event Date To': event_dt_to_str,
                'Time From': event_ti_fm, 'Time To': event_ti_to, 'Requester Name': requester_name,
                'Requester Phone': request_phone, 'Requester Email': request_email
            }
            missing_fields = [name for name, value in required_fields.items() if not value]
            if missing_fields:
                 flash(f"❌ Please fill in all required fields: {', '.join(missing_fields)}.", "danger")
                 # Redirect back to the GET request for this same job on validation error
                 return redirect(url_for('update_job', photoid=photoid))
            # --- End Basic Validation ---

            # --- Convert and Validate Dates AFTER checking they exist ---
            try:
                event_dt_fm = datetime.strptime(event_dt_fm_str, '%Y-%m-%d').date()
                event_dt_to = datetime.strptime(event_dt_to_str, '%Y-%m-%d').date()
                # Check if dates are logical
                if event_dt_fm > event_dt_to:
                    flash("❌ Event 'Date From' cannot be after 'Date To'.", "danger")
                    return redirect(url_for('update_job', photoid=photoid))
            except ValueError:
                 # Handle cases where date strings are not in the expected format
                 flash("❌ Invalid date format. Please use YYYY-MM-DD.", "danger")
                 return redirect(url_for('update_job', photoid=photoid))

            print(f"📅 Parsed Event Date From: {event_dt_fm}, To: {event_dt_to}")

            # --- Update job details in job_detail table ---
            print("🔄 Updating job details in job_detail table...")
            job.eventcode = eventcode
            job.r_type = r_type
            job.event_title = event_title
            job.event_venue = event_venue
            job.event_dt_fm = event_dt_fm
            job.event_dt_to = event_dt_to
            job.event_ti_fm = event_ti_fm
            job.event_ti_to = event_ti_to
            job.requester_name = requester_name
            job.request_phone = request_phone
            job.request_email = request_email
            job.request_div = request_div
            job.remarks = remarks
            job.photographer_selection = photographer_selection # Update the initial list string if you store it

            # --- Photographer Assignment Logic (Simplified: Delete then Insert) ---
            print("🔄 Processing photographer assignments...")

            # 1. Clear existing assignments for this job *within the updated date range*
            # This handles date range changes correctly (shrinking or expanding)
            print(f"🗑️ Clearing assignments for photoid={job.photoid} between {event_dt_fm} and {event_dt_to}")
            db.session.execute(
                text("""
                    DELETE FROM job_photographers
                    WHERE photoid = :photoid
                    AND event_date >= :start_date
                    AND event_date <= :end_date
                """),
                {"photoid": job.photoid, "start_date": event_dt_fm, "end_date": event_dt_to}
            )

            # 2. Prepare new assignments to insert based on form checkboxes
            new_assignments = []
            current_date = event_dt_fm
            while current_date <= event_dt_to:
                date_str = current_date.strftime('%Y-%m-%d')
                # Construct the name attribute used for checkboxes for this day
                key = f'day_photographers_{date_str}'
                # Get the list of values (photographer names) from checked boxes with this name
                selected_photographers_for_day = request.form.getlist(key)

                if selected_photographers_for_day: # Only add if at least one photographer is checked for the day
                    # Store as comma-separated string (adjust if your schema uses multiple rows per day/photographer)
                    photographer_names_str = ', '.join(selected_photographers_for_day)
                    print(f"➕ Preparing assignment for {date_str}: {photographer_names_str}")
                    new_assignments.append({
                        "photoid": job.photoid,
                        "event_date": current_date, # Use the date object for insertion
                        "photographer_name": photographer_names_str
                    })
                else:
                     print(f"⚪ No photographers assigned for {date_str}") # Log days with no assignments

                # Move to the next day
                current_date += timedelta(days=1)

            # 3. Bulk insert new assignments if any were prepared
            if new_assignments:
                print(f"➕ Bulk inserting {len(new_assignments)} new photographer assignments...")
                # Ensure the parameter names in the dictionary match the VALUES clause placeholders
                db.session.execute(
                    text("""
                        INSERT INTO job_photographers (photoid, event_date, photographer_name)
                        VALUES (:photoid, :event_date, :photographer_name)
                    """),
                   new_assignments # Pass the list of dictionaries for bulk insert
                )
            # --- End Photographer Assignment Logic ---

            # --- Commit the transaction ---
            # All changes (job details and photographer assignments) are saved together
            db.session.commit()
            print("✅ Job update successful!")

            # *** SUCCESS: Flash message and Redirect ***
            # Create a user-friendly success message
            flash(f'✅ Job "{job.jobcode}" updated successfully!', 'success') # 'success' category for Bootstrap styling
            # Redirect the user to the main job listing page (adjust 'job' if your route name is different)
            return redirect(url_for('job'))

        except Exception as e:
            # If any error occurs during the try block, roll back the transaction
            db.session.rollback()
            print(f"❌ Update Error for job {photoid}: {str(e)}")
            # Print the full error traceback to the console/logs for debugging
            traceback.print_exc()

            # *** ERROR: Flash message and Redirect back to the form ***
            # Create a user-friendly error message
            flash(f'❌ Error updating job "{job.jobcode}": {str(e)}', 'danger') # 'danger' category for Bootstrap styling
            # Redirect the user back to the same update page so they can correct errors
            return redirect(url_for('update_job', photoid=photoid))

    # --- GET Request Logic ---
    # (This part executes when the page is loaded initially OR after a redirect back on error)
    print(f"🔄 Loading update form for photoid={photoid}")

    # Fetch supporting data needed to render the form
    event_codes = db.session.execute(text("SELECT code, description FROM event_code ORDER BY code")).fetchall()
    event_venues = db.session.execute(text("SELECT id, name FROM event_venue ORDER BY name")).fetchall()

    # Fetch active photographers - **Adjusted to provide list of dicts for template**
    photographers_query = db.session.execute(
        text("SELECT name FROM photographers WHERE status = 'active' ORDER BY name")
    ).fetchall()
    # Create list of dictionaries like [{'name': 'Alice'}, {'name': 'Bob'}]
    # This matches how the template iterates: {% for p in photographers %} {{ p.name }} {% endfor %}
    photographers_list = [{'name': p[0]} for p in photographers_query] # Access the first element (name)

    # Fetch existing daily assignments to pre-populate checkboxes via JavaScript
    daily_assignments = {}
    existing_assignments_query = db.session.execute(
        text("SELECT event_date, photographer_name FROM job_photographers WHERE photoid = :photoid"),
        {"photoid": photoid}
    ).fetchall()

    # Populate the dictionary for the template's JavaScript (used for pre-checking boxes)
    for assign_rec in existing_assignments_query:
        event_date = assign_rec[0] # Assuming event_date is the first column
        photographer_names_str = assign_rec[1] # Assuming photographer_name is the second

        date_key = str(event_date) # Use YYYY-MM-DD string as key for JS dictionary
        # Split the stored comma-separated string back into a list for JS 'includes' check
        # Handle empty/null strings gracefully to avoid errors
        daily_assignments[date_key] = [name.strip() for name in photographer_names_str.split(',') if name.strip()] if photographer_names_str else []

    print("📌 Existing Daily Assignments for JS:", daily_assignments)
    print("📌 Photographer list for dropdown:", photographers_list)

    # Render the update form template, passing all necessary data
    return render_template(
        'update_job.html',
        job=job, # The job object being updated
        event_codes=event_codes, # List of event codes for dropdown
        event_venues=event_venues, # List of venues for dropdown
        photographers=photographers_list, # List of photographer dicts for dropdown/JS
        daily_assignments=daily_assignments # Dict for JS to pre-check daily assignments
    )
#==========================================================
#           DELETE JOB(soft delete)  
#==========================================================

@app.route('/delete_job/<int:photoid>', methods=['POST'])
def delete_job(photoid):
    # Use first_or_404 to handle not found cases cleanly
    job = JobDetail.query.filter_by(photoid=photoid).first_or_404()

    if job.is_deleted:  # Prevent accidental re-deletion
        flash('⚠️ Job is already marked as deleted.', 'warning')
        return redirect(url_for('job'))

    try:
        job.is_deleted = True  # Mark as deleted
        # Optional: You might want to clear associated photographer assignments as well
        # db.session.execute(text("DELETE FROM job_photographers WHERE photoid = :photoid"), {"photoid": photoid})
        db.session.commit()
        flash('✅ Job marked as deleted successfully.', 'success') # Changed message slightly
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error during soft delete for job {photoid}: {str(e)}")
        traceback.print_exc()
        flash(f'❌ Error marking job as deleted: {str(e)}', 'danger')

    return redirect(url_for('job'))

#==========================================================
#                 VIEWING A JOB(view_job.html) needs to be do
#==========================================================

# Ensure the color helper function is defined in your app.py
def get_color_for_photographer(name, color_map, default_color='#E0E0E0'):
    """Assigns a color based on photographer name."""
    if not name: return default_color
    hash_code = 0
    for char in name: hash_code = ord(char) + ((hash_code << 5) - hash_code)
    r = (hash_code & 0xFF0000) >> 16; g = (hash_code & 0x00FF00) >> 8; b = hash_code & 0x0000FF
    r = (r + 255) // 2; g = (g + 255) // 2; b = (b + 255) // 2
    color = f"#{r:02x}{g:02x}{b:02x}"
    if name not in color_map: color_map[name] = color
    return color_map[name]

# --- DELETE or COMMENT OUT the old conflicting route ---
# @app.route('/view/<int:photoid>')
# def view_job(photoid):
#     job = JobDetail.query.get_or_404(photoid)
#     return render_template('view_job.html', job=job)
# --- END delete/comment out ---


# --- NEW Combined Route ---
@app.route('/view_job/<int:photoid>') # Using int converter for photoid if it's an integer ID
def view_job(photoid):       # Use a unique function name!
    """Display details for a specific job and its schedule context."""
    assignments_by_date = {}
    photographer_colors = {}
    calendar_data = None # Initialize calendar data as None

    try:
        # 1. Fetch the main job
        # Use filter_by if photoid is not the primary key, or get if it is. Adjust as needed.
        job = JobDetail.query.filter_by(photoid=photoid).first_or_404()

        # Proceed with calendar only if job has a start date
        if job.event_dt_fm:
            # 2. Determine the month/year for the calendar
            year = job.event_dt_fm.year
            month = job.event_dt_fm.month

            # --- Integrated Calendar Data Fetching Logic ---
            try:
                # Calculate date range for the month
                first_day_of_month = date(year, month, 1)
                if month == 12:
                    last_day_of_month = date(year, month, 31)
                else:
                    _, num_days = calendar.monthrange(year, month)
                    last_day_of_month = date(year, month, num_days)

                # Query the database using JOIN
                query = db.session.query(
                    JobDetail.event_dt_fm,
                    JobDetail.event_dt_to,
                    JobPhotographers.photographer_name,
                    JobDetail.jobcode,
                    JobDetail.event_title,
                    JobDetail.photoid
                ).join(
                    JobPhotographers, JobDetail.photoid == JobPhotographers.photoid
                ).filter(
                    JobDetail.event_dt_fm <= last_day_of_month,
                    (JobDetail.event_dt_to >= first_day_of_month) | (JobDetail.event_dt_to == None)
                ).order_by(JobDetail.event_dt_fm, JobPhotographers.photographer_name)

                results = query.all()

                # Process the results
                for event_start, event_end, photographer, jobcode, title, result_photoid in results:
                    if not event_start: continue
                    actual_end_date = event_end if event_end else event_start
                    photographer_name = photographer or "Unassigned"

                    current_date = event_start
                    while current_date <= actual_end_date:
                        if first_day_of_month <= current_date <= last_day_of_month:
                            date_str = current_date.strftime('%Y-%m-%d')
                            if date_str not in assignments_by_date:
                                assignments_by_date[date_str] = []
                            color = get_color_for_photographer(photographer_name, photographer_colors)
                            assignments_by_date[date_str].append({
                                'photographer': photographer_name,
                                'jobcode': jobcode or 'N/A',
                                'title': title or 'No Title',
                                'color': color,
                                'photoid': result_photoid
                            })
                        current_date += timedelta(days=1)
                        if current_date > actual_end_date + timedelta(days=366): break # Safety break

                # Get calendar structure
                month_calendar = calendar.monthcalendar(year, month)

                # Package calendar context
                calendar_data = {
                    'year': year,
                    'month_name': calendar.month_name[month],
                    'month_num': month,
                    'month_calendar': month_calendar,
                    'assignments': assignments_by_date,
                    'today_str': date.today().strftime('%Y-%m-%d'),
                    'photographer_colors': photographer_colors
                }

            except Exception as cal_e:
                # Log error fetching calendar data but still show job details
                current_app.logger.error(f"Error fetching calendar data for job {photoid}: {cal_e}", exc_info=True)
                # calendar_data remains None
        # --- End Integrated Calendar Logic ---

        # Render the template with job details and potentially calendar data
        return render_template('view_job.html', job=job, calendar_data=calendar_data)

    except Exception as e:
        # Handle errors fetching the main job or other unexpected errors
        current_app.logger.error(f"Error in view_job for {photoid}: {e}", exc_info=True)
        # from flask import abort
        # abort(500) # Or render a specific error page
        return "Error loading job details", 500

#==========================================================
#   MAILING JOB ACKNOWLEDGEMENT CARDS(NEEDS TO BE DONE)                  
#==========================================================

@app.route('/mail/<int:photoid>')
def mail_job(photoid):
    job = JobDetail.query.get_or_404(photoid)
    flash(f'Email sent for Job ID: {photoid}', 'info')  # Integrate with actual mail service
    return redirect(url_for('job'))

#==========================================================
#    PRINTING JOB ACKNOWLEDGEMENTS(Workup more nicely)     
#==========================================================

@app.route('/print/<int:photoid>')
def print_job(photoid):
    job = JobDetail.query.get_or_404(photoid)
    return render_template('print_page.html', job=job)  # Implement actual print logic

import os
import shutil
import json
import traceback # For better error logging
from flask import request, jsonify, session, render_template, redirect, url_for
# Ensure secure_filename is imported for basic filename sanitization
from werkzeug.utils import secure_filename
from datetime import datetime
# Assuming app, db, and models are correctly imported from your project structure
# from . import app, db
# from .models import JobDetail, Keyword, KeywordEntry
from sqlalchemy import text, cast, ARRAY

# ==========================================================
#               EXISTING ROUTES (Keep As Is)
# ==========================================================
@app.route('/key_entry')
def key_entry():
    """Render the keyword entry page."""
    return render_template('keyent.html')

@app.route('/get_events', methods=['POST'])
def get_events():
    """Fetch events based on the selected date."""
    try:
        data = request.get_json()
        selected_date = datetime.strptime(data['event_date'], "%Y-%m-%d").date()

        # Consider adding an index on event_dt_fm and event_dt_to for performance
        events = JobDetail.query.filter(
            (JobDetail.event_dt_fm == selected_date) |
            ((JobDetail.event_dt_fm <= selected_date) & (JobDetail.event_dt_to >= selected_date))
        ).all()

        # Include necessary details needed for the dropdown and subsequent lookups
        event_list = [
            {
                "photoid": event.photoid,
                "jobcode": event.jobcode,
                "event_title": event.event_title,
                # Optionally include other details here if it avoids the second fetch
                "photographer_name": event.photographer_selection,
                "type_of_coverage": event.r_type
            }
            for event in events
        ]
        return jsonify(event_list)

    except Exception as e:
        app.logger.error(f"Error in /get_events: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to fetch events."}), 500

@app.route('/get_event_details', methods=['POST'])
def get_event_details():
    """Fetch event details when an event is selected."""
    # This might be redundant if /get_events returns all needed info
    try:
        data = request.get_json()
        photoid = data.get('photoid')

        if not photoid:
             return jsonify({"error": "Missing Photo ID"}), 400

        event = JobDetail.query.filter_by(photoid=photoid).first()
        if event:
            event_data = {
                "photographer_name": event.photographer_selection,
                "jobcode": event.jobcode,
                "type_of_coverage": event.r_type,
                "title": event.event_title,
                "event_date": event.event_dt_fm.strftime("%Y-%m-%d") if event.event_dt_fm else None
            }
            return jsonify(event_data)
        else:
            return jsonify({"error": "Event not found"}), 404

    except Exception as e:
        app.logger.error(f"Error in /get_event_details: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to fetch event details."}), 500


@app.route('/suggest_keywords', methods=['POST'])
def suggest_keywords():
    """Auto-suggest keywords from the database based on user input."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()

        if not query or len(query) < 1: # Add minimum length if desired
            return jsonify([])

        # Use parameterized query for security
        sql_query = text("SELECT DISTINCT keyword FROM keywords WHERE LOWER(keyword) LIKE :query LIMIT 10")
        keywords = db.session.execute(sql_query, {"query": f"{query.lower()}%"}).fetchall()

        keyword_list = [kw[0] for kw in keywords]
        return jsonify(keyword_list)

    except Exception as e:
        app.logger.error(f"Error in /suggest_keywords: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to suggest keywords."}), 500

# This route seems unused by the provided HTML, but keep if needed elsewhere
@app.route('/add_keyword', methods=['POST'])
def add_keyword():
    """Allow users to add a keyword if it doesn't exist."""
    try:
        data = request.get_json()
        new_keyword_text = data.get("keyword", "").strip()

        if not new_keyword_text:
            return jsonify({"error": "Keyword cannot be empty"}), 400

        # Case-insensitive check might be better depending on requirements
        existing_keyword = Keyword.query.filter(db.func.lower(Keyword.keyword) == new_keyword_text.lower()).first()

        if existing_keyword:
            return jsonify({"message": "Keyword already exists", "keyword": existing_keyword.keyword}), 200

        new_entry = Keyword(keyword=new_keyword_text) # Store with original casing? Or normalize?
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "Keyword added", "keyword": new_entry.keyword}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in /add_keyword: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to add keyword."}), 500

# This route seems unused by the provided HTML, but keep if needed elsewhere
@app.route('/get_keywords', methods=['GET'])
def get_keywords():
    """Fetch all keywords from the database."""
    try:
        keywords = Keyword.query.order_by(Keyword.keyword).all()
        keyword_list = [{"id": kw.id, "keyword": kw.keyword} for kw in keywords]
        return jsonify(keyword_list)

    except Exception as e:
        app.logger.error(f"Error in /get_keywords: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to get keywords."}), 500


@app.route('/generate_destination_path', methods=['POST'])
def generate_destination_path():
    """Generate destination folder name using jobcode and event date."""
    try:
        data = request.get_json()
        jobcode = data.get('jobcode')
        # Use a default or handle missing session gracefully
        usercode = session.get("username", "default_user")

        if not jobcode:
            return jsonify({"error": "Missing jobcode"}), 400

        event = JobDetail.query.filter_by(jobcode=jobcode).first()
        if not event:
            return jsonify({"error": "Event not found for given jobcode"}), 404

        if not event.event_dt_fm:
            return jsonify({"error": "Event date is missing in the database for this jobcode"}), 400

        # Format date components
        year = event.event_dt_fm.strftime("%Y")
        month = event.event_dt_fm.strftime("%m")
        day = event.event_dt_fm.strftime("%d")

        # Extract event code and photoid safely
        parts = jobcode.split('/')
        if len(parts) != 3:
            # Log the problematic jobcode
            app.logger.warning(f"Invalid jobcode format encountered: {jobcode}")
            return jsonify({"error": f"Invalid jobcode format: {jobcode}"}), 400

        event_code, _, photoid = parts

        # Define the base path from configuration or environment variable for flexibility
        # Example: base_upload_path = app.config.get('UPLOAD_FOLDER_BASE', 'D:/') # Default to D:/ if not configured
        base_upload_path = 'D:/' # Hardcoded for now as per original code
        destination_path = os.path.join(base_upload_path, year, month, f"{event_code}-{day}-{usercode}-{photoid}")

        # Normalize path separators for consistency (optional but good practice)
        destination_path = os.path.normpath(destination_path)

        return jsonify({"destination_path": destination_path})

    except Exception as e:
        app.logger.error(f"Error in /generate_destination_path: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to generate destination path."}), 500

#       MODIFIED ROUTE TO HANDLE FILE UPLOADS

@app.route('/copy_files', methods=['POST'])
def copy_files_upload():
    """
    Handles UPLOADING files selected via 'webkitdirectory' input.
    Expects multipart/form-data with 'files', 'destination_folder',
    and 'relative_paths' (JSON string list matching the order of 'files').
    """
    errors = []
    uploaded_file_details = [] # Store details of successfully uploaded files
    destination_folder = None

    # --- Basic Security: Check if user is logged in (if applicable) ---
    # if 'username' not in session:
    #     return jsonify({"errors": ["User not authenticated."]}), 401

    try:
        # --- 1. Get Data from Form and Files ---
        # Use request.form for text data, request.files for files in multipart/form-data
        destination_folder = request.form.get('destination_folder')
        relative_paths_json = request.form.get('relative_paths') # Expecting a JSON string list
        uploaded_files = request.files.getlist('files') # Key used in frontend FormData

        app.logger.info(f"Received upload request. Destination: {destination_folder}, Files count: {len(uploaded_files)}")
        # app.logger.debug(f"Relative paths JSON: {relative_paths_json}") # Be careful logging potentially large data

        # --- 2. Validation ---
        if not destination_folder:
            errors.append("Missing destination folder path.")
        else:
            # More robust path validation (example)
            allowed_base = os.path.normpath("D:/") # Normalize for comparison
            norm_dest = os.path.normpath(destination_folder)
            if not norm_dest.startswith(allowed_base) or ".." in norm_dest.split(os.sep):
                 errors.append(f"Invalid or disallowed destination folder path: {destination_folder}")
                 destination_folder = None # Prevent use

        if not uploaded_files:
            errors.append("No files were received.")

        relative_paths = []
        if not relative_paths_json:
            errors.append("Missing relative path information.")
        elif not errors: # Only parse if no prior errors
             try:
                 relative_paths = json.loads(relative_paths_json)
                 if not isinstance(relative_paths, list):
                      errors.append("Relative paths format is invalid (not a list).")
                 elif len(relative_paths) != len(uploaded_files):
                      errors.append(f"Mismatch between number of files ({len(uploaded_files)}) and relative paths ({len(relative_paths)}).")
             except json.JSONDecodeError:
                 errors.append("Invalid JSON format for relative paths.")

        if errors:
            app.logger.warning(f"Validation errors for upload: {errors}")
            return jsonify({"errors": errors}), 400

        # --- 3. Ensure Base Destination Exists (Only if valid) ---
        try:
            os.makedirs(destination_folder, exist_ok=True)
            app.logger.info(f"Ensured destination folder exists: {destination_folder}")
        except OSError as e:
            errors.append(f"Server error: Failed to create destination folder '{destination_folder}': {e}")
            app.logger.error(f"OSError creating destination folder: {e}\n{traceback.format_exc()}")
            return jsonify({"errors": errors}), 500

        # --- 4. Process Each Uploaded File ---
        for i, file in enumerate(uploaded_files):
            if file and file.filename: # Basic check for valid FileStorage object
                try:
                    original_relative_path = relative_paths[i]
                    app.logger.debug(f"Processing file index {i}, relative path: '{original_relative_path}'")

                    # --- Sanitize and Construct Path ---
                    # Normalize separators and remove leading/trailing slashes
                    clean_relative_path = os.path.normpath(original_relative_path.strip('/\\'))

                    # Split into parts and validate against traversal
                    path_parts = clean_relative_path.split(os.sep)
                    if ".." in path_parts or "." in path_parts: # Basic check
                         errors.append(f"Skipped file due to invalid relative path components ('..' or '.'): '{original_relative_path}'")
                         app.logger.warning(f"Invalid path component detected in: {original_relative_path}")
                         continue

                    # Secure the final filename part
                    safe_filename = secure_filename(path_parts[-1])
                    if not safe_filename: # secure_filename might return empty string
                        safe_filename = f"file_{i}_upload" # Fallback filename
                        app.logger.warning(f"Used fallback filename for index {i} as original was unsafe.")

                    # Reconstruct the safe relative path excluding the filename
                    safe_relative_dir_path = os.path.join(*path_parts[:-1])

                    # Final destination path on the server
                    full_dest_path = os.path.join(destination_folder, safe_relative_dir_path, safe_filename)
                    full_dest_dir = os.path.dirname(full_dest_path)

                    # --- Create Subdirectories if needed ---
                    if not os.path.exists(full_dest_dir):
                        try:
                            os.makedirs(full_dest_dir, exist_ok=True)
                            app.logger.debug(f"Created subdirectory: {full_dest_dir}")
                        except OSError as e:
                            errors.append(f"Failed to create sub-directory '{full_dest_dir}' for '{original_relative_path}': {e}")
                            app.logger.error(f"OSError creating subdirectory {full_dest_dir}: {e}")
                            continue # Skip this file

                    # --- Save the File ---
                    try:
                        file.save(full_dest_path)
                        uploaded_file_details.append({
                            "original_path": original_relative_path,
                            "saved_path": full_dest_path,
                            "size": os.path.getsize(full_dest_path) # Get size after saving
                        })
                        app.logger.info(f"Successfully saved file to: {full_dest_path}")
                    except Exception as e:
                        errors.append(f"Failed to save file '{original_relative_path}' to '{full_dest_path}': {str(e)}")
                        app.logger.error(f"Error saving file {full_dest_path}: {e}\n{traceback.format_exc()}")

                except IndexError:
                    errors.append(f"Internal error: Missing relative path for file index {i}.")
                    app.logger.error(f"IndexError accessing relative_paths at index {i}")
                except Exception as e:
                    # Catch other unexpected errors during file processing
                    errors.append(f"Unexpected error processing file index {i} ('{file.filename}'): {str(e)}")
                    app.logger.error(f"Unexpected error processing file {file.filename}: {e}\n{traceback.format_exc()}")
            else:
                 # Log if an invalid file part was received
                 errors.append(f"Skipped invalid or unnamed file upload at index {i}.")
                 app.logger.warning(f"Received invalid file part at index {i}")


        # --- 5. Return Final Response ---
        if errors:
            app.logger.warning(f"Upload completed with errors: {errors}")
            # Even with errors, some files might have succeeded (207 Multi-Status)
            return jsonify({
                "message": "File upload processed with errors.",
                "errors": errors,
                "uploaded_files": [d["saved_path"] for d in uploaded_file_details] # Return list of saved paths
            }), 207
        else:
            app.logger.info(f"All {len(uploaded_file_details)} files uploaded successfully to {destination_folder}.")
            return jsonify({
                "success": f"All {len(uploaded_file_details)} files uploaded successfully.",
                "uploaded_files": [d["saved_path"] for d in uploaded_file_details] # Return list of saved paths
            }), 200 # OK

    except Exception as e:
        # Catch unexpected errors during request handling phase
        app.logger.error(f"Fatal error in /copy_files (upload handler): {e}\n{traceback.format_exc()}")
        return jsonify({"errors": ["An unexpected server error occurred during file upload processing."]}), 500


# ==========================================================
#     KEYWORD ENTRY AND OTHER EXISTING ROUTES (Keep As Is)
# ==========================================================
@app.route('/add_keyword_entry', methods=['POST'])
def add_keyword_entry():
    """Add keywords from the form to 'keyword_entry' table after ensuring they exist in 'keywords'."""
    # Use session for user info
    user = session.get("username", "guest") # Get username or use default

    try:
        data = request.get_json()
        jobcode = data.get('jobcode')
        # Filename might need context - is it one file, or applied to all in the path?
        # Assuming it might be a placeholder or specific file if known.
        filename = data.get('filename', 'N/A')
        keywords_text = data.get('keywords', [])  # List of keyword strings
        path = data.get('path') # The destination path where files were copied/uploaded

        if not jobcode or not path or not keywords_text:
            return jsonify({"error": "Missing jobcode, destination path, or keywords"}), 400

        valid_keyword_ids = []
        valid_keyword_texts = [] # Store the text of keywords actually added/found

        for keyword_str in keywords_text:
            keyword_str = keyword_str.strip()
            if not keyword_str:
                continue

            # Check/add keyword (case-insensitive check recommended)
            keyword_obj = Keyword.query.filter(db.func.lower(Keyword.keyword) == keyword_str.lower()).first()

            if not keyword_obj:
                # Add new keyword if it doesn't exist
                app.logger.info(f"Adding new keyword: {keyword_str}")
                keyword_obj = Keyword(keyword=keyword_str) # Save with original case?
                db.session.add(keyword_obj)
                # Commit here or after the loop? Committing inside might be slower but safer per keyword.
                # Let's commit after the loop for efficiency. Need to flush to get ID.
                db.session.flush() # Assigns ID without full commit
                if keyword_obj.id is None: # Check if flush worked
                     db.session.commit() # Commit if flush didn't assign ID (less likely)

            if keyword_obj.id: # Ensure we have an ID
                valid_keyword_ids.append(keyword_obj.id)
                valid_keyword_texts.append(keyword_obj.keyword) # Use the potentially normalized text from DB
            else:
                 app.logger.error(f"Failed to get ID for keyword: {keyword_str}")
                 # Decide how to handle this - skip keyword or raise error? Skipping for now.

        # Commit any newly added keywords now
        db.session.commit()

        if not valid_keyword_ids:
             app.logger.warning(f"No valid keywords found or added for jobcode {jobcode}, path {path}.")
             return jsonify({"error": "No valid keywords provided or could be added."}), 400

        # Prepare data for KeywordEntry
        # Check if an entry already exists for this specific jobcode/path combination (optional)
        # For simplicity, adding a new entry each time for now.

        # Use SQLAlchemy ARRAY type if your DB supports it (like PostgreSQL)
        keyword_id_array = valid_keyword_ids # Pass the list directly
        keyword_text_array = valid_keyword_texts # Pass the list directly

        new_entry = KeywordEntry(
            jobcode=jobcode,
            filename=filename, # Store filename context if provided
            keyword_id=keyword_id_array,   # Use list for ARRAY type
            keywords=keyword_text_array,   # Use list for ARRAY type
            user=user,
            path=path,
            entry_date=datetime.utcnow(), # Use UTC for consistency
            mody_date=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()

        app.logger.info(f"Keywords {valid_keyword_texts} added for jobcode {jobcode}, path {path}")
        return jsonify({"message": "Keywords added successfully", "keywords_added": valid_keyword_texts}), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in /add_keyword_entry: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to add keyword entry."}), 500


@app.route('/get_keyword_entries', methods=['GET'])
def get_keyword_entries():
    """Fetch all keyword entries along with keyword names."""
    try:
        # Add pagination or filtering later if needed
        entries = KeywordEntry.query.order_by(KeywordEntry.entry_date.desc()).all()
        result = []

        for entry in entries:
            # Keyword names are stored directly in the 'keywords' array column now
            keyword_names = entry.keywords if entry.keywords else []

            result.append({
                "jobcode": entry.jobcode,
                "filename": entry.filename,
                "keywords": keyword_names, # Use stored text array
                "entry_date": entry.entry_date.strftime("%Y-%m-%d %H:%M:%S") if entry.entry_date else None,
                "mody_date": entry.mody_date.strftime("%Y-%m-%d %H:%M:%S") if entry.mody_date else None,
                "user": entry.user,
                "path": entry.path
            })

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error in /get_keyword_entries: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to retrieve keyword entries."}), 500


# This route seems separate, using raw SQL and different logic (merging keywords).
# Keep it if it serves a different purpose, but ensure it's secure and correct.
# It uses request.form, implying a standard HTML form post, not related to the JS app directly?
@app.route('/submit', methods=['POST'])
def submit_form():
    """Handles submission from a potentially different form (uses request.form). Merges keywords."""
    # WARNING: This route uses raw SQL and manual array formatting.
    # Consider using SQLAlchemy for consistency and safety if possible.
    # Also needs proper error handling and connection management.
    conn = None # Ensure connection is managed
    try:
        # Use session user if available
        user = session.get("username", request.form.get('user', 'guest')) # Get username

        path = request.form.get('path')
        jobcode = request.form.get('jobcode')
        keywords_raw = request.form.get('keywords', '') # Comma-separated string

        if not path or not jobcode or not user:
             # Redirect or return error
             return "Missing required form fields (path, jobcode, user).", 400

        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

        if not keywords:
             return "No keywords provided.", 400

        # Replace with SQLAlchemy session if possible
        # conn = get_db_connection() # Replace with db.session access
        # cursor = conn.cursor()

        keyword_ids = []
        keyword_texts = []

        for keyword_name in keywords:
            # Check/add keyword (use SQLAlchemy session)
             keyword_obj = Keyword.query.filter(db.func.lower(Keyword.keyword) == keyword_name.lower()).first()
             if not keyword_obj:
                  keyword_obj = Keyword(keyword=keyword_name)
                  db.session.add(keyword_obj)
                  db.session.flush() # Get ID before commit

             if keyword_obj.id:
                 keyword_ids.append(keyword_obj.id)
                 keyword_texts.append(keyword_obj.keyword) # Use consistent casing
             else:
                 # Handle error - keyword couldn't be added/found
                 app.logger.error(f"Could not process keyword '{keyword_name}' in /submit route.")
                 # Optionally raise an error or continue

        # Commit any new keywords added in the loop
        db.session.commit()

        if not keyword_ids:
             return "No valid keywords could be processed.", 400


        # Check for existing entry using SQLAlchemy
        existing_entry = KeywordEntry.query.filter_by(path=path, jobcode=jobcode, user=user).first()

        if existing_entry:
            # Merge keywords safely
            existing_keyword_ids = existing_entry.keyword_id if existing_entry.keyword_id else []
            existing_keyword_texts = existing_entry.keywords if existing_entry.keywords else []

            # Use sets for efficient merging and uniqueness
            updated_keyword_ids = list(set(existing_keyword_ids) | set(keyword_ids))
            updated_keyword_texts = list(set(existing_keyword_texts) | set(keyword_texts))

            # Update existing entry
            existing_entry.keyword_id = updated_keyword_ids
            existing_entry.keywords = updated_keyword_texts
            existing_entry.mody_date = datetime.utcnow()
            app.logger.info(f"Updating keywords for existing entry: path={path}, jobcode={jobcode}")

        else:
            # Insert new entry
            new_entry = KeywordEntry(
                path=path,
                jobcode=jobcode,
                user=user,
                keyword_id=keyword_ids, # List for ARRAY type
                keywords=keyword_texts, # List for ARRAY type
                entry_date=datetime.utcnow(),
                mody_date=datetime.utcnow()
            )
            db.session.add(new_entry)
            app.logger.info(f"Creating new keyword entry: path={path}, jobcode={jobcode}")

        db.session.commit() # Commit the update or insert

        return redirect(url_for('index')) # Redirect to index page on success

    except Exception as e:
        if db.session.is_active:
             db.session.rollback()
        app.logger.error(f"Error in /submit route: {e}\n{traceback.format_exc()}")
        # Provide a user-friendly error page or message
        return f"An error occurred: {e}", 500


#==========================================================
#                 Image Viewing (imgview.html)  
#==========================================================

# --- Helper Function (Keep or Modify) ---
def get_images_from_directory(directory):
    """ Returns a list of image files from the given directory. """
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    try:
        # SECURITY: Basic check - Ensure directory seems plausible before listing
        # More robust checks happen in the image_preview route
        if not directory or not os.path.isabs(directory): # Example check: require absolute paths
             print(f"Warning: Attempt to access non-absolute path: {directory}")
             # return [] # Or raise an error depending on policy
             # Allowing relative paths might be ok if base directory is strictly controlled

        if os.path.exists(directory) and os.path.isdir(directory):
            # List files and filter by extension
            files = [f for f in os.listdir(directory)
                     if os.path.isfile(os.path.join(directory, f)) and # Ensure it's a file
                     os.path.splitext(f)[1].lower() in valid_extensions]
            return sorted(files) # Sort for consistent order
        else:
            print(f"Directory not found or not a directory: {directory}")
            return [] # Return empty list if path doesn't exist/isn't a dir
    except OSError as e: # Catch potential permission errors etc.
        print(f"OS Error accessing directory {directory}: {e}")
        return []
    except Exception as e: # Catch other unexpected errors
         print(f"Unexpected error accessing directory {directory}: {e}")
         return []


# --- Path Parsing Helper ---
# Adjust the regex if your path structure is different
# Example: Matches /.../YYYY/MM/... or \...\YYYY\MM\...
# It captures YYYY, MM, and the part *after* YYYY/MM/
PATH_REGEX = re.compile(r'.*[/\\\\](\d{4})[/\\\\](\d{1,2})[/\\\\](.*)')

def parse_path(path_string):
    """Parses a path string to extract year, month, and coverage name/subpath."""
    if not path_string:
        return None
    match = PATH_REGEX.match(path_string)
    if match:
        try:
            year = int(match.group(1))
            month = int(match.group(2))
            # The rest of the path after YYYY/MM/ can be used as a name/identifier
            coverage_name = match.group(3)
            # Return the full original path as well for the value
            return {'year': year, 'month': month, 'coverage': coverage_name, 'full_path': path_string}
        except (ValueError, IndexError):
             print(f"Error parsing matched groups for path: {path_string}")
             return None # Error during conversion or group access
    else:
        # Optional: Log paths that don't match the expected format
        # print(f"Path did not match expected YYYY/MM format: {path_string}")
        pass # Silently ignore non-matching paths or handle differently
    return None

@app.route("/imgview.html", methods=["GET", "POST"])
def imgview():
    selected_year = request.form.get("year", type=int)
    selected_month = request.form.get("month", type=int)
    # Use .get("coverage_path", "") which defaults to empty string if not found
    selected_path = request.form.get("coverage_path", "").strip()
    files = [] # Initialize files list
    years = set()
    months_by_year = defaultdict(set)
    paths_for_selection = [] # Paths matching current selection (for POST reload)
    all_parsed_paths = {} # Cache parsed data {full_path: {'year': y, 'month': m, ...}}

    # Fetch all unique paths from the KeywordEntry table
    # Using with_entities is efficient as it only selects the 'path' column
    # Using distinct() ensures we only process each unique path once
    try:
        path_entries = db.session.query(KeywordEntry.path).distinct().all()
        all_paths = [entry[0] for entry in path_entries] # Extract path string from tuple
    except Exception as e:
        print(f"Database error fetching paths: {e}")
        # Handle error appropriately, maybe show an error message to the user
        all_paths = [] # Proceed with empty data or return an error template

    # Parse fetched paths
    for path_str in all_paths:
        parsed = parse_path(path_str)
        if parsed:
            years.add(parsed['year'])
            months_by_year[parsed['year']].add(parsed['month'])
            all_parsed_paths[parsed['full_path']] = parsed # Store parsed data

    sorted_years = sorted(list(years), reverse=True)
    # Create a structure easily convertible to JSON for JS dropdowns
    # Ensure months are sorted numerically within each year
    month_options = {y: sorted(list(m)) for y, m in months_by_year.items()}

    # --- Handle POST Request ---
    if request.method == "POST":
        # Basic validation: Ensure year, month, and path were submitted
        if selected_year and selected_month and selected_path:
            # Security/Validation: Check if the submitted path is one we know about
            # and if its parsed year/month match the submitted year/month
            if selected_path in all_parsed_paths:
                path_data = all_parsed_paths[selected_path]
                if path_data['year'] == selected_year and path_data['month'] == selected_month:
                    # Path is valid and matches selection, try to get images
                    print(f"Fetching images for validated path: {selected_path}")
                    files = get_images_from_directory(selected_path) # Fetch the image files

                    # Prepare paths for the dropdown for the *currently* selected Y/M
                    # This ensures the path dropdown is correctly populated on page reload after POST
                    paths_for_selection = sorted([
                        p for p, data in all_parsed_paths.items()
                        if data['year'] == selected_year and data['month'] == selected_month
                    ])
                else:
                    # Data mismatch (e.g., user manipulated form)
                    print(f"Warning: Submitted path '{selected_path}' did not match year '{selected_year}' / month '{selected_month}'. Resetting.")
                    selected_path = "" # Reset path
                    files = [] # Clear files
            else:
                 # Submitted path wasn't found in our database list
                 print(f"Warning: Submitted path '{selected_path}' not found in database. Resetting.")
                 selected_path = "" # Reset path
                 files = [] # Clear files
        else:
            # Incomplete submission
            print("Incomplete form submission (Year, Month, or Path missing).")
            selected_path = "" # Ensure path is reset if submission was incomplete
            files = [] # Clear files

    # --- Render Template ---
    return render_template(
        "imgview.html",
        years=sorted_years,
        month_options_json=month_options, # Pass structure for JS
        selected_year=selected_year,      # Pass back selected values
        selected_month=selected_month,
        available_paths=paths_for_selection, # Paths for the dropdown (only relevant on POST)
        selected_path=selected_path,      # Pass back selected path
        files=files                       # Pass list of image filenames
    )

# API Endpoint to get paths for a given Year/Month
@app.route("/get_paths", methods=["GET"])
def get_paths():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not year or not month:
        return jsonify({'error': 'Year and Month parameters are required'}), 400

    # Fetch paths matching the year and month from the database
    # Using LIKE can be inefficient on large tables without proper indexing.
    # Consider database-specific functions or filtering pre-fetched data if performance is an issue.

    # Construct the LIKE pattern carefully based on expected path structure
    # This assumes paths contain /YYYY/MM/ or \YYYY\MM\ (adjust if needed)
    # Using % at start/end allows flexibility but might slow down queries.
    # {:02d} ensures month is zero-padded (e.g., 05 for May)
    like_pattern_fwd = f"%/{year}/{month:02d}/%" # Forward slash
    like_pattern_bwd = f"%\\{year}\\{month:02d}\\%" # Backward slash (need escaping)

    try:
        # Query using OR for different slash types
        matching_entries = db.session.query(KeywordEntry.path)\
            .filter(db.or_(KeywordEntry.path.like(like_pattern_fwd),
                           KeywordEntry.path.like(like_pattern_bwd)))\
            .distinct()\
            .all()

        # Extract paths from the result tuples
        paths = sorted([entry[0] for entry in matching_entries])

    except Exception as e:
        print(f"Database error fetching paths for {year}/{month}: {e}")
        return jsonify({'error': 'Database query failed'}), 500

    return jsonify({'paths': paths}) # Return sorted full paths


# Keep the gallery route if needed, but its client-side logic might need rework
@app.route("/gallery.html")
def gallery():
    return render_template("gallery.html")

# Image preview route - serves the actual image file
@app.route("/image_preview/<path:filename>") # Use path converter for flexibility
def image_preview(filename):
    """ Serves an image from the selected directory. """
    directory = request.args.get("directory", "").strip()

    # --- SECURITY CHECKS ---
    if not directory or not filename:
        print("Access Denied: Missing directory or filename parameter.")
        return "Missing parameters", 400

    # 1. Validate the directory against known paths from the database
    #    This prevents serving files from arbitrary locations.
    try:
        entry_exists = db.session.query(KeywordEntry.path).filter(KeywordEntry.path == directory).first()
        if not entry_exists:
           print(f"Access Denied: Directory '{directory}' not found in keyword_entry table.")
           # Don't reveal too much info in error messages
           return "Not Found", 404 # Use 404 Not Found
    except Exception as e:
         print(f"Database error checking directory {directory}: {e}")
         return "Server Error", 500

    # 2. Basic Path Sanity Checks
    #    - Ensure the directory is absolute (or within a controlled base)
    #    - Prevent directory traversal in filename itself
    if ".." in filename or filename.startswith(("/", "\\")):
        print(f"Access Denied: Invalid filename format '{filename}'.")
        return "Invalid filename", 400
    # if not os.path.isabs(directory): # Enforce absolute paths if required by your setup
    #    print(f"Access Denied: Directory '{directory}' is not absolute.")
    #    return "Invalid directory", 400

    # 3. Check physical existence (redundant if list was generated correctly, but good defense)
    #    Construct the full path *safely*
    try:
        # os.path.join handles path separators correctly
        # Important: Ensure directory itself doesn't contain malicious sequences bypassed earlier
        full_path = os.path.join(directory, filename)

        # Check if the directory exists and is actually a directory
        if not os.path.isdir(directory):
             print(f"Error: Directory '{directory}' not found or not a directory on filesystem.")
             return "Not Found", 404

        # Check if the file exists and is actually a file within that directory
        if not os.path.isfile(full_path):
             print(f"Error: File '{filename}' not found or not a file in directory '{directory}'.")
             return "Not Found", 404

        # Final check: Ensure the resolved full_path hasn't escaped the intended directory
        # (os.path.join might resolve '..' sequences depending on OS)
        # Check if full_path still starts with the validated directory path
        # Use os.path.normpath for consistent comparisons
        if not os.path.normpath(full_path).startswith(os.path.normpath(directory)):
            print(f"Access Denied: Path traversal detected. Resolved path '{full_path}' escaped directory '{directory}'.")
            return "Invalid path", 400

    except Exception as e:
         print(f"Error checking file/directory existence for {filename} in {directory}: {e}")
         return "Server Error", 500


    # 4. If all checks pass, serve the file
    print(f"Serving file: {filename} from directory: {directory}")
    try:
        # Use Flask's send_from_directory for safer serving
        return send_from_directory(directory, filename)
    except Exception as e:
        # Catch potential errors during file serving (e.g., permissions changed)
        print(f"Error serving file {filename} from {directory}: {e}")
        return "Error serving file", 500

#==========================================================
#           Gallery (gallery.html)  
#==========================================================

# --- Configuration ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/gallery') # Gallery is now at /gallery
def gallery_page():
    """Renders the main gallery page."""
    return render_template('gallery.html')

def get_db_connection():  # <-- RENAME HERE
    conn = None
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="media2",
            user="postgres",
            password="user123" # Consider using environment variables later for security
        )
        # print("Database connection successful") # Optional debug line
        return conn
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None # Or raise e, depending on how you want to handle errors
    
@app.route('/api/images')
def get_images():
    """API endpoint to fetch image data (supports searching and limit)."""
    search_term = request.args.get('search', '')
    folder_filter = request.args.get('folder', None)
    limit = request.args.get('limit', type=int, default=None) # Get limit parameter

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Base query (consider adding folder column if used)
    base_query = "SELECT id, filename, filepath, description, folder, uploaded_at FROM images"
    count_query = "SELECT COUNT(*) FROM images" # For total count potentially
    params = []
    conditions = []

    if search_term:
        conditions.append("(filename ILIKE %s OR description ILIKE %s)")
        params.extend([f"%{search_term}%", f"%{search_term}%"])

    if folder_filter:
        conditions.append("folder = %s")
        params.append(folder_filter)

    # Construct WHERE clause
    where_clause = ""
    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    # Final query for data
    query = base_query + where_clause + " ORDER BY uploaded_at DESC, filename ASC" # Order for preview/gallery

    # Add LIMIT if specified
    if limit and limit > 0:
        query += " LIMIT %s"
        params.append(limit)

    # Query for total count (considering filters)
    count_query += where_clause

    try:
        # Execute main query
        cursor.execute(query, tuple(params))
        images = cursor.fetchall()

        # Execute count query (using same params minus the limit)
        cursor.execute(count_query, tuple(params[:-1] if limit else params))
        total_count = cursor.fetchone()['count']

    except psycopg2.Error as e:
        print(f"Error fetching images: {e}")
        images = []
        total_count = 0
    finally:
        cursor.close()
        conn.close()

    # Add the full URL path for the image source
    for image in images:
        # Securely generate URL - url_for is safer if serve_upload handles complex paths well
        # Or keep the simpler string concat if filepath is guaranteed safe/simple
        # image['url'] = url_for('serve_upload', filepath=image['filepath'], _external=False)
        image['url'] = f"/uploads/{image['filepath']}" # Keep simple version for now

    # Return data along with total count (useful for gallery page)
    return jsonify({
        "images": images,
        "total_count": total_count,
        "filter": { # Echo back filters applied (useful for UI state)
             "search": search_term,
             "folder": folder_filter,
             "limit": limit
        }
    })


@app.route('/uploads/<path:filepath>')
def serve_upload(filepath):
    try:
        safe_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], filepath))
        if not safe_path.startswith(app.config['UPLOAD_FOLDER']):
             raise ValueError("Attempted directory traversal")
        directory = os.path.dirname(safe_path)
        filename = os.path.basename(safe_path)
        return send_from_directory(directory, filename)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error serving file {filepath}: {e}")
        abort(404)
    except Exception as e:
        print(f"Unexpected error serving file {filepath}: {e}")
        abort(500)


@app.route('/download/image/<int:image_id>')
def download_single_image(image_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT filename, filepath FROM images WHERE id = %s", (image_id,))
        image = cursor.fetchone()
        if not image: abort(404, "Image not found")
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filepath'])
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename, as_attachment=True, download_name=image['filename'])
    except psycopg2.Error as e: abort(500)
    except FileNotFoundError: abort(404)
    except Exception as e: abort(500)
    finally: cursor.close(); conn.close()


@app.route('/download/selected')
def download_selected_images():
    image_ids_str = request.args.get('ids')
    if not image_ids_str: abort(400, "No image IDs provided")
    try:
        image_ids = [int(id) for id in image_ids_str.split(',')]
        if not image_ids: abort(400, "Invalid image IDs")
    except ValueError: abort(400, "Invalid image IDs format")

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT id, filename, filepath FROM images WHERE id = ANY(%s::int[])"
        cursor.execute(query, (image_ids,))
        images = cursor.fetchall()
        if not images: abort(404, "No valid images found.")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            added_files = set()
            for image in images:
                 if image['filename'] in added_files:
                     name, ext = os.path.splitext(image['filename'])
                     zip_filename = f"{name}_{image['id']}{ext}"
                 else:
                     zip_filename = image['filename']
                     added_files.add(zip_filename)
                 file_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filepath'])
                 if os.path.exists(file_path): zf.write(file_path, arcname=zip_filename)
                 else: print(f"Warning: File not found ID {image['id']}: {file_path}")

        memory_file.seek(0)
        return Response(memory_file, mimetype='application/zip', headers={'Content-Disposition': 'attachment;filename=selected_images.zip'})
    except psycopg2.Error as e: abort(500)
    except FileNotFoundError as e: abort(500)
    except Exception as e: abort(500)
    finally: cursor.close(); conn.close()


@app.route('/download/all') # Or /download/folder/<foldername>
def download_all_images():
    folder_filter = request.args.get('folder', None)
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = "SELECT id, filename, filepath FROM images"
        params = []
        zip_filename_base = "all_images"
        if folder_filter:
            query += " WHERE folder = %s"
            params.append(folder_filter)
            zip_filename_base = f"images_{folder_filter}"
        query += " ORDER BY filename ASC"
        cursor.execute(query, tuple(params))
        images = cursor.fetchall()
        if not images: abort(404, "No images found.")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
             added_files = set()
             for image in images:
                 if image['filename'] in added_files:
                     name, ext = os.path.splitext(image['filename'])
                     zip_filename = f"{name}_{image['id']}{ext}"
                 else:
                     zip_filename = image['filename']
                     added_files.add(zip_filename)
                 file_path = os.path.join(app.config['UPLOAD_FOLDER'], image['filepath'])
                 if os.path.exists(file_path): zf.write(file_path, arcname=zip_filename)
                 else: print(f"Warning: File not found ID {image['id']}: {file_path}")

        memory_file.seek(0)
        return Response(memory_file, mimetype='application/zip', headers={'Content-Disposition': f'attachment;filename={zip_filename_base}.zip'})
    except psycopg2.Error as e: abort(500)
    except FileNotFoundError as e: abort(500)
    except Exception as e: abort(500)
    finally: cursor.close(); conn.close()


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

#==========================================================
#           Photographer Schedule (schedule.html)  
#==========================================================

# Helper function to generate colors (simple approach)
def get_color_for_photographer(name, color_map, default_color='#E0E0E0'):
    """Assigns a color based on photographer name."""
    if not name:
        return default_color
    # Simple hash-based color generation (can be improved)
    hash_code = 0
    for char in name:
        hash_code = ord(char) + ((hash_code << 5) - hash_code)
    # Generate somewhat distinct pastel colors
    r = (hash_code & 0xFF0000) >> 16
    g = (hash_code & 0x00FF00) >> 8
    b = hash_code & 0x0000FF
    # Mix with white to make pastel
    r = (r + 255) // 2
    g = (g + 255) // 2
    b = (b + 255) // 2
    color = f"#{r:02x}{g:02x}{b:02x}"
    # Store in map for consistency within the request
    if name not in color_map:
         color_map[name] = color
    return color_map[name]

@app.route('/schedule')
@app.route('/schedule/<int:year>/<int:month>')
def photographer_schedule(year=None, month=None):
    """Display photographer assignments in a monthly calendar."""
    try:
        # Determine the year and month to display
        if year is None or month is None:
            today = date.today()
            year, month = today.year, today.month
        else:
            # Basic validation for year/month
            if not (1 <= month <= 12):
                 return "Invalid month", 400
            try:
                 # Check if date is valid
                 today = date(year, month, 1)
            except ValueError:
                 return "Invalid year/month combination", 400

        # Calculate first and last day of the target month
        first_day_of_month = date(year, month, 1)
        if month == 12:
            last_day_of_month = date(year, month, 31)
            next_month, next_year = 1, year + 1
            prev_month, prev_year = 11, year
        elif month == 1:
            # calendar.monthrange handles leap years correctly for last day
            _, num_days = calendar.monthrange(year, month)
            last_day_of_month = date(year, month, num_days)
            next_month, next_year = 2, year
            prev_month, prev_year = 12, year - 1
        else:
            _, num_days = calendar.monthrange(year, month)
            last_day_of_month = date(year, month, num_days)
            next_month, next_year = month + 1, year
            prev_month, prev_year = month - 1, year


        # Fetch assignments that overlap with the current month
        # An event overlaps if: (EventStart <= MonthEnd) and (EventEnd >= MonthStart)
        assignments = JobDetail.query.filter(
            JobDetail.event_dt_fm <= last_day_of_month,
            (JobDetail.event_dt_to >= first_day_of_month) | (JobDetail.event_dt_to == None) # Handle events without an end date? Assumed same as start if null.
        ).order_by(JobDetail.event_dt_fm).all()

        assignments_by_date = {}
        photographer_colors = {} # To store colors assigned per photographer

        # Process assignments into a date-keyed dictionary
        for job in assignments:
            if not job.event_dt_fm: continue # Skip jobs without a start date

            start_date = job.event_dt_fm
            # If event_dt_to is null, assume it's a single-day event
            end_date = job.event_dt_to if job.event_dt_to else start_date

            # Iterate through each day the event spans
            current_date = start_date
            while current_date <= end_date:
                 # Only include days within the *target month*
                if first_day_of_month <= current_date <= last_day_of_month:
                    date_str = current_date.strftime('%Y-%m-%d')
                    if date_str not in assignments_by_date:
                        assignments_by_date[date_str] = []

                    photographer = job.photographer_selection or "Unassigned"
                    color = get_color_for_photographer(photographer, photographer_colors)

                    assignments_by_date[date_str].append({
                        'photographer': photographer,
                        'jobcode': job.jobcode or 'N/A',
                        'title': job.event_title or 'No Title',
                        'color': color
                    })
                # Move to the next day
                current_date += timedelta(days=1)
                # Safety break for potential infinite loops if dates are weird
                if current_date > end_date + timedelta(days=1): break


        # Get calendar structure for the month
        month_calendar = calendar.monthcalendar(year, month) # List of weeks, each week a list of day numbers (0 for padding)

        # Prepare context for the template
        context = {
            'year': year,
            'month_name': calendar.month_name[month],
            'month_num': month,
            'month_calendar': month_calendar, # The grid structure
            'assignments': assignments_by_date, # The assignments keyed by 'YYYY-MM-DD'
            'today_str': date.today().strftime('%Y-%m-%d'),
            'prev_month': prev_month,
            'prev_year': prev_year,
            'next_month': next_month,
            'next_year': next_year,
            'photographer_colors': photographer_colors # Pass the generated color map
        }

        return render_template('schedule.html', **context)

    except Exception as e:
        current_app.logger.error(f"Error generating schedule for {year}-{month}: {e}", exc_info=True)
        return "Error generating schedule", 500

#==========================================================
#         Event_codes(event_codes.html)  
#==========================================================
@app.route('/event_codes')
def event_codes():
    try:
        event_codes = EventCode.query.all()
        rows = [(event.code, event.description, event.examples) for event in event_codes]
        return render_template('event_codes.html', rows=rows)
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return "Database error occurred", 500


if __name__ == '__main__':
    serve(app, host="127.0.0.1", port=5000)