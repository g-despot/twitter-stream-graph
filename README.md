<h1 align="center">
 🔍 Twitter Stream Graph 🔍
</h1>

<p align="center">
  <a href="https://github.com/g-despot/twitter-network-analysis/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/g-despot/twitter-network-analysis" alt="license" title="license"/>
  </a>
  <a href="https://github.com/g-despot/twitter-network-analysis">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="build" title="build"/>
  </a>
</p>

<p align="center">
  <a href="https://twitter.com/intent/follow?screen_name=memgraphdb">
    <img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Follow @memgraphdb"/>
  </a>
  <a href="https://memgr.ph/join-discord">
    <img src="https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"/>
  </a>
</p>

A web application that uses Memgraph, a graph stream-processing platform, to
ingest real-time data from Twitter. Data is streamed via [Apache
Kafka](https://kafka.apache.org/) and stream processing is performed with
Memgraph.

## App architecture

<p align="left">
  <img width="600px" src="https://raw.githubusercontent.com/memgraph/twitter-network-analysis/main/img/stream-processing-arc-01-01.png" alt="memgraph-tutorial-twitter-app-architecture">
</p>

## Prerequisites

You will need:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with
  Docker Desktop on Windows and macOS)

## Running the app

### With a bash script

1. You can start everything but the frontend client and Twitter scraper by **running a bash script**:

```
bash docker_build.sh
```

2. Now it's time to start scraping Twitter for a specific hashtag:

```
docker-compose up stream
```

3. After that, in another window, start the React client with:

```
docker-compose up frontend
```

The React application will be running on `http://localhost:3000`.

## Dynamic PageRank visualization

![memgraph-tutorial-pagerank-stream](https://raw.githubusercontent.com/memgraph/twitter-network-analysis/main/img/memgraph-tutorial-pagerank-stream.gif)
