/* Getolog Moderator Mini App */

const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.setHeaderColor('#232023');
tg.setBackgroundColor('#232023');

const AUTH = `tma ${tg.initData}`;

// ── API Helper ──
async function api(method, path, body) {
    const opts = {
        method,
        headers: { 'Authorization': AUTH, 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    try {
        const res = await fetch(`/api/mod${path}`, opts);
        if (res.status === 401) { showSessionExpired(); return { error: 'unauthorized' }; }
        return await res.json();
    } catch (e) {
        return { error: e.message };
    }
}

// ── UI Helpers ──
function toast(msg, type) {
    type = type || 'success';
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function() { el.remove(); }, 2500);
}

function fmtMoney(n) {
    return Math.round(n).toLocaleString('uz').replace(/,/g, ' ');
}

function fmtDate(iso) {
    if (!iso) return '\u2014';
    return new Date(iso).toLocaleDateString('uz', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function showLoader(container) {
    container.innerHTML = '<div class="loader"><div class="spinner"></div>Yuklanmoqda...</div>';
}

function showEmpty(container, icon, text) {
    container.innerHTML = '<div class="empty"><div class="empty-icon">' + icon + '</div><div class="empty-text">' + text + '</div></div>';
}

function showSessionExpired() {
    document.querySelector('main').innerHTML =
        '<div class="empty" style="margin-top:80px;">' +
        '<div class="empty-icon">\uD83D\uDD12</div>' +
        '<div class="empty-text">Sessiya tugagan. Botda /modlog orqali qayta kiring.</div>' +
        '</div>';
    document.querySelector('.tab-bar').style.display = 'none';
}

// ── Tab Switching ──
var tabs = document.querySelectorAll('.tab');
var views = document.querySelectorAll('.view');

tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
        var target = tab.dataset.tab;
        tabs.forEach(function(t) { t.classList.remove('active'); });
        tab.classList.add('active');
        views.forEach(function(v) { v.classList.remove('active'); });
        document.getElementById('view-' + target).classList.add('active');
        loadTab(target);
    });
});

function loadTab(tab) {
    if (tab === 'stats') loadStats();
    else if (tab === 'admins') loadAdmins();
    else if (tab === 'bots') loadBots();
    else if (tab === 'settings') loadSettings();
}

// ══════════════════════
// ── STATS TAB ──
// ══════════════════════
async function loadStats() {
    var c = document.getElementById('stats-content');
    showLoader(c);

    var data = await api('GET', '/stats');
    if (data.error) { showEmpty(c, '\u26A0\uFE0F', "Ma'lumot yuklanmadi"); return; }

    c.innerHTML =
        '<div class="stats-grid">' +
        '<div class="stat-card"><div class="stat-value">' + (data.total_admins || 0) + '</div><div class="stat-label">Adminlar</div></div>' +
        '<div class="stat-card accent"><div class="stat-value">' + (data.paid_admins || 0) + '</div><div class="stat-label">Pullik adminlar</div></div>' +
        '<div class="stat-card"><div class="stat-value">' + (data.total_bots || 0) + '</div><div class="stat-label">Aktiv botlar</div></div>' +
        '<div class="stat-card"><div class="stat-value">' + (data.total_end_users || 0) + '</div><div class="stat-label">End userlar</div></div>' +
        '<div class="stat-card"><div class="stat-value">' + (data.total_payments || 0) + '</div><div class="stat-label">Tasdiqlangan</div></div>' +
        '<div class="stat-card accent"><div class="stat-value">' + fmtMoney(data.total_revenue || 0) + '</div><div class="stat-label">Tushum (UZS)</div></div>' +
        '<div class="stat-card"><div class="stat-value">' + (data.active_subscriptions || 0) + '</div><div class="stat-label">Aktiv obunalar</div></div>' +
        '</div>';
}

// ══════════════════════
// ── ADMINS TAB ──
// ══════════════════════
var adminsCache = [];

async function loadAdmins() {
    var c = document.getElementById('admins-content');
    showLoader(c);

    var data = await api('GET', '/admins');
    if (data.error) { showEmpty(c, '\u26A0\uFE0F', 'Yuklanmadi'); return; }

    adminsCache = data.admins || [];
    if (!adminsCache.length) { showEmpty(c, '\uD83D\uDC65', "Hali adminlar yo'q"); return; }
    renderAdmins(c);
}

