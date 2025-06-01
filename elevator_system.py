# Elevator System Implementation
# This code simulates a multi-elevator system in a building with multiple floors.
# The system handles elevator requests, manages elevator movement, and tracks elevator states.
# Problem statement: https://codezym.com/question/11

from collections import defaultdict, deque

class Solution:
    """
    Main controller class for the elevator system that manages all lifts and user requests.
    Acts as the central coordinator between user requests and individual elevator operations.
    """
    def __init__(self):
        # Initialize basic system parameters
        self.floors_count = 0  # Total number of floors in the building
        self.lifts_count = 0   # Total number of lifts/elevators available
        self.lifts_capacity = 0  # Maximum capacity of each lift (number of people)
        self.helper = None  # Helper utility for output/logging (not used in this example)
        self.lifts = []  # List to store all lift objects

    def init(self, floors, lifts, lifts_capacity, helper):
        """
        Initializes the elevator system with the specified parameters.
        Args:
            floors (int): The number of floors in the building.
            lifts (int): The number of lifts in the system.
            lifts_capacity (int): The maximum number of people per lift.
            helper (Helper11): Helper class for printing and other actions.
        """
        self.floors_count = floors
        self.lifts_count = lifts
        self.lifts_capacity = lifts_capacity
        self.helper = helper
        # Create lift objects based on the specified count
        self.lifts = [Lift(floors, lifts_capacity) for _ in range(lifts)]
        # self.helper.println("Lift system initialized ...")

    def request_lift(self, floor, direction):
        """
        Handles a user pressing the UP or DOWN button outside the lift.
        This method finds the most optimal lift to send to the requested floor.
        
        Args:
            floor (int): The floor where the request is made.
            direction (str): The direction ('U' for up or 'D' for down).
        
        Returns:
            int: Index of the selected lift or -1 if no lift is available.
        """
        lift_index = -1  # Default to -1 (no lift available)
        time_taken = -1  # Initialize time with -1 (no valid time yet)
        
        # Iterate through all lifts to find the optimal one
        for i, lift in enumerate(self.lifts):
            # Get estimated time for this lift to reach the requested floor
            time = lift.get_time_to_reach_floor(floor, direction)
            
            # Skip this lift if it can't serve this request (-1) or is already at capacity
            if time < 0 or lift.count_people(floor, direction) >= self.lifts_capacity:
                continue
                
            # Select this lift if it's the first valid one or faster than previously selected
            if time_taken < 0 or time < time_taken:
                time_taken = time
                lift_index = i
                
        # If a suitable lift was found, add the request to that lift
        if lift_index >= 0:
            self.lifts[lift_index].add_incoming_request(floor, direction)
            
        return lift_index

    def press_floor_button_in_lift(self, lift_index, floor):
        """
        Simulates a user pressing a floor button inside the lift.
        This registers where the person inside the lift wants to go.
        
        Args:
            lift_index (int): Index of the lift.
            floor (int): The destination floor button pressed.
        """
        lift = self.lifts[lift_index]
        # Add the destination floor to the lift's outgoing requests
        # Using the lift's current direction since the passenger is already inside
        lift.add_outgoing_request(floor, lift.get_move_direction())

    def get_lift_state(self, lift_index):
        """
        Returns the current state of the lift as a formatted string.
        Format: "current_floor-direction-people_count"
        
        Args:
            lift_index (int): Index of the lift.
        
        Returns:
            str: String representation of the lift's state.
        """
        if lift_index < 0 or lift_index >= len(self.lifts):
            return ""  # Return empty string for invalid lift index
        lift = self.lifts[lift_index]
        return f"{lift.get_current_floor()}-{lift.get_move_direction()}-{lift.get_current_people_count()}"

    def tick(self):
        """
        Advances the system time by one second.
        This method is called every second to update all lift positions and states.
        """
        # Update each lift's state for the next time unit
        for lift in self.lifts:
            lift.tick()

class Lift:
    """
    Represents a single elevator in the system.
    Manages its own state, position, and passenger requests.
    Uses the State pattern to handle different movement behaviors.
    """
    def __init__(self, floors, capacity):
        self.current_floor = 0  # Start at ground floor
        self.floors = floors  # Total number of floors in the building
        self.capacity = capacity  # Maximum number of people this lift can carry
        
        # Track pickup requests (where people are waiting)
        self.incoming_requests_count = set()  # Floors where people are waiting
        
        # Track dropoff requests (where people inside want to go)
        # Key: floor number, Value: number of people going to that floor
        self.outgoing_requests_count = defaultdict(int)
        
        # Create state objects for the different possible states of the lift
        self.moving_up_state = MovingUpState(self)  # Moving upward normally
        self.moving_down_state = MovingDownState(self)  # Moving downward normally
        self.idle_state = IdleState(self)  # Not moving, waiting for requests
        self.moving_up_to_pick_first = MovingUpToPickFirstState(self)  # Going up to get first passenger
        self.moving_down_to_pick_first = MovingDownToPickFirstState(self)  # Going down to get first passenger
        
        # Start in idle state
        self.state = self.idle_state

    def get_current_people_count(self):
        """Returns total number of people currently in the lift"""
        # Sum all people going to various floors
        return sum(self.outgoing_requests_count.values())

    def get_time_to_reach_floor(self, floor, direction):
        """
        Estimates time (in ticks) for this lift to reach a specific floor.
        Delegates to the current state to calculate based on current movement pattern.
        
        Args:
            floor (int): Target floor
            direction (str): Requested direction ('U' or 'D')
            
        Returns:
            int: Estimated time units or -1 if lift cannot service this request
        """
        return self.state.get_time_to_reach_floor(floor, direction)

    def add_incoming_request(self, floor, direction):
        """
        Registers a pickup request (someone waiting at a floor).
        
        Args:
            floor (int): Floor where person is waiting
            direction (str): Direction they want to go ('U' or 'D')
        """
        # If lift is idle, determine new state based on request
        if self.state.get_direction() == 'I':
            if floor == self.current_floor:
                # Person is on the same floor, start moving in requested direction
                self.set_state(direction)
            else:
                # Need to move to pick up the person
                if floor > self.current_floor:
                    # Need to go up to reach person
                    # If they want to go up too, just move up; otherwise go up to pick them up first
                    self.state = self.moving_up_state if direction == 'U' else self.moving_up_to_pick_first
                else:
                    # Need to go down to reach person
                    # If they want to go down too, just move down; otherwise go down to pick them up first
                    self.state = self.moving_down_state if direction == 'D' else self.moving_down_to_pick_first
        
        # Add the floor to our pickup set
        self.incoming_requests_count.add(floor)

    def add_outgoing_request(self, floor, direction):
        """
        Registers a dropoff request (someone inside the lift wants to go to a floor).
        
        Args:
            floor (int): Destination floor
            direction (str): Current direction of travel ('U' or 'D')
        """
        # Increment the count of people going to this floor
        self.outgoing_requests_count[floor] += 1

    def count_people(self, floor, direction):
        """
        Counts the number of people who would be in the lift when it reaches the given floor.
        Used to check if the lift would be full.
        
        Args:
            floor (int): The floor to check
            direction (str): The direction of movement
            
        Returns:
            int: Number of people who would be in the lift
        """
        return self.state.count_people(floor, direction)

    def get_move_direction(self):
        """Returns current direction of movement: 'U' (up), 'D' (down), or 'I' (idle)"""
        return self.state.get_direction()

    def get_current_floor(self):
        """Returns the current floor number"""
        return self.current_floor

    def tick(self):
        """
        Advances the lift by one time unit.
        Delegates to the current state to handle movement logic.
        """
        # Let the current state handle the movement logic
        self.state.tick()
        
        # If no more requests, go to idle state
        if not self.outgoing_requests_count and not self.incoming_requests_count:
            self.set_state('I')

    def set_state(self, direction):
        """
        Changes the lift's state based on direction.
        
        Args:
            direction (str): 'U' for up, 'D' for down, 'I' for idle
        """
        if direction == 'U':
            self.state = self.moving_up_state
        elif direction == 'D':
            self.state = self.moving_down_state
        else:
            self.state = self.idle_state

    def set_current_floor(self, current_floor):
        """Updates the lift's current floor position"""
        self.current_floor = current_floor


class LiftState:
    """
    Base class for all lift states using the State pattern.
    Defines the interface for all concrete lift states.
    """
    def __init__(self, lift):
        self.lift = lift  # Reference to the lift this state belongs to

    def get_direction(self):
        """Returns the movement direction in this state"""
        return 'I'  # Default is idle

    def get_time_to_reach_floor(self, floor, direction):
        """Calculates time to reach a floor in this state"""
        return 0  # Default implementation

    def count_people(self, floor, direction):
        """Estimates people count at a specific floor"""
        return 0  # Default implementation

    def tick(self):
        """Handles one time unit of movement in this state"""
        pass  # Default does nothing


