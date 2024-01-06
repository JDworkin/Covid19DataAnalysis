from flask import Flask, render_template
from io import BytesIO
import base64
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

app = Flask(__name__)


@app.route('/')
def index():
    # Load the COVID-19 dataset
    url = ("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/country_data/United"
           "%20Kingdom.csv")
    df = pd.read_csv(url)

    # Convert the 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    # Forward-fill NaN values in date-related columns
    df = df.ffill()

    # Handle missing values
    df = df.dropna()
    columns_to_drop = ['source_url', 'location']
    df_new = df.drop(columns=columns_to_drop)

    # Set the style of seaborn
    sns.set(style="whitegrid")

    # Create a new DataFrame with the required columns
    columns_to_plot = ['date', 'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_boosters']
    df_plot = df_new[columns_to_plot]

    # Melt the DataFrame to long format for easier plotting
    df_plot = pd.melt(df_plot, id_vars='date', var_name='Vaccination Type', value_name='Count')

    # Change the names within the legend
    df_plot['Vaccination Type'] = df_plot['Vaccination Type'].map({
        'total_vaccinations': 'Total Vaccinations',
        'people_vaccinated': 'People Vaccinated',
        'people_fully_vaccinated': 'People Fully Vaccinated',
        'total_boosters': 'Total Boosters'})

    # Create a line plot using seaborn
    plt.figure(figsize=(12, 6))
    lineplot = sns.lineplot(x='date', y='Count', hue='Vaccination Type', data=df_plot)

    # Customize the plot
    lineplot.set_title('Vaccination Trends Over Time')
    lineplot.set_xlabel('Date')
    lineplot.set_ylabel('Count')

    # Display the legend outside the plot
    lineplot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    # Format the x-axis dates
    lineplot.xaxis.set_major_locator(mdates.MonthLocator())
    lineplot.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %Y'))
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Save the plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    # Encode the plot as base64 and pass it to the template
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('index.html', plot_url=plot_url)


if __name__ == '__main__':
    app.run(debug=True)
