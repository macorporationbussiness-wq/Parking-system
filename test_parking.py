import unittest
from parking_lot import ParkingLot, Vehicle, ParkingSlot, HashTable
from datetime import datetime

class TestHashTable(unittest.TestCase):
    """Test cases for HashTable implementation"""
    
    def setUp(self):
        self.hash_table = HashTable(size=10)
    
    def test_insert_and_get(self):
        """Test inserting and retrieving values"""
        self.hash_table.insert("ABC123", {"slot": 1})
        result = self.hash_table.get("ABC123")
        self.assertEqual(result, {"slot": 1})
    
    def test_insert_duplicate(self):
        """Test updating existing key"""
        self.hash_table.insert("ABC123", {"slot": 1})
        self.hash_table.insert("ABC123", {"slot": 2})
        result = self.hash_table.get("ABC123")
        self.assertEqual(result, {"slot": 2})
    
    def test_get_nonexistent(self):
        """Test getting non-existent key"""
        result = self.hash_table.get("NONEXISTENT")
        self.assertIsNone(result)
    
    def test_delete(self):
        """Test deleting key-value pair"""
        self.hash_table.insert("ABC123", {"slot": 1})
        self.assertTrue(self.hash_table.delete("ABC123"))
        self.assertIsNone(self.hash_table.get("ABC123"))
    
    def test_delete_nonexistent(self):
        """Test deleting non-existent key"""
        self.assertFalse(self.hash_table.delete("NONEXISTENT"))
    
    def test_contains(self):
        """Test contains method"""
        self.hash_table.insert("ABC123", {"slot": 1})
        self.assertTrue(self.hash_table.contains("ABC123"))
        self.assertFalse(self.hash_table.contains("NONEXISTENT"))
    
    def test_load_factor(self):
        """Test load factor calculation"""
        self.assertEqual(self.hash_table.load_factor(), 0)
        self.hash_table.insert("ABC123", {"slot": 1})
        self.assertEqual(self.hash_table.load_factor(), 0.1)
    
    def test_resize(self):
        """Test hash table resizing"""
        # Start with size 5
        small_table = HashTable(size=5)
        small_table.insert("key1", "value1")
        small_table.insert("key2", "value2")
        small_table.insert("key3", "value3")
        small_table.insert("key4", "value4")  # This should trigger resize
        
        self.assertGreater(small_table.size, 5)
        self.assertEqual(small_table.get("key1"), "value1")
        self.assertEqual(small_table.get("key4"), "value4")

class TestVehicle(unittest.TestCase):
    """Test cases for Vehicle class"""
    
    def test_vehicle_creation(self):
        """Test vehicle object creation"""
        vehicle = Vehicle("ABC123", "Car", "1234567890")
        self.assertEqual(vehicle.registration_number, "ABC123")
        self.assertEqual(vehicle.vehicle_type, "Car")
        self.assertEqual(vehicle.contact_number, "1234567890")
        self.assertIsInstance(vehicle.entry_time, datetime)
    
    def test_vehicle_uppercase(self):
        """Test registration number is converted to uppercase"""
        vehicle = Vehicle("abc123", "Car")
        self.assertEqual(vehicle.registration_number, "ABC123")
    
    def test_vehicle_to_dict(self):
        """Test vehicle serialization"""
        vehicle = Vehicle("ABC123", "Car", "1234567890")
        vehicle_dict = vehicle.to_dict()
        
        self.assertEqual(vehicle_dict['registration_number'], "ABC123")
        self.assertEqual(vehicle_dict['vehicle_type'], "Car")
        self.assertEqual(vehicle_dict['contact_number'], "1234567890")
        self.assertIn('entry_time', vehicle_dict)
    
    def test_vehicle_from_dict(self):
        """Test vehicle deserialization"""
        original_vehicle = Vehicle("ABC123", "Car", "1234567890")
        vehicle_dict = original_vehicle.to_dict()
        
        restored_vehicle = Vehicle.from_dict(vehicle_dict)
        self.assertEqual(restored_vehicle.registration_number, "ABC123")
        self.assertEqual(restored_vehicle.vehicle_type, "Car")
        self.assertEqual(restored_vehicle.contact_number, "1234567890")

