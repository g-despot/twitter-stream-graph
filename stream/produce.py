from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable
from time import sleep
import argparse
import json
import os
import tweepy

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAL6WbAEAAAAAk6l%2FJs5FHIaruNNZAsypC5DGZSQ%3DqKoDmp7lf24GmSNMJchzKsVSgZrrRRIgd8t71UirM32Z8PbyHI"
KAFKA_IP = os.getenv("KAFKA_IP", "localhost")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9093")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "tweets")

args = None
producer = None
twitter_client = None
twitter_stream = None


def get_admin_client(ip, port):
    retries = 30
    while True:
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=ip + ":" + port, client_id="test"
            )
            return admin_client
        except NoBrokersAvailable:
            retries -= 1
            if not retries:
                raise
            sleep(1)


def create_topic(ip, port, topic):
    admin_client = get_admin_client(ip, port)
    my_topic = [NewTopic(name=topic, num_partitions=1, replication_factor=1)]
    try:
        admin_client.create_topics(new_topics=my_topic, validate_only=False)
    except TopicAlreadyExistsError:
        pass
    print("All topics:")
    print(admin_client.list_topics())


def create_kafka_producer(ip, port):
    retries = 30
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers=ip + ":" + port)
            return producer
        except NoBrokersAvailable:
            retries -= 1
            if not retries:
                raise
            print("Failed to connect to Kafka")
            sleep(1)


def process_referenced_tweets(referenced_tweets, original_tweet_id):
    for referenced_tweet in referenced_tweets:
        tweet = twitter_client.get_tweet(
            id=referenced_tweet.id, tweet_fields=["author_id"]
        ).data

        user = twitter_client.get_user(id=tweet.author_id).data
        message = {
            "user_id": user.id,
            "user_username": user.username,
            "tweet_id": tweet.id,
            "tweet_text": tweet.text,
            "type": referenced_tweet.type,
            "original_tweet_id": original_tweet_id,
        }
        print(f"Message: {message}")

        producer.send(KAFKA_TOPIC, json.dumps(message).encode("utf8"))
        producer.flush()


def process_tweet(tweet):
    user = twitter_client.get_user(id=tweet.author_id).data
    message = {
        "user_id": user.id,
        "user_username": user.username,
        "tweet_id": tweet.id,
        "tweet_text": tweet.text,
        "type": "ORIGINAL",
        "original_tweet_id": "ORIGINAL",
    }
    print(f"Message: {message}")

    if tweet.referenced_tweets:
        process_referenced_tweets(tweet.referenced_tweets, tweet.id)

    producer.send(KAFKA_TOPIC, json.dumps(message).encode("utf8"))
    producer.flush()


class MyStreamListener(tweepy.StreamingClient):
    def __init__(self, n_tweets):
        super().__init__(BEARER_TOKEN)
        self.n_tweets = n_tweets

    def on_tweet(self, tweet):
        try:
            process_tweet(tweet)
            sleep(args.stream_delay)
        except Exception as e:
            print(f"Error: {e}")

        self.n_tweets -= 1
        if self.n_tweets == 0:
            self.disconnect()

    def on_errors(self, error):
        print(f"Twitter stream disconnected with error: {error}")
        sleep(args.stream_delay)
        return False


def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))
    if x < 0.0 or x > 3.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 3.0]" % (x,))
    return x


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stream-delay",
        type=restricted_float,
        default=2.0,
        help="Seconds to wait before producing a new message (MIN=0.0, MAX=3.0)",
    )
    value = parser.parse_args()
    return value


def main():
    global args
    args = parse_arguments()

    create_topic(KAFKA_IP, KAFKA_PORT, KAFKA_TOPIC)
    global producer
    producer = create_kafka_producer(KAFKA_IP, KAFKA_PORT)
    print("Created Kafka producer")

    global twitter_client, twitter_stream
    twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)
    twitter_stream = MyStreamListener(1)

    hashtags = ["#Ukraine"]
    print(f"Watch for hashtags: {hashtags}")
    twitter_stream.add_rules(tweepy.StreamRule(hashtags))

    print("Start stream")
    twitter_stream.filter(tweet_fields=["author_id", "referenced_tweets"])
    print("Exiting app")


if __name__ == "__main__":
    main()
