from flask import Blueprint, render_template, request, flash, redirect, url_for

reminders_bp = Blueprint('reminders', __name__, template_folder='templates')

@reminders_bp.route('/reminders', methods=['GET'])
def simulate():
    return render_template('reminders.html')

@reminders_bp.route('/reminders/send', methods=['POST'])
def send():
    channel = request.form['channel']
    message = request.form['message']
    # Just simulate (you could log or print instead)
    flash(f'Reminder simulated via {channel.upper()}: "{message}"', 'success')
    return redirect(url_for('reminders.simulate'))
