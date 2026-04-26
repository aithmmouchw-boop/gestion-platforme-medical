document.addEventListener("DOMContentLoaded", () => {
    const medias = document.querySelectorAll(".interactive-media");
    const counters = document.querySelectorAll(".counter");
    const previewTabs = document.querySelectorAll(".preview-tab");
    const previewPanels = document.querySelectorAll(".preview-panel");
    const pricingToggle = document.getElementById("pricing-toggle");
    const priceValues = document.querySelectorAll(".price-value");
    const sections = document.querySelectorAll("main section, footer");

    medias.forEach((media) => {
        media.classList.add("auto-float");
    });

    const animateCounter = (el) => {
        if (el.dataset.animated === "true") {
            return;
        }
        el.dataset.animated = "true";
        const target = Number(el.dataset.target || "0");
        const suffix = el.dataset.suffix || "";
        const duration = 1500;
        const startAt = performance.now();

        const tick = (now) => {
            const progress = Math.min(1, (now - startAt) / duration);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.floor(target * eased);
            el.textContent = `${value.toLocaleString("fr-FR")}${suffix}`;
            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        };

        requestAnimationFrame(tick);
    };

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.35,
        }
    );

    counters.forEach((counter) => observer.observe(counter));

    previewTabs.forEach((tab) => {
        tab.addEventListener("click", (event) => {
            event.preventDefault();
            previewTabs.forEach((item) => item.classList.remove("active"));
            tab.classList.add("active");
            const targetPanelId = tab.dataset.targetPanel;
            if (targetPanelId) {
                previewPanels.forEach((panel) => panel.classList.remove("active"));
                const nextPanel = document.getElementById(targetPanelId);
                if (nextPanel) {
                    nextPanel.classList.add("active");
                }
            }
        });
    });

    const setPricingMode = (yearly) => {
        if (!pricingToggle) {
            return;
        }
        pricingToggle.classList.toggle("is-yearly", yearly);
        priceValues.forEach((el) => {
            const next = yearly ? el.dataset.yearly : el.dataset.monthly;
            if (next) {
                el.textContent = Number(next).toLocaleString("fr-FR");
            }
        });
    };

    if (pricingToggle) {
        pricingToggle.addEventListener("click", () => {
            const isYearly = pricingToggle.classList.contains("is-yearly");
            setPricingMode(!isYearly);
        });
    }

    sections.forEach((section, index) => {
        if (index > 0) {
            section.classList.add("reveal-on-scroll");
        }
    });

    const revealObserver = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15 }
    );

    document.querySelectorAll(".reveal-on-scroll").forEach((item) => revealObserver.observe(item));

    medias.forEach((media) => {
        media.addEventListener("click", () => {
            media.classList.remove("is-active");
            window.requestAnimationFrame(() => media.classList.add("is-active"));
            setTimeout(() => media.classList.remove("is-active"), 550);
        });
    });
});
