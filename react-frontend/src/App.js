import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post('http://localhost/ask', {
        question: question,
      });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error asking question:', error);
      setAnswer('Error asking question');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Ask a Question</h1>
        <form onSubmit={handleSubmit}>
          <label>
            Question:
            <input type="text" value={question} onChange={handleQuestionChange} size="50" />
          </label>
          <button type="submit">Ask</button>
        </form>
        <h2>Answer</h2>
        <p>{answer}</p>
      </header>
    </div>
  );
}

export default App;
