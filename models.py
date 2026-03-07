from extensions import db

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    company = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    status = db.Column(db.String(50))

    @classmethod
    def add_customer(cls, name, email, company, phone, status="prospect"):
        customer = cls(
            name=name,
            email=email,
            company=company,
            phone=phone,
            status=status
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    @classmethod
    def get_all_customers(cls):
        return cls.query.all()

    @classmethod
    def get_customer_by_id(cls, customer_id):
        return cls.query.get(customer_id)

    @classmethod
    def update_customer(cls, customer_id, name, email, company, phone, status):
        customer = cls.query.get(customer_id)
        if customer:
            customer.name = name
            customer.email = email
            customer.company = company
            customer.phone = phone
            customer.status = status
            db.session.commit()

    @classmethod
    def delete_customer(cls, customer_id):
        customer = cls.query.get(customer_id)
        if customer:
            db.session.delete(customer)
            db.session.commit()


class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    company = db.Column(db.String(120))
    value = db.Column(db.Float)
    source = db.Column(db.String(100))
    status = db.Column(db.String(50), default="new")

    @classmethod
    def add_lead(cls, name, email, company, value, source):
        lead = cls(
            name=name,
            email=email,
            company=company,
            value=value,
            source=source
        )
        db.session.add(lead)
        db.session.commit()
        return lead

    @classmethod
    def get_all_leads(cls):
        return cls.query.all()

    @classmethod
    def get_lead_by_id(cls, lead_id):
        return cls.query.get(lead_id)

    @classmethod
    def delete_lead(cls, lead_id):
        lead = cls.query.get(lead_id)
        if lead:
            db.session.delete(lead)
            db.session.commit()