class TestParkingSlot(unittest.TestCase):
    """Test cases for ParkingSlot class"""
    
    def setUp(self):
        self.slot = ParkingSlot(1, 1)
    
    def test_slot_creation(self):
        """Test parking slot creation"""
        self.assertEqual(self.slot.slot_number, 1)
        self.assertEqual(self.slot.floor, 1)
        self.assertEqual(self.slot.status, "free")
        self.assertIsNone(self.slot.vehicle)
        self.assertIsNone(self.slot.occupied_since)
    
    def test_occupy_slot(self):
        """Test occupying a slot"""
        vehicle = Vehicle("ABC123", "Car")
        result = self.slot.occupy(vehicle)
        
        self.assertTrue(result)
        self.assertEqual(self.slot.status, "occupied")
        self.assertEqual(self.slot.vehicle, vehicle)
        self.assertIsInstance(self.slot.occupied_since, datetime)
    
    def test_occupy_occupied_slot(self):
        """Test occupying already occupied slot"""
        vehicle1 = Vehicle("ABC123", "Car")
        vehicle2 = Vehicle("XYZ789", "Bike")
        
        self.slot.occupy(vehicle1)
        result = self.slot.occupy(vehicle2)
        
        self.assertFalse(result)
        self.assertEqual(self.slot.vehicle, vehicle1)  # Should still be first vehicle
    
    def test_free_slot(self):
        """Test freeing a slot"""
        vehicle = Vehicle("ABC123", "Car")
        self.slot.occupy(vehicle)
        freed_vehicle = self.slot.free()
        
        self.assertEqual(freed_vehicle, vehicle)
        self.assertEqual(self.slot.status, "free")
        self.assertIsNone(self.slot.vehicle)
        self.assertIsNone(self.slot.occupied_since)
    
    def test_free_already_free_slot(self):
        """Test freeing already free slot"""
        freed_vehicle = self.slot.free()
        self.assertIsNone(freed_vehicle)
    
    def test_slot_serialization(self):
        """Test slot serialization and deserialization"""
        vehicle = Vehicle("ABC123", "Car", "1234567890")
        self.slot.occupy(vehicle)
        
        slot_dict = self.slot.to_dict()
        restored_slot = ParkingSlot.from_dict(slot_dict)
        
        self.assertEqual(restored_slot.slot_number, 1)
        self.assertEqual(restored_slot.floor, 1)
        self.assertEqual(restored_slot.status, "occupied")
        self.assertEqual(restored_slot.vehicle.registration_number, "ABC123")

