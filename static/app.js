document.addEventListener('DOMContentLoaded', () => {
  const passwordToggle = document.querySelector('.toggle-password');
  if (passwordToggle) {
    passwordToggle.addEventListener('click', () => {
      const input = passwordToggle.parentElement.querySelector('input');
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      passwordToggle.textContent = visible ? '◉' : '◌';
      passwordToggle.setAttribute('aria-label', visible ? 'Show password' : 'Hide password');
    });
  }

  const welcome = document.querySelector('[data-welcome-loader]');
  if (welcome && window.SHADOWNET_WELCOME_REDIRECT) {
    const countdown = document.getElementById('countdown');
    let remaining = Number(window.SHADOWNET_WELCOME_SECONDS || 5);
    const timer = setInterval(() => {
      remaining -= 1;
      if (countdown) countdown.textContent = Math.max(remaining, 0);
      if (remaining <= 0) {
        clearInterval(timer);
        window.location.href = window.SHADOWNET_WELCOME_REDIRECT;
      }
    }, 1000);
  }

  const modal = document.getElementById('assistantModal');
  const openButtons = document.querySelectorAll('[data-open-assistant]');
  const closeButtons = document.querySelectorAll('[data-close-assistant]');
  const form = document.getElementById('assistantForm');
  const input = document.getElementById('assistantInput');
  const messages = document.getElementById('assistantMessages');

  const openModal = () => {
    if (!modal) return;
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    if (input) input.focus();
  };
  const closeModal = () => {
    if (!modal) return;
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
  };
  openButtons.forEach(button => button.addEventListener('click', openModal));
  closeButtons.forEach(button => button.addEventListener('click', closeModal));
  if (modal) modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

  if (form && input && messages) {
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      const userBubble = document.createElement('div');
      userBubble.className = 'user-message';
      userBubble.textContent = text;
      messages.appendChild(userBubble);
      input.value = '';
      messages.scrollTop = messages.scrollHeight;
      try {
        const response = await fetch('/api/assistant', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({message: text})
        });
        const data = await response.json();
        const botBubble = document.createElement('div');
        botBubble.className = 'bot-message';
        botBubble.textContent = data.reply || 'I could not process that question.';
        messages.appendChild(botBubble);
      } catch (_error) {
        const botBubble = document.createElement('div');
        botBubble.className = 'bot-message';
        botBubble.textContent = 'Assistant connection failed. Try again.';
        messages.appendChild(botBubble);
      }
      messages.scrollTop = messages.scrollHeight;
    });
  }
});
