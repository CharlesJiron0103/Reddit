import json
import sys
from datetime import time
import time
from pprint import pprint
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
from slack_token import *
from transformers import pipeline

comments = set()
time_stamp_of_reddit_message = set()

happy_face = "\U0001F600"
thumb_up = "\U0001F44D"
neutral_face = "\U0001F611"
thumb_down = "\U0001F44E"
crossed_out = "\U0001F635"

client = WebClient(token=slack_token)
logger = logging.getLogger(__name__)


def new_post_to_slack(dataQuery, num):
    get_reddit_time_stamp_from_messages_in_slack()

    url_to_get_comment = f"https://api.pushshift.io/reddit/comment/search/?q={dataQuery}&size={num}"
    r = requests.get(url_to_get_comment)
    data = json.loads(r.text, strict=False)
    pprint(data)
    print("\n\n\n\n")

    if data:

        count = len(data['data']) - 1
        print(f'ID: {count}')

        for _ in data['data']:

            if str(data['data'][count]['created_utc']) not in time_stamp_of_reddit_message:

                # PERMA-URL of Comment
                url_Actual = data['data'][count]['permalink']

                # Comment Author
                author = data['data'][count]['author']

                # Comment Itself without limiting to 128 char
                body = str(data['data'][count]['body'])

                # Comment with the limit of 128 Char
                first_128 = body[0:128]

                # Default Limit of 128 Characters and Implementing them in a Sentiment Model Analysis
                specific_model = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
                sentiment = specific_model(first_128)
                print(sentiment)

                # Grabbing the Label of the Comments Sentiment
                onlyLabel = sentiment[0]['label']

                # Outputting the Label of the Comments Sentiment
                print(f'Sentiment Label: {onlyLabel}')

                # Rounds the Initial Output to the nearest fourth. Then Multiplies by 100 to get the percentage.
                # Then round the percentage to the nearest whole number.
                onlyScore = round(round(sentiment[0]['score'], 4) * 100)

                # Outputs both the Score and Comment
                print(f'Sentiment Score: {onlyScore}%')
                print(f'Comment: {first_128}')

                # Comment Sub-Reddit
                subR = data['data'][count]['subreddit']

                # Full Comment Link
                postUrl = f"https://www.reddit.com/{url_Actual}"

                # Comment Date in UTC Format
                create = data['data'][count]['created_utc']

                # Converting to readable Time of Year, Month, Day, Hour, Second, AM or PM
                post_created_date = time.strftime('%Y-%m-%d', time.localtime(create))

                post_created_time = time.strftime('%I:%M:%S %p', time.localtime(create))

                # Conversion completed to Date
                date = post_created_date

                # Conversion Completed to Time
                time_com = post_created_time

                # # Outputting everything into a file
                # fp = open("CommentInformation.txt", "w")
                #
                # fp.write("Reddit Comments")
                # fp.write(f"\nAuthor: u/{author}")
                # fp.write(f"\nSub-Reddit: r/{subR}")
                # fp.write(f'\nURL: <a href="{postUrl}</a')
                # fp.write(f'\nCreated: {date}')
                # fp.write(f'\nComment: {first_128}')

                # Checks Sentiment Score Percentage.
                if onlyLabel == "POS":  # If Score is greater than 75 then display percentage score and thumbs-up

                    # fp.write(f'\nSentiment Analysis: {onlyScore}% - {thumb_up}')
                    very_Good = f'POSITIVE'
                    very_score_pos = f'{onlyScore}% - {thumb_up}'

                    # Using this title to implement the link in it for easier access.
                    title = "View Comment"

                    # Displaying it in Slack
                    blocks = [{
                        "type": "divider"
                    },

                        {
                            "type": "header",
                            "text":
                                {
                                    "type": "plain_text",
                                    "text": f"Reddit Scrapa {happy_face}\n Comment pulled from keyword {dataQuery}",
                                    "emoji": True
                                }

                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Author*: \nu/{author}\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sub Reddit*: \nr/{subR}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*When*: \n{date}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Time*: \n{time_com}'
                                },
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Comment*: \n{first_128}'
                                },
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Label*\n{very_Good}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Score*: \n{very_score_pos}'
                                },
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": "A new Reddit post mentions the keyword: *"
                                            + query.replace('\"', '').capitalize() +
                                            f"*\n\n*<{postUrl}|{title}>*"
                                }
                        },
                    ]
                    requests.post('https://slack.com/api/chat.postMessage', {
                        'token': slack_token,
                        'channel': slack_channel,
                        'text': create,
                        'blocks': json.dumps(blocks) if blocks else None
                    }).json()
                elif onlyLabel == "NEU":
                    # fp.write(f'Sentiment Analysis: {onlyScore}% - {neutral_face}')
                    very_neutral = f'NEUTRAL'
                    very_score_neu = f'{onlyScore}% - {neutral_face}'

                    title = "View Comment"
                    # Displaying it in Slack
                    blocks = [{
                        "type": "divider"
                    },

                        {
                            "type": "header",
                            "text":
                                {
                                    "type": "plain_text",
                                    "text": f"Reddit Scrapa {happy_face}\n Comment pulled from keyword {dataQuery}",
                                    "emoji": True
                                }

                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Author*: \nu/{author}\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sub Reddit*: \nr/{subR}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*When*: \n{date}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Time*: \n{time_com}'
                                },
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Comment*: {first_128}'
                                },
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Label*\n{very_neutral}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Score*: \n{very_score_neu}'
                                },
                            ]
                        },
                        {
                          "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": "A new Reddit post mentions the keyword: *"
                                            + query.replace('\"', '').capitalize() +
                                            f"*\n\n*<{postUrl}|{title}>*"
                                }
                        },
                    ]
                    requests.post('https://slack.com/api/chat.postMessage', {
                        'token': slack_token,
                        'channel': slack_channel,
                        'text': create,
                        'blocks': json.dumps(blocks) if blocks else None
                    }).json()

                elif onlyLabel == "NEG":

                    # fp.write(f'Sentiment Analysis: {onlyScore}% - {thumb_down}')
                    very_bad = f'NEGATIVE'
                    very_score_bad = f'{onlyScore}% - {thumb_down}'

                    title = "View Comment"
                    # Displaying it in Slack
                    blocks = [{
                        "type": "divider"
                    },

                        {
                            "type": "header",
                            "text":
                                {
                                    "type": "plain_text",
                                    "text": f"Reddit Scrapa {happy_face}\n Comment pulled from keyword {dataQuery}",
                                    "emoji": True
                                }

                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Author*: \nu/{author}\n"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sub Reddit*: \nr/{subR}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*When*: \n{date}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Time*: \n{time_com}'
                                },
                            ]

                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Comment*: \n{first_128}'
                                },
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Label*\n{very_bad}'
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f'*Sentiment Score*: \n{very_score_bad}'
                                },
                            ]
                        },
                        {
                            "type": "divider"
                        },
                        {
                            "type": "section",
                            "text":
                                {
                                    "type": "mrkdwn",
                                    "text": "A new Reddit post mentions the keyword: *"
                                            + query.replace('\"', '').capitalize() +
                                            f"*\n\n*<{postUrl}|{title}>*"
                                }
                        },
                    ]
                    requests.post('https://slack.com/api/chat.postMessage', {
                        'token': slack_token,
                        'channel': slack_channel,
                        'text': create,
                        'blocks': json.dumps(blocks) if blocks else None
                    }).json()
                else:
                    print(f'how did you get here in ths section: {crossed_out}')
                # fp.close()
            count -= 1
        else:
            print('no new posts')

    else:
        print("There's been an error with the API")


