import numpy as np
import pandas as pd
import os
import math

def incorporate_result(dist_df, model):
    '''Input: dist_df--the main data frame containing the data for model
              model -- the solved model
              model.matching -- pyo boolean variable for when a residence is matched to a precinct (res, prec):bool
    output: dataframe containing only the matched residences and precincts'''

    #turn matched solution into df
    matching_list= [(key[0], key[1], model.matching[key].value) for key in model.matching]
    matching_df = pd.DataFrame(matching_list, columns = ['id_orig', 'id_dest', 'matching'])

    #merge with dist_df
    result_df = pd.merge(dist_df, matching_df, on = ['id_orig', 'id_dest'])

    #keep only pairs that have been matched
    #if no matches, raise error
    if all(result_df['matching'].isnull()):
        raise ValueError('The model has no matched precincts')
    result_df = result_df.loc[result_df['matching'] ==1]
    return(result_df)

def demographic_domain_summary(result_df, domain):
    '''Input: result_df-- the distance an demographic population data for the matched residences and precincts
        domain-- ['id_dest', 'id_orig'] either the precinct of residence 
    Output: Calculate the average distances traveled by each demographic group that is assigned to each precinct or that lives in each residence.'''

    if domain not in ['id_dest', 'id_orig']:
        raise ValueError('domain much be in [id_dest, id_orig]')
    #Transform to get distance and population by demographic, destination pairs
    demographic_all = pd.melt(result_df[[domain, 'distance_m', 'population','white', 'black', 'native', 'asian', 'hispanic']], id_vars = [domain, 'distance_m'], value_vars = ['population','white', 'black', 'native', 'asian', 'hispanic'], var_name = 'demographic', value_name = 'demo_pop')

    #create a weighted distance column for people of each demographic
    demographic_all['weighted_dist'] = demographic_all['demo_pop']*demographic_all['distance_m']

    #calculate the total population of each demographic sent to each precinct
    demographic_pop = demographic_all[[domain, 'demographic', 'demo_pop']].groupby([domain, 'demographic']).agg('sum')

    #calculate the total distance traveled by each demographic group
    demographic_dist = demographic_all[[domain, 'demographic', 'weighted_dist']].groupby([domain, 'demographic']).agg('sum')

    #merge the datasets
    demographic_prec = pd.concat([demographic_dist, demographic_pop], axis = 1)

    #calculate the average distance
    demographic_prec['avg_dist'] =  demographic_prec['weighted_dist']/ demographic_prec['demo_pop']
    return demographic_prec

def demographic_summary(demographic_df, result_df, beta, alpha):
    '''Input: demographic_df-- the distance an demographic population data for the matched residences and precincts
    beta -- the inequality aversion factor
    alpha -- the data derived normalization factor
    Output: Calculate the average distances traveled by each demographic group.'''

    #calculate the total distance traveled by each demographic group
    demographic_dist = demographic_df['weighted_dist'].groupby('demographic').agg('sum')

    #calculate the total population of each demographic sent to each precinct
    demographic_population = demographic_df['demo_pop'].groupby('demographic').agg('sum')

    #merge the datasets
    demographic_summary = pd.concat([demographic_dist, demographic_population], axis = 1)

    #for base line comparison, or if config.beta ==0
    demographic_summary['avg_dist'] = demographic_summary['weighted_dist']/demographic_summary['demo_pop']

    if beta !=0: 
        #TODO: (DS) alpha be recalculated at this step for each
        #demographic group to get the y_ede?

        #add the distance_m column back in from dist_df
        #1) first make demographics a column, not an index
        demographic_by_res = demographic_df.reset_index(['demographic'])
        #2) set index for results to 'id_orig'
        distances = result_df[['id_orig', 'distance_m']].set_index('id_orig')
        #3) merge on id_orig (index for both)
        demographics = demographic_by_res.merge(distances, left_index = True, right_index = True, how = 'outer')

        #add in a KP factor column
        demographics['KP_factor'] =  math.e**(-beta*alpha*demographics['distance_m'])
        #calculate the summand for the objective function
        demographics['demo_res_obj_summand'] = demographics['demo_pop']*demographics['KP_factor']

        #compute the ede for each demographic group
        demographic_ede = demographics[['demographic','demo_res_obj_summand', 'demo_pop']].groupby('demographic').agg('sum')
        demographic_ede['avg_KP_weight'] =  demographic_ede.demo_res_obj_summand/demographic_ede.demo_pop
        demographic_ede['y_EDE'] = (-1/(beta * alpha))*np.log(demographic_ede['avg_KP_weight'])

        #merge the datasets
        demographic_summary = pd.concat([demographic_summary[['weighted_dist', 'avg_dist']], demographic_ede], axis = 1)
    return demographic_summary

def write_results(result_folder, run_prefix, result_df, demographic_prec, demographic_res, demographic_ede):
    '''Write result, demographic_prec, demographic_res and demographic_ede to file'''

    #check if the directory exists
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    result_file = f'{run_prefix}_result.csv'
    precinct_summary = f'{run_prefix}_precinct_distances.csv'
    residence_summary = f'{run_prefix}_residence_distances.csv'
    y_ede_summary = f'{run_prefix}_edes.csv'
    result_df.to_csv(os.path.join(result_folder, result_file), index = True)
    demographic_prec.to_csv(os.path.join(result_folder, precinct_summary), index = True)
    demographic_res.to_csv(os.path.join(result_folder, residence_summary), index = True)
    demographic_ede.to_csv(os.path.join(result_folder, y_ede_summary), index = True)
    return