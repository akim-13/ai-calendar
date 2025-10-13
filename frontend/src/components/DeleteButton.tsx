import React, { useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../api";

const DeleteButton: React.FC = () => {
  const [response, setResponse] = useState<string | null>(null);

  const sendRequest = async () => {
    try {
      //in quotes add the url to the request, for delete, the ending means /delete/(task id)
      const res = await axios.delete<{ message: string }>(`${API_BASE_URL}/delete/1`);
      setResponse(res.data.message);
    } catch (error) {
      console.error("Error sending request:", error);
      setResponse("Failed to send request.");
    }
  };

  return (
    <div>
      <button onClick={sendRequest}>Send API Request</button>
      {response && <p>Response: {response}</p>}
    </div>
  );
};

export default DeleteButton;
