// ── Telegram WebApp SDK ──
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor('#232023');
tg.setBackgroundColor('#232023');

const AUTH = `tma ${tg.initData}`;

// ── API Helper ──
async function api(method, path, body = null) {
    const opts = {
        method,
        headers: {
            'Authorization': AUTH,
            'Content-Type': 'application/json',
        },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`/api${path}`, opts);
    return res.json();
}

// ── Toast ──
function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2500);
}

// ── Tab Switching ──
const tabs = document.querySelectorAll('.tab');
const views = document.querySelectorAll('.view');

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.dataset.tab;
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        views.forEach(v => v.classList.remove('active'));
        document.getElementById(`view-${target}`).classList.add('active');
        loadTab(target);
    });
});

function loadTab(tab) {
    switch (tab) {
        case 'dashboard': loadDashboard(); break;
        case 'payments': loadPayments(); break;
        case 'users': loadUsers(); break;
        case 'settings': loadSettings(); break;
    }
}

// ── Format Helpers ──
function fmtMoney(n) {
    return Math.round(n).toLocaleString('uz').replace(/,/g, ' ');
}

function fmtDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('uz', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function showLoader(container) {
    container.innerHTML = '<div class="loader"><div class="spinner"></div>Yuklanmoqda...</div>';
}

function showEmpty(container, icon, text) {
    container.innerHTML = `<div class="empty"><div class="empty-icon">${icon}</div><div class="empty-text">${text}</div></div>`;
}

// ══════════════════════════════════════
// ── DASHBOARD ──
// ══════════════════════════════════════
async function loadDashboard() {
    const container = document.getElementById('dashboard-content');
    showLoader(container);

    const data = await api('GET', '/stats');
    if (data.error) {
        showEmpty(container, '⚠️', 'Ma\'lumot yuklanmadi');
        return;
    }

    container.innerHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${data.total_users || 0}</div>
                <div class="stat-label">Foydalanuvchilar</div>
            </div>
            <div class="stat-card accent">
                <div class="stat-value">${fmtMoney(data.total_revenue || 0)}</div>
                <div class="stat-label">Tushum (UZS)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.total_payments || 0}</div>
                <div class="stat-label">Tasdiqlangan</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.pending_payments || 0}</div>
                <div class="stat-label">Kutilayotgan</div>
            </div>
        </div>
    `;
}

// ══════════════════════════════════════
// ── PAYMENTS ──
// ══════════════════════════════════════
async function loadPayments() {
    const container = document.getElementById('payments-content');
    showLoader(container);

    const data = await api('GET', '/payments');
    if (data.error) {
        showEmpty(container, '⚠️', 'Yuklanmadi');
        return;
    }

    const payments = data.payments || [];
    if (!payments.length) {
        showEmpty(container, '💳', 'Kutilayotgan to\'lovlar yo\'q');
        return;
    }

    container.innerHTML = payments.map(p => `
        <div class="card" id="payment-${p.id}">
            <div class="card-row">
                <div class="card-info">
                    <div class="card-name">@${p.end_user.username || p.end_user.telegram_id}</div>
                    <div class="card-meta">${fmtMoney(p.amount)} UZS · ${p.channel.title} · ${fmtDate(p.created_at)}</div>
                </div>
            </div>
            <div style="display:flex;gap:8px;margin-top:10px">
                ${p.screenshot_file_id ? `<button class="btn btn-ghost btn-sm" onclick="viewScreenshot(${p.id})">📷 Chek</button>` : ''}
                <button class="btn btn-success btn-sm" onclick="approvePayment(${p.id})">✅ Tasdiqlash</button>
                <button class="btn btn-danger btn-sm" onclick="rejectPayment(${p.id})">❌ Rad</button>
            </div>
        </div>
    `).join('');
}

async function viewScreenshot(paymentId) {
    const modal = document.getElementById('screenshot-modal');
    const img = document.getElementById('screenshot-img');
    img.src = '';
    modal.classList.remove('hidden');

    const data = await api('GET', `/payments/${paymentId}/screenshot`);
    if (data.url) {
        img.src = data.url;
    } else {
        img.alt = 'Rasm yuklanmadi';
    }
}

async function approvePayment(paymentId) {
    const card = document.getElementById(`payment-${paymentId}`);
    const btns = card.querySelectorAll('.btn');
    btns.forEach(b => b.disabled = true);

    const data = await api('POST', `/payments/${paymentId}/approve`);
    if (data.ok) {
        card.remove();
        toast('To\'lov tasdiqlandi!');
        tg.HapticFeedback.notificationOccurred('success');
    } else {
        toast(data.error || 'Xatolik', 'error');
        btns.forEach(b => b.disabled = false);
    }
}

async function rejectPayment(paymentId) {
    const card = document.getElementById(`payment-${paymentId}`);
    const btns = card.querySelectorAll('.btn');
    btns.forEach(b => b.disabled = true);

    const data = await api('POST', `/payments/${paymentId}/reject`);
    if (data.ok) {
        card.remove();
        toast('To\'lov rad etildi');
        tg.HapticFeedback.notificationOccurred('warning');
    } else {
        toast(data.error || 'Xatolik', 'error');
        btns.forEach(b => b.disabled = false);
    }
}

// ══════════════════════════════════════
// ── USERS ──
// ══════════════════════════════════════
let usersCache = [];

async function loadUsers() {
    const container = document.getElementById('users-content');
    showLoader(container);

    const data = await api('GET', '/users');
    if (data.error) {
        showEmpty(container, '⚠️', 'Yuklanmadi');
        return;
    }

    usersCache = data.users || [];
    if (!usersCache.length) {
        showEmpty(container, '👥', 'Hali foydalanuvchilar yo\'q');
        return;
    }

    renderUsers(container);
}

function renderUsers(container) {
    container.innerHTML = usersCache.map(u => `
        <div class="card" id="user-${u.id}">
            <div class="card-row">
                <div class="card-info">
                    <div class="card-name">
                        @${u.username || u.telegram_id}
                        ${u.banned ? '<span class="badge badge-danger">Ban</span>' : ''}
                    </div>
                    <div class="card-meta">${u.language.toUpperCase()} · ${fmtDate(u.created_at)}</div>
                </div>
                <div class="card-actions">
                    <button class="btn btn-ghost btn-icon btn-sm" onclick="openMessageModal(${u.id}, '${(u.username || u.telegram_id)}')">
                        💬
                    </button>
                    ${u.banned
                        ? `<button class="btn btn-success btn-icon btn-sm" onclick="toggleBan(${u.id}, false)">🔓</button>`
                        : `<button class="btn btn-danger btn-icon btn-sm" onclick="toggleBan(${u.id}, true)">🚫</button>`
                    }
                </div>
            </div>
        </div>
    `).join('');
}

async function toggleBan(userId, ban) {
    const endpoint = ban ? 'ban' : 'unban';
    const data = await api('POST', `/users/${userId}/${endpoint}`);
    if (data.ok) {
        const user = usersCache.find(u => u.id === userId);
        if (user) user.banned = ban;
        renderUsers(document.getElementById('users-content'));
        toast(ban ? 'Foydalanuvchi bloklandi' : 'Blokdan chiqarildi');
        tg.HapticFeedback.notificationOccurred(ban ? 'warning' : 'success');
    } else {
        toast(data.error || 'Xatolik', 'error');
    }
}

// ── Individual Message ──
let messageTargetId = null;

function openMessageModal(userId, username) {
    messageTargetId = userId;
    document.getElementById('modal-username').textContent = `@${username}`;
    document.getElementById('modal-text').value = '';
    document.getElementById('message-modal').classList.remove('hidden');
    document.getElementById('modal-text').focus();
}

function closeMessageModal() {
    document.getElementById('message-modal').classList.add('hidden');
    messageTargetId = null;
}

async function sendMessage() {
    if (!messageTargetId) return;

    const text = document.getElementById('modal-text').value.trim();
    if (!text) return;

    const sendBtn = document.getElementById('modal-send');
    sendBtn.disabled = true;

    const data = await api('POST', `/users/${messageTargetId}/message`, { text });
    if (data.ok) {
        toast('Xabar yuborildi!');
        tg.HapticFeedback.notificationOccurred('success');
        closeMessageModal();
    } else {
        toast(data.error || 'Xatolik', 'error');
    }

    sendBtn.disabled = false;
}

// ── Broadcast ──
function openBroadcastModal() {
    messageTargetId = null;
    document.getElementById('modal-username').textContent = `Barcha foydalanuvchilarga (${usersCache.filter(u => !u.banned).length} ta)`;
    document.getElementById('modal-text').value = '';
    document.getElementById('message-modal').classList.remove('hidden');
    document.getElementById('modal-send').onclick = sendBroadcast;
    document.getElementById('modal-text').focus();
}

async function sendBroadcast() {
    const text = document.getElementById('modal-text').value.trim();
    if (!text) return;

    const sendBtn = document.getElementById('modal-send');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Yuborilmoqda...';

    const data = await api('POST', '/broadcast', { text });
    if (data.ok) {
        toast(`${data.sent} ta userga yuborildi!`);
        tg.HapticFeedback.notificationOccurred('success');
        closeMessageModal();
    } else {
        toast(data.error || 'Xatolik', 'error');
    }

    sendBtn.disabled = false;
    sendBtn.textContent = 'Yuborish';
    // Reset onclick to individual
    sendBtn.onclick = sendMessage;
}

// ══════════════════════════════════════
// ── SETTINGS ──
// ══════════════════════════════════════
async function loadSettings() {
    const container = document.getElementById('settings-content');
    showLoader(container);

    const data = await api('GET', '/settings');
    if (data.error) {
        showEmpty(container, '⚠️', 'Yuklanmadi');
        return;
    }

    container.innerHTML = `
        <div style="text-align:center;margin-bottom:20px;">
            <div style="font-size:16px;font-weight:600;">@${data.bot_username || '—'}</div>
            ${data.channel ? `<div style="font-size:13px;color:var(--light-400);">📢 ${data.channel.title}</div>` : ''}
        </div>
        <div class="form-group">
            <label class="form-label">Salomlash xabari</label>
            <textarea class="form-textarea" id="set-welcome" rows="3">${data.welcome_message || ''}</textarea>
        </div>
        <div class="form-group">
            <label class="form-label">Karta raqami</label>
            <input class="form-input" id="set-card" type="text" value="${data.card_number || ''}" placeholder="8600 0000 0000 0000" maxlength="19">
        </div>
        ${data.channel ? `
        <div class="form-group">
            <label class="form-label">Narx (UZS)</label>
            <input class="form-input" id="set-price" type="number" value="${data.channel.price}" min="1000">
        </div>
        ` : ''}
        <button class="btn btn-primary btn-full" onclick="saveSettings()">Saqlash</button>
    `;
}

async function saveSettings() {
    const body = {
        welcome_message: document.getElementById('set-welcome')?.value,
        card_number: document.getElementById('set-card')?.value,
    };

    const priceEl = document.getElementById('set-price');
    if (priceEl) body.price = Number(priceEl.value);

    const data = await api('PUT', '/settings', body);
    if (data.ok) {
        toast('Sozlamalar saqlandi!');
        tg.HapticFeedback.notificationOccurred('success');
    } else {
        toast(data.error || 'Xatolik', 'error');
    }
}

// ── Screenshot Modal Close ──
document.getElementById('screenshot-close')?.addEventListener('click', () => {
    document.getElementById('screenshot-modal').classList.add('hidden');
});

// ── Message Modal Buttons ──
document.getElementById('modal-cancel')?.addEventListener('click', closeMessageModal);
document.getElementById('modal-send')?.addEventListener('click', sendMessage);

// ── Initial Load ──
loadDashboard();