function renderAdmins(container) {
    var html = '';
    adminsCache.forEach(function(a) {
        var planClass = a.plan === 'free' ? 'warning' : 'success';
        var banBtn = a.banned
            ? '<button class="btn btn-success btn-icon btn-sm" onclick="toggleAdminBan(' + a.id + ', false)">\uD83D\uDD13</button>'
            : '<button class="btn btn-danger btn-icon btn-sm" onclick="toggleAdminBan(' + a.id + ', true)">\uD83D\uDEAB</button>';

        html += '<div class="card" id="admin-' + a.id + '">' +
            '<div class="card-row"><div class="card-info">' +
            '<div class="card-name">@' + (a.username || a.telegram_id) +
            (a.banned ? ' <span class="badge badge-danger">Ban</span>' : '') +
            ' <span class="badge badge-' + planClass + '">' + a.plan + '</span></div>' +
            '<div class="card-meta">' + (a.full_name || '\u2014') + ' \u00B7 ' + a.bot_count + ' bot \u00B7 ' + fmtDate(a.created_at) + '</div>' +
            '</div><div class="card-actions">' + banBtn + '</div></div></div>';
    });
    container.innerHTML = html;
}

async function toggleAdminBan(adminId, ban) {
    var endpoint = ban ? 'ban' : 'unban';
    var data = await api('POST', '/admins/' + adminId + '/' + endpoint);
    if (data.ok) {
        var admin = adminsCache.find(function(a) { return a.id === adminId; });
        if (admin) admin.banned = ban;
        renderAdmins(document.getElementById('admins-content'));
        toast(ban ? 'Admin bloklandi' : 'Blokdan chiqarildi');
        try { tg.HapticFeedback.notificationOccurred(ban ? 'warning' : 'success'); } catch(e) {}
    } else {
        toast(data.error || 'Xatolik', 'error');
    }
}

// ══════════════════════
// ── BOTS TAB ──
// ══════════════════════
async function loadBots() {
    var c = document.getElementById('bots-content');
    showLoader(c);

    var data = await api('GET', '/bots');
    if (data.error) { showEmpty(c, '\u26A0\uFE0F', 'Yuklanmadi'); return; }

    var bots = data.bots || [];
    if (!bots.length) { showEmpty(c, '\uD83E\uDD16', "Aktiv botlar yo'q"); return; }

    var html = '';
    bots.forEach(function(b) {
        var channels = b.channels.map(function(ch) { return ch.title; }).join(', ');
        html += '<div class="card"><div class="card-row"><div class="card-info">' +
            '<div class="card-name">@' + (b.bot_username || '\u2014') + '</div>' +
            '<div class="card-meta">Egasi: @' + (b.owner_username || b.owner_telegram_id) +
            (channels ? ' \u00B7 ' + channels : '') + '</div>' +
            '</div></div></div>';
    });
    c.innerHTML = html;
}

// ══════════════════════
// ── SETTINGS TAB ──
// ══════════════════════
function loadSettings() {
    var c = document.getElementById('settings-content');
    c.innerHTML =
        '<div class="form-group">' +
        '<label class="form-label">Joriy parol</label>' +
        '<input class="form-input" id="set-current-pwd" type="password" placeholder="Joriy parolni kiriting">' +
        '</div>' +
        '<div class="form-group">' +
        '<label class="form-label">Yangi parol</label>' +
        '<input class="form-input" id="set-new-pwd" type="password" placeholder="Yangi parolni kiriting (kamida 4 belgi)">' +
        '</div>' +
        '<button class="btn btn-primary btn-full" id="btn-change-pwd" onclick="changePassword()">Parolni o\'zgartirish</button>';
}

async function changePassword() {
    var current = document.getElementById('set-current-pwd').value.trim();
    var newPwd = document.getElementById('set-new-pwd').value.trim();
    var btn = document.getElementById('btn-change-pwd');

    if (!current || !newPwd) { toast("Barcha maydonlarni to'ldiring", 'error'); return; }
    if (newPwd.length < 4) { toast('Parol kamida 4 ta belgi', 'error'); return; }

    btn.disabled = true;
    btn.textContent = 'Saqlanmoqda...';

    var data = await api('POST', '/password', { current_password: current, new_password: newPwd });

    btn.disabled = false;
    btn.textContent = "Parolni o'zgartirish";

    if (data.ok) {
        toast("Parol o'zgartirildi!");
        try { tg.HapticFeedback.notificationOccurred('success'); } catch(e) {}
        document.getElementById('set-current-pwd').value = '';
        document.getElementById('set-new-pwd').value = '';
    } else if (data.error === 'wrong_password') {
        toast("Joriy parol noto'g'ri", 'error');
    } else {
        toast(data.error || 'Xatolik', 'error');
    }
}

// ── Initial Load ──
loadStats();
