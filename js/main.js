document.addEventListener('DOMContentLoaded', () => {
  // ==========================================================================
  // MOBILE HAMBURGER MENU
  // ==========================================================================
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('.nav-menu');

  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('active');
      navMenu.classList.toggle('active');
    });

    // Close menu when clicking nav links
    document.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
      });
    });
  }

  // ==========================================================================
  // STICKY HEADER ON SCROLL
  // ==========================================================================
  const header = document.querySelector('.header');
  const handleScrollHeader = () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };
  
  if (header) {
    window.addEventListener('scroll', handleScrollHeader);
    handleScrollHeader(); // Initial check
  }

  // ==========================================================================
  // ACTIVE NAVIGATION LINK MARKER
  // ==========================================================================
  const highlightActiveLink = () => {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      // Resolve path matching for sub-directories or index
      if (currentPath.endsWith(linkPath) || 
          (linkPath === '../index.html' && currentPath.includes('/pages/')) ||
          (linkPath === 'index.html' && (currentPath.endsWith('/') || currentPath.endsWith('index.html')))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  };
  highlightActiveLink();

  // ==========================================================================
  // BACK TO TOP BUTTON
  // ==========================================================================
  const backToTopBtn = document.querySelector('.back-to-top');
  
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        backToTopBtn.classList.add('show');
      } else {
        backToTopBtn.classList.remove('show');
      }
    });

    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // ==========================================================================
  // SCROLL-TRIGGERED FADE-IN ANIMATIONS (IntersectionObserver)
  // ==========================================================================
  const fadeElements = document.querySelectorAll('.animate-fade-in');
  
  if ('IntersectionObserver' in window && fadeElements.length > 0) {
    const fadeObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('appear');
          observer.unobserve(entry.target); // Stop tracking once animated
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    fadeElements.forEach(el => fadeObserver.observe(el));
  } else {
    // Fallback if IntersectionObserver not supported
    fadeElements.forEach(el => el.classList.add('appear'));
  }

  // ==========================================================================
  // COOKIE CONSENT BANNER
  // ==========================================================================
  const cookieBanner = document.querySelector('.cookie-banner');
  const cookieAcceptBtn = document.querySelector('.cookie-accept');
  
  if (cookieBanner && cookieAcceptBtn) {
    const isAccepted = localStorage.getItem('moundCookieAccepted');
    
    if (!isAccepted) {
      setTimeout(() => {
        cookieBanner.classList.add('show');
      }, 2000); // Trigger after 2 seconds
    }

    cookieAcceptBtn.addEventListener('click', () => {
      localStorage.setItem('moundCookieAccepted', 'true');
      cookieBanner.classList.remove('show');
    });
  }

  // ==========================================================================
  // RELEASE COUNTDOWN TIMER (July 15, 2026)
  // ==========================================================================
  const countdownDays = document.getElementById('days');
  const countdownHours = document.getElementById('hours');
  const countdownMinutes = document.getElementById('minutes');
  const countdownSeconds = document.getElementById('seconds');

  if (countdownDays && countdownHours && countdownMinutes && countdownSeconds) {
    const releaseDate = new Date('July 15, 2026 00:00:00').getTime();

    const updateCountdown = () => {
      const now = new Date().getTime();
      const distance = releaseDate - now;

      if (distance < 0) {
        document.querySelector('.countdown-container').innerHTML = 
          '<div class="countdown-val" style="font-size: 1.5rem;">THE MOUND HAS RISEN! AVAILABLE NOW</div>';
        return;
      }

      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      countdownDays.innerText = String(days).padStart(2, '0');
      countdownHours.innerText = String(hours).padStart(2, '0');
      countdownMinutes.innerText = String(minutes).padStart(2, '0');
      countdownSeconds.innerText = String(seconds).padStart(2, '0');
    };

    updateCountdown(); // Run immediately
    setInterval(updateCountdown, 1000);
  }

  // ==========================================================================
  // CANVAS ELDRITCH PARTICLE EFFECT SYSTEM
  // ==========================================================================
  const canvas = document.getElementById('hero-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.offsetWidth;
      canvas.height = canvas.parentElement.offsetHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle class representing floating bioluminescent orbs
    class EldritchParticle {
      constructor() {
        this.reset();
      }

      reset() {
        this.x = Math.random() * canvas.width;
        this.y = canvas.height + Math.random() * 50; // Spawn below bottom edge
        this.size = Math.random() * 3 + 1; // Size of particle
        this.speedY = -(Math.random() * 0.8 + 0.3); // Upward float speed
        this.speedX = Math.random() * 0.4 - 0.2; // Gentle horizontal sway
        this.opacity = Math.random() * 0.5 + 0.2; // Transparency
        this.hue = Math.random() > 0.3 ? 160 : 280; // Teal (Cthulhian) or Purple (Void)
        this.wobbleSpeed = Math.random() * 0.02 + 0.005;
        this.wobbleRange = Math.random() * 2 + 1;
        this.wobbleAngle = Math.random() * Math.PI;
      }

      update() {
        this.y += this.speedY;
        this.wobbleAngle += this.wobbleSpeed;
        this.x += this.speedX + Math.sin(this.wobbleAngle) * (this.wobbleRange / 10);
        
        // Slowly fade particles out as they reach top 20%
        if (this.y < canvas.height * 0.2) {
          this.opacity -= 0.005;
        }

        // Reset if out of bounds or invisible
        if (this.y < 0 || this.opacity <= 0 || this.x < 0 || this.x > canvas.width) {
          this.reset();
        }
      }

      draw() {
        ctx.beginPath();
        // Bioluminescent glow radial gradient
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, this.size * 3
        );
        gradient.addColorStop(0, `rgba(${this.hue === 160 ? '0, 255, 204' : '177, 0, 255'}, ${this.opacity})`);
        gradient.addColorStop(0.4, `rgba(${this.hue === 160 ? '0, 242, 254' : '122, 0, 255'}, ${this.opacity * 0.4})`);
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        
        ctx.fillStyle = gradient;
        ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Initialize particles
    const particleCount = 45;
    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      // Stagger initial vertical positions
      const p = new EldritchParticle();
      p.y = Math.random() * canvas.height;
      particles.push(p);
    }

    const animateParticles = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      particles.forEach(p => {
        p.update();
        p.draw();
      });
      
      animationFrameId = requestAnimationFrame(animateParticles);
    };

    animateParticles();
  }
});