class TestParkingLot(unittest.TestCase):
    """Test cases for ParkingLot class"""
    
    def setUp(self):
        self.parking_lot = ParkingLot(total_slots=10)
    
    def test_parking_lot_initialization(self):
        """Test parking lot initialization"""
        self.assertEqual(self.parking_lot.total_slots, 10)
        self.assertEqual(len(self.parking_lot.slots), 10)
        self.assertEqual(len(self.parking_lot.free_slots), 10)
        self.assertEqual(self.parking_lot.free_slots, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    def test_allocate_slot_success(self):
        """Test successful slot allocation"""
        result = self.parking_lot.allocate_slot("ABC123", "Car", "1234567890")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['slot_number'], 1)
        self.assertTrue(self.parking_lot.vehicle_table.contains("ABC123"))
        self.assertEqual(len(self.parking_lot.free_slots), 9)
    
    def test_allocate_slot_duplicate(self):
        """Test allocating slot for already parked vehicle"""
        self.parking_lot.allocate_slot("ABC123", "Car")
        result = self.parking_lot.allocate_slot("ABC123", "Car")
        
        self.assertFalse(result['success'])
        self.assertIn("already parked", result['message'])
    
    def test_allocate_slot_full(self):
        """Test allocating when parking lot is full"""
        # Fill all slots
        for i in range(10):
            self.parking_lot.allocate_slot(f"CAR{i:03d}", "Car")
        
        result = self.parking_lot.allocate_slot("NEWCAR", "Car")
        self.assertFalse(result['success'])
        self.assertIn("full", result['message'])
    
    def test_remove_vehicle_success(self):
        """Test successful vehicle removal"""
        self.parking_lot.allocate_slot("ABC123", "Car")
        result = self.parking_lot.remove_vehicle("ABC123")
        
        self.assertTrue(result['success'])
        self.assertFalse(self.parking_lot.vehicle_table.contains("ABC123"))
        self.assertEqual(len(self.parking_lot.free_slots), 10)
    
    def test_remove_nonexistent_vehicle(self):
        """Test removing non-existent vehicle"""
        result = self.parking_lot.remove_vehicle("NONEXISTENT")
        
        self.assertFalse(result['success'])
        self.assertIn("not found", result['message'])
    
    def test_find_vehicle_by_registration(self):
        """Test finding vehicle by registration"""
        self.parking_lot.allocate_slot("ABC123", "Car", "1234567890")
        result = self.parking_lot.find_vehicle_by_registration("ABC123")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['registration_number'], "ABC123")
        self.assertEqual(result['slot_number'], 1)
        self.assertEqual(result['vehicle_type'], "Car")
        self.assertEqual(result['contact_number'], "1234567890")
    
    def test_find_nonexistent_vehicle(self):
        """Test finding non-existent vehicle"""
        result = self.parking_lot.find_vehicle_by_registration("NONEXISTENT")
        self.assertFalse(result['success'])
    
    def test_find_vehicle_by_slot(self):
        """Test finding vehicle by slot number"""
        self.parking_lot.allocate_slot("ABC123", "Car")
        result = self.parking_lot.find_vehicle_by_slot(1)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['registration_number'], "ABC123")
        self.assertEqual(result['slot_number'], 1)
    
    def test_find_vehicle_by_invalid_slot(self):
        """Test finding vehicle by invalid slot number"""
        result = self.parking_lot.find_vehicle_by_slot(100)
        self.assertFalse(result['success'])
    
    def test_find_vehicle_by_free_slot(self):
        """Test finding vehicle in free slot"""
        result = self.parking_lot.find_vehicle_by_slot(1)
        self.assertFalse(result['success'])
        self.assertIn("free", result['message'])
    
    def test_get_all_slots(self):
        """Test getting all slots information"""
        self.parking_lot.allocate_slot("ABC123", "Car")
        slots = self.parking_lot.get_all_slots()
        
        self.assertEqual(len(slots), 10)
        self.assertEqual(slots[0]['status'], 'occupied')
        self.assertEqual(slots[1]['status'], 'free')
    
    def test_get_statistics(self):
        """Test getting parking lot statistics"""
        self.parking_lot.allocate_slot("ABC123", "Car")
        self.parking_lot.allocate_slot("XYZ789", "Bike")
        
        stats = self.parking_lot.get_statistics()
        
        self.assertEqual(stats['total_slots'], 10)
        self.assertEqual(stats['occupied_slots'], 2)
        self.assertEqual(stats['free_slots'], 8)
        self.assertEqual(stats['utilization_percentage'], 20.0)
        self.assertEqual(stats['vehicle_type_distribution']['Car'], 1)
        self.assertEqual(stats['vehicle_type_distribution']['Bike'], 1)
    
    def test_serialization_deserialization(self):
        """Test parking lot serialization and deserialization"""
        # Add some vehicles
        self.parking_lot.allocate_slot("ABC123", "Car", "1111111111")
        self.parking_lot.allocate_slot("XYZ789", "Bike", "2222222222")
        
        # Serialize to dict
        parking_dict = self.parking_lot.to_dict()
        
        # Create new parking lot from dict
        new_parking_lot = ParkingLot.from_dict(parking_dict)
        
        # Verify data integrity
        self.assertEqual(new_parking_lot.total_slots, 10)
        self.assertEqual(len(new_parking_lot.slots), 10)
        self.assertEqual(len(new_parking_lot.free_slots), 8)
        
        # Verify vehicles are restored
        result1 = new_parking_lot.find_vehicle_by_registration("ABC123")
        result2 = new_parking_lot.find_vehicle_by_registration("XYZ789")
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertEqual(result1['contact_number'], "1111111111")
        self.assertEqual(result2['contact_number'], "2222222222")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_complete_workflow(self):
        """Test complete parking workflow"""
        parking_lot = ParkingLot(total_slots=5)
        
        # Allocate 3 vehicles
        result1 = parking_lot.allocate_slot("CAR001", "Car", "1111111111")
        result2 = parking_lot.allocate_slot("CAR002", "SUV", "2222222222")
        result3 = parking_lot.allocate_slot("BIKE01", "Bike", "3333333333")
        
        self.assertTrue(result1['success'])
        self.assertTrue(result2['success'])
        self.assertTrue(result3['success'])
        
        # Verify statistics
        stats = parking_lot.get_statistics()
        self.assertEqual(stats['occupied_slots'], 3)
        self.assertEqual(stats['free_slots'], 2)
        
        # Remove one vehicle
        remove_result = parking_lot.remove_vehicle("CAR002")
        self.assertTrue(remove_result['success'])
        
        # Verify updated statistics
        stats = parking_lot.get_statistics()
        self.assertEqual(stats['occupied_slots'], 2)
        self.assertEqual(stats['free_slots'], 3)
        
        # Allocate another vehicle
        result4 = parking_lot.allocate_slot("CAR003", "Car", "4444444444")
        self.assertTrue(result4['success'])
        
        # Final verification
        final_stats = parking_lot.get_statistics()
        self.assertEqual(final_stats['occupied_slots'], 3)
        self.assertEqual(final_stats['free_slots'], 2)

if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)