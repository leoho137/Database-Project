from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from db import get_db

bp = Blueprint('donation', __name__, url_prefix='/donation')

@bp.route('/accept', methods=('GET', 'POST'))
@login_required
def accept_donation():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Validate if the logged-in user has the 'staff' role
    cursor.execute(
        "SELECT 1 FROM Act WHERE userName = %s AND roleID = 'staff'",
        (current_user.username,)
    )
    is_staff = cursor.fetchone()

    if not is_staff:
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
        has_pieces = int(request.form['hasPieces'])  # Number of pieces (0 if no pieces)

        # Validate donor
        cursor.execute('SELECT * FROM Person WHERE userName = %s', (donor_id,))
        donor = cursor.fetchone()
        if donor is None:
            flash("Invalid donor ID.")
            return render_template('donation/accept_donation.html')

        try:
            # Insert item
            cursor.execute(
                "INSERT INTO Item (iDescription, color, material, mainCategory, subCategory, hasPieces) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (item_data['description'], item_data['color'], item_data['material'], item_data['mainCategory'],
                 item_data['subCategory'], has_pieces)
            )
            item_id = cursor.lastrowid

            # Insert pieces if applicable
            if has_pieces > 0:
                for i in range(1, has_pieces + 1):
                    piece_data = {
                        'pieceNum': i,
                        'pDescription': request.form[f'pDescription_{i}'],
                        'length': int(request.form[f'length_{i}']),
                        'width': int(request.form[f'width_{i}']),
                        'height': int(request.form[f'height_{i}']),
                        'roomNum': request.form[f'roomNum_{i}'],
                        'shelfNum': request.form[f'shelfNum_{i}'],
                        'pNotes': request.form[f'pNotes_{i}']
                    }
                    cursor.execute(
                        "INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (item_id, piece_data['pieceNum'], piece_data['pDescription'], piece_data['length'],
                         piece_data['width'], piece_data['height'], piece_data['roomNum'], piece_data['shelfNum'],
                         piece_data['pNotes'])
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
    return render_template('donation/accept_donation.html')
