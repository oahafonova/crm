from flask import Blueprint, jsonify, request
from flasgger import swag_from
from app import db, Customer, Lead

api = Blueprint("api", __name__, url_prefix="/api")


# -------- Customers API --------

@api.route("/customers", methods=["GET"])
@swag_from({
    "tags": ["Customers"],
    "responses": {
        200: {
            "description": "Liste aller Kunden"
        }
    }
})
def get_customers():
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


@api.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):

    c = Customer.query.get_or_404(id)

    return jsonify({
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "company": c.company,
        "phone": c.phone,
        "status": c.status
    })


@api.route("/customers", methods=["POST"])
def create_customer():

    data = request.json

    c = Customer(
        name=data["name"],
        email=data["email"],
        company=data["company"],
        phone=data["phone"],
        status=data.get("status", "prospect")
    )

    db.session.add(c)
    db.session.commit()

    return jsonify({"message": "Customer created", "id": c.id}), 201


@api.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):

    c = Customer.query.get_or_404(id)
    data = request.json

    c.name = data.get("name", c.name)
    c.email = data.get("email", c.email)
    c.company = data.get("company", c.company)
    c.phone = data.get("phone", c.phone)
    c.status = data.get("status", c.status)

    db.session.commit()

    return jsonify({"message": "Customer updated"})


@api.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):

    c = Customer.query.get_or_404(id)

    db.session.delete(c)
    db.session.commit()

    return jsonify({"message": "Customer deleted"})


# -------- Leads API --------

@api.route("/leads", methods=["GET"])
def get_leads():

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


@api.route("/leads/<int:id>", methods=["GET"])
def get_lead(id):

    l = Lead.query.get_or_404(id)

    return jsonify({
        "id": l.id,
        "name": l.name,
        "email": l.email,
        "company": l.company,
        "value": l.value,
        "source": l.source
    })


@api.route("/leads", methods=["POST"])
def create_lead():

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

    return jsonify({"message": "Lead created", "id": l.id}), 201


@api.route("/leads/<int:id>", methods=["DELETE"])
def delete_lead(id):

    l = Lead.query.get_or_404(id)

    db.session.delete(l)
    db.session.commit()

    return jsonify({"message": "Lead deleted"})