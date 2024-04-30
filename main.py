from common_imports import pd, np, tk, ttk, messagebox, sco, plt, FigureCanvasTkAgg, yf, Figure, sm, go, sns, datetime, timedelta, mdates, FuncFormatter
import requests
from CAPM_function import CAPM_Computation
from date_utils import get_start_date

def add_ticker():
    ticker_symbol = ticker_entry.get().strip().upper()
    if not ticker_symbol:
        messagebox.showinfo("Error", "Ticker symbol cannot be empty.")
        return
    try:
        ticker_data = yf.Ticker(ticker_symbol)
        company_name = ticker_data.info.get('longName', 'N/A')
        if company_name != 'N/A' and ticker_symbol not in added_tickers:
            added_tickers[ticker_symbol] = company_name
            companies_listbox.insert(tk.END, f"{company_name} ({ticker_symbol})")
            ticker_entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Info", "Company already added or not found.")
    except Exception as e:
        messagebox.showinfo("Error", f"Failed to fetch data for {ticker_symbol}: {e}")

def remove_ticker():
    try:
        selection = companies_listbox.curselection()[0]
        ticker_symbol = companies_listbox.get(selection).split(' (')[-1][:-1]
        del added_tickers[ticker_symbol]
        companies_listbox.delete(selection)
    except IndexError:
        messagebox.showinfo("Error", "Please select a ticker to remove.")

def pegCalc(ticker):
    API_KEY = 'pk_25b93d888bab4fc28c85fff7f7cb2240'

    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}'

    response = requests.get(url)
    data = response.json()

    # Assuming the PEG ratio is directly available
    peg_ratio = data.get('PEGRatio', 'Data Not Available')

    if peg_ratio is None or not isinstance(peg_ratio, (str, float, int)) or not str(peg_ratio).replace('.', '', 1).isdigit():
        # Handle the case where PEG ratio is not available
        # Option 1: Return a default value, e.g., -1, to indicate unavailable data
        return -1 
    else:
        return float(peg_ratio)

def calculate_pb_ratio(ticker_symbol):
    ticker_data = yf.Ticker(ticker_symbol)
    pb_ratio = ticker_data.info.get('priceToBook', -1)
    return pb_ratio



