from flask import Flask, render_template, request, session, jsonify
from data import items

app = Flask(__name__)
app.secret_key = 'sklfjhkjsahdfkjasbfejhbajcbjhabf732q8db32o8c7bq2f8d7bdhq278dh872hdo23o78hdo7382hdq'  # Replace with a secure key in production

@app.route('/', methods=['GET'])
def index():
    # Initialize session data if not present
    session_reviewed = session.get('reviewed', [])
    session_learned = session.get('learned', [])

    total_items = len(items)
    reviewed_count = len(session_reviewed)
    learned_count = len(session_learned)

    reviewed_progress = int((reviewed_count / total_items) * 100) if total_items else 0
    learned_progress = int((learned_count / total_items) * 100) if total_items else 0

    return render_template('home.html', items=items, reviewed=session_reviewed,
                           learned=session_learned,
                           reviewed_progress=reviewed_progress,
                           learned_progress=learned_progress)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    item_id = str(data.get('item_id'))  # Ensure item_id is a string
    status_type = data.get('status_type')
    checked = data.get('checked')

    # Retrieve session data
    session_reviewed = session.get('reviewed', [])
    session_learned = session.get('learned', [])

    if status_type == 'reviewed':
        if checked:
            if item_id not in session_reviewed:
                session_reviewed.append(item_id)
        else:
            if item_id in session_reviewed:
                session_reviewed.remove(item_id)
        session['reviewed'] = session_reviewed
    elif status_type == 'learned':
        if checked:
            if item_id not in session_learned:
                session_learned.append(item_id)
        else:
            if item_id in session_learned:
                session_learned.remove(item_id)
        session['learned'] = session_learned

    # Force the session to recognize the modifications
    session.modified = True

    total_items = len(items)
    reviewed_count = len(session_reviewed)
    learned_count = len(session_learned)

    reviewed_progress = int((reviewed_count / total_items) * 100) if total_items else 0
    learned_progress = int((learned_count / total_items) * 100) if total_items else 0

    return jsonify({
        'reviewed_progress': reviewed_progress,
        'learned_progress': learned_progress
    })

if __name__ == '__main__':
    app.run(debug=True)