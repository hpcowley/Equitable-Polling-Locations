for i in range(11, 31):
    with open(f'Gwinnett_GA_driving_no_bg_no_ed_{i}.yaml', 'w') as f:
        f.write(f"""# Constants for the optimization function
location: Gwinnett_GA
year:
    - '2020'
    - '2022'
bad_types: 
    - 'Elec Day School - Potential'
    - 'Elec Day Church - Potential'
    - 'Elec Day Other - Potential'
    - 'bg_centroid' 
beta: -2
time_limit: 360000 #100 hours minutes
capacity: 5

####Optional#####
precincts_open: {i}
max_min_mult: 5 #scalar >= 1
maxpctnew: 1 # in interval [0,1]
minpctold: .8 # in interval [0,1]
driving: True
""")
