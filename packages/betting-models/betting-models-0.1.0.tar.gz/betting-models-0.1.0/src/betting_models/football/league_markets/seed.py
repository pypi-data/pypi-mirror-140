'''Dispatch match markets seeding model'''

from json import dumps

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from betting_models.core.allocation import Allocator


class FootballFTRLeagueGenerator:
    def __init__(self):
        pass
    
    def _json_encode(self, matchids, leagueid, seeds):
        'Convert seed allocation array into json'
        packet = {}
        packet['LeagueId'] = leagueid
        packet['Lines'] = []
        
        # Loop through all non-zero betting combinations
        lines = np.where(seeds > 0)
        for i in range(lines[0].shape[0]):    
            outcomes = tuple(j[i] for j in lines)
            value = int(seeds[outcomes])  # int required for json encoder
            # Map outcomes to WKW input
            WKW_map = {0:1, 1:0, 2:2}
            WKW_outcomes = list(outcomes)
            WKW_outcomes = tuple(map(WKW_map.get, WKW_outcomes))
            
            zipped = zip(matchids, WKW_outcomes)
            
            line = {}
            line['Predictions'] = []
            line['NumberOfBets'] = value
            
            # For each match bet in line, extract matchid and outcome
            for matchid, WKW_outcome in zipped:
                event = {}
                event['MatchId'] = matchid
                event['Prediction'] = int(WKW_outcome)
                line['Predictions'].append(event)
            # For each betting combination add a line
            packet['Lines'].append(line)
        # JSON encode output
        json = dumps(packet)
        return json
    
    def _implied_2_tensor(self, implied_probs):
        'Converts implied probabilities list of arrays to n-dimensional tensor'
        implied_tensor = 1
        for T in implied_probs:
            implied_tensor = np.tensordot(implied_tensor, T, axes=0)
        return implied_tensor

    def _plot_allocation(self, df):        
        'Plot betting allocation vs implied probability of outcomes'
        fig, ax = plt.subplots()
        for col in df.columns:    
            ax.plot(df.index,
                    df[col],
                    label=col,
                    #color='blue',
                    #alpha=1
                    )
            ax.legend()
            ax.set_title('Seed allocation')
        return fig

    def print_status(self, prob_list, seeds):
        'Visualises status of seed given batch split, outcome probas etc...'
        n_seeds = np.sum(seeds)
        
        # Plot relative allocation
        seed_alloc = seeds / n_seeds
        implied_probs_tensor = self._implied_2_tensor(prob_list)
        seed_alloc = seed_alloc.reshape((-1,1))
        implied_probs_tensor = implied_probs_tensor.reshape((-1,1))
        data = (implied_probs_tensor, seed_alloc)
        zipped = np.concatenate(data, axis=1)
        
        cols = ['implied_probability', 'seed_allocation']
        allocation_df = pd.DataFrame(zipped, columns=cols)
        allocation_df.sort_values('implied_probability', ascending=False, inplace=True)
        allocation_df.reset_index(drop=True, inplace=True)
        fig = self._plot_allocation(allocation_df)  # return your plot as compatible data
        
        # Info printouts
        #print(f'Total seeds: {n_seeds}')
        #print(f'Max seeding bet: {max_seed}')
        return fig

    def decimal_2_probs(self, decimal_odds_arr):
        probs_arr = 1 / decimal_odds_arr
        normed_probs_arr = probs_arr / np.sum(probs_arr)
        return normed_probs_arr

    def run(
        self,
        n_seeds, 
        tol, 
        odds_list,
        matchids, 
        leagueid, 
        random_seed=False
    ):
        'Add first seeding batch to league'
        prob_list = list(map(self.decimal_2_probs, odds_list))

        alloc = Allocator(n_seeds, tol)
        # Get tailed seed bets if random seed specified, otherwise vanilla
        if random_seed:
            _, _, seeds = alloc.gen_tailed_seeds(prob_list, random_seed=random_seed)
        else:
            _, _, seeds = alloc.gen_vanilla_seeds(prob_list)
        json = self._json_encode(matchids, leagueid, seeds)
        fig = self.print_status(prob_list, seeds)
        return json, fig
