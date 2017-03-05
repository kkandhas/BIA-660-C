import os
import requests
from flask import Flask, request, Response
import datetime
import time

application = Flask(__name__)

# SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')

slack_inbound_url = 'https://hooks.slack.com/services/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'
# slack_inbound_url = 'https://hooks.slack.com/services/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'

server_is_at = os.popen("curl icanhazip.com").read()


@application.route('/slack', methods=['POST'])
def inbound():
    response = {'username': 'karan_bot', 'icon_emoji': ':robot_face:'}
    # if request.form.get('token') == SLACK_WEBHOOK_SECRET:
    channel = request.form.get('channel_name')
    username = request.form.get('user_name')
    text = request.form.get('text')
    inbound_message = username + " in " + channel + " says: " + text
    owner_name = 'kkandhas'
    my_chatbot_name = 'karan_bot'

    if username != my_chatbot_name and username in [owner_name, 'zac.wentzell']:

        # Task 1
        if str(text) == '&lt;BOTS_RESPOND&gt;' and username == 'zac.wentzell':
            time.sleep(3)
            response['text'] = 'Hello, my name is ' + my_chatbot_name + \
                               '. I belong to ' + owner_name + '. I live at ' + format(server_is_at)
        # Task 2 & 3
        elif '&lt;I_NEED_HELP_WITH_CODING&gt;' in text.split(':'):
            query = text.split(':')
            if '[' in query[1]:
                sub_str = query[1].split('[')
                api_str = "https://api.stackexchange.com/2.2/search/advanced?page=5&pagesize=5&order=asc&" \
                          "sort=relevance&q=" + sub_str[0] + "&accepted=True"
                for i, x in enumerate(sub_str):
                    if i != 0:
                        api_str = api_str + "&tagged=" + x.strip(']')

                api_str += '&site=stackoverflow'
            else:
                api_str = "https://api.stackexchange.com/2.2/search/advanced?page=5&pagesize=5&order=asc&sort" \
                          "=relevance&q=" + query[1] + "&accepted=True&site=stackoverflow"

            r = requests.get(api_str)
            temp = r.json()
            strtxt = str(' ')
            for i, x in enumerate(temp['items']):
                title = '*' + temp['items'][i]['title'] + '*'
                link = '<' + temp['items'][i]['link'] + '|Link>'
                rpno = temp['items'][i]['answer_count']
                date = temp['items'][i]['creation_date']
                dd = datetime.datetime.fromtimestamp(date).strftime('%c')
                strtxt = strtxt + title + '? ' + link + ' (' + str(rpno) + ' responses ) ' + str(dd) + '\n\n'
            response['text'] = strtxt
        # Task 4
        elif "&lt;WHAT'S_THE_WEATHER_LIKE_AT&gt;" in text.split(':'):
            query = text.split(':')
            temp = query[1].split(',')

            if len(temp[0]) <= 6:
                api_str = 'http://api.wunderground.com/api/9cd1d67d77ace1a5/conditions/q/' + temp[0] + ',us.json'
                api_str2 = 'http://api.wunderground.com/api/9cd1d67d77ace1a5/forecast/q/' + temp[0] + '.json'
            else:
                k = temp[0].split(',')
                z = k[0].split(' ')

                api_str = 'http://api.wunderground.com/api/9cd1d67d77ace1a5/conditions/q/' + temp[len(temp) - 1] + '/' \
                          + z[len(z) - 1] + '.json'
                api_str2 = 'http://api.wunderground.com/api/9cd1d67d77ace1a5/forecast/q/' + temp[len(temp) - 1] + '/' \
                           + z[len(z) - 1] + '.json'

            r = requests.get(api_str)
            time.sleep(3)
            r2 = requests.get(api_str2)
            tmp = r.json()
            tmp2 = r2.json()

            strtxt = "*Weather Information* \n"
            response['attachments'] = \
                [
                    dict(fallback="Required plain-text summary of the attachment.",
                         color="#36a64f",

                         title=tmp['current_observation']['display_location']['city'],
                         title_link=tmp['current_observation']['forecast_url'],
                         text="Click on the City for more details",
                         fields=[
                             dict(title="Temperature",
                                  value=tmp['current_observation']['temperature_string'],
                                  short=True),
                             dict(title="Feels Like",
                                  value=tmp['current_observation']['feelslike_string'],
                                  short=True),
                             dict(title="High | Low",
                                  value=tmp2['forecast']['simpleforecast']['forecastday'][1]['high']['fahrenheit'] \
                                        + ' F (' + tmp2['forecast']['simpleforecast']['forecastday'][1]['high'][
                                            'celsius'] + ' C)|' \
                                        + tmp2['forecast']['simpleforecast']['forecastday'][1]['low']['fahrenheit'] \
                                        + ' F (' + tmp2['forecast']['simpleforecast']['forecastday'][1]['low'][
                                            'celsius'] + ' C)',
                                  short=True),
                             dict(title="Weather",
                                  value=tmp['current_observation']['weather'],
                                  short=True),
                             dict(title="Wind",
                                  value=tmp['current_observation']['wind_string'],
                                  short=False),
                             dict(title="Humidity",
                                  value=tmp['current_observation']['relative_humidity'],
                                  short=True),
                             dict(title="Visibility",
                                  value=tmp['current_observation']['visibility_mi'] + 'miles',
                                  short=True)
                         ],
                         image_url=tmp2['forecast']['simpleforecast']['forecastday'][1]['icon_url'],
                         footer="Weather API",
                         footer_icon="https://platform.slack-edge.com/img/default_application_icon.png",
                         ts=tmp2['forecast']['simpleforecast']['forecastday'][0]['date']['epoch'])
                ]

            response['text'] = strtxt
        else:
            response['text'] = 'Hi Karan. What can I do for you ?'

        r = requests.post(slack_inbound_url, json=response)

    print inbound_message
    print request.form

    return Response(), 200


@application.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=41953)
