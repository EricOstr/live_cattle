# Plot predicted vs. actual values
fig, ax = plt.subplots()


ax.scatter(data_pct_change.index, y, label='Actual', color='blue')
ax.scatter(data_pct_change.index, model.predict(X), label='Fitted', color='red')

# Draw interconnecting line from predicted to actual
for i in range(len(data_pct_change)):
    ax.plot([data_pct_change.index[i], data_pct_change.index[i]], [model.predict(X)[i], y[i]], color='red', linewidth=1)

ax.set_xlabel('Date')
ax.set_ylabel('Cattle cash price % change')
ax.set_title('Fitted vs. Actual Values')

ax.legend()
plt.show()


####################################################################################################

# root mean squared error
def rmse(y_true, y_pred):
    return np.sqrt((y_true - y_pred[0]) ** 2)


# mean absolute error
def mae(y_true, y_pred):
    return abs(y_true - y_pred[0])



# Initialize lists to store results
predicted_values_rf = pd.Series()
rmse_values_rf = pd.Series()
mae_values_rf = pd.Series()


# Iterate over each row of data
for i in range(len(data_pct_change)):

# i=0


    test_df, train_df = pop_row(data_pct_change, i) # pop the i-th row from data as the test set

    # Split data into training and test sets
    y_test = test_df[test_df.columns[0]]
    X_test = test_df[test_df.columns[1:]]

    y_train = train_df[train_df.columns[0]]
    X_train = train_df[train_df.columns[1:]]

    # Fit model on training data
    rf = RandomForestRegressor(n_estimators=1000, random_state=42)
    model = rf.fit(X_train, y_train)

    # Predict test data
    y_pred = pd.Series(model.predict(X_test))
    y_pred.index = X_test.index

    # Calculate errors
    rmse_val = rmse(y_test, y_pred)
    mae_val = mae(y_test, y_pred)


    # Append results to lists
    predicted_values_rf = predicted_values_rf.append(y_pred)
    rmse_values_rf = rmse_values_rf.append(rmse_val)
    mae_values_rf = mae_values_rf.append(mae_val)



####################################################################################################

