"""JS injected once at page load — chip styling + auto-scroll."""

JS = """
<script>
(function () {
    function enhanceChips() {
        document.querySelectorAll('[data-testid="stButton"] button').forEach(function (btn) {
            if (btn.innerText.trim().endsWith('›')) {
                btn.classList.add('dm-chip');
            }
        });
    }

    function scrollToLatest() {
        const msgs = document.querySelectorAll('[data-testid="stChatMessage"]');
        if (msgs.length > 0) {
            msgs[msgs.length - 1].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    const observer = new MutationObserver(function () {
        enhanceChips();
        scrollToLatest();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    enhanceChips();
})();
</script>
"""
