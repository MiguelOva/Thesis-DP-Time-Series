import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from plotly import tools
from plotly.offline import init_notebook_mode, iplot

init_notebook_mode(connected=True)
import plotly.graph_objs as go
import gc


def extract_data_v2(ticker, start_date, end_date):
    # Check if the date is in the correct format
    try:
        pd.to_datetime(start_date)
        pd.to_datetime(end_date)
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

    # Download data from yfinance API
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        try:
            data = pd.read_csv(f"data_{ticker}.csv")
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.loc[(data["Date"] >= start_date) & (data["Date"] <= end_date),
                            ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']]
            data = data.rename(columns={'Adj Close': 'Adj_Close'})
            print(f"No data was retrieved from yfinance API for {ticker}. Using locally stored data instead.")
        except FileNotFoundError:
            raise FileNotFoundError(f"No data was found for {ticker} locally.")
    else:
        data["Date"] = data.index
        data.to_csv(f"data_{ticker}.csv", index=False)
        print(f"Data was successfully retrieved from yfinance API for {ticker}.")

        data = data.loc[:, ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
        data["Date"] = data["Date"].dt.normalize()
        data = data.rename(columns={'Adj Close': 'Adj_Close'})
        data = data.loc[(data["Date"] >= start_date) & (data["Date"] <= end_date), :]
    # Display the dataframe
    print(data)

    # Plot the data
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data["Date"], data["Adj_Close"], label=ticker)
    ax.set_xlabel("Date")
    ax.set_ylabel("Adjusted Close Price")
    ax.set_title(f"{ticker} Stock Price from {start_date} to {end_date}")
    ax.legend()
    plt.show()
    print(f"Data is for the interval from {start_date} to {end_date}")

    # Ask the user if they want to see more visualizations
    more_viz = input("Do you want to see more visualizations? (yes/no)")
    if more_viz.lower() == "yes":
        # Default resampling is set to per Hour.
        # Here we decided to downsample the data into days, months, quarters and years for visualization and further analysis.
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.set_index('Date')
        df = data.copy()
        df_day = df.resample('D').mean()
        df_week = df.resample('W').mean()
        df_month = df.resample('M').mean()
        df_quarter = df.resample('A-DEC').mean()
        df_year = df.resample('A-DEC').mean()

        print("What type of resampled data would you like to visualize?")
        print(
            "1. Daily frequency\n2. Weekly frequency\n3. Monthly frequency\n4. Quarterly frequency\n5. Annual frequency")
        resampled_choice = int(input("Enter the number corresponding to your choice: "))
        if resampled_choice == 1:
            resampled_df = df_day
        elif resampled_choice == 2:
            resampled_df = df_week
        elif resampled_choice == 3:
            resampled_df = df_month
        elif resampled_choice == 4:
            resampled_df = df_quarter
        elif resampled_choice == 5:
            resampled_df = df_year
        else:
            raise ValueError("Invalid choice entered. Please enter a number between 1 to 5.")

        # Plot the resampled data
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(resampled_df.index, resampled_df["Adj_Close"], label=ticker)
        ax.set_xlabel("Date")
        ax.set_ylabel("Adjusted Close Price")
        ax.set_title(
            f"{ticker} Stock Price ({resampled_df.index[0].date()} to {resampled_df.index[-1].date()}) Resampled to {resampled_df.index.freqstr}")
        ax.legend()
        plt.show()

        # Ask if the user wants to see more visualizations
        more_viz = input("Do you want to see more visualizations? (yes/no)")

        if more_viz.lower() == "yes":
            print("What would you like to do?")
            print("1. Resample the data")
            print("2. New visualization")
            choice = int(input("Enter the number corresponding to your choice: "))

            if choice == 1:
                # Repeat the resampling process
                print("What type of resampled data would you like to visualize?")
                print(
                    "1. Daily frequency\n2. Weekly frequency\n3. Monthly frequency\n4. Quarterly frequency\n5. Annual frequency")
                resampled_choice = int(input("Enter the number corresponding to your choice: "))

                if resampled_choice == 1:
                    resampled_df = df_day
                elif resampled_choice == 2:
                    resampled_df = df_week
                elif resampled_choice == 3:
                    resampled_df = df_month
                elif resampled_choice == 4:
                    resampled_df = df_quarter
                elif resampled_choice == 5:
                    resampled_df = df_year
                else:
                    raise ValueError("Invalid choice entered. Please enter a number between 1 to 5.")

                # Plot the resampled data
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(resampled_df.index, resampled_df["Adj_Close"], label=ticker)
                ax.set_xlabel("Date")
                ax.set_ylabel("Adjusted Close Price")
                ax.set_title(
                    f"{ticker} Stock Price ({resampled_df.index[0].date()} to {resampled_df.index[-1].date()}) Resampled to {resampled_df.index.freqstr}")
                ax.legend()
                plt.show()

            elif choice == 2:
                print("What type of resampled data would you like to visualize?")
                print(
                    "1. Daily frequency\n2. Weekly frequency\n3. Monthly frequency\n4. Quarterly frequency\n5. Annual frequency")
                resampled_choice = int(input("Enter the number corresponding to your choice: "))

                if resampled_choice == 1:
                    resampled_df = df_day
                elif resampled_choice == 2:
                    resampled_df = df_week
                elif resampled_choice == 3:
                    resampled_df = df_month
                elif resampled_choice == 4:
                    resampled_df = df_quarter
                elif resampled_choice == 5:
                    resampled_df = df_year
                else:
                    raise ValueError("Invalid choice entered. Please enter a number between 1 to 5.")

                resampled_df = resampled_df.reset_index()
                trace1 = go.Scatter(
                    x=resampled_df['Date'],
                    y=resampled_df['Open'].astype(float),
                    mode='lines',
                    name='Open')
                trace2 = go.Scatter(
                    x=resampled_df['Date'],
                    y=resampled_df['Close'].astype(float),
                    mode='lines',
                    name='Close')
                trace3 = go.Scatter(
                    x=resampled_df['Date'],
                    y=resampled_df['Adj_Close'].astype(float),
                    mode='lines',
                    name='Weighted Avg')
                layout = dict(
                    title='Historical Bitcoin Prices (2012-2018) with the Slider ',
                    xaxis=dict(
                        rangeselector=dict(
                            buttons=list([
                                dict(count=6,
                                     label='6m',
                                     step='month',
                                     stepmode='backward'),
                                dict(count=12,
                                     label='1y',
                                     step='month',
                                     stepmode='backward'),
                                dict(count=36,
                                     label='3y',
                                     step='month',
                                     stepmode='backward'),
                                dict(step='all')
                            ])
                        ),
                        rangeslider=dict(
                            visible=True
                        ),
                        type='date'
                    )
                )
                _ = [trace1, trace2, trace3]
                fig = dict(data=_, layout=layout)
                new_visualization = iplot(fig, filename="Time Series with Rangeslider")
                return new_visualization
                pass
            else:
                raise ValueError("Invalid choice entered. Please enter a number between 1 to 2.")


