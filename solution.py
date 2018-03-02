import numpy as np
import random as rd
def get_distance(
            loc_1,
            loc_2):
    try:
        return abs(loc_1[0] - loc_2[0]) + abs(loc_1[1] - loc_2[1])
    except:
        import pdb; pdb.set_trace()

def assign_ride(
            vehicle_list,
            ride_reward_list,
            current_step
):
    for vehicle, ride_reward in zip(vehicle_list, ride_reward_list):
        if ride_reward[0]._ride_free == False:
            raise ValueError('Ride can not be assign cz occupied')
        vehicle.set_dest(ride_reward[0].get_dest())
        vehicle.set_reward(ride_reward[1])
        vehicle.set_arrival_time(
                            current_step,
                            ride_reward[0].get_start(),
                            ride_reward[0].get_dest(),
                            ride_reward[0]._early_start
        )
        vehicle.set_occupied()
        vehicle.add_ride(ride_reward[0]._ride_id)
        ride_reward[0].set_occupied()

class Map(object):
    """docstring for Map."""
    def __init__(self,num_row, num_col):
        super(Map, self).__init__()
        self._num_row = num_row
        self._num_col = num_col

class Ride(object):
    """docstring for Ride."""
    def __init__(self,ridge, ride_id):
        super(Ride, self).__init__()
        self._start_row = ridge[0]
        self._start_col = ridge[1]
        self._dest_row = ridge[2]
        self._dest_col = ridge[3]
        self._early_start = ridge[4]
        self._late_finish = ridge[5]
        self._ride_id = ride_id

        self._ride_free = True

    def set_occupied(self):
        if self._ride_free == False:
            raise ValueError('Ride not free')
        else:
            self._ride_free = False
    def get_start(self):
        return (self._start_row, self._start_col)

    def get_dest(self):
        return (self._dest_row, self._dest_col)

    def compute_reward(
                    self,
                    ref_point,
                    current_step,
                    start_ontime_bonus
    ):
        time_to_customer = get_distance(
                                    self.get_start(),
                                    ref_point
        )
        time_ride = get_distance(
                                self.get_start(),
                                self.get_dest()
        )
        if time_to_customer + time_ride + current_step > self._late_finish:
            reward = 0
        else:
            reward = 0
            if current_step + time_to_customer == self._early_start:
                reward += start_ontime_bonus
            reward += time_ride
        return reward

class Rides(object):
    """docstring for Ridges."""
    def __init__(
                    self,
                    ride_list):
        super(Rides, self).__init__()
        self._ride_list = ride_list

    def compute_reward(
                self,
                ref_point,
                current_step,
                start_ontime_bonus
    ):
        ride_reward_list_ret = []
        for ride in self._ride_list:
            if ride._ride_free == False:
                continue
            reward = ride.compute_reward(
                ref_point,
                current_step,
                start_ontime_bonus
            )
            if reward > 0:
                ride_reward_list_ret.append((ride, reward))
        ride_reward_list_ret = sorted(
                                    ride_reward_list_ret,
                                    key=lambda x: x[1],
                                    reverse=True
        )
        return ride_reward_list_ret

class Vehicle(object):    #vehicle id(0 base), status, predif_arrive_time
    """docstring for Vehicle."""
    def __init__(self,vehicle_id):
        super(Vehicle, self).__init__()
        self._vehicle_id = vehicle_id
        self._vehicle_free = True

        self._loc = (0, 0)
        self._assined_ride = []

    def get_reward(self):
        return self._reward

    def add_ride(self, ride_idx):
        self._assined_ride.append(ride_idx)

    def free_vehicle(self):
        self._vehicle_free = True
        self._loc = self._dest

    def set_arrival_time(
                    self,
                    current_step,
                    start_pos,
                    dest,
                    early_start
    ):
        self._arrival_time = max(
                                current_step + get_distance(
                                                    self._loc,
                                                    start_pos
                                                    ),
                                early_start
        ) + get_distance(start_pos, dest)

    def set_dest(self, dest):
        self._dest = dest

    def set_reward(self, reward):
        self._reward = reward

    def set_occupied(self):
        if self._vehicle_free == False:
            raise ValueError('vehicle not free')
        else:
            self._vehicle_free = False
    def statue_check():
        if status:
            return True
        else:
            return False

    def cal_time():
        pass


