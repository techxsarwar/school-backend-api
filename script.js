document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Libraries
    AOS.init({
        duration: 1000,
        once: true,
        mirror: false
    });

    // --- Admin Connection (Traffic & Ads) ---
    // --- CMS API Integration ---
    const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? "http://127.0.0.1:5000/api"
        : "https://school-backend-api-5hkh.onrender.com/api";

    async function initCMS() {
        try {
            // 1. Track Visit
            fetch(`${API_BASE}/track-visit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page: document.title })
            });

            // 2. Fetch Settings
            const res = await fetch(`${API_BASE}/settings`);
            const settings = await res.json();

            // Check Maintenance Mode
            if (settings.maintenance_mode === 'true') {
                document.body.innerHTML = `
                    <div style="height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#050505;color:white;text-align:center;font-family:sans-serif;">
                        <i class="fas fa-tools" style="font-size:3rem;color:#ff4747;margin-bottom:20px;"></i>
                        <h1>Under Maintenance</h1>
                        <p style="color:#888;margin-top:10px;">We are upgrading the system. Please check back later.</p>
                    </div>
                `;
                return; // Stop execution
            }

            // Announcement Bar
            if (settings.announcement_active === 'true' && settings.announcement_text) {
                const banner = document.createElement('div');
                banner.className = 'ad-banner';
                banner.innerHTML = `
                    <span>${settings.announcement_text}</span>
                    <button class="ad-close" onclick="this.parentElement.remove()">&times;</button>
                `;
                document.body.prepend(banner);
                document.body.classList.add('has-ad');
            }

        } catch (error) {
            console.error("CMS Connection Failed", error);
        }
    }

    // Run connection
    initCMS();

    // Contact Form Handler (Global)
    window.submitContact = async function (e) {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalText = btn.innerText;
        btn.innerText = "Sending...";

        const formData = {
            name: document.getElementById('contact-name').value,
            email: document.getElementById('contact-email').value,
            message: document.getElementById('contact-message').value
        };

        try {
            const res = await fetch(`${API_BASE}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await res.json();

            if (data.success) {
                btn.innerText = "Message Sent!";
                btn.style.background = "#27c93f";
                e.target.reset();
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.background = "";
                }, 3000);
            } else {
                alert("Error sending message.");
                btn.innerText = originalText;
            }
        } catch (err) {
            alert("Network Error");
            btn.innerText = originalText;
        }
    }

    // 2. Preloader Logic - REMOVED

    // 3. Custom Cursor - REMOVED


    // 4. Typewriter Effect
    class TypeWriter {
        constructor(txtElement, words, wait = 3000) {
            this.txtElement = txtElement;
            this.words = words;
            this.txt = '';
            this.wordIndex = 0;
            this.wait = parseInt(wait, 10);
            this.type();
            this.isDeleting = false;
        }

        type() {
            // Current index of word
            const current = this.wordIndex % this.words.length;
            // Get full text of current word
            const fullTxt = this.words[current];

            // Check if deleting
            if (this.isDeleting) {
                // Remove char
                this.txt = fullTxt.substring(0, this.txt.length - 1);
            } else {
                // Add char
                this.txt = fullTxt.substring(0, this.txt.length + 1);
            }

            // Insert txt into element
            this.txtElement.innerHTML = `<span class="txt">${this.txt}</span>`;

            // Initial Type Speed
            let typeSpeed = 200;

            if (this.isDeleting) {
                typeSpeed /= 2;
            }

            // If word is complete
            if (!this.isDeleting && this.txt === fullTxt) {
                // Make pause at end
                typeSpeed = this.wait;
                // Set delete to true
                this.isDeleting = true;
            } else if (this.isDeleting && this.txt === '') {
                this.isDeleting = false;
                // Move to next word
                this.wordIndex++;
                // Pause before start typing
                typeSpeed = 500;
            }

            setTimeout(() => this.type(), typeSpeed);
        }
    }

    // Init TypeWriter
    const txtElement = document.querySelector('.txt-type');
    if (txtElement) {
        const words = JSON.parse(txtElement.getAttribute('data-words'));
        const wait = txtElement.getAttribute('data-wait');
        new TypeWriter(txtElement, words, wait);
    }

    // --- Timeline Scroll Animation ---
    const timelineContainer = document.querySelector('.timeline-container');
    const timelineFill = document.getElementById('timelineFill');

    if (timelineContainer && timelineFill) {
        window.addEventListener('scroll', () => {
            const containerTop = timelineContainer.getBoundingClientRect().top + window.scrollY;
            const containerHeight = timelineContainer.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollY = window.scrollY;

            // Calculate how much of the timeline has been scrolled past
            // Start filling when the top of the container hits the middle of the screen
            const startOffset = windowHeight / 2;

            // Math to determine fill percentage
            let fillHeight = scrollY + startOffset - containerTop;

            // Clamp value between 0 and containerHeight
            if (fillHeight < 0) fillHeight = 0;
            if (fillHeight > containerHeight) fillHeight = containerHeight;

            const percentage = (fillHeight / containerHeight) * 100;
            timelineFill.style.height = `${percentage}%`;
        });
    }

    // 5. Particles Background (Canvas)
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        let particlesArray;

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2 + 0.1; // Small stars/nodes
                this.speedX = Math.random() * 1 - 0.5; // Slow movement
                this.speedY = Math.random() * 1 - 0.5;
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x > canvas.width || this.x < 0) this.speedX = -this.speedX;
                if (this.y > canvas.height || this.y < 0) this.speedY = -this.speedY;
            }
            draw() {
                ctx.fillStyle = 'rgba(103, 61, 230, 0.5)'; // Accent color
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        function initParticles() {
            particlesArray = [];
            for (let i = 0; i < 50; i++) { // Number of particles
                particlesArray.push(new Particle());
            }
        }

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particlesArray.length; i++) {
                particlesArray[i].update();
                particlesArray[i].draw();
                // Connect particles
                for (let j = i; j < particlesArray.length; j++) {
                    const dx = particlesArray[i].x - particlesArray[j].x;
                    const dy = particlesArray[i].y - particlesArray[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < 150) {
                        ctx.strokeStyle = 'rgba(103, 61, 230, 0.1)';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(particlesArray[i].x, particlesArray[i].y);
                        ctx.lineTo(particlesArray[j].x, particlesArray[j].y);
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animateParticles);
        }

        initParticles();
        animateParticles();

        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            initParticles();
        });
    }

    // 6. GitHub Projects Fetcher (Optimized for Tilt)
    const projectsGrid = document.getElementById('projects-grid');
    const username = 'darsarwaraltaf';
    const apiUrl = `https://api.github.com/users/${username}/repos?sort=updated&per_page=6`;

    async function fetchProjects() {
        if (!projectsGrid) return;
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error(`GitHub API Error: ${response.status}`);
            const data = await response.json();
            const projects = data.filter(repo => !repo.fork).slice(0, 6);
            renderProjects(projects);
        } catch (error) {
            console.error('Error fetching projects:', error);
            projectsGrid.innerHTML = `<div class="error-state" style="grid-column:1/-1;text-align:center;">Failed to load projects. Check console.</div>`;
        }
    }

    function renderProjects(projects) {
        projectsGrid.innerHTML = '';
        projects.forEach((repo, index) => {
            const card = document.createElement('div');
            // Add Tilt Attribute and AOS
            card.className = 'project-card';
            card.setAttribute('data-tilt', ''); // Vanilla-Tilt trigger
            card.setAttribute('data-tilt-max', '10');
            card.setAttribute('data-aos', 'fade-up');
            card.setAttribute('data-aos-delay', index * 100);

            const description = repo.description || 'No description available.';
            const language = repo.language || 'Code';

            card.innerHTML = `
                <div class="project-top">
                    <i class="far fa-folder folder-icon"></i>
                    <div class="project-links">
                         ${repo.homepage ? `<a href="${repo.homepage}" target="_blank"><i class="fas fa-external-link-alt"></i></a>` : ''}
                        <a href="${repo.html_url}" target="_blank"><i class="fab fa-github"></i></a>
                    </div>
                </div>
                <h3>${repo.name}</h3>
                <p>${description}</p>
                <div class="project-tech-list">
                    <span>${language}</span>
                    <span>${repo.stargazers_count > 0 ? `<i class="fas fa-star"></i> ${repo.stargazers_count}` : ''}</span>
                </div>
            `;
            projectsGrid.appendChild(card);
        });

        // Re-init Tilt after injecting elements
        VanillaTilt.init(document.querySelectorAll(".project-card"), {
            max: 10,
            speed: 400,
            glare: true,
            "max-glare": 0.2
        });
    }

    fetchProjects();

    // 7. Hamburger Menu (Side Drawer)
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            const icon = hamburger.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });

        // Close on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                hamburger.querySelector('i').classList.add('fa-bars');
                hamburger.querySelector('i').classList.remove('fa-times');
            });
        });
    }

    // 8. Back to Top
    const backToTop = document.querySelector('.back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                backToTop.classList.add('active');
            } else {
                backToTop.classList.remove('active');
            }
        });
    }

    // 9. Featured Project Carousel
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    let currentSlide = 0;

    function showSlide(n) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        currentSlide = (n + slides.length) % slides.length;

        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => showSlide(currentSlide - 1));
        nextBtn.addEventListener('click', () => showSlide(currentSlide + 1));

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => showSlide(index));
        });
    }

    // 10. Dynamic Copyright Year
    const yearSpan = document.getElementById('current-year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});
function toggleMenu() {
    const nav = document.getElementById('navLinks');
    nav.classList.toggle('active');
}