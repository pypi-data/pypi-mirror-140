#https://lambert-guillaume.medium.com/how-to-deploy-delta-neutral-liquidity-in-uniswap-or-why-euler-finance-is-a-game-changer-for-lps-1d91efe1e8ac
import pandas as pd

def amt_assets_from_range(num_asset1, orig_price_denom_asset2, lower_price_denom_asset2, upper_price_denom_asset2, target_pool_value):
    
    L = num_asset1 * ((orig_price_denom_asset2 ** 0.5) * (upper_price_denom_asset2 ** 0.5)) / ((upper_price_denom_asset2  ** 0.5) - (orig_price_denom_asset2 ** 0.5))
    num_asset2 = L * ((orig_price_denom_asset2 ** 0.5) - (lower_price_denom_asset2 ** 0.5))
    
    orig_value_asset_in_asset2 = num_asset1 * orig_price_denom_asset2 + num_asset2    
    scale_up_ratio =  target_pool_value/orig_value_asset_in_asset2
    
    scaled_num_asset1 = num_asset1 * scale_up_ratio
    scaled_num_asset2 = num_asset2 * scale_up_ratio

    scaled_value_asset_in_asset2 = scaled_num_asset1 * orig_price_denom_asset2 + scaled_num_asset2    
    
    dict_val = {
    "num_asset1" : num_asset1,
    "num_asset2" : num_asset2,
    "scaled_num_asset1" : scaled_num_asset1,
    "scaled_num_asset2" : scaled_num_asset2,    
    "orig_value_asset_in_asset2": orig_value_asset_in_asset2,
    "scaled_value_asset_in_asset2": scaled_value_asset_in_asset2
    }            
    
    return dict_val

def uniswap_v3_hedging_ratio_amt(lower_price_denom_asset2, upper_price_denom_asset2, value_asset_in_asset2, orig_price_denom_asset2):
    
    a = (upper_price_denom_asset2 /lower_price_denom_asset2) ** 0.25 - 1
    b = (upper_price_denom_asset2/lower_price_denom_asset2) ** 0.5 - 1
    
    hedge_ratio = a/b        
    
    hedge_num_asset1 = value_asset_in_asset2 * hedge_ratio / orig_price_denom_asset2
    
    dict_val = {
    "hedge_ratio" : hedge_ratio,
    "hedge_num_asset1" : hedge_num_asset1
    }  
    
    return dict_val

if __name__ == "__main__":   
    
    num_asset1 = 2
    orig_price_denom_asset2 = 2000  #Take this as current price
    lower_price_denom_asset2 = 1500
    upper_price_denom_asset2 = 2500
    target_pool_value = 20000 
    
    res = amt_assets_from_range(num_asset1, orig_price_denom_asset2, lower_price_denom_asset2, upper_price_denom_asset2, target_pool_value)    
    uniswap_v3_hedging_ratio_amt(lower_price_denom_asset2, upper_price_denom_asset2, res['scaled_value_asset_in_asset2'], orig_price_denom_asset2)    
    
    
    