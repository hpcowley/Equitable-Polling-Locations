import Gwinnett_GA_configs.Gwinnett_config_original_2020 as config
import os
import warnings
from model_data import (build_source, clean_data, alpha_min)
from model_factory import polling_model_factory
from model_solver import solve_model
from model_results import (incorporate_result,demographic_domain_summary, demographic_summary,write_results,)

#check if source data avaible
source_file_name = config.location + '.csv'
source_path = os.path.join('datasets','polling', config.location, source_file_name)
if not os.path.exists(source_path):
    warnings.warn(f'File {source_path} not found. Creating it.')
    build_source(config.location)

#get main data frame
dist_df = clean_data(config.location, config.level, config.year)

#get alpha
alpha_df = clean_data(config.location, 'original', config.year)
    # TODO: (CR) I don't like having to call this twice like this. Need a better method
alpha  = alpha_min(alpha_df)

#build model
ea_model = polling_model_factory(dist_df, alpha, config)
print(f'model built. Solve for {config.time_limit} seconds')

#solve model
#TODO: (CR) this should probably be moved to a log file somewhere
solve_model(ea_model, config.time_limit)

#incorporate result into main dataframe
result_df = incorporate_result(dist_df, ea_model)

#calculate the new alpha given this assignment
alpha_new = alpha_min(result_df)

#calculate the average distances traveled by each demographic to the assigned precinct
demographic_prec = demographic_domain_summary(result_df, 'id_dest')

#calculate the average distances traveled by each demographic by residence
demographic_res = demographic_domain_summary(result_df, 'id_orig')

#calculate the average distances (and y_ede if beta !=0) traveled by each demographic
demographic_ede = demographic_summary(demographic_res, result_df,config.beta, alpha_new)

result_folder = f'{config.location}_results'
run_prefix = f'{config.location}_{config.year}_{config.level}_beta={config.beta}_min_old={config.minpctold}_max_new={config.maxpctnew}_num_locations={config.precincts_open}'

write_results(result_folder, run_prefix, result_df, demographic_prec, demographic_res, demographic_ede)

