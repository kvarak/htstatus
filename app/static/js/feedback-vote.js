// Toggle the user's upvote on a feedback item; updates the score and the button.
// Buttons with data-show-label also switch their text.
function vote(button, feedbackId) {
  fetch(`/feedback/${feedbackId}/vote`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({vote_type: 'up'})
  })
    .then(response => response.json())
    .then(data => {
      if (!data.success) return;
      document.getElementById(`score-${feedbackId}`).textContent = data.vote_score;
      const up = data.user_vote === 'up';
      button.classList.toggle('btn-success', up);
      button.classList.toggle('btn-outline-success', !up);
      button.title = up ? 'Remove your upvote' : 'Upvote this feedback';
      if ('showLabel' in button.dataset) {
        button.innerHTML = '↑ <i class="fas fa-thumbs-up"></i> ' + (up ? 'Remove Upvote' : 'Upvote');
      }
    })
    .catch(error => console.error('Vote failed:', error));
}
