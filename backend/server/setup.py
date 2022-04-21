from gqlalchemy import (
    Memgraph,
    MemgraphKafkaStream,
    MemgraphTrigger,
)
from gqlalchemy.models import (
    TriggerEventType,
    TriggerEventObject,
    TriggerExecutionPhase,
)
from time import sleep
import logging
import os

BROKER = os.getenv("BROKER", "kafka")

log = logging.getLogger("server")


def connect_to_memgraph(memgraph_ip, memgraph_port):
    memgraph = Memgraph(host=memgraph_ip, port=int(memgraph_port))
    while True:
        try:
            if memgraph._get_cached_connection().is_active():
                return memgraph
        except:
            log.info("Memgraph probably isn't running.")
            sleep(1)


def run(memgraph):
    try:
        memgraph.drop_database()

        log.info("Setting up PageRank")
        memgraph.execute("CALL pagerank_online.set(100, 0.2) YIELD *")
        memgraph.execute(
            """CREATE TRIGGER pagerank_trigger 
               BEFORE COMMIT 
               EXECUTE CALL pagerank_online.update(createdVertices, createdEdges, deletedVertices, deletedEdges) YIELD *
               SET node.rank = rank
               CALL publisher.update_rank(node, rank);"""
        )

        log.info("Creating stream connections on Memgraph")
        stream = MemgraphKafkaStream(
            name="twitter",
            topics=["twitter"],
            transform="twitter.tweet",
            bootstrap_servers="'kafka:9092'",
        )

        memgraph.create_stream(stream)
        memgraph.start_stream(stream)

        log.info("Creating triggers on Memgraph")
        trigger = MemgraphTrigger(
            name="created_trigger",
            event_type=TriggerEventType.CREATE,
            event_object=TriggerEventObject.ALL,
            execution_phase=TriggerExecutionPhase.AFTER,
            statement="CALL publisher.create(createdObjects)",
        )
        memgraph.create_trigger(trigger)

    except Exception as e:
        log.info(f"Error on stream and trigger creation: {e}")
        pass
