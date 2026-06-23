import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any

class Vehicle:
    """Represents a vehicle in the parking system"""
    def __init__(self, registration_number: str, vehicle_type: str = "Car", contact_number: str = ""):
        self.registration_number = registration_number.upper()
        self.vehicle_type = vehicle_type
        self.contact_number = contact_number
        self.entry_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'contact_number': self.contact_number,
            'entry_time': self.entry_time.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vehicle':
        vehicle = cls(
            data['registration_number'],
            data.get('vehicle_type', 'Car'),
            data.get('contact_number', '')
        )
        vehicle.entry_time = datetime.fromisoformat(data['entry_time'])
        return vehicle
    
    def __repr__(self):
        return f"Vehicle({self.registration_number}, {self.vehicle_type})"

class ParkingSlot:
    """Represents a single parking slot"""
    def __init__(self, slot_number: int, floor: int = 1):
        self.slot_number = slot_number
        self.floor = floor
        self.status = "free"  # free, occupied
        self.vehicle: Optional[Vehicle] = None
        self.occupied_since: Optional[datetime] = None
    
    def occupy(self, vehicle: Vehicle) -> bool:
        """Occupy this slot with a vehicle"""
        if self.status == "occupied":
            return False
        self.status = "occupied"
        self.vehicle = vehicle
        self.occupied_since = datetime.now()
        return True
    
    def free(self) -> Optional[Vehicle]:
        """Free this slot and return the vehicle that was parked"""
        if self.status == "free":
            return None
        vehicle = self.vehicle
        self.status = "free"
        self.vehicle = None
        self.occupied_since = None
        return vehicle
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'slot_number': self.slot_number,
            'floor': self.floor,
            'status': self.status,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'occupied_since': self.occupied_since.isoformat() if self.occupied_since else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingSlot':
        slot = cls(data['slot_number'], data.get('floor', 1))
        slot.status = data['status']
        if data['vehicle']:
            slot.vehicle = Vehicle.from_dict(data['vehicle'])
            slot.occupied_since = datetime.fromisoformat(data['occupied_since']) if data['occupied_since'] else None
        return slot
    
    def __repr__(self):
        status = f"Occupied by {self.vehicle}" if self.status == "occupied" else "Free"
        return f"Slot({self.slot_number}, Floor {self.floor}, {status})"

