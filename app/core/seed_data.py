import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models.load import Load


def create_sample_loads():
    """Create sample load data for testing"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Sample loads data
        sample_loads = [
            {
                "load_id": "LOAD001",
                "origin": "Chicago, IL",
                "destination": "Dallas, TX",
                "pickup_datetime": datetime.now() + timedelta(days=1),
                "delivery_datetime": datetime.now() + timedelta(days=3),
                "equipment_type": "Dry Van",
                "loadboard_rate": 2100.00,
                "notes": "High value freight, requires experienced driver",
                "weight": 45000,
                "commodity_type": "Electronics",
                "num_of_pieces": 75,
                "miles": 925,
                "dimensions": "53ft trailer"
            },
            {
                "load_id": "LOAD002",
                "origin": "Los Angeles, CA",
                "destination": "Phoenix, AZ",
                "pickup_datetime": datetime.now() + timedelta(hours=12),
                "delivery_datetime": datetime.now() + timedelta(days=2),
                "equipment_type": "Flatbed",
                "loadboard_rate": 1800.00,
                "notes": "Construction materials, secure properly",
                "weight": 48000,
                "commodity_type": "Construction Materials",
                "num_of_pieces": 25,
                "miles": 370,
                "dimensions": "48ft flatbed"
            },
            {
                "load_id": "LOAD003",
                "origin": "Miami, FL",
                "destination": "Atlanta, GA",
                "pickup_datetime": datetime.now() + timedelta(days=2),
                "delivery_datetime": datetime.now() + timedelta(days=4),
                "equipment_type": "Reefer",
                "loadboard_rate": 2300.00,
                "notes": "Temperature controlled, food grade",
                "weight": 42000,
                "commodity_type": "Frozen Foods",
                "num_of_pieces": 120,
                "miles": 650,
                "dimensions": "53ft reefer"
            },
            {
                "load_id": "LOAD004",
                "origin": "Denver, CO",
                "destination": "Salt Lake City, UT",
                "pickup_datetime": datetime.now() + timedelta(hours=8),
                "delivery_datetime": datetime.now() + timedelta(days=1, hours=12),
                "equipment_type": "Dry Van",
                "loadboard_rate": 1600.00,
                "notes": "Standard freight, no special requirements",
                "weight": 38000,
                "commodity_type": "General Freight",
                "num_of_pieces": 50,
                "miles": 500,
                "dimensions": "53ft trailer"
            },
            {
                "load_id": "LOAD005",
                "origin": "Houston, TX",
                "destination": "New Orleans, LA",
                "pickup_datetime": datetime.now() + timedelta(days=1, hours=6),
                "delivery_datetime": datetime.now() + timedelta(days=2, hours=18),
                "equipment_type": "Tanker",
                "loadboard_rate": 2500.00,
                "notes": "Hazmat certified driver required",
                "weight": 50000,
                "commodity_type": "Chemicals",
                "num_of_pieces": 1,
                "miles": 350,
                "dimensions": "Tanker trailer"
            },
            {
                "load_id": "LOAD006",
                "origin": "Seattle, WA",
                "destination": "Portland, OR",
                "pickup_datetime": datetime.now() + timedelta(hours=6),
                "delivery_datetime": datetime.now() + timedelta(days=1),
                "equipment_type": "Dry Van",
                "loadboard_rate": 900.00,
                "notes": "Short haul, quick turnaround",
                "weight": 25000,
                "commodity_type": "Retail Goods",
                "num_of_pieces": 35,
                "miles": 173,
                "dimensions": "48ft trailer"
            },
            {
                "load_id": "LOAD007",
                "origin": "Nashville, TN",
                "destination": "Louisville, KY",
                "pickup_datetime": datetime.now() + timedelta(days=3),
                "delivery_datetime": datetime.now() + timedelta(days=4),
                "equipment_type": "Flatbed",
                "loadboard_rate": 1200.00,
                "notes": "Machinery transport, requires crane",
                "weight": 47000,
                "commodity_type": "Machinery",
                "num_of_pieces": 3,
                "miles": 175,
                "dimensions": "48ft flatbed"
            },
            {
                "load_id": "LOAD008",
                "origin": "Phoenix, AZ",
                "destination": "Las Vegas, NV",
                "pickup_datetime": datetime.now() + timedelta(hours=18),
                "delivery_datetime": datetime.now() + timedelta(days=2),
                "equipment_type": "Dry Van",
                "loadboard_rate": 1100.00,
                "notes": "Casino supplies, time sensitive",
                "weight": 30000,
                "commodity_type": "Entertainment Supplies",
                "num_of_pieces": 80,
                "miles": 295,
                "dimensions": "53ft trailer"
            }
        ]
        
        # Check if loads already exist to avoid duplicates
        existing_load_ids = {load.load_id for load in db.query(Load).all()}
        
        for load_data in sample_loads:
            if load_data["load_id"] not in existing_load_ids:
                load = Load(**load_data)
                db.add(load)
        
        db.commit()
        print(f"Successfully seeded {len([l for l in sample_loads if l['load_id'] not in existing_load_ids])} loads")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_loads() 