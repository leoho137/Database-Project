from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import login_required, current_user
from .db import get_db

# Define the blueprint
donation_bp = Blueprint('donation', __name__, url_prefix='/donation')

@donation_bp.route('/accept', methods=('GET', 'POST'))
@login_required
def accept_donation():
    if 'staff' not in session.get('roles', []):
        flash("Only staff members can accept donations.")
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        donor_id = request.form['donorID']
        item_data = {
            'description': request.form['description'],
            'color': request.form['color'],
            'material': request.form['material'],
            'mainCategory': request.form['mainCategory'],
            'subCategory': request.form['subCategory']
        }
        location_data = {
            'roomNum': request.form['roomNum'],
            'shelfNum': request.form['shelfNum'],
        }
        db = get_db()
        cursor = db.cursor()

        # Validate donor
        cursor.execute('SELECT * FROM Person WHERE userName = %s', (donor_id,))
        donor = cursor.fetchone()
        if donor is None:
            flash("Invalid donor ID.")
            return render_template('donation/accept.html')

        # Insert item and related records
        try:
            cursor.execute(
                "INSERT INTO Item (iDescription, color, material, mainCategory, subCategory) "
                "VALUES (%s, %s, %s, %s, %s)",
                (item_data['description'], item_data['color'], item_data['material'], item_data['mainCategory'], item_data['subCategory'])
            )
            item_id = cursor.lastrowid

            # Insert Piece location
            cursor.execute(
                "INSERT INTO Piece (ItemID, roomNum, shelfNum) VALUES (%s, %s, %s)",
                (item_id, location_data['roomNum'], location_data['shelfNum'])
            )

            # Record donation
            cursor.execute(
                "INSERT INTO DonatedBy (ItemID, userName, donateDate) VALUES (%s, %s, CURDATE())",
                (item_id, donor_id)
            )
            db.commit()
            flash("Donation accepted successfully!")
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}")
    return render_template('donation/accept.html')
