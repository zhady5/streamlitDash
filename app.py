import dash

from data_processing import  load_data, process_data

from functions import date_ago, convert_date, get_gradient_color, get_current_previous_sums, create_table, hex_to_rgb\
                            , interpolate_color, gradient_color_func \
                        , calculate_mean_max_subs, calculate_mean_posts, calculate_mean_views, calculate_mean_reacts\
                        , load_stopwords_from_file

from layouts import create_layout
from callbacks import register_callbacks

channels, posts, reactions, subscribers, views = load_data()
processed_data = process_data(channels, posts, reactions, subscribers, views)

# Настройка приложения Dash
external_stylesheets = [
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css',
    'https://fonts.googleapis.com/css?family=Merriweather|Open+Sans&display=swap',
    'Desktop/notebooks/custom-styles.css'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets )
# Макет приложения
server = app.server

app.layout = create_layout(processed_data)
register_callbacks(app, processed_data)

if __name__ == '__main__':
    app.run_server(debug=True, port=8015)