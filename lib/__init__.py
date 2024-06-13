import sqlite3

CONN = sqlite3.connect('company.db')
CURSOR = CONN.cursor()

class DatabaseConnectionManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
            self.conn.close()

class Department:
    db_name = 'company.db'
    all = {}

    def __init__(self, name):
        self.name = name
        self.id = None

    def __repr__(self):
        return f"Department(id={self.id}, name={self.name})"

    @classmethod
    def create_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            ''')

    @classmethod
    def drop_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('DROP TABLE IF EXISTS departments')

    def save(self):
        with DatabaseConnectionManager(self.db_name) as cursor:
            if self.id is None:
                cursor.execute('''
                    INSERT INTO departments (name)
                    VALUES (?)
                ''', (self.name,))
                self.id = cursor.lastrowid
                Department.all[self.id] = self
            else:
                cursor.execute('''
                    UPDATE departments
                    SET name = ?
                    WHERE id = ?
                ''', (self.name, self.id))

    @classmethod
    def create(cls, name):
        department = cls(name)
        department.save()
        return department

    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            instance = cls.all[row[0]]
        else:
            instance = cls(row[1])
            instance.id = row[0]
            cls.all[instance.id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM departments WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return cls.instance_from_db(row)
            else:
                return None

    @classmethod
    def find_by_name(cls, name):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM departments WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return cls.instance_from_db(row)
            else:
                return None

    def update(self):
        if self.id is not None:
            self.save()

    def delete(self):
        if self.id is not None:
            with DatabaseConnectionManager(self.db_name) as cursor:
                cursor.execute('DELETE FROM departments WHERE id = ?', (self.id,))
                del Department.all[self.id]
                self.id = None

    @classmethod
    def get_all(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM departments')
            rows = cursor.fetchall()
            return [cls.instance_from_db(row) for row in rows]

class Employee:
    db_name = 'company.db'
    all = {}

    def __init__(self, name, job_title, department_id):
        self.name = name
        self.job_title = job_title
        self.department_id = department_id
        self.id = None

    def __repr__(self):
        return f"Employee(id={self.id}, name={self.name}, job_title={self.job_title}, department_id={self.department_id})"

    @classmethod
    def create_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    job_title TEXT,
                    department_id INTEGER,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            ''')

    @classmethod
    def drop_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('DROP TABLE IF EXISTS employees')

    def save(self):
        with DatabaseConnectionManager(self.db_name) as cursor:
            if self.id is None:
                cursor.execute('''
                    INSERT INTO employees (name, job_title, department_id)
                    VALUES (?, ?, ?)
                ''', (self.name, self.job_title, self.department_id))
                self.id = cursor.lastrowid
                Employee.all[self.id] = self
            else:
                cursor.execute('''
                    UPDATE employees
                    SET name = ?, job_title = ?, department_id = ?
                    WHERE id = ?
                ''', (self.name, self.job_title, self.department_id, self.id))

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            instance = cls.all[row[0]]
        else:
            instance = cls(row[1], row[2], row[3])
            instance.id = row[0]
            cls.all[instance.id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM employees WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return cls.instance_from_db(row)
            else:
                return None

    @classmethod
    def find_by_name(cls, name):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM employees WHERE name = ?', (name,))
            row = cursor.fetchone()
            if row:
                return cls.instance_from_db(row)
            else:
                return None

    def update(self):
        if self.id is not None:
            self.save()

    def delete(self):
        if self.id is not None:
            with DatabaseConnectionManager(self.db_name) as cursor:
                cursor.execute('DELETE FROM employees WHERE id = ?', (self.id,))
                del Employee.all[self.id]
                self.id = None

    @classmethod
    def get_all(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM employees')
            rows = cursor.fetchall()
            return [cls.instance_from_db(row) for row in rows]

def reviews(self):
    try:
        with DatabaseConnectionManager(self.db_name) as cursor:
            cursor.execute('SELECT * FROM reviews WHERE employee_id =?', (self.id,))
            rows = cursor.fetchall()
            if rows is None:
                print("No rows returned from query")
                return [] 
            return [Review.instance_from_db(row) for row in rows if row is not None]
    except Exception as e:
        print(f"Error in reviews method: {e}")
        return [] 


class Review:
    db_name = 'company.db'
    all = {}

    def __init__(self, year, summary, employee_id):
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
        self.id = None

    def __repr__(self):
        return f"Review(id={self.id}, year={self.year}, summary={self.summary}, employee_id={self.employee_id})"

    @classmethod
    def create_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY,
                    year INTEGER,
                    summary TEXT,
                    employee_id INTEGER,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            ''')

    @classmethod
    def drop_table(cls):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('DROP TABLE IF EXISTS reviews')

    def save(self):
        with DatabaseConnectionManager(self.db_name) as cursor:
            if self.id is None:
                cursor.execute('''
                    INSERT INTO reviews (year, summary, employee_id)
                    VALUES (?, ?, ?)
                ''', (self.year, self.summary, self.employee_id))
                self.id = cursor.lastrowid
                Review.all[self.id] = self
            else:
                cursor.execute('''
                    UPDATE reviews
                    SET year = ?, summary = ?, employee_id = ?
                    WHERE id = ?
                ''', (self.year, self.summary, self.employee_id, self.id))

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            instance = cls.all[row[0]]
        else:
            instance = cls(row[1], row[2], row[3])
            instance.id = row[0]
            cls.all[instance.id] = instance
        return instance

    @classmethod
    def find_by_id(cls, id):
        with DatabaseConnectionManager(cls.db_name) as cursor:
            cursor.execute('SELECT * FROM reviews WHERE id = ?', (id,))
            row = cursor.fetchone()
            if row:
                return cls.instance_from_db(row)
            else:
                return None

    def update(self):
        if self.id is not None:
            self.save()

    def delete(self):
        if self.id is not None:
            with DatabaseConnectionManager(self.db_name) as cursor:
                cursor.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
                del Review.all[self.id]
                self.id = None


   