def calculate_metric():
   
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Canvas):
            widget.destroy()

    metric = metric_combobox.get()
    selected_tickers = list(added_tickers.keys())
    print(selected_tickers)
    selected_timehorizon = time_horizon_var.get()


    if metric in ["P/E Ratio", "Beta"]:
        # Collect data for P/E Ratio and Beta
        values = []
        # tickers = list(added_tickers.keys())
        for ticker_symbol in selected_tickers:
            ticker_data = yf.Ticker(ticker_symbol)
            if metric == "P/E Ratio":
                value = ticker_data.info.get('forwardPE', 'N/A')
            elif metric == "Beta":
                value = ticker_data.info.get('beta', 'N/A')
            values.append(value if value != 'N/A' else 0)  # Replace 'N/A' with 0 for plotting

        # Benchmark values
        benchmark_value = 1.0 if metric == "Beta" else sum(values) / len(values) if values else 0

        # Plotting for P/E Ratio and Beta
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        ax.bar(selected_tickers, values, color='skyblue')
        ax.axhline(y=benchmark_value, color='r', linestyle='-', label='Benchmark')
        ax.set_xlabel('Ticker Symbols')
        ax.set_ylabel(metric)
        ax.set_title(f'{metric} of Added Companies')
        ax.legend()

    elif metric in ["PEG Ratio", "PB Ratio"]:
            fig = Figure(figsize=(10, 4), dpi=100)
            ax = fig.add_subplot(1,1,1)
            values = []
            tickers_with_data = []

            for ticker_symbol in selected_tickers:
                if metric == "PEG Ratio":
                    value = pegCalc(ticker_symbol)
                elif metric == "PB Ratio":
                    value = calculate_pb_ratio(ticker_symbol)

                if value != -1:
                    values.append(value)
                    tickers_with_data.append(ticker_symbol)

            ax.bar(tickers_with_data, values, color='blue')
            ax.set_title(f"{metric} for Selected Tickers")
            ax.set_ylabel(metric)
            ax.set_xlabel("Ticker Symbols")

    elif metric == "Adj Close Line Chart":
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        #selected_tickers = list(added_tickers.keys())
        display_tickers = ['^SPX', '^DJI'] + selected_tickers
        for ticker_symbol in display_tickers:
            ticker_data = yf.Ticker(ticker_symbol)
            hist = ticker_data.history(period=selected_timehorizon)
            price_column = 'Adj Close' if 'Adj Close' in hist.columns else 'Close'
            ax.plot(hist.index, hist[price_column], label=ticker_symbol)
        ax.set_title("Adjusted Close Price Over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Adjusted Close Price")
        ax.legend()

        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_horizontalalignment('right')  # Improve alignment of the rotated labels

        # Format the dates on the x-axis to be more readable
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))


        # Display legend
        ax.legend()
        # This ensures everything is nicely laid out
        fig.tight_layout()


    elif metric == "Average Daily Change":
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        empty_data = True
        #selected_tickers = list(added_tickers.keys())
        display_tickers = ['^SPX', '^DJI'] + selected_tickers
        for ticker_symbol in display_tickers:
            ticker_data = yf.Ticker(ticker_symbol)
            hist = ticker_data.history(period=selected_timehorizon)
            if not hist.empty:
                    empty_data = False
                    if metric == "Adj Close Line Chart":
                        price_column = 'Adj Close' if 'Adj Close' in hist.columns else 'Close'
                        ax.plot(hist.index, hist[price_column], label=ticker_symbol)
                    elif metric == "Average Daily Change":
                        daily_changes = hist['Close'].pct_change().dropna()
                        if not daily_changes.empty:
                            ax.plot(daily_changes.index, daily_changes.cumsum(), label=f"{ticker_symbol} Cumulative")

        if empty_data:
                messagebox.showinfo("Info", "No data available for the selected tickers and time period.")
        else:
                ax.set_title("Cumulative Daily Percentage Change")
                ax.set_xlabel("Date")
                ax.set_ylabel("Cumulative Change (%)")
                ax.legend()

                for label in ax.get_xticklabels():
                    label.set_rotation(45)
                    label.set_horizontalalignment('right')  # Improve alignment of the rotated labels

                # Format the dates on the x-axis to be more readable
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                # Display legend
                ax.legend()
                # This ensures everything is nicely laid out
                fig.tight_layout()


    elif metric == "CAPM":
        # Define the start and end dates
        string_cut_position = len(selected_timehorizon)-1       # position to pull the time frame
        time_unit = selected_timehorizon[-1]
        time_frame = int(selected_timehorizon[0:string_cut_position])
        print("time unit:", time_unit, "time frame:", time_frame)
        # Find the start and end dates
        end_date, start_date = get_start_date(time_unit, time_frame)
        Cap_M_values = []
        spy_return = 0
        rfrr = 0
        fig = Figure(figsize=(10,4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        # Call the CAPM computation
        for ticker_symbol in selected_tickers:
            try:
                cap_m, spy_return, rfrr = CAPM_Computation(ticker_symbol, start_date, end_date)
                # cap_m = cap_m.fillna(0)  # Replace NaNs with 0
                Cap_M_values.append((ticker_symbol, cap_m))


            except Exception as e:
                print(f"Failed to fetch or calculate CAPM for {ticker_symbol}: {e}")
                Cap_M_values.append((ticker_symbol, None))

        print(Cap_M_values)
        # Ensure there is data to unpack and plot
        if Cap_M_values:
            # plt.figure(figsize=(10, 4))
            tickers, capms = zip(*Cap_M_values)  # Unpack the list of tuples

            tickers, capms = zip(*Cap_M_values)
            ax.bar(tickers, capms, color='skyblue')
            ax.set_xlabel('Ticker Symbols')
            ax.set_ylabel('CAPM Expected Return')
            ax.set_title('CAPM Expected Return for Selected Tickers Against the S&P 500')
            ax.axhline(y=spy_return, color='r', linestyle='--', label='S&P500 Benchmark')
            ax.axhline(y=rfrr, color='g', linestyle='--', label='Risk Free Rate of Return')
            ax.legend()
        else:
            print("No CAPM data available to plot.")


    elif metric == "RSI":
        rsi_values = []
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        for ticker_symbol in selected_tickers:
            try:
                ticker_data = yf.Ticker(ticker_symbol)
                hist = ticker_data.history(period=selected_timehorizon)
                price_column = 'Adj Close' if 'Adj Close' in hist.columns else 'Close'

                # Ensure you're applying diff() to the DataFrame column
                delta = hist[price_column].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()

                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                rsi = rsi.fillna(0)  # Replace NaNs with 0

                rsi_values.append((ticker_symbol, rsi.iloc[-1]))

            except Exception as e:
                print(f"Failed to fetch or calculate RSI for {ticker_symbol}: {e}")
                rsi_values.append((ticker_symbol, None))

        # print(rsi_values)
        # Ensure there is data to unpack and plot
        if rsi_values:
            tickers, rsis = zip(*rsi_values)
            ax.bar(tickers, rsis, color='skyblue')
            ax.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
            ax.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
            ax.set_xlabel('Ticker Symbols')
            ax.set_ylabel('RSI')
            ax.set_title('RSI Values for Selected Tickers')
            ax.set_ylim(0, 100)
            ax.legend()
        else:
            print("No RSI data available to plot.")



    elif metric in ["Dividend Yield", "D/E Ratio", "EBITDA"]:
        
        values = []
        tickers = list(added_tickers.keys())
        for ticker_symbol in tickers:
            ticker_data = yf.Ticker(ticker_symbol)
            if metric == "Dividend Yield":
                value = ticker_data.info.get('dividendYield', 0)  # Convert to percentage
                # Convert to percentage if not None
                if value is not None:
                    value *= 100
                else:
                    value = "N/A"
            elif metric == "D/E Ratio":
                value = ticker_data.info.get('debtToEquity', 'N/A')
            elif metric == "EBITDA":
                value = ticker_data.info.get('ebitda', 'N/A')
                value = value / 1e6  # Convert to millions if needed
               

            values.append(value if value != 'N/A' else np.nan)  # Use nan for missing values

        # Filter out missing data
        valid_values = [v for v in values if not np.isnan(v)]
        if not valid_values:
            messagebox.showinfo("Info", "No valid data available for the selected metric.")
            return
        # Plot
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(1,1,1)
        ax.bar(tickers, values, color='skyblue', label=metric)
        ax.set_xlabel('Ticker Symbols')
        ax.set_ylabel(metric)
        ax.set_title(f'{metric} of Added Companies')
        ax.legend()

    # Embed the figure in the Tkinter window
    if metric in ["P/E Ratio", "PEG Ratio", "PB Ratio", "Beta", "Adj Close Line Chart", "Average Daily Change", "Dividend Yield", "D/E Ratio", "EBITDA", "RSI","CAPM"]:
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=5, column=0, columnspan=3, sticky="nsew")
        canvas.draw()


def on_time_horizon_change(*args):
    # Fetch the selected time horizon using the get method of StringVar
    key = time_horizon_var.get()
    print(f"Selected Time Horizon: {time_horizons[key]}")

# Define your time horizons
time_horizons = {
    '1D': '1 day',
    '5D': '5 days',
    '1M': '1 month',
    '3M': '3 months',
    '6M': '6 months',
    '1Y': '1 year',
    '2Y': '2 years',
    '5Y': '5 years',
    '10Y': '10 years',
    'YTD': 'Year to date'
}

# Set up the UI
root = tk.Tk()
root.title("Stock Data Fetcher")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ticker_label = ttk.Label(frame, text="Enter ticker symbol:")
ticker_label.grid(row=0, column=0, sticky=tk.W)

ticker_entry = ttk.Entry(frame, width=20)
ticker_entry.grid(row=0, column=1, sticky=tk.W)

add_button = ttk.Button(frame, text="Add Ticker", command=add_ticker)
add_button.grid(row=0, column=2)

remove_button = tk.Button(frame, text="Remove Ticker", command=remove_ticker)
remove_button.grid(row=1, column=2)

# Time Horizon Dropdown
time_horizon_var = tk.StringVar(root)
time_horizon_var.set('1M')  # Set default value
time_horizon_label = tk.Label(frame, text="Time Horizon:")
time_horizon_label.grid(row=1, column=0, sticky=tk.W)
time_horizon_dropdown = tk.OptionMenu(frame, time_horizon_var, *time_horizons.keys())
time_horizon_dropdown.grid(row=1, column=1, sticky=tk.W)
time_horizon_var.trace("w", on_time_horizon_change)



companies_label = ttk.Label(frame, text="Added Companies:")
companies_label.grid(row=2, column=0, sticky=tk.W)

# Store the ticker symbols from the user
added_tickers = {}

companies_listbox = tk.Listbox(frame)
companies_listbox.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

metric_label = ttk.Label(frame, text="Plot Metric:")
metric_label.grid(row=4, column=0, sticky=tk.W)
metric_combobox = ttk.Combobox(frame, values=["P/E Ratio", "PEG Ratio", "PB Ratio", "Adj Close Line Chart", "Average Daily Change", "Beta", "CAPM", "Dividend Yield", "D/E Ratio", "EBITDA", "RSI"])
metric_combobox.grid(row=4, column=1, sticky=tk.W)
plot_button = ttk.Button(frame, text="Calculate", command=calculate_metric)
plot_button.grid(row=4, column=2)


root.mainloop()
