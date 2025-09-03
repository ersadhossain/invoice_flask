from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from weasyprint import HTML
import tempfile
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "your_secret_key_here"   # Required for CSRF protection in Flask-WTF

# --- Form Class ---
class InvoiceForm(FlaskForm):
    invoice_no = StringField("Invoice No", validators=[DataRequired()])
    invoice_date = DateField("Invoice Date", default=date.today, format='%Y-%m-%d')
    client_name = StringField("Client Name", validators=[DataRequired()])
    client_address = TextAreaField("Client Address", validators=[DataRequired()])
    client_gstin = StringField("Client GSTIN")
    subscription_period = StringField("Subscription Period", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired()])
    gst_percentage = DecimalField("GST %", default=18)
    razorpay_txn_id = StringField("Razorpay TXN ID")
    submit = SubmitField("Generate PDF")


# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def create_invoice():
    form = InvoiceForm()
    if form.validate_on_submit():
        invoice = form.data

        # Calculate GST & totals
        amount = float(invoice["amount"])
        gst_percentage = float(invoice["gst_percentage"])
        gst_amount = amount * gst_percentage / 100
        total_amount = amount + gst_amount

        html_string = render_template(
            "invoice_template.html",
            invoice=invoice,
            gst_amount=gst_amount,
            total_amount=total_amount,
            cgst=gst_amount / 2,
            sgst=gst_amount / 2,
        )

        # Generate temporary PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            HTML(string=html_string).write_pdf(tmp.name)
            tmp_path = tmp.name

        return send_file(tmp_path, as_attachment=True,
                         download_name=f"Invoice-{invoice['invoice_no']}.pdf")

    return render_template("create_invoice.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
