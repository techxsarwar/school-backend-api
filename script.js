// --- 1. CONFIG & LIBRARIES ---
// API handled by utils.js

document.addEventListener('DOMContentLoaded', () => {

    // AOS Init
    if (typeof AOS !== 'undefined') AOS.init({ duration: 1000, once: true });

    // --- 2. CORE FUNCTIONS ---

    // A. Identity (SEO & Profile)
    async function loadIdentity() {
        try {
            const s = await API.get('/api/settings');

            // Profile
            if (s.profile_name) safeText('profile-name', s.profile_name);
            if (s.profile_headline) safeText('profile-headline', s.profile_headline);
            if (s.profile_about) safeText('profile-about', s.profile_about);
            if (s.resume_link && document.getElementById('resume-btn')) {
                document.getElementById('resume-btn').href = s.resume_link;
            }

            // SEO
            if (s.site_title) document.title = s.site_title;
            updateMeta('description', s.meta_description);
            updateMeta('keywords', s.meta_keywords);

            // Maintenance Check
            checkMaintenance(s);
            // Announcement Check
            checkAnnouncement(s);

            // Socials
            if (s.social_github) updateLink('social-github', s.social_github);
            if (s.social_linkedin) updateLink('social-linkedin', s.social_linkedin);
            if (s.social_instagram) updateLink('social-instagram', s.social_instagram);
            if (s.social_twitter) updateLink('social-twitter', s.social_twitter);

        } catch (e) {
            console.error("Identity Error", e);
        }
    }

    function updateLink(id, url) {
        const el = document.getElementById(id);
        if (el) el.href = url;
    }

    // B. Projects (Portfolio)
    async function loadProjects() {
        try {
            const grid = document.getElementById('projects-grid');
            if (!grid) return;

            const data = await API.get('/api/projects');

            if (data.length === 0) {
                grid.innerHTML = '<p style="color:#666;text-align:center;grid-column:1/-1;">Adding cool projects soon...</p>';
                return;
            }

            const published = data.filter(p => p.status === 'Published' || p.status === 'Live');

            grid.innerHTML = published.map((p, i) => `
                <div class="glass-card project-card" data-aos="fade-up" data-aos-delay="${i * 100}">
                    <div class="project-img" style="height:200px; overflow:hidden; border-radius:12px 12px 0 0;">
                        <img src="${p.image_url}" style="width:100%; height:100%; object-fit:cover; transition:0.5s;">
                    </div>
                    <div style="padding:20px;">
                        <div style="font-size:0.8rem; color:var(--primary-accent); margin-bottom:5px;">${p.tags}</div>
                        <h3 style="margin-bottom:10px; color:white;">${p.title}</h3>
                        <p style="color:#aaa; font-size:0.9rem; margin-bottom:20px;">${p.description || ''}</p>
                        <a href="${p.link_url}" target="_blank" class="action-btn" style="padding:8px 20px; font-size:0.9rem;">View Project</a>
                    </div>
                </div>
            `).join('');

        } catch (e) { console.error("Projects Error", e); }
    }

    // C. Content (Testimonials & Blog)
    async function loadTestimonials() {
        try {
            const container = document.getElementById('testimonials-container');
            if (!container) return;
            const data = await API.get('/api/testimonials');

            if (data.length === 0) return; // Hide if empty

            container.innerHTML = data.map(t => `
                <div class="glass-card" style="padding:25px; border-radius:12px;" data-aos="fade-up">
                    <div style="display:flex; gap:15px; align-items:center; margin-bottom:15px;">
                         <img src="${t.image_url || 'https://ui-avatars.com/api/?name=' + t.name}" style="width:50px; height:50px; border-radius:50%;">
                         <div>
                             <h4 style="margin:0; color:white;">${t.name}</h4>
                             <small style="color:#888;">${t.role || 'Client'}</small>
                         </div>
                    </div>
                    <div style="color:#ffc107; margin-bottom:10px;">${"★".repeat(t.rating)}</div>
                    <p style="color:#ccc; font-style:italic;">"${t.review_text}"</p>
                </div>
            `).join('');
        } catch (e) { }
    }

    async function loadBlog() {
        try {
            const container = document.getElementById('blog-container');
            if (!container) return;
            const data = await API.get('/api/posts');

            if (data.length === 0) {
                container.innerHTML = '<p style="text-align:center;color:#666;grid-column:1/-1;">Writing new thoughts...</p>';
                return;
            }

            const published = data.filter(p => p.status === 'Published');

            container.innerHTML = published.map(p => `
                <div class="glass-card" style="border-radius:12px; overflow:hidden;" data-aos="fade-up">
                    <div style="height:180px; background:url('${p.image_url}') center/cover;"></div>
                    <div style="padding:20px;">
                        <small style="color:var(--primary-accent)">${p.date_posted}</small>
                        <h3 style="margin:10px 0; color:white;">${p.title}</h3>
                        <p style="color:#999; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">${p.content}</p>
                        <a href="#" style="color:white; text-decoration:none; margin-top:15px; display:inline-block;">Read More &rarr;</a>
                    </div>
                </div>
            `).join('');
        } catch (e) { }
    }

    // --- 3. HELPERS ---

    function safeText(id, txt) {
        const el = document.getElementById(id);
        if (el) el.textContent = txt;
    }

    function updateMeta(name, content) {
        if (!content) return;
        let tag = document.querySelector(`meta[name="${name}"]`);
        if (!tag) {
            tag = document.createElement('meta');
            tag.name = name;
            document.head.appendChild(tag);
        }
        tag.content = content;
    }

    function checkMaintenance(s) {
        if (s.maintenance_mode === '1' || s.maintenance_mode === 'true') {
            // Calculate time
            let timeHtml = '';
            let isTimeUp = false;
            if (s.maintenance_end_time && s.maintenance_end_time !== 'null') {
                const end = new Date(s.maintenance_end_time).getTime();
                const now = new Date().getTime();
                if (now > end) { isTimeUp = true; } // Expired
                else {
                    timeHtml = '<div style="margin-top:20px; color:#27c93f;">Updating system...</div>';
                }
            }

            if (!isTimeUp) {
                document.body.innerHTML = `
                    <div style="height:100vh; background:#050505; color:white; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; font-family:sans-serif;">
                        <i class="fas fa-hammer" style="font-size:3rem; color:#ff4747; margin-bottom:20px;"></i>
                        <h1>Under Maintenance</h1>
                        <p style="color:#888;">We are improving the experience.</p>
                        ${timeHtml}
                    </div>
                 `;
                throw new Error("Maintenance Mode Active");
            }
        }
    }

    function checkAnnouncement(s) {
        if ((s.announcement_active === '1' || s.announcement_active === 'true') && s.announcement_text) {
            const key = 'closed_ann_' + btoa(s.announcement_text).substring(0, 5);
            if (sessionStorage.getItem(key)) return;

            const div = document.createElement('div');
            const color = s.announcement_color || '#333';

            if (s.announcement_type === 'popup') {
                div.style.cssText = `position:fixed; bottom:30px; right:30px; background:#111; border-left:4px solid ${color}; padding:20px; border-radius:8px; width:300px; z-index:9999; box-shadow:0 10px 40px rgba(0,0,0,0.5); color:white; animation:slideUp 0.5s ease;`;
                div.innerHTML = `
                    <h4 style="margin:0 0 5px 0; color:${color}">Announcement</h4>
                    <p style="margin:0; font-size:0.9rem; color:#ccc;">${s.announcement_text}</p>
                    <button onclick="this.parentElement.remove(); sessionStorage.setItem('${key}', 1);" style="position:absolute; top:10px; right:10px; background:none; border:none; color:#666; cursor:pointer;">&times;</button>
                 `;
            } else {
                div.style.cssText = `background:${color}; color:white; padding:10px; text-align:center; position:relative; z-index:9999;`;
                div.innerHTML = `
                    <span>${s.announcement_text}</span>
                    <button onclick="this.parentElement.remove(); sessionStorage.setItem('${key}', 1);" style="background:none; border:none; color:white; margin-left:15px; cursor:pointer;">&times;</button>
                 `;
                document.body.prepend(div);
            }
            if (s.announcement_type === 'popup') document.body.appendChild(div);
        }
    }

    // --- 4. EXECUTE ---
    // Track Visit
    API.post('/api/track-visit', { page: document.title });

    // Load Modules
    loadIdentity(); // Also checks maintenance
    loadProjects();
    loadTestimonials();
    loadBlog();

    // Mobile Menu Logic
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = hamburger.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });

        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                const icon = hamburger.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
    }

    // Interactive Elements
    window.submitContact = async function (e) {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const oldText = btn.innerHTML;
        btn.innerHTML = 'Sending...';

        try {
            await API.post('/api/messages', {
                name: document.getElementById('contact-name').value,
                email: document.getElementById('contact-email').value,
                message: document.getElementById('contact-message').value
            });

            btn.innerHTML = 'Message Sent!';
            btn.style.background = '#27c93f';
            showToast('Message sent successfully!');
            setTimeout(() => { btn.innerHTML = oldText; btn.style.background = ''; e.target.reset(); }, 3000);
        } catch (err) {
            btn.innerHTML = oldText;
            showToast(err.message || 'Failed to send', 'error');
        }
    }
});

// Mobile Menu Helper (Global Fallback)
function toggleMenu() {
    const nav = document.querySelector('.nav-links');
    if (nav) nav.classList.toggle('active');
}

/* --- LOGIN LOGIC --- */
async function handleLogin(e) {
    e.preventDefault();

    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const btn = document.getElementById('loginBtn');
    const card = document.getElementById('loginCard');
    const errorMsg = document.getElementById('errorMessage');

    // Reset State
    btn.classList.add('loading');
    card.classList.remove('shake');
    errorMsg.classList.remove('show');

    try {
        const data = await API.post('/api/login', {
            username: usernameInput.value,
            password: passwordInput.value
        });

        if (data.success) {
            setTimeout(() => {
                localStorage.setItem('token', data.token);
                window.location.href = 'admin.html';
            }, 800);
        } else {
            throw new Error(data.message);
        }

    } catch (err) {
        setTimeout(() => {
            btn.classList.remove('loading');
            card.classList.add('shake');
            errorMsg.querySelector('span').innerText = err.message || "Invalid Credentials";
            errorMsg.classList.add('show');
            setTimeout(() => {
                card.classList.remove('shake');
            }, 500);
        }, 800);
    }
}