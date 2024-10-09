from flask import Flask, render_template, request
import requests
import datetime


app = Flask(__name__)


# OpenWeatherMap API key
API_KEY = '9cf0c53738ce2dc46796129c0f16bcda'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    # Current weather API call
    current_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=imperial'
    current_response = requests.get(current_url)
    current_data = current_response.json()

    if current_data['cod'] == 200:
        weather_data = {
            'city': city,
            'country': current_data['sys']['country'],
            'temperature': current_data['main']['temp'],
            'description': current_data['weather'][0]['description'],
            'icon': current_data['weather'][0]['icon'],
            'wind_speed': current_data['wind']['speed'],
            'pressure': current_data['main']['pressure'],
            'humidity': current_data['main']['humidity'],
            'sunrise': datetime.datetime.fromtimestamp(current_data['sys']['sunrise']).strftime('%H:%M:%S'),
            'sunset': datetime.datetime.fromtimestamp(current_data['sys']['sunset']).strftime('%H:%M:%S'),
            'day': datetime.datetime.now().strftime('%A'),
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        }
    else:
        error_message = current_data['message']
        return render_template('error.html', error_message=error_message)

    # Weekly forecast API call
    forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=imperial'
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()

    weekly_forecast = []
    if forecast_data['cod'] == '200':
        current_date = None
        forecast_group = None
        for forecast in forecast_data['list']:
            forecast_date = datetime.datetime.fromtimestamp(
                forecast['dt']).strftime('%Y-%m-%d')
            forecast_day = datetime.datetime.fromtimestamp(
                forecast['dt']).strftime('%A')
            if forecast_date != current_date:
                if forecast_group:
                    weekly_forecast.append(forecast_group)
                forecast_group = {
                    'day': forecast_day,
                    'date': forecast_date,
                    'temperature': forecast['main']['temp'],
                    'humidity': forecast['main']['humidity'],
                    'wind_speed': forecast['wind']['speed'],
                    'description': forecast['weather'][0]['description'],
                    'icon': forecast['weather'][0]['icon'],
                    'forecasts': []
                }
                current_date = forecast_date
            forecast_item = {
                'temperature': forecast['main']['temp'],
                'humidity': forecast['main']['humidity'],
                'wind_speed': forecast['wind']['speed'],
                'description': forecast['weather'][0]['description'],
                'icon': forecast['weather'][0]['icon']
            }
            forecast_group['forecasts'].append(forecast_item)
        if forecast_group:
            weekly_forecast.append(forecast_group)
    else:
        error_message = forecast_data['message']
        return render_template('error.html', error_message=error_message)

    return render_template('weather.html', weather=weather_data, weekly_forecast=weekly_forecast)


if __name__ == '__main__':
    app.run(debug=True)