def get_reddit_time_stamp_from_messages_in_slack():
    # conversation_history = []
    # ID of the channel you want to send the message to
    # channel_id = "C046QKCC97W"

    try:
        limit = 250
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id, limit=limit)

        conversation_history = result["messages"]
        # If a message is not made by the bot, skip it since only bot message will have the reddit post timestamp
        for message in conversation_history:
            # only thing I found unique to distinguish messages
            # if message["blocks"][0]["type"] == 'section':
            time_stamp_of_reddit_message.add(message['text'])
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


def get_posts_from_pushshift(url):
    r = ''
    number_of_tries = 0
    dat = url['data']
    while True:
        try:
            # Pushshift API rate limit is 60 requests per minute(1 request per second)
            if number_of_tries <= 4:
                # Adding sleep to avoid hitting the limit
                time.sleep(1)
                r = requests.get(url)
                if r.status_code != 200:
                    number_of_tries += 1
                    print("error code", r.status_code)
                    time.sleep(7)
                    continue
                else:
                    break
            else:
                return []
        except Exception as e:
            print("error: ", e)
            time.sleep(5)
            continue
    return json.loads(r.text, strict=False) and dat


if __name__ == "__main__":

    print("Welcome to ARD - Addigys' Reddit Depository\n")
    userInput = input("To Start the Program. Please Enter Y: ")

    print("\nWelcome the program will start in a few second....")

    amount = int(input("Enter the amount of comments you would like to view\n"))
    print("NOTE: Size has be equal or less then 25 and greater than 1")

    size = amount

    while userInput == "Y" or userInput == "y":

        START = time.time()

        if size <= 25 or size >= 1:

            while True:
                # if dataQuery has spaces, need to wrap it in \"dataQuery with spaces\"
                # queries = ['jamf', 'mosyle', 'kandji', 'jamf', "\"manage apple devices\""]
                queries = ['Black Adam', 'Addigy']

                print("\n\nEnter 1 to check for new posts and comments\n"
                      "Enter 2 to exit the program\n")

                user_input = int(input('enter choice: '))
                if user_input == 1:
                    # iterating through the queries
                    for query in queries:
                        new_post_to_slack(query, size)
                    get_reddit_time_stamp_from_messages_in_slack()
                    end = time.time()
                    print(f'It took {end - START} second!')
                    exit()
                elif user_input > 1 or user_input < 1:
                    sys.exit("Wrong Choice. Restart the program to continue...")

        else:
            print("Exceeded Size Amount. Please Input an Appropriate Range of 1-25....")
    else:
        sys.exit("The Correct Option was not selected. Please Try Again...")
