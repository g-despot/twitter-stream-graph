//import { useState } from 'react';
import "./App.css";
import PageRank from "./components/PageRank";
import React from "react";
import io from "socket.io-client";

export default class App extends React.Component {
  render() {
    const socket = io("http://localhost:5000/", { transports: ["websocket"] });
    return (
      <div
        className="App">
        <PageRank socket={socket} />
      </div>
    );
  }
}