class HashTable:
    """Custom Hash Table implementation for vehicle storage"""
    def __init__(self, size: int = 100):
        self.size = size
        self.table: List[List[tuple]] = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key: str) -> int:
        """Generate hash for a key using SHA-256"""
        return int(hashlib.sha256(key.encode()).hexdigest(), 16) % self.size
    
    def insert(self, key: str, value: Any) -> bool:
        """Insert a key-value pair into the hash table"""
        if self.load_factor() > 0.7:
            self._resize()
        
        index = self._hash(key)
        bucket = self.table[index]
        
        # Check if key already exists
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return True
        
        # Key doesn't exist, add new entry
        bucket.append((key, value))
        self.count += 1
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        index = self._hash(key)
        bucket = self.table[index]
        
        for k, v in bucket:
            if k == key:
                return v
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key-value pair"""
        index = self._hash(key)
        bucket = self.table[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.count -= 1
                return True
        return False
    
    def contains(self, key: str) -> bool:
        """Check if key exists in hash table"""
        return self.get(key) is not None
    
    def load_factor(self) -> float:
        """Calculate current load factor"""
        return self.count / self.size
    
    def _resize(self) -> None:
        """Resize the hash table when load factor is high"""
        new_size = self.size * 2
        new_table = [[] for _ in range(new_size)]
        
        # Rehash all entries
        for bucket in self.table:
            for key, value in bucket:
                new_index = self._hash(key) % new_size
                new_table[new_index].append((key, value))
        
        self.size = new_size
        self.table = new_table
    
    def get_all_entries(self) -> List[tuple]:
        """Get all key-value pairs in the hash table"""
        entries = []
        for bucket in self.table:
            entries.extend(bucket)
        return entries

class ParkingLot:
    """Main Parking Lot management system using Hash Table"""
    
    def __init__(self, total_slots: int = 100):
        self.total_slots = total_slots
        self.slots: List[ParkingSlot] = []
        self.vehicle_table = HashTable(size=total_slots * 2)  # Double size for better performance
        self.free_slots: List[int] = []
        self.activity_log: List[Dict] = []
        
        self._initialize_slots()
    
    def _initialize_slots(self) -> None:
        """Initialize all parking slots"""
        slots_per_floor = 20
        floor_number = 1
        
        for i in range(self.total_slots):
            slot_number = i + 1
            if slot_number > floor_number * slots_per_floor:
                floor_number += 1
            
            slot = ParkingSlot(slot_number, floor_number)
            self.slots.append(slot)
            self.free_slots.append(slot_number)
        
        # Sort free slots for optimal allocation
        self.free_slots.sort()
        self._log_activity("System initialized", f"Created {self.total_slots} parking slots")
    
    def allocate_slot(self, registration_number: str, vehicle_type: str = "Car", contact_number: str = "") -> Dict[str, Any]:
        """Allocate a parking slot to a vehicle"""
        # Check if vehicle is already parked
        if self.vehicle_table.contains(registration_number):
            return {
                'success': False,
                'message': f'Vehicle {registration_number} is already parked in the lot'
            }
        
        # Check if parking lot is full
        if not self.free_slots:
            return {
                'success': False,
                'message': 'Parking lot is full'
            }
        
        # Get the best available slot (lowest number)
        slot_number = self.free_slots.pop(0)
        slot = self.slots[slot_number - 1]
        
        # Create vehicle and occupy slot
        vehicle = Vehicle(registration_number, vehicle_type, contact_number)
        slot.occupy(vehicle)
        
        # Store in hash table (store as dict for JSON serialization)
        self.vehicle_table.insert(registration_number, {
            'slot_number': slot_number,
            'vehicle': vehicle.to_dict(),  # Store as dict, not object
            'floor': slot.floor
        })
        
        self._log_activity("Vehicle allocated", 
                          f"Vehicle {registration_number} allocated to Slot {slot_number}",
                          registration_number,
                          slot_number)
        
        return {
            'success': True,
            'slot_number': slot_number,
            'floor': slot.floor,
            'message': f'Vehicle allocated to Slot {slot_number} on Floor {slot.floor}'
        }
    
    def remove_vehicle(self, registration_number: str) -> Dict[str, Any]:
        """Remove a vehicle from the parking lot"""
        # Find vehicle in hash table
        vehicle_info = self.vehicle_table.get(registration_number)
        if not vehicle_info:
            return {
                'success': False,
                'message': f'Vehicle {registration_number} not found in parking lot'
            }
        
        slot_number = vehicle_info['slot_number']
        slot = self.slots[slot_number - 1]
        
        # Free the slot
        freed_vehicle = slot.free()
        
        # Remove from hash table
        self.vehicle_table.delete(registration_number)
        
        # Add slot back to free slots and maintain order
        self.free_slots.append(slot_number)
        self.free_slots.sort()
        
        self._log_activity("Vehicle removed", 
                          f"Vehicle {registration_number} removed from Slot {slot_number}",
                          registration_number,
                          slot_number)
        
        return {
            'success': True,
            'slot_number': slot_number,
            'message': f'Vehicle {registration_number} removed from Slot {slot_number}'
        }
    
    def find_vehicle_by_registration(self, registration_number: str) -> Dict[str, Any]:
        """Find vehicle by registration number using hash table"""
        vehicle_info = self.vehicle_table.get(registration_number)
        if not vehicle_info:
            return {
                'success': False,
                'message': f'Vehicle {registration_number} not found'
            }
        
        # Convert stored dict back to Vehicle object for processing
        vehicle_dict = vehicle_info['vehicle']
        vehicle = Vehicle.from_dict(vehicle_dict)
        
        slot = self.slots[vehicle_info['slot_number'] - 1]
        
        # Calculate parking duration
        duration = datetime.now() - vehicle.entry_time
        hours = duration.total_seconds() / 3600
        
        return {
            'success': True,
            'registration_number': registration_number,
            'slot_number': vehicle_info['slot_number'],
            'floor': vehicle_info['floor'],
            'vehicle_type': vehicle.vehicle_type,
            'contact_number': vehicle.contact_number,
            'entry_time': vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            'parking_duration_hours': round(hours, 2),
            'message': f'Vehicle found in Slot {vehicle_info["slot_number"]}'
        }
    
    def find_vehicle_by_slot(self, slot_number: int) -> Dict[str, Any]:
        """Find vehicle by slot number"""
        if slot_number < 1 or slot_number > self.total_slots:
            return {
                'success': False,
                'message': f'Invalid slot number. Must be between 1 and {self.total_slots}'
            }
        
        slot = self.slots[slot_number - 1]
        if slot.status != "occupied":
            return {
                'success': False,
                'message': f'Slot {slot_number} is free'
            }
        
        vehicle = slot.vehicle
        duration = datetime.now() - vehicle.entry_time
        hours = duration.total_seconds() / 3600
        
        return {
            'success': True,
            'slot_number': slot_number,
            'floor': slot.floor,
            'registration_number': vehicle.registration_number,
            'vehicle_type': vehicle.vehicle_type,
            'contact_number': vehicle.contact_number,
            'entry_time': vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
            'parking_duration_hours': round(hours, 2),
            'message': f'Slot {slot_number} occupied by {vehicle.registration_number}'
        }
    
    def find_vehicle_by_contact(self, contact_number: str) -> Dict[str, Any]:
        """Find vehicle by contact number"""
        for entry in self.vehicle_table.get_all_entries():
            key, vehicle_info = entry
            vehicle_dict = vehicle_info['vehicle']
            vehicle = Vehicle.from_dict(vehicle_dict)
            
            if vehicle.contact_number == contact_number:
                return self.find_vehicle_by_registration(vehicle.registration_number)
        
        return {
            'success': False,
            'message': f'No vehicle found with contact number {contact_number}'
        }
    
    def get_all_slots(self) -> List[Dict[str, Any]]:
        """Get status of all slots"""
        slots_data = []
        for slot in self.slots:
            slot_data = {
                'slot_number': slot.slot_number,
                'floor': slot.floor,
                'status': slot.status,
                'is_occupied': slot.status == 'occupied'
            }
            
            if slot.vehicle:
                duration = datetime.now() - slot.vehicle.entry_time
                hours = duration.total_seconds() / 3600
                
                slot_data.update({
                    'registration_number': slot.vehicle.registration_number,
                    'vehicle_type': slot.vehicle.vehicle_type,
                    'contact_number': slot.vehicle.contact_number,
                    'entry_time': slot.vehicle.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'parking_duration_hours': round(hours, 2)
                })
            
            slots_data.append(slot_data)
        
        return slots_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parking lot statistics"""
        occupied_count = self.vehicle_table.count
        free_count = self.total_slots - occupied_count
        utilization = (occupied_count / self.total_slots) * 100 if self.total_slots > 0 else 0
        
        # Vehicle type distribution
        vehicle_types = {}
        for entry in self.vehicle_table.get_all_entries():
            vehicle_info = entry[1]
            vehicle_dict = vehicle_info['vehicle']
            vehicle_type = vehicle_dict['vehicle_type']
            vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
        
        return {
            'total_slots': self.total_slots,
            'occupied_slots': occupied_count,
            'free_slots': free_count,
            'utilization_percentage': round(utilization, 2),
            'vehicle_type_distribution': vehicle_types,
            'hash_table_load_factor': round(self.vehicle_table.load_factor(), 4),
            'hash_table_size': self.vehicle_table.size,
            'hash_table_entries': self.vehicle_table.count
        }
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activities"""
        return self.activity_log[-limit:]
    
    def _log_activity(self, action: str, description: str, registration_number: str = "", slot_number: int = 0) -> None:
        """Log system activity"""
        activity = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': action,
            'description': description,
            'registration_number': registration_number,
            'slot_number': slot_number
        }
        self.activity_log.append(activity)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parking lot to dictionary for session storage"""
        return {
            'total_slots': self.total_slots,
            'slots': [slot.to_dict() for slot in self.slots],
            'free_slots': self.free_slots,
            'activity_log': self.activity_log,
            'vehicle_table_entries': [
                (key, value) for key, value in self.vehicle_table.get_all_entries()
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingLot':
        """Create parking lot from dictionary"""
        parking_lot = cls(data['total_slots'])
        
        # Rebuild slots
        parking_lot.slots = [ParkingSlot.from_dict(slot_data) for slot_data in data['slots']]
        parking_lot.free_slots = data['free_slots']
        parking_lot.activity_log = data['activity_log']
        
        # Rebuild hash table (entries are already stored as dicts)
        for key, value in data['vehicle_table_entries']:
            parking_lot.vehicle_table.insert(key, value)
        
        return parking_lot
    
    def __repr__(self):
        stats = self.get_statistics()
        return f"ParkingLot(Slots: {stats['occupied_slots']}/{stats['total_slots']} occupied, Utilization: {stats['utilization_percentage']}%)"