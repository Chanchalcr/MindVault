interface AnswerDisplayProps {
  question: string;
  answer: string;
}

export default function AnswerDisplay({ question, answer }: AnswerDisplayProps) {
  return (
    <div className="answer-container">
      <div className="question-display">
        <h3>Question:</h3>
        <p>{question}</p>
      </div>
      <div className="answer-display">
        <h3>Answer:</h3>
        <p>{answer}</p>
      </div>
    </div>
  );
}
