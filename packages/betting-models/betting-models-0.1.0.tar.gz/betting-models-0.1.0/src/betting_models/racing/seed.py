'''Dispatch racing markets seeding model'''

from json import dumps

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from betting_models.core.allocation import Allocator


class RacingGenerator:
    def __init__(self):
        pass
    
    def _json_encode(self, leagueid, raceids, runners, seeds):
        '''Convert seed allocation array into json
        
        Args:
        raceids (iter): Iterable of raceids
        runners (iter): Iterable of runners ordered by raceid
        seeds (np.array): Seeding bet allocation array
        '''
        packet = {}
        packet['LeagueId'] = leagueid
        packet['Lines'] = []
        
        # Loop through all non-zero betting combinations
        lines = np.where(seeds > 0)
        for i in range(lines[0].shape[0]):    
            outcomes = tuple(j[i] for j in lines)
            value = int(seeds[outcomes])  # int required for json encoder
            # Map predicted outcomes to ponies
            event_outcomes = list(outcomes)

            winners = [runners[race][outcome] for race, outcome in enumerate(event_outcomes)]
            zipped = zip(raceids, winners)
            
            line = {}
            line['Predictions'] = []
            line['NumberOfBets'] = value
            
            # For each match bet in line, extract matchid and outcome
            for matchid, winner in zipped:
                event = {}
                event['RaceId'] = matchid
                event['Prediction'] = winner
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
        leagueid,
        raceids, 
        runners, 
    ):
        'Add first seeding batch to league'
        prob_list = list(map(self.decimal_2_probs, odds_list))

        alloc = Allocator(n_seeds, tol)
        _, _, seeds = alloc.gen_vanilla_seeds(prob_list)
        json = self._json_encode(leagueid, raceids, runners, seeds)
        fig = self.print_status(prob_list, seeds)
        return json, fig
