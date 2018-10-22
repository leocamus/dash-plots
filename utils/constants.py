import os

five_levels_up = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

travel_times_dir = os.path.join(five_levels_up, '02_datasets/02_travel_times')
