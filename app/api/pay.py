from bottle import (
    post,
    request,
    response,
    jinja2_template as template,
)

from app.models.user import (
    get_user,
)

from app.models.session import (
    logged_in,
)


@post('/pay')
@logged_in
def do_payment(db, session):
    session_id = request.forms.get("session_id")
    sender = get_user(db, session.get_username())
    recipient = db.execute(
        "SELECT * FROM users WHERE users.username='{}' LIMIT 1 OFFSET 0".format(
            request.forms.get('recipient')
        )
    ).fetchone()
    payment_amount = int(request.forms.get('amount'))
    error = None
    if (session_id is None):
        response.status = 401
        error = "No session id provided, you dirty CSRFer."
    elif (session_id != session.get_id()):
        response.status = 401
        error = "Incorrect session id, you dirty CSRFer."
    elif (sender.get_coins() < payment_amount):
        response.status = 400
        error = "Not enough funds."
    elif (payment_amount < 0):
        response.status = 400
        error = "Payment amount cannot be negative."
    elif (recipient is None):
        response.status = 400
        error = "Recipient {} does not exist.".format(request.forms.get('recipient'))
    elif (recipient['username'] == sender.username):
        response.status = 400
        error = "Cannot pay self."
    else:
        sender.debit_coins(payment_amount)
        db.execute(
            "UPDATE users SET coins={} WHERE users.username='{}'".format(
                recipient['coins'] + payment_amount, recipient['username']
            )
        )
    return template(
        "profile",
        user=sender,
        session_user=sender,
        payment_error=error,
    )
