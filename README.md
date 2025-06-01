# Elevator System Implementation

A Python simulation of a multi-elevator system in a building.  
Uses the State pattern to manage elevator movement, pickups and drop-offs across multiple floors.

## Features

- Configurable number of floors and lifts  
- Per-lift capacity constraints  
- Handles external calls (UP/DOWN) and internal floor requests  
- State-based movement: Idle, Moving Up, Moving Down, Transitional pickup states  
- Time estimation for optimal lift selection  
- Simple text-based simulation via a `tick()` driver

## Code Structure

### Solution  
Central controller:  
- `init(floors, lifts, capacity, helper)`  
- `request_lift(floor, direction)` → best lift index or -1  
- `press_floor_button_in_lift(lift_index, floor)`  
- `get_lift_state(lift_index)` → e.g. `"3-U-2"` (floor-direction-passengerCount)  
- `tick()` → advance all lifts by one time unit  

### Lift  
Represents a single elevator:  
- Tracks `current_floor`, `incoming_requests_count`, `outgoing_requests_count`  
- Delegates movement logic to a `state` instance  

### LiftState and Concrete States  
Defines the state interface and behaviors:  
- `IdleState`  
- `MovingUpState`  
- `MovingDownState`  
- `MovingUpToPickFirstState` (transitional up → down)  
- `MovingDownToPickFirstState` (transitional down → up)  

Each state implements:  
- `get_direction()` → `'U'`, `'D'` or `'I'`  
- `get_time_to_reach_floor(floor, direction)` → estimated ticks or -1  
- `count_people(floor, direction)` → capacity check  
- `tick()` → move one floor, handle pickups/drop-offs, state transitions  

## Usage

1. Ensure Python 3 installed.  
2. Place `elevator_system.py` in your working directory.  
3. Run simulation:

   ```sh
   python elevator_system.py
   ```

4. Modify or extend the `if __name__ == "__main__":` block to simulate custom call/tick sequences.

## Example

```python
from elevator_system import Solution

sol = Solution()
sol.init(floors=6, lifts=2, lifts_capacity=10, helper=None)

# External call: floor 0 → UP
lift_id = sol.request_lift(0, "U")
print("Assigned Lift:", lift_id)

# Passenger enters and presses floor 5
sol.press_floor_button_in_lift(lift_id, 5)

# Simulate 5 time units
for t in range(5):
    sol.tick()
    print(sol.get_lift_state(lift_id))
```

## License

MIT License – feel free to use, modify, and extend.  
