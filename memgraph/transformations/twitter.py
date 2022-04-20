import mgp
import json


@mgp.transformation
def tweet(messages: mgp.Messages,) -> mgp.Record():
    result_queries = []

    for i in range(messages.total_messages()):
        message = messages.message_at(i)
        tweet_dict = json.loads(message.payload().decode("utf8"))
        result_queries.append(
            mgp.Record(
                query=(
                    "MERGE (u:User {id: $user_id, username: $user_username}) "
                    "MERGE (t:Tweet {id: $tweet_id}) "
                    "SET t.text = $tweet_text "
                    "MERGE (u)-[:TWEETED]->(t)"
                ),
                parameters={
                    "user_id": tweet_dict["user_id"],
                    "user_username": tweet_dict["user_username"],
                    "tweet_id": tweet_dict["tweet_id"],
                    "tweet_text": tweet_dict["tweet_text"],
                    "type": tweet_dict["type"],
                    "original_tweet_id": tweet_dict["original_tweet_id"],
                },
            )
        )
        if tweet_dict["type"] != "ORIGINAL":
            result_queries.append(
                mgp.Record(
                    query=(
                        "MERGE (t1:Tweet {id: $tweet_id}) "
                        "MERGE (t2:Tweet {id: $original_tweet_id}) "
                        "MERGE (t2)-[r:RETWEETED]->(t1)"
                    ),
                    parameters={
                        "tweet_id": tweet_dict["tweet_id"],
                        "rel_type": tweet_dict["type"],
                        "original_tweet_id": tweet_dict["original_tweet_id"],
                    },
                )
            )
    return result_queries
