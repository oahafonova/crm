from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import Swagger, swag_from

# ---------------------- App Konfiguration ----------------------
app = Flask(__name__)
app.secret_key = "geheim"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy
db = SQLAlchemy(app)

# Swagger
swagger = Swagger(app)

# ---------------------- Datenbankmodelle ----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    value = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(120), nullable=False)

# ---------------------- Sample Data ----------------------
def init_sample_data():
    if not Customer.query.first():
        db.session.add(Customer(name='John Doe', email='john@example.com', company='Acme Corp', phone='555-0001', status='active'))
        db.session.add(Customer(name='Jane Smith', email='jane@example.com', company='Tech Solutions', phone='555-0002', status='prospect'))
        db.session.add(Customer(name='Bob Wilson', email='bob@example.com', company='Global Industries', phone='555-0003', status='inactive'))
        db.session.add(Lead(name='Alice Brown', email='alice@example.com', company='StartUp Inc', value=50000, source='Website'))
        db.session.add(Lead(name='Charlie Davis', email='charlie@example.com', company='Enterprise Ltd', value=100000, source='Referral'))
        db.session.commit()

with app.app_context():
    db.create_all()
    init_sample_data()

# ---------------------- Auth Routes ----------------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Benutzer existiert bereits!", "error")
            return redirect(url_for("register"))
        hashed_pw = generate_password_hash(password)
        db.session.add(User(username=username, password=hashed_pw))
        db.session.commit()
        flash("Registrierung erfolgreich!", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))
        else:
            flash("Ungültiger Benutzername oder Passwort!", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Du wurdest ausgeloggt.", "success")
    return redirect(url_for("login"))

# ---------------------- Index ----------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()
    leads = Lead.query.all()
    total_value = sum(l.value for l in leads)
    customers = Customer.query.all()
    status_counts = {}
    for c in customers:
        status_counts[c.status] = status_counts.get(c.status, 0) + 1
    source_counts = {}
    for l in leads:
        source_counts[l.source] = source_counts.get(l.source, 0) + 1
    return render_template(
        "index.html",
        total_customers=total_customers,
        total_leads=total_leads,
        status_counts=status_counts,
        source_counts=source_counts
    )
# ---------------------- Customers (HTML CRM) ----------------------
@app.route("/customers")
def customers():
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_customers = Customer.query.all()
    return render_template("customers.html", customers=all_customers)


@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer = Customer.query.get_or_404(customer_id)
    return render_template("customer_detail.html", customer=customer)


@app.route("/customers/add", methods=["GET","POST"])
def add_customer():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        customer = Customer(
            name=request.form.get("name"),
            email=request.form.get("email"),
            company=request.form.get("company"),
            phone=request.form.get("phone"),
            status=request.form.get("status","prospect")
        )

        db.session.add(customer)
        db.session.commit()

        flash("Customer hinzugefügt!", "success")
        return redirect(url_for("customers"))

    return render_template("add_customer.html")


@app.route("/customers/<int:customer_id>/edit", methods=["GET","POST"])
def edit_customer(customer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer = Customer.query.get_or_404(customer_id)

    if request.method == "POST":
        customer.name = request.form.get("name")
        customer.email = request.form.get("email")
        customer.company = request.form.get("company")
        customer.phone = request.form.get("phone")
        customer.status = request.form.get("status")

        db.session.commit()

        flash("Customer updated", "success")
        return redirect(url_for("customers"))

    return render_template("edit_customer.html", customer=customer)

@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer(customer_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    customer = Customer.query.get_or_404(customer_id)

    db.session.delete(customer)
    db.session.commit()

    flash("Customer gelöscht", "success")
    return redirect(url_for("customers"))

# ---------------------- Leads (HTML CRM) ----------------------

@app.route("/leads")
def leads():
    if "user_id" not in session:
        return redirect(url_for("login"))

    all_leads = Lead.query.all()
    return render_template("leads.html", leads=all_leads)


@app.route("/leads/<int:lead_id>")
def lead_detail(lead_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    lead = Lead.query.get_or_404(lead_id)
    return render_template("lead_detail.html", lead=lead)


@app.route("/leads/add", methods=["GET","POST"])
def add_lead():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        lead = Lead(
            name=request.form.get("name"),
            email=request.form.get("email"),
            company=request.form.get("company"),
            value=float(request.form.get("value")),
            source=request.form.get("source")
        )

        db.session.add(lead)
        db.session.commit()

        flash("Lead hinzugefügt!", "success")
        return redirect(url_for("leads"))

    return render_template("add_lead.html")


@app.route("/leads/<int:lead_id>/delete", methods=["POST"])
def delete_lead(lead_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    lead = Lead.query.get_or_404(lead_id)

    db.session.delete(lead)
    db.session.commit()

    flash("Lead gelöscht", "success")
    return redirect(url_for("leads"))

# ---------------------- API Routes ----------------------

@app.route("/api/customers", methods=["GET"])
def api_get_customers():
    """
    Get all customers
    ---
    tags:
      - Customers
    responses:
      200:
        description: Liste aller Kunden
        schema:
          type: array
          items:
            properties:
              id:
                type: integer
              name:
                type: string
              email:
                type: string
              company:
                type: string
              phone:
                type: string
              status:
                type: string
    """

    customers = Customer.query.all()

    result = []

    for c in customers:
        result.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "company": c.company,
            "phone": c.phone,
            "status": c.status
        })

    return jsonify(result)

@app.route("/api/customers", methods=["POST"])
def api_create_customer():
    """
    Create new customer
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            name:
              type: string
            email:
              type: string
            company:
              type: string
            phone:
              type: string
            status:
              type: string
    responses:
      201:
        description: Customer created
    """

    data = request.json

    c = Customer(
        name=data["name"],
        email=data["email"],
        company=data["company"],
        phone=data["phone"],
        status=data.get("status","prospect")
    )

    db.session.add(c)
    db.session.commit()

    return jsonify({"message":"customer created"}), 201

@app.route("/api/customers/<int:id>", methods=["GET"])
def api_get_customer(id):
    """
    Get customer by ID
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: Customer ID
    responses:
      200:
        description: Customer found
    """

    c = Customer.query.get_or_404(id)

    return jsonify({
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "company": c.company,
        "phone": c.phone,
        "status": c.status
    })
@app.route("/api/customers/<int:id>", methods=["PUT"])
def api_update_customer(id):
    """
    Update customer
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          properties:
            name:
              type: string
            email:
              type: string
            company:
              type: string
            phone:
              type: string
            status:
              type: string
    responses:
      200:
        description: Customer updated
    """

    c = Customer.query.get_or_404(id)
    data = request.json

    c.name = data.get("name", c.name)
    c.email = data.get("email", c.email)
    c.company = data.get("company", c.company)
    c.phone = data.get("phone", c.phone)
    c.status = data.get("status", c.status)

    db.session.commit()

    return jsonify({"message": "customer updated"})

@app.route("/api/customers/<int:id>", methods=["DELETE"])
def api_delete_customer(id):
    """
    Delete customer
    ---
    tags:
      - Customers
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted
    """

    c = Customer.query.get_or_404(id)

    db.session.delete(c)
    db.session.commit()

    return jsonify({"message": "customer deleted"})

# -------- LEADS API --------

@app.route("/api/leads", methods=["GET"])
def api_get_leads():
    """
    Get all leads
    ---
    tags:
      - Leads
    responses:
      200:
        description: Liste aller Leads
    """

    leads = Lead.query.all()

    result = []

    for l in leads:
        result.append({
            "id": l.id,
            "name": l.name,
            "email": l.email,
            "company": l.company,
            "value": l.value,
            "source": l.source
        })

    return jsonify(result)


@app.route("/api/leads/<int:id>", methods=["GET"])
def api_get_lead(id):

    l = Lead.query.get_or_404(id)

    return jsonify({
        "id":l.id,
        "name":l.name,
        "email":l.email,
        "company":l.company,
        "value":l.value,
        "source":l.source
    })

@app.route("/api/leads", methods=["POST"])
def api_create_lead():
    """
    Create new lead
    ---
    tags:
      - Leads
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            name:
              type: string
            email:
              type: string
            company:
              type: string
            value:
              type: number
            source:
              type: string
    responses:
      201:
        description: Lead created
    """

    data = request.json

    l = Lead(
        name=data["name"],
        email=data["email"],
        company=data["company"],
        value=data["value"],
        source=data["source"]
    )

    db.session.add(l)
    db.session.commit()

    return jsonify({"message": "lead created"}), 201
@app.route("/api/leads/<int:id>", methods=["PUT"])
def api_update_lead(id):
    """
    Update lead
    ---
    tags:
      - Leads
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          properties:
            name:
              type: string
            email:
              type: string
            company:
              type: string
            value:
              type: number
            source:
              type: string
    responses:
      200:
        description: Lead updated
    """

    l = Lead.query.get_or_404(id)
    data = request.json

    l.name = data.get("name", l.name)
    l.email = data.get("email", l.email)
    l.company = data.get("company", l.company)
    l.value = data.get("value", l.value)
    l.source = data.get("source", l.source)

    db.session.commit()

    return jsonify({"message": "lead updated"})

@app.route("/api/leads/<int:id>", methods=["DELETE"])
def api_delete_lead_api(id):
    """
    Delete lead
    ---
    tags:
      - Leads
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lead deleted
    """

    l = Lead.query.get_or_404(id)

    db.session.delete(l)
    db.session.commit()

    return jsonify({"message": "lead deleted"})

# ---------------------- Fehlerseiten ----------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500

# ---------------------- App starten ----------------------

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)