// --- UTILS & API ---

(function () {
    // 1. API CONFIG
    const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const BASE_URL = isLocal ? "http://127.0.0.1:5000" : "https://school-backend-api-5hkh.onrender.com";

    // 2. API OBJECT
    window.API = {
        base: BASE_URL,

        async get(endpoint) {
            try {
                const res = await fetch(`${BASE_URL}${endpoint}`);
                if (!res.ok) throw new Error(`API Error: ${res.status}`);
                return await res.json();
            } catch (err) {
                console.error(err);
                window.showToast(err.message, 'error');
                throw err;
            }
        },

        async post(endpoint, data) {
            try {
                const res = await fetch(`${BASE_URL}${endpoint}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                const d = await res.json();
                if (!d.success && !res.ok) throw new Error(d.message || 'Request failed');
                return d;
            } catch (err) {
                console.error(err);
                window.showToast(err.message, 'error');
                throw err;
            }
        },

        async put(endpoint, data) {
            try {
                const res = await fetch(`${BASE_URL}${endpoint}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await res.json();
            } catch (err) {
                console.error(err);
                throw err;
            }
        },

        async delete(endpoint, id) {
            try {
                const url = id ? `${BASE_URL}${endpoint}?id=${id}` : `${BASE_URL}${endpoint}`;
                const res = await fetch(url, { method: 'DELETE' });
                return await res.json();
            } catch (err) {
                console.error(err);
                throw err;
            }
        }
    };

    // 3. TOAST NOTIFICATIONS
    // Inject CSS
    const style = document.createElement('style');
    style.innerHTML = `
        #toast-container { position: fixed; top: 20px; right: 20px; z-index: 10000; }
        .toast {
            background: #333; color: white; padding: 12px 20px; border-radius: 6px;
            margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex; align-items: center; gap: 10px;
            animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
            min-width: 250px;
        }
        .toast.success { border-left: 4px solid #27c93f; }
        .toast.error { border-left: 4px solid #ff4747; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes fadeOut { to { opacity: 0; pointer-events: none; } }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);

    window.showToast = function (message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}" style="color:${type === 'success' ? '#27c93f' : '#ff4747'}"></i>
            <span>${message}</span>
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    };

})();
