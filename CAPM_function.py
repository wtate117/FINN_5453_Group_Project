# functions for CAPM model
from common_imports import datetime, relativedelta, date, np, yf, pdr
from date_utils import date_months_back, date_years_back

def get_investment_returns(stock_symbol, beta_timeframe, beta_interval):
    """
    Download historical closing prices and calculate monthly returns for a stock and market index.
    Parameters:
    - stock_symbol: The ticker symbol for the stock or market index
    - start_date: The start date for the historical data (YYYY-MM-DD).
    - end_date: The end date for the historical data (YYYY-MM-DD).

    Returns:
    a pandas df of the pct change of the ticker over the period
    """

    # By default we will find the 5 year monthly beta
    end_date, start_date = date_years_back(beta_timeframe)
    # Download historical data for the stock and market index
    stock_data = yf.download(stock_symbol, start=start_date, end=end_date, interval=beta_interval)
    # Calculate daily returns for the stock and market index
    stock_returns = stock_data['Close'].pct_change().dropna()
    return stock_returns


def calculate_beta(ticker, market_index, beta_timeframe = 5, beta_interval = '1mo'):
    """
    Calculate the beta of an investment using historical returns.

    Parameters:
    - ticker: A list or numpy array of the investment's historical returns.
    - market_index: A list or numpy array of the market's historical returns.

    Returns:
    - The beta of the investment.
    """
    # create the lists
    investment_returns = get_investment_returns(ticker, beta_timeframe, beta_interval)
    market_returns = get_investment_returns(market_index, beta_timeframe, beta_interval)
    # Calculate covariance between investment returns and market returns
    covariance = np.cov(investment_returns, market_returns)[0, 1]
    # Calculate variance of the market returns
    variance = np.var(market_returns)
    # Calculate beta
    beta = covariance / variance
    print(f'The {beta_timeframe} year {beta_interval} interval beta for {ticker} is: {beta: .2f}')
    return beta


# ret function to provide the return of a ticker over the supplied period
def ticker_return_over_period(ticker, start_date, end_date):
    # Download historical data for the ticker
    data = yf.download(ticker, start=start_date, end=end_date)

    # Calculate the return
    initial_price = data['Adj Close'].iloc[0]  # Price at the start of the period
    final_price = data['Adj Close'].iloc[-1]  # Price at the end of the period
    return_over_timeframe = (final_price / initial_price) - 1

    # Print the return
    print(f"The 1-year return of {ticker} from {start_date} to {end_date} was {return_over_timeframe:.2%}")

    return return_over_timeframe

# find the risk-free rate of return using 3 month treasury bill
def risk_free_rate_of_return():
    # Go back three months for the risk-free rate of return
    end_date, start_date = date_months_back(3)

    risk_free_ror_df = pdr.get_data_fred('DTB3', start_date, end_date)

    # Ensure there's at least one valid rate and convert the last available rate to decimal
    if not risk_free_ror_df.empty:
        risk_free_rate = risk_free_ror_df.iloc[-1, 0] / 100  # Convert to decimal
    else:
        print("Risk-free rate data is unavailable.")
        return 0.05
    print(f'rfrr: {risk_free_rate: .2%}')
    return risk_free_rate



def CAPM_Computation(ticker, start_date, end_date, market_index_symbol = 'SPY'):
    '''
        :param beta: sensitivity of the investment compared to the sensitivity of the market
            beta > 1 is more violatile than the market
        :param market_return: expected market return, the S&P is used over the same time horizon as the asset being looked at
        :param risk_free_ror: risk free return found using DTB3 which is a three month Treasure bill
        '''
    market_return = ticker_return_over_period(market_index_symbol, start_date, end_date)
    risk_free_ror = risk_free_rate_of_return()
    beta = calculate_beta(ticker, market_index_symbol, 5, '1mo')
    # Calculate the expected return
    expected_investment_return = risk_free_ror + beta * (market_return - risk_free_ror)

    # print(f'CAPM expects a return of {expected_investment_return: .2%} for {ticker}.')
    CAPM_string = f'CAPM expects a return of {expected_investment_return: .2%} for {ticker}.'
    print(CAPM_string)

    return expected_investment_return, market_return, risk_free_ror   #, beta, risk_free_ror


"""
market_index_symbol = 'SPY'  # Example market index (S&P 500) # ^GSPC is another option, DJI
end_date = datetime.now()
start_date = date(end_date.year - 5, end_date.month, end_date.day)

stock_symbol = 'AEYE'  # Example stock (Apple Inc.)
full_process = CAPM_Computation(stock_symbol, start_date, end_date, market_index_symbol)

print(f'The full process model expects a return of {full_process: .2%} for {stock_symbol}.')
"""