class MovingUpState(LiftState):
    """
    State representing a lift moving upward serving normal requests.
    The lift is already carrying passengers or responding to pickup requests above.
    """
    def get_direction(self):
        return 'U'  # Lift is moving up

    def get_time_to_reach_floor(self, floor, direction):
        """
        Calculate time to reach the requested floor when moving up.
        Only accepts UP requests from floors above the current position.
        
        Args:
            floor (int): Target floor
            direction (str): Requested direction ('U' or 'D')
            
        Returns:
            int: Time to reach or -1 if cannot service
        """
        # Only service UP requests from floors above current position
        if direction != 'U' or floor < self.lift.get_current_floor():
            return -1
        
        # Time equals number of floors to travel
        return floor - self.lift.get_current_floor()

    def count_people(self, floor, direction):
        """
        When moving up, count passengers going to floors above the requested floor.
        This helps determine if the lift would be full by the time it reaches the requested floor.
        """
        if direction != 'U':
            return 0
            
        # Count people going to floors above the target floor
        return sum(v for f, v in self.lift.outgoing_requests_count.items() if f > floor)

    def tick(self):
        """
        Handle one time unit of upward movement:
        1. Clear any pickup requests at current floor
        2. Move up one floor
        3. Drop off any passengers at the new floor
        """
        # Remove current floor from pickup requests
        self.lift.incoming_requests_count.discard(self.lift.get_current_floor())
        
        # Check if we should transition to idle
        if not self.lift.incoming_requests_count and not self.lift.outgoing_requests_count:
            return
            
        # Move up one floor
        self.lift.set_current_floor(self.lift.get_current_floor() + 1)
        
        # Drop off passengers at this floor (if any)
        self.lift.outgoing_requests_count.pop(self.lift.get_current_floor(), None)


class MovingDownState(LiftState):
    """
    State representing a lift moving downward serving normal requests.
    The lift is already carrying passengers or responding to pickup requests below.
    """
    def get_direction(self):
        return 'D'  # Lift is moving down

    def get_time_to_reach_floor(self, floor, direction):
        """
        Calculate time to reach the requested floor when moving down.
        Only accepts DOWN requests from floors below the current position.
        """
        # Only service DOWN requests from floors below current position
        if direction != 'D' or floor > self.lift.get_current_floor():
            return -1
            
        # Time equals number of floors to travel
        return self.lift.get_current_floor() - floor

    def count_people(self, floor, direction):
        """
        When moving down, count passengers going to floors below the requested floor.
        This helps determine if the lift would be full by the time it reaches the requested floor.
        """
        if direction != 'D':
            return 0
            
        # Count people going to floors below the target floor
        return sum(v for f, v in self.lift.outgoing_requests_count.items() if f < floor)

    def tick(self):
        """
        Handle one time unit of downward movement:
        1. Clear any pickup requests at current floor
        2. Move down one floor
        3. Drop off any passengers at the new floor
        """
        # Remove current floor from pickup requests
        self.lift.incoming_requests_count.discard(self.lift.get_current_floor())
        
        # Check if we should transition to idle
        if not self.lift.incoming_requests_count and not self.lift.outgoing_requests_count:
            return
            
        # Move down one floor
        self.lift.set_current_floor(self.lift.get_current_floor() - 1)
        
        # Drop off passengers at this floor (if any)
        self.lift.outgoing_requests_count.pop(self.lift.get_current_floor(), None)


class IdleState(LiftState):
    """
    State representing a lift that is not moving and waiting for requests.
    """
    def get_direction(self):
        return 'I'  # Lift is idle

    def get_time_to_reach_floor(self, floor, direction):
        """
        Calculate time to reach floor from idle state.
        An idle lift can accept any request and time is just the distance.
        """
        # Time is just the distance in floors (absolute difference)
        return abs(floor - self.lift.get_current_floor())


