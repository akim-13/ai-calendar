import React, { useState } from "react";
import axios from "axios";

const CompleteButton: React.FC = () => {
  const [response, setResponse] = useState<string | null>(null);

  const sendRequest = async () => {
    try {
      //in quotes add the url to the request, for delete, the ending means /delete/(task id)
      const res = await axios.put<{ message: string }>("http://127.0.0.1:8000/update/1");
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

export default CompleteButton;