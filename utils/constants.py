import os

five_levels_up = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

waze_dir = os.path.join(five_levels_up, '02_datasets/02_waze')