class MovingUpToPickFirstState(LiftState):
    """
    Special state when lift is moving up to pick up a passenger who wants to go down.
    This is a transitional state - the lift will switch to moving down once it picks up the passenger.
    """
    def get_direction(self):
        return 'U'  # Currently moving up

    def get_time_to_reach_floor(self, floor, direction):
        """
        Calculate time for a lift moving up to pick someone, then going back down.
        This is a more complex calculation because the lift will change direction.
        """
        next_stop = self.next_stop()  # Find highest floor with a pickup request
        
        # Only handle DOWN calls from floors at or below the next pickup
        if direction != 'D' or floor > next_stop:
            return -1

        # Compute total travel time in two legs:
        #  1) Leg-1: Rise from current floor up to the first pickup (next_stop)
        #  2) Leg-2: Then descend from next_stop back down to the caller's floor
        return (
            next_stop - self.lift.get_current_floor()  # Time to go up to highest pickup
            + next_stop - floor  # Time to come back down to requested floor
        )

    def next_stop(self):
        """Find the highest floor with a pickup request - that's where we're heading"""
        return max(self.lift.incoming_requests_count, default=-1)

    def tick(self):
        """
        Move up one floor, and if we've reached our target pickup floor,
        switch to moving down state (since we're picking up passengers going down).
        """
        # Move up one floor
        self.lift.set_current_floor(self.lift.get_current_floor() + 1)
        
        # If we've reached the highest pickup request, switch to moving down
        if self.lift.get_current_floor() == self.next_stop():
            self.lift.set_state('D')


class MovingDownToPickFirstState(LiftState):
    """
    Special state when lift is moving down to pick up a passenger who wants to go up.
    This is a transitional state - the lift will switch to moving up once it picks up the passenger.
    """
    def get_direction(self):
        return 'D'  # Currently moving down

    def get_time_to_reach_floor(self, floor, direction):
        """
        Calculate time for a lift moving down to pick someone, then going back up.
        This is a more complex calculation because the lift will change direction.
        """
        next_stop = self.next_stop()  # Find lowest floor with a pickup request
        
        # Only handle UP calls from floors at or above the next pickup
        if direction != 'U' or floor < next_stop:
            return -1
            
        if next_stop < 0:
            next_stop = floor
            
        # Calculate time: first go down to lowest pickup, then back up to requested floor
        return self.lift.get_current_floor() - next_stop + floor - next_stop

    def next_stop(self):
        """Find the lowest floor with a pickup request - that's where we're heading"""
        return min(self.lift.incoming_requests_count, default=-1)

    def tick(self):
        """
        Move down one floor, and if we've reached our target pickup floor,
        switch to moving up state (since we're picking up passengers going up).
        """
        # Move down one floor
        self.lift.set_current_floor(self.lift.get_current_floor() - 1)
        
        # If we've reached the lowest pickup request, switch to moving up
        if self.lift.get_current_floor() == self.next_stop():
            self.lift.set_state('U')


# Test code for the elevator system
if __name__ == "__main__":
    # Initialize the system with 6 floors, 2 lifts, 10 people capacity per lift
    sol = Solution()
    sol.init(floors=6, lifts=2, lifts_capacity=10, helper=None)
    print(f"System initialized: floors={sol.floors_count}, lifts={sol.lifts_count}")

    # Simulate a call from floor 5 going UP
    idx = sol.request_lift(5, "U")
    print(f"request_lift(5, 'U') returned lift: {idx}")

    # Display the current state of all lifts after the request
    print("Lift states after request:")
    for i in range(sol.lifts_count):
        lift = sol.lifts[i]
        print(f"  Lift {i}: floor={lift.get_current_floor()}, "
              f"dir={lift.get_move_direction()}, "
              f"people={lift.get_current_people_count()}, "
              f"incoming={sorted(lift.incoming_requests_count)}, "
              f"outgoing={dict(lift.outgoing_requests_count)}")

    # Simulate the system running for up to 5 time units
    target_floor = 5
    max_ticks = 5
    for t in range(1, max_ticks + 1):
        # Advance time by one unit
        sol.tick()
        
        # Display the updated state of all lifts
        print(f"\nAfter tick #{t}:")
        for i in range(sol.lifts_count):
            lift = sol.lifts[i]
            print(f"  Lift {i}: floor={lift.get_current_floor()}, "
                  f"dir={lift.get_move_direction()}, "
                  f"people={lift.get_current_people_count()}, "
                  f"incoming={sorted(lift.incoming_requests_count)}, "
                  f"outgoing={dict(lift.outgoing_requests_count)}")
                  
        # Stop simulation if any lift has reached the target floor
        if any(l.get_current_floor() == target_floor for l in sol.lifts):
            print(f"\n→ A lift reached floor {target_floor} on tick #{t}")
            break