class Fleet(object):
    """docstring for Fleet."""
    def __init__(self, vehicle_list):
        super(Fleet, self).__init__()
        self._vehicle_list = vehicle_list

    def if_any_vehicle_free(self, current_step):
        for vehicle in self._vehicle_list:
            if vehicle._arrival_time == current_step:
                return True
        return False


    def get_free_vehicle_idx(self, current_step):
        return [
                    vehicle_idx for vehicle_idx, _ in enumerate(self._vehicle_list) \
                        if self._vehicle_list[vehicle_idx]._arrival_time == current_step
                ]

    def free_vehicle(self, free_vehicle_idx):
        for vehicle_idx in free_vehicle_idx:
            self._vehicle_list[vehicle_idx].free_vehicle()

    def get_free_vehicle(self, free_vehicle_idx):
        free_vehicle_idx = rd.sample(free_vehicle_idx, len(free_vehicle_idx))
        free_vehicle_list = [
            self._vehicle_list[vehicle_idx] for vehicle_idx in free_vehicle_idx
        ]
        return free_vehicle_list


    def get_free_vehicle_total_reward(self, free_vehicle_idx):
        total_free_vehicle_reward = np.sum(
                [
                    self._vehicle_list[vehicle_idx].get_reward() \
                    for vehicle_idx in  free_vehicle_idx]
        )
        return total_free_vehicle_reward

class Simulator(object):
    """docstring for Simulator."""
    def __init__(
                        self,
                        road_map,
                        fleet,
                        rides,
                        start_ontime_bonus,
                        total_step
    ):
        super(Simulator, self).__init__()
        self._road_map = road_map
        self._fleet = fleet
        self._rides = rides

        self._start_ontime_bonus = start_ontime_bonus
        self._total_step = total_step

        self._current_step = 0

        self._reward = 0

    def _simulate_first_step(self):
        ride_reward_list = self._rides.compute_reward(
                                    ref_point=(0, 0),
                                    current_step=self._current_step,
                                    start_ontime_bonus=start_ontime_bonus
        )
        assign_ride(
            self._fleet._vehicle_list,
            ride_reward_list[:len(self._fleet._vehicle_list)],
            self._current_step
        )
        reward = 0
        self._current_step += 1

    def _simulate_one_step(self):
        if self._current_step > self._total_step:
            print('Max current_step overcounted!')
        if self._fleet.if_any_vehicle_free(self._current_step):
            free_vehicle_idx = self._fleet.get_free_vehicle_idx(self._current_step)
            self._reward += self._fleet.get_free_vehicle_total_reward(free_vehicle_idx)
            self._fleet.free_vehicle(free_vehicle_idx)
            free_vehicle_list = self._fleet.get_free_vehicle(free_vehicle_idx) # should already random
            for free_vehicle in free_vehicle_list:

                ride_reward_list = self._rides.compute_reward(
                                free_vehicle._loc,
                                current_step=self._current_step,
                                start_ontime_bonus=start_ontime_bonus
                )
                if ride_reward_list == []:
                    return
                try:
                    assign_ride(
                        [free_vehicle],
                        [ride_reward_list[0]],
                        self._current_step
                    )
                except:
                    import pdb; pdb.set_trace()
        else:
            pass
        self._current_step += 1

    def simulate(self):
        self._simulate_first_step()
        for i in range(self._total_step - 1):
            self._simulate_one_step()

    def get_total_reward(self):
        return self._reward

def init_schedule(path='Files_in/d_metropolis.in'):
    with open(path, 'r') as f:
        num_row, num_col, num_vehicle, num_ride, start_ontime_bonus, total_step = \
            [int(s) for s in f.readline().split(' ')]

        road_map = Map(num_row, num_col) # init road map

        vehicle_list = [Vehicle(vehicle_id) for vehicle_id in range(num_vehicle)]

        fleet = Fleet(vehicle_list)

        ride_list = []
        for ride_id in range(num_ride):
            ride_args = [int(s) for s in f.readline().split(' ')]
            ride_list.append(Ride(ride_args, ride_id))
        rides = Rides(ride_list)

    return road_map, fleet, rides, start_ontime_bonus, total_step

if __name__ == '__main__':
    road_map, fleet, ridges, start_ontime_bonus, total_step = \
                                                    init_schedule()
    simulator = Simulator(
                    road_map,
                    fleet,
                    ridges,
                    start_ontime_bonus,
                    total_step
    )

    simulator.simulate()

    print(simulator.get_total_reward())
