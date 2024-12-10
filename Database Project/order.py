from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_login import login_required, current_user
from db import get_db

bp = Blueprint('order', __name__, url_prefix='/order')

@bp.route('/find', methods=('GET', 'POST'))
@login_required
def find_order():
    if request.method == 'POST':
        order_id = request.form['orderID']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT i.ItemID, i.iDescription, p.roomNum, p.shelfNum 
            FROM Item i
            JOIN ItemIn ii ON i.ItemID = ii.ItemID
            JOIN Piece p ON i.ItemID = p.ItemID
            WHERE ii.orderID = %s
            """,
            (order_id,)
        )
        items = cursor.fetchall()
        if items:
            return render_template('order/order_results.html', items=items)
        else:
            flash("No items found for the given Order ID.")
    return render_template('order/find_order.html')

@bp.route('/start', methods=('GET', 'POST'))
@login_required
def start_order():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Check if the logged-in user is a staff member
    cursor.execute(
        "SELECT 1 FROM Act WHERE userName = %s AND roleID = 'staff'",
        (current_user.username,)
    )
    is_staff = cursor.fetchone()

    if not is_staff:
        flash("Only staff members can start orders.")
        return redirect(url_for('order.find_order'))

    if request.method == 'POST':
        client_username = request.form['clientUsername']

        # Check if the client exists
        cursor.execute("SELECT * FROM Person WHERE userName = %s", (client_username,))
        client = cursor.fetchone()

        if not client:
            flash("Client username not found.")
            return render_template('order/start_order.html')

        # Assign a new order ID
        try:
            cursor.execute(
                "INSERT INTO Ordered (orderDate, supervisor, client) VALUES (CURDATE(), %s, %s)",
                (current_user.username, client_username)
            )
            order_id = cursor.lastrowid
            db.commit()

            # Store the order ID in the session
            session['order_id'] = order_id
            flash(f"Order started successfully. Order ID: {order_id}")
            return redirect(url_for('order.view_order', order_id=order_id))
        except Exception as e:
            db.rollback()
            flash(f"Error starting order: {e}")

    return render_template('order/start_order.html')


@bp.route('/view/<int:order_id>', methods=['GET'])
@login_required
def view_order(order_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT o.orderID, o.orderDate, o.supervisor, o.client, p.fname AS client_fname, p.lname AS client_lname 
        FROM Ordered o
        JOIN Person p ON o.client = p.userName
        WHERE o.orderID = %s
        """,
        (order_id,)
    )
    order_details = cursor.fetchone()

    if not order_details:
        flash("Order not found.")
        return redirect(url_for('order.find_order'))

    return render_template('order/view_order.html', order=order_details)

@bp.route('/add_to_order', methods=('GET', 'POST'))
@login_required
def add_to_order():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Validate if the logged-in user is a staff member
    cursor.execute(
        "SELECT 1 FROM Act WHERE userName = %s AND roleID = 'staff'",
        (current_user.username,)
    )
    is_staff = cursor.fetchone()

    if not is_staff:
        flash("Only staff members can add items to an order.")
        return redirect(url_for('order.start_order'))

    # Check if an order ID exists in the session
    order_id = session.get('order_id')
    if not order_id:
        flash("No active order. Please start an order first.")
        return redirect(url_for('order.start_order'))

    # Fetch main categories for the dropdown
    cursor.execute("SELECT DISTINCT mainCategory FROM Category")
    categories = cursor.fetchall()

    subcategories = []
    available_items = []
    if request.method == 'POST':
        # Fetch subcategories based on selected main category
        main_category = request.form['mainCategory']
        cursor.execute(
            "SELECT DISTINCT subCategory FROM Category WHERE mainCategory = %s",
            (main_category,)
        )
        subcategories = cursor.fetchall()

        # Fetch items based on selected category and subcategory
        if 'subCategory' in request.form:
            sub_category = request.form['subCategory']
            cursor.execute(
                """
                SELECT i.ItemID, i.iDescription, i.color, i.material
                FROM Item i
                LEFT JOIN ItemIn ii ON i.ItemID = ii.ItemID
                WHERE i.mainCategory = %s AND i.subCategory = %s AND ii.ItemID IS NULL
                """,
                (main_category, sub_category)
            )
            available_items = cursor.fetchall()

        # If an item is selected to add to the order
        if 'itemID' in request.form:
            item_id = request.form['itemID']
            try:
                cursor.execute(
                    "INSERT INTO ItemIn (ItemID, orderID, found) VALUES (%s, %s, FALSE)",
                    (item_id, order_id)
                )
                db.commit()
                flash("Item added to the order successfully.")
                return redirect(url_for('order.add_to_order'))
            except Exception as e:
                db.rollback()
                flash(f"Error adding item to the order: {e}")

    return render_template(
        'order/add_to_order.html',
        categories=categories,
        subcategories=subcategories,
        available_items=available_items,
        order_id=order_id
    )
