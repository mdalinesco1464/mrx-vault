if (window.location.protocol === "http:" || window.location.protocol === "https:") {

    document.addEventListener('focusin', function(event) {
        let target = event.target;
        if (target.tagName !== 'INPUT') return;

        let form = target.closest('form') || document.body;
        let hostname = window.location.hostname;
        let passwordFields = form.querySelectorAll('input[type="password"]');
        let userField = form.querySelector('input[type="text"], input[type="email"]');

        if (target.type === 'password' && !target.value) {
            let isSignUp = passwordFields.length > 1 || 
                           document.body.innerText.toLowerCase().includes('sign up') || 
                           document.body.innerText.toLowerCase().includes('register') ||
                           document.body.innerText.toLowerCase().includes('create account');

            if (isSignUp) {
                // ব্যাকগ্রাউন্ডের মাধ্যমে জেনারেট এপিআই কল করা
                chrome.runtime.sendMessage({ action: "fetch_generate" }, (data) => {
                    if (data && data.success) {
                        target.value = data.password;
                        if (passwordFields.length > 1) {
                            passwordFields.forEach(pf => { if(!pf.value) pf.value = data.password; });
                        }
                        if (userField && !userField.value) {
                            userField.value = data.username;
                        }
                    }
                });
            } else {
                // ব্যাকগ্রাউন্ডের মাধ্যমে ভল্ট থেকে ডাটা আনা
                chrome.runtime.sendMessage({ action: "fetch_get", title: hostname }, (data) => {
                    if (data && data.success) {
                        if (userField && !userField.value) userField.value = data.username;
                        target.value = data.password;
                    }
                });
            }
        }
    });

    // ফর্ম সাবমিট হলে অটো-সেভ করা
    document.addEventListener('submit', function(event) {
        let form = event.target;
        let userField = form.querySelector('input[type="text"], input[type="email"]');
        let passField = form.querySelector('input[type="password"]');

        if (userField && passField && passField.value) {
            let credentialData = {
                title: window.location.hostname,
                username: userField.value,
                password: passField.value
            };

            chrome.runtime.sendMessage({ action: "fetch_save", data: credentialData }, (response) => {
                console.log('MRX-Vault Auto-Saved:', response);
            });
        }
    });
}