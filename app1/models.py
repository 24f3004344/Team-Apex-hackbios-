from datetime import date, datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# -------------------------------------------------------------------
# Association Table: Many-to-Many (Hospital <-> Specialty)
# -------------------------------------------------------------------
hospital_specialties = db.Table(
    'hospital_specialties',
    db.Column('hospital_id', db.Integer, db.ForeignKey('hospitals.id', ondelete='CASCADE'), primary_key=True),
    db.Column('specialty_id', db.Integer, db.ForeignKey('specialties.id', ondelete='CASCADE'), primary_key=True)
)


# -------------------------------------------------------------------
# Master Table: Specialties
# -------------------------------------------------------------------
class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Specialty {self.name}>"


# -------------------------------------------------------------------
# Core User Model (Authentication & Central Identity)
# -------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    mobile_no = db.Column(db.String(15), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Secure Aadhaar handling (masked last 4 digits for UI, hash for lookup)
    aadhar_last4 = db.Column(db.String(4), nullable=True)
    aadhar_hash = db.Column(db.String(64), unique=True, nullable=True)
    
    # Roles: 'admin', 'hospital', 'driver', 'patient', 'doctor', 'asha'
    role = db.Column(db.String(20), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # 1-to-1 Profile Relationships (Explicitly bound to their respective user_id columns)
    patient_profile = db.relationship(
        'Patient',
        foreign_keys='Patient.user_id',
        backref=db.backref('user', foreign_keys='Patient.user_id'),
        uselist=False,
        cascade='all, delete-orphan'
    )
    doctor_profile = db.relationship(
        'Doctor',
        foreign_keys='Doctor.user_id',
        backref=db.backref('user', foreign_keys='Doctor.user_id'),
        uselist=False,
        cascade='all, delete-orphan'
    )
    asha_profile = db.relationship(
        'AshaWorker',
        foreign_keys='AshaWorker.user_id',
        backref=db.backref('user', foreign_keys='AshaWorker.user_id'),
        uselist=False,
        cascade='all, delete-orphan'
    )
    driver_profile = db.relationship(
        'Driver',
        foreign_keys='Driver.user_id',
        backref=db.backref('user', foreign_keys='Driver.user_id'),
        uselist=False,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# -------------------------------------------------------------------
# Hospital Model
# -------------------------------------------------------------------
class Hospital(db.Model):
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    emergency_phone = db.Column(db.String(20), nullable=True)
    location_text = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    specialties = db.relationship(
        'Specialty',
        secondary=hospital_specialties,
        backref=db.backref('hospitals', lazy='dynamic'),
        lazy='subquery'
    )

    doctors = db.relationship('Doctor', backref='hospital', lazy='dynamic')
    drivers = db.relationship('Driver', backref='hospital', lazy='dynamic')
    asha_workers = db.relationship('AshaWorker', backref='hospital', lazy='dynamic')

    def __repr__(self):
        return f"<Hospital {self.name}>"


# -------------------------------------------------------------------
# Patient Profile & Past Medical Reports
# -------------------------------------------------------------------
class Patient(db.Model):
    __tablename__ = 'patients'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    emergency_contact = db.Column(db.String(15), nullable=True)
    assigned_asha_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    assigned_asha = db.relationship('User', foreign_keys=[assigned_asha_id], backref='assigned_patients')
    reports = db.relationship('PatientReport', backref='patient', cascade='all, delete-orphan')

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __repr__(self):
        return f"<Patient UserID:{self.user_id} DOB:{self.date_of_birth}>"


class PatientReport(db.Model):
    __tablename__ = 'patient_reports'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.user_id', ondelete='CASCADE'), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(100), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    uploaded_by = db.relationship('User', foreign_keys=[uploaded_by_id])

    def __repr__(self):
        return f"<PatientReport {self.title} (Patient #{self.patient_id})>"


# -------------------------------------------------------------------
# Doctor, ASHA Worker, & Driver Profiles
# -------------------------------------------------------------------
class Doctor(db.Model):
    __tablename__ = 'doctors'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id', ondelete='SET NULL'), nullable=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id', ondelete='SET NULL'), nullable=True)
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    salary = db.Column(db.Float, nullable=True)
    consultation_fee = db.Column(db.Float, nullable=True)
    is_available = db.Column(db.Boolean, default=True, index=True)

    specialty = db.relationship('Specialty', backref='doctors')
    schedules = db.relationship('DoctorSchedule', backref='doctor', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Doctor UserID:{self.user_id} License:{self.license_number}>"


class DoctorSchedule(db.Model):
    __tablename__ = 'doctor_schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.user_id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.String(15), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"<DoctorSchedule Doctor:{self.doctor_id} {self.day_of_week} {self.start_time}-{self.end_time}>"


class AshaWorker(db.Model):
    __tablename__ = 'asha_workers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    assigned_hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id', ondelete='SET NULL'), nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    salary = db.Column(db.Float, nullable=True)
    work_shift = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<AshaWorker UserID:{self.user_id}>"


class Driver(db.Model):
    __tablename__ = 'drivers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id', ondelete='SET NULL'), nullable=True)
    vehicle_number = db.Column(db.String(50), nullable=False)
    license_number = db.Column(db.String(100), nullable=False)
    is_on_duty = db.Column(db.Boolean, default=False, index=True)
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Driver UserID:{self.user_id} Vehicle:{self.vehicle_number} OnDuty:{self.is_on_duty}>"