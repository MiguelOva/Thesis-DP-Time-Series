import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from plotly import tools
from plotly.offline import init_notebook_mode, iplot
from sklearn.preprocessing import MinMaxScaler, StandardScaler

init_notebook_mode(connected=True)
import plotly.graph_objs as go
import gc


def extract_data_v3(ticker, start_date, end_date):
    # Block 1: Date format checking
    try:
        pd.to_datetime(start_date)
        pd.to_datetime(end_date)
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

    # Block 2: Downloading data from yfinance API
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        try:
            data = pd.read_csv(f"data_{ticker}.csv")
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.loc[(data["Date"] >= start_date) & (data["Date"] <= end_date),
                            ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
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

    # Block 3: Displaying dataframe
    display(data)

    # Block 4: Normalization
    normalize = input("Do you want to normalize the data? (yes/no)").lower()
    if normalize == "yes":
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.set_index('Date')
        df_day = data.resample("D").mean()
        df_week = data.resample("W").mean()
        df_month = data.resample("M").mean()
        df_quarter = data.resample("Q").mean()
        df_year = data.resample("A").mean()

        # Block 5: Resampled data selection
        print("What type of resampled data would you like to visualize?")
        print(
            "1. Daily frequency\n2. Weekly frequency\n3. Monthly frequency\n4. Quarterly frequency\n5. Annual frequency")
        resampled_choice = int(input("Enter the number corresponding to your choice: "))
        if resampled_choice == 1:
            data = data.resample("D").mean()
        elif resampled_choice == 2:
            data = data.resample("W").mean()
        elif resampled_choice == 3:
            data = data.resample("M").mean()
        elif resampled_choice == 4:
            data = data.resample("Q").mean()
        elif resampled_choice == 5:
            data = data.resample("Y").mean()
        else:
            raise ValueError("Invalid choice entered. Please enter a number between 1 to 5.")

        # Block 6: return resampled data
        # Apply the Standard Scaler to the dataset
        scaler = StandardScaler()
        data_normalized = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
        temp = data.reset_index()
        data_normalized['Date'] = temp['Date']
        data_normalized = data_normalized.set_index(data_normalized.Date)
        data_normalized = data_normalized.drop(columns=['Date'])
        data_normalized.head()
        display(data_normalized)

    # Block 7: Perform train-test-split on the normalized dataset
    print("Do you want to perform train test split on the dataset?")
    choice = input("Enter Y for Yes or N for No: ")
    if choice.lower() == 'y':
        splitter = input("Enter the splitter date in the format YYYY-MM-DD: ")
        # split data into train and test sets
        data_train = data_normalized.loc[data_normalized.index <= splitter]
        data_test = data_normalized.loc[data_normalized.index > splitter]

        # split x_train and y_train
        X_train, y_train = data_train.iloc[:, :-1], data_train.iloc[:, -1]
        X_test, y_test = data_test.iloc[:, :-1], data_test.iloc[:, -1]

        # Convert to numpy arrays
        y_train = y_train.to_numpy()
        y_test = y_test.to_numpy()
        X_train = X_train.to_numpy()
        X_test = X_test.to_numpy()

        # reshaping to  3D [samples, timesteps, features]
        X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
        X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
        print("Train set shape: ", X_train.shape, y_train.shape)
        print("Test set shape: ", X_test.shape, y_test.shape)

        return X_train, y_train, X_test, y_test
    else:
        print("Train test split is not performed.")
        return data_normalized