import { useState } from 'react';

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  isLoading: boolean;
  disabled: boolean;
}

export default function QuestionInput({ onSubmit, isLoading, disabled }: QuestionInputProps) {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !disabled) {
      onSubmit(question.trim());
      setQuestion('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="question-form">
      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question about your document..."
        disabled={disabled || isLoading}
        className="question-input"
        rows={3}
      />
      <button
        type="submit"
        disabled={!question.trim() || disabled || isLoading}
        className="submit-button"
      >
        {isLoading ? 'Generating Answer...' : 'Ask Question'}
      </button>
    </form>
  );
}
