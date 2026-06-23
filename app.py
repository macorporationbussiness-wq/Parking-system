from flask import Flask, render_template, request, jsonify, session, flash, redirect, url_for
from parking_lot import ParkingLot
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'parking_system_secret_key_2024_professional'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize parking lot
def initialize_parking_lot():
    """Initialize or retrieve parking lot from session"""
    if 'parking_lot' not in session:
        parking_lot = ParkingLot(total_slots=100)
        session['parking_lot'] = parking_lot.to_dict()
    return ParkingLot.from_dict(session['parking_lot'])

def save_parking_lot(parking_lot):
    """Save parking lot to session"""
    session['parking_lot'] = parking_lot.to_dict()
    session.modified = True

@app.route('/')
def index():
    """Main dashboard with animations and statistics"""
    try:
        parking_lot = initialize_parking_lot()
        stats = parking_lot.get_statistics()
        recent_activities = parking_lot.get_recent_activities()
        
        return render_template('index.html', 
                             stats=stats,
                             recent_activities=recent_activities,
                             current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('index.html', stats={}, recent_activities=[])

@app.route('/allocate', methods=['GET', 'POST'])
def allocate_slot():
    """Allocate parking slot to vehicle with enhanced validation"""
    parking_lot = initialize_parking_lot()
    message = None
    status = None
    allocated_slot = None
    
    if request.method == 'POST':
        try:
            reg_number = request.form.get('registration_number', '').strip().upper()
            vehicle_type = request.form.get('vehicle_type', 'Car')
            contact_number = request.form.get('contact_number', '').strip()
            
            # Enhanced validation
            if not reg_number:
                message = "❌ Registration number is required"
                status = 'error'
            elif len(reg_number) < 6:
                message = "❌ Registration number must be at least 6 characters"
                status = 'error'
            else:
                result = parking_lot.allocate_slot(reg_number, vehicle_type, contact_number)
                
                if result['success']:
                    allocated_slot = result['slot_number']
                    message = f"✅ Success! Vehicle {reg_number} allocated to Slot {allocated_slot}"
                    status = 'success'
                    save_parking_lot(parking_lot)
                else:
                    message = f"❌ Allocation failed: {result['message']}"
                    status = 'error'
                    
        except Exception as e:
            message = f"❌ System error: {str(e)}"
            status = 'error'
    
    return render_template('allocate.html', 
                         message=message, 
                         status=status, 
                         allocated_slot=allocated_slot)

@app.route('/remove', methods=['GET', 'POST'])
def remove_vehicle():
    """Remove vehicle from parking with confirmation"""
    parking_lot = initialize_parking_lot()
    message = None
    status = None
    removed_vehicle = None
    
    if request.method == 'POST':
        try:
            reg_number = request.form.get('registration_number', '').strip().upper()
            confirmation = request.form.get('confirmation', 'no')
            
            if not reg_number:
                message = "❌ Please enter registration number"
                status = 'error'
            else:
                # Check if vehicle exists first
                vehicle_info = parking_lot.find_vehicle_by_registration(reg_number)
                
                if not vehicle_info['success']:
                    message = f"❌ Vehicle {reg_number} not found in parking lot"
                    status = 'error'
                elif confirmation == 'no':
                    # Show confirmation page
                    return render_template('remove_confirm.html', 
                                         vehicle_info=vehicle_info,
                                         reg_number=reg_number)
                else:
                    # Proceed with removal
                    result = parking_lot.remove_vehicle(reg_number)
                    if result['success']:
                        removed_vehicle = reg_number
                        message = f"✅ Vehicle {reg_number} successfully removed from Slot {result['slot_number']}"
                        status = 'success'
                        save_parking_lot(parking_lot)
                    else:
                        message = f"❌ Removal failed: {result['message']}"
                        status = 'error'
                        
        except Exception as e:
            message = f"❌ System error: {str(e)}"
            status = 'error'
    
    return render_template('remove.html', 
                         message=message, 
                         status=status, 
                         removed_vehicle=removed_vehicle)

@app.route('/search', methods=['GET', 'POST'])
def search_vehicle():
    """Advanced search with multiple criteria"""
    parking_lot = initialize_parking_lot()
    results = None
    search_type = None
    query = None
    
    if request.method == 'POST':
        try:
            search_type = request.form.get('search_type', 'registration')
            query = request.form.get('query', '').strip().upper()
            
            if not query:
                flash('Please enter search criteria', 'warning')
            else:
                if search_type == 'registration':
                    results = parking_lot.find_vehicle_by_registration(query)
                elif search_type == 'slot':
                    try:
                        slot_num = int(query)
                        results = parking_lot.find_vehicle_by_slot(slot_num)
                    except ValueError:
                        results = {'success': False, 'message': 'Invalid slot number format'}
                elif search_type == 'contact':
                    results = parking_lot.find_vehicle_by_contact(query)
                
        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')
    
    return render_template('search.html', 
                         results=results, 
                         search_type=search_type, 
                         query=query)

@app.route('/display')
def display_slots():
    """Display all slots with filtering options"""
    parking_lot = initialize_parking_lot()
    
    # Get filter parameters
    filter_type = request.args.get('filter', 'all')
    floor_filter = request.args.get('floor', 'all')
    
    slots_data = parking_lot.get_all_slots()
    statistics = parking_lot.get_statistics()
    
    # Apply filters
    if filter_type == 'occupied':
        slots_data = [slot for slot in slots_data if slot['status'] == 'occupied']
    elif filter_type == 'free':
        slots_data = [slot for slot in slots_data if slot['status'] == 'free']
    
    if floor_filter != 'all':
        try:
            floor_num = int(floor_filter)
            slots_data = [slot for slot in slots_data if slot['floor'] == floor_num]
        except ValueError:
            pass
    
    return render_template('display.html', 
                         slots=slots_data,
                         statistics=statistics,
                         filter_type=filter_type,
                         floor_filter=floor_filter)

@app.route('/api/statistics')
def get_statistics():
    """API endpoint for real-time statistics"""
    try:
        parking_lot = initialize_parking_lot()
        return jsonify({
            'success': True,
            'data': parking_lot.get_statistics()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/slots')
def get_slots_api():
    """API endpoint for slots data"""
    try:
        parking_lot = initialize_parking_lot()
        slots_data = parking_lot.get_all_slots()
        return jsonify({
            'success': True,
            'data': slots_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/allocate', methods=['POST'])
def api_allocate_slot():
    """API endpoint for slot allocation"""
    try:
        data = request.get_json()
        parking_lot = initialize_parking_lot()
        
        result = parking_lot.allocate_slot(
            data.get('registration_number'),
            data.get('vehicle_type', 'Car'),
            data.get('contact_number')
        )
        
        if result['success']:
            save_parking_lot(parking_lot)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'System error: {str(e)}'
        }), 500

@app.route('/api/remove', methods=['POST'])
def api_remove_vehicle():
    """API endpoint for vehicle removal"""
    try:
        data = request.get_json()
        parking_lot = initialize_parking_lot()
        
        result = parking_lot.remove_vehicle(data.get('registration_number'))
        
        if result['success']:
            save_parking_lot(parking_lot)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'System error: {str(e)}'
        }), 500

@app.route('/reset')
def reset_system():
    """Reset parking lot (for testing)"""
    session.pop('parking_lot', None)
    flash('🔄 Parking system has been reset successfully!', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)