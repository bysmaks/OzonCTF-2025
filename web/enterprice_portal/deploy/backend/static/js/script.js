// Simple animations
document.addEventListener('DOMContentLoaded', () => {
    // Animate feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');
    
    const animateOnScroll = () => {
        featureCards.forEach((card, index) => {
            const cardPosition = card.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.3;
            
            if (cardPosition < screenPosition) {
                card.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`;
            }
        });
    };
    
    // Initial check
    animateOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', animateOnScroll);
});

// Add some basic animations to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .feature-card {
        opacity: 0;
    }
`;
document.head.appendChild(style);