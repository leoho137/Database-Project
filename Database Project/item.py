from flask import Blueprint, request, render_template, flash
from flask_login import login_required
from db import get_db

# Define the Blueprint
bp = Blueprint('item', __name__, url_prefix='/item')

@bp.route('/find', methods=('GET', 'POST'))
@login_required
def find_item():
    if request.method == 'POST':
        item_id = request.form['itemID']
        print(f"Received itemID: {item_id}")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Query to find locations of all pieces of an item
        cursor.execute(
            "SELECT roomNum, shelfNum FROM Piece WHERE ItemID = %s", (item_id,)
        )
        pieces = cursor.fetchall()

        if pieces:
            return render_template('item/item_results.html', pieces=pieces)
        else:
            flash("No pieces found for the given Item ID.")
    return render_template('item/find_item.html')
