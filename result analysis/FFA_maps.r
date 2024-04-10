#######
#Change directory
#######
setwd(here())

#######
#source functions
#######
source('result analysis/map_functions.R')
source('result analysis/graph_functions.R')

#######
#Set Constants
#######
#Location must be part of config folder string

location = 'Cobb_GA'
config_folder ='Cobb_GA_no_bg_school_configs'

#some values for graph labeling
#county = gsub('.{3}$','',location)
#county_config_ = paste0(county, '_', 'config', '_')

#######
#Check that location and folders valid
#######

check_location_valid(location, config_folder)
check_config_folder_valid(config_folder)

#########
#Make maps and cartograms
#########
#set result folder
result_folder = paste(location, 'results', sep = '_')

#get all file names the result_folder with the strings config_folder and 'residence_distances'
res_dist_list = list.files(result_folder)[grepl('residence_distances', list.files(result_folder))]
res_dist_list = res_dist_list[grepl(config_folder, res_dist_list)]

#check if relevant directory exists
plot_folder = paste0('result analysis/', config_folder)
if (!file.exists(file.path(here(), plot_folder))){
    dir.create(file.path(here(), plot_folder))
}

#get avg distance bounds for maps
color_bounds <- distance_bounds(location, config_folder)

#Choosing not to do cartograms because of convergence difficulties
#sapply(res_dist_list, function(x)make_bg_maps(x, 'cartogram'))
sapply(res_dist_list, function(x)make_bg_maps(config_folder, x, 'map'))
sapply(res_dist_list, function(x)make_demo_dist_map(config_folder, x, 'black'))

