library(here)

#######
#Change directory
#######
setwd(here())

#######
#source functions
#######

source('result analysis/graph_functions.R')


#######
#Set Constants
#######
#Location must be part of config folder string

location = 'DeKalb_GA'
config_folder = 'DeKalb_GA_bg_penalized_no_school_configs'
FFA_poll_number  = 20 #the optimal number of polls that FFA is suggesting for this county

#######
#Location of original location results
#and other related constants
#######

original_locations = paste(location, 'original', 'configs', sep = '_')

#######
#Check that location and folders valid
#this also ensures that you are in the right folder to read data
#######

check_location_valid(location, config_folder)
check_config_folder_valid(config_folder)

#######
#Read in data
#Run this for each of the folders under consideration
#Recall, output of form: list(ede_df, precinct_df, residence_df, result_df)
#######
config_df_list <- read_result_data(config_folder, 'placement')
#config_ede_df<- config_df_list[[1]]
#config_precinct_df<- config_df_list[[2]]
#config_residence_df<- config_df_list[[3]]
#config_result_df<- config_df_list[[4]]

orig_df_list <- read_result_data(original_locations, 'placement')
#defined as above

#######
#Check result validity
#######

#This will return and descriptor case of inconsistency
bad_runs <- check_run_validity(rbind(config_df_list[[4]], orig_df_list[[4]]))

#remove any bad runs from the data
config_df_list <- lapply(config_df_list, function(x){x[!(descriptor %in% bad_runs), ]})

#######
#Plot data
#######
plot_folder = paste0('result analysis/', config_folder)
if (file.exists(file.path(here(), plot_folder))){
    setwd(file.path(here(), plot_folder))    
} else{
    dir.create(file.path(here(), plot_folder))
    setwd(file.path(here(), plot_folder))
}

#Plot the edes for all runs in config_folder by demographic
plot_demographic_edes(config_df_list[[1]])

#Plot the edes for all runs in original_location and equivalent optimization runs by demographic
plot_original_optimized(config_df_list[[1]], orig_df_list[[1]])

#Plot the edes for all runs in config_folder for the population as a whole
plot_population_edes(config_df_list[[1]])

#Plot which precincts are used for each number of polls
plot_precinct_persistence(config_df_list[[2]])

#Boxplots of the average distances traveled and the y_edes at each run in folder
plot_boxplots(config_df_list[[3]])

#Histgram of the original distributions and that for the desired number of polls
plot_orig_ideal_hist(orig_df_list[[3]], config_df_list[[3]], FFA_poll_number)

#if you want to compare config_folder runs to a different folder, this plots on a population level
#config_folder2 = 
#compare_configs(config_df_list[1], config_folder2)
