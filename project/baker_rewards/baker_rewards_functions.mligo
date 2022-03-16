#include "../common/functions.mligo"

let rec calculate_rewards (data : provider_data) (current_counter : nat) (store : storage) : tez =
    if data.counter > current_counter then
        data.accumulated
    else
        let added_reward = 
            match Big_map.find_opt data.counter store.lqt_history with
            | None -> (failwith("no history counter") : tez)
            | Some history ->
                data.lqt_shares * history.total_fees / history.total_lqt
            in
        let new_data = { data with counter = data.counter + 1n; accumulated = data.accumulated + added_reward } in
        calculate_rewards new_data current_counter store