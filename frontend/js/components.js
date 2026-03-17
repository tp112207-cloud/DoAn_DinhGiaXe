// ===== SHARED COMPONENTS =====
const API_BASE = '/api';

// Get current page name from URL
function getCurrentPage() {
  const path = window.location.pathname;
  const page = path.split('/').pop().replace('.html', '');
  if (!page || page === '' || page === 'index') return 'home';
  return page;
}

// Navbar HTML
function createNavbar() {
  const currentPage = getCurrentPage();
  const pages = [
    { id: 'home', label: 'Trang chủ', href: 'index.html' },
    { id: 'du-doan', label: 'Dự đoán giá', href: 'du-doan.html' },
    { id: 'phan-tich', label: 'Phân tích', href: 'phan-tich.html' },
    { id: 'lich-su', label: 'Lịch sử', href: 'lich-su.html' },
    { id: 'gioi-thieu', label: 'Giới thiệu', href: 'gioi-thieu.html' },
  ];

  const userStr = localStorage.getItem('user');
  let userHtml = '<a href="dang-nhap.html" class="btn btn-primary btn-sm">Đăng nhập</a>';
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      userHtml = `
            <span style="font-size: 0.9rem; font-weight: 500; margin-right: 12px;">Hi, ${user.name}</span>
            <button onclick="logout()" class="btn btn-outline btn-sm">Đăng xuất</button>
          `;
    } catch (e) { }
  }

  return `
    <nav class="navbar" id="navbar">
      <div class="container">
        <a href="index.html" class="nav-logo">
          <div class="logo-icon">🚗</div>
          <span>AutoVision<span style="color: var(--accent-secondary)">.AI</span></span>
        </a>
        <ul class="nav-links" id="navLinks">
          ${pages.map(p => `
            <li><a href="${p.href}" class="${currentPage === p.id ? 'active' : ''}">${p.label}</a></li>
          `).join('')}
        </ul>
        <div class="nav-actions">
          <button class="theme-toggle" id="themeToggle" title="Chuyển theme">🌙</button>
          ${userHtml}
          <button class="mobile-toggle" id="mobileToggle">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
    </nav>
  `;
}

function logout() {
  localStorage.removeItem('user');
  window.location.reload();
}

// Footer HTML
function createFooter() {
  return `
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <a href="index.html" class="nav-logo" style="margin-bottom:8px">
              <div class="logo-icon">🚗</div>
              <span>AutoVision<span style="color: var(--accent-secondary)">.AI</span></span>
            </a>
            <p>Nền tảng AI dự đoán giá xe ô tô hàng đầu Việt Nam. Sử dụng Machine Learning để đưa ra mức giá chính xác nhất.</p>
          </div>
          <div class="footer-col">
            <h4>Trang</h4>
            <a href="index.html">Trang chủ</a>
            <a href="du-doan.html">Dự đoán giá</a>
            <a href="phan-tich.html">Phân tích</a>
            <a href="lich-su.html">Lịch sử</a>
          </div>
          <div class="footer-col">
            <h4>Thông tin</h4>
            <a href="gioi-thieu.html">Giới thiệu</a>
            <a href="gioi-thieu.html#faq">FAQ</a>
            <a href="gioi-thieu.html#tech">Công nghệ</a>
          </div>
        </div>
        <div class="footer-bottom">
          <span>© 2026 AutoVision.AI - Đồ án AI Dự đoán giá xe</span>
          <span>Made with ❤️ using Python & Machine Learning</span>
        </div>
      </div>
    </footer>
  `;
}

// Initialize page
function initPage() {
  // Insert navbar
  const navPlaceholder = document.getElementById('nav-placeholder');
  if (navPlaceholder) navPlaceholder.innerHTML = createNavbar();

  // Insert footer
  const footerPlaceholder = document.getElementById('footer-placeholder');
  if (footerPlaceholder) footerPlaceholder.innerHTML = createFooter();

  // Theme toggle
  initTheme();

  // Mobile menu
  initMobileMenu();

  // Scroll animations
  initScrollAnimations();

  // Custom Cursor
  initCursorGlow();

  // Init Chatbot
  if(typeof initChatbot === 'function') {
      initChatbot();
  }
}

// ===== CHATBOT COMPONENT =====
function initChatbot() {
    const chatbotHtml = `
      <div id="aiChatbot" class="chatbot-container">
        <button id="chatbotToggle" class="chatbot-toggle">
            <span style="font-size: 1.5rem;">✨</span>
        </button>
        <div id="chatbotWindow" class="chatbot-window">
            <div class="chatbot-header">
                <div class="chatbot-header-info">
                    <span class="chatbot-icon">🤖</span>
                    <span class="chatbot-title">AutoVision AI</span>
                </div>
                <button id="chatbotClose" class="chatbot-close">✕</button>
            </div>
            <div id="chatbotMessages" class="chatbot-messages">
                <div class="chat-message bot">
                    <div class="bubble">Xin chào! Tôi có thể giúp gì cho bạn với AutoVision?</div>
                </div>
            </div>
            <div class="chatbot-input-area">
                <input type="text" id="chatbotInput" placeholder="Nhập tin nhắn..." autocomplete="off">
                <button id="chatbotSend">➤</button>
            </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', chatbotHtml);

    const toggle = document.getElementById('chatbotToggle');
    const close = document.getElementById('chatbotClose');
    const win = document.getElementById('chatbotWindow');
    const input = document.getElementById('chatbotInput');
    const sendBtn = document.getElementById('chatbotSend');
    const messagesEl = document.getElementById('chatbotMessages');

    let chatHistory = [];

    toggle.addEventListener('click', () => {
        win.classList.toggle('open');
        if (win.classList.contains('open')) input.focus();
    });

    close.addEventListener('click', () => {
        win.classList.remove('open');
    });

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) return;
        
        input.value = '';
        addMessage('user', text);
        chatHistory.push({ role: 'user', content: text });
        
        // Show loading
        const loaderId = 'loader-' + Date.now();
        messagesEl.insertAdjacentHTML('beforeend', `
            <div id="${loaderId}" class="chat-message bot">
                <div class="bubble loading">...</div>
            </div>
        `);
        messagesEl.scrollTop = messagesEl.scrollHeight;

        try {
            const res = await fetchAPI('/chat', {
                method: 'POST',
                body: JSON.stringify({ messages: chatHistory })
            });

            document.getElementById(loaderId)?.remove();

            if (res && res.response) {
                addMessage('bot', res.response);
                chatHistory.push({ role: 'model', content: res.response });
            } else {
                addMessage('bot', 'Xin lỗi, tôi đang gặp lỗi kết nối.', true);
            }
        } catch(e) {
            document.getElementById(loaderId)?.remove();
            addMessage('bot', 'Đã xảy ra lỗi.', true);
        }
    }

    function addMessage(sender, text, isError = false) {
        let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\n/g, '<br>');
        
        // Minimal code block rendering if exists
        formattedText = formattedText.replace(/\`(.*?)\`/g, '<code>$1</code>');

        messagesEl.insertAdjacentHTML('beforeend', `
            <div class="chat-message ${sender}">
                <div class="bubble ${isError ? 'error' : ''}">${formattedText}</div>
            </div>
        `);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Theme management
function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);

  const btn = document.getElementById('themeToggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('themeToggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Mobile menu
function initMobileMenu() {
  const toggle = document.getElementById('mobileToggle');
  const links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
    });
    // Close on link click
    links.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => links.classList.remove('open'));
    });
  }
}

// Scroll reveal animations
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.reveal').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'all 0.6s ease-out';
    observer.observe(el);
  });
}

// Utility: Format price (đã là VND)
function formatPrice(price_vnd) {
  if (price_vnd >= 1000000000) return (price_vnd / 1000000000).toFixed(2).replace('.00', '') + ' Tỷ';
  if (price_vnd >= 1000000) return (price_vnd / 1000000).toFixed(0) + ' Triệu';
  return formatNumber(Math.round(price_vnd)) + ' VNĐ';
}

// Utility: Format number with commas
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Utility: Fetch from API
async function fetchAPI(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    return null;
  }
}

// Prediction history (localStorage)
function savePrediction(input, result) {
  const history = JSON.parse(localStorage.getItem('predictions') || '[]');
  history.unshift({
    id: Date.now(),
    timestamp: new Date().toISOString(),
    input,
    result
  });
  // Keep last 50
  if (history.length > 50) history.pop();
  localStorage.setItem('predictions', JSON.stringify(history));
}

function getPredictions() {
  return JSON.parse(localStorage.getItem('predictions') || '[]');
}

function clearPredictions() {
  localStorage.removeItem('predictions');
}

// ===== CURSOR GLOW EFFECT =====
function initCursorGlow() {
  if (window.innerWidth < 768) return;

  const glow = document.createElement('div');
  glow.className = 'cursor-glow';
  document.body.appendChild(glow);

  let mouseX = 0;
  let mouseY = 0;
  let ballX = 0;
  let ballY = 0;
  const speed = 0.1;

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  function animate() {
    let distX = mouseX - ballX;
    let distY = mouseY - ballY;

    ballX = ballX + (distX * speed);
    ballY = ballY + (distY * speed);

    glow.style.left = ballX + 'px';
    glow.style.top = ballY + 'px';

    requestAnimationFrame(animate);
  }
  animate();
}

// Init on DOM ready
document.addEventListener('DOMContentLoaded', initPage);
