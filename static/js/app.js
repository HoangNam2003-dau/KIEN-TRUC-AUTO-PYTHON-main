function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-10px)";
        setTimeout(() => toast.remove(), 250);
    }, 2200);
}

function updateCartCount(count) {
    const cartCountText = document.getElementById("cart-count-text");
    if (cartCountText) {
        cartCountText.textContent = count;
    }
}

function addToCart(carId) {
    fetch(`/api/cart/add/${carId}`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok || data.success) {
            updateCartCount(data.cart_count || 0);
            showToast(data.message || "Đã thêm vào giỏ hàng", "success");
        } else {
            showToast(data.message || "Không thể thêm vào giỏ hàng", "error");
        }
    })
    .catch(() => {
        showToast("Có lỗi xảy ra khi thêm vào giỏ hàng", "error");
    });
}

function initBannerSlider(){
  const slider = document.getElementById('homeBannerSlider');
  if(!slider) return;
  const slides = slider.querySelectorAll('.banner-slide');
  const dots = slider.querySelectorAll('.banner-dot');
  const prev = slider.querySelector('.banner-nav.prev');
  const next = slider.querySelector('.banner-nav.next');
  let index = 0;
  let timer = null;

  const goTo = (i) => {
    index = (i + slides.length) % slides.length;
    slides.forEach((slide, idx) => slide.classList.toggle('active', idx === index));
    dots.forEach((dot, idx) => dot.classList.toggle('active', idx === index));
  };

  const start = () => {
    stop();
    timer = setInterval(() => goTo(index + 1), 3000);
  };

  const stop = () => {
    if (timer) clearInterval(timer);
  };

  prev?.addEventListener('click', () => { goTo(index - 1); start(); });
  next?.addEventListener('click', () => { goTo(index + 1); start(); });
  dots.forEach((dot, idx) => dot.addEventListener('click', () => { goTo(idx); start(); }));
  slider.addEventListener('mouseenter', stop);
  slider.addEventListener('mouseleave', start);
  document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());

  goTo(0);
  start();
}

document.addEventListener('DOMContentLoaded', initBannerSlider);
function toggleSearchBox() {
    const box = document.getElementById("searchPopup");
    if (box) {
        box.classList.toggle("active");
    }
}   