if (window.location.protocol === "http:" || window.location.protocol === "https:") {

    // ইনপুটে ভ্যালু সেট করার পর ব্রাউজারকে তা জানানোর ফাংশন (React/Angular সাপোর্ট করার জন্য জরুরি)
    function setNativeValue(element, value) {
        let lastValue = element.value;
        element.value = value;
        let event = new Event('input', { bubbles: true });
        let tracker = element._valueTracker;
        if (tracker) {
            tracker.setValue(lastValue);
        }
        element.dispatchEvent(event);
        element.dispatchEvent(new Event('change', { bubbles: true }));
    }

    // ইউজারনেম বা ইমেইল ফিল্ড নিখুঁتভাবে খোঁজার ফাংশন
    function findUserField(container) {
        let fields = container.querySelectorAll('input[type="text"], input[type="email"], input:not([type])');
        for (let field of fields) {
            let nameAttr = (field.name || '').toLowerCase();
            let idAttr = (field.id || '').toLowerCase();
            let placeholder = (field.placeholder || '').toLowerCase();
            
            if (nameAttr.includes('user') || nameAttr.includes('email') || nameAttr.includes('login') ||
                idAttr.includes('user') || idAttr.includes('email') || idAttr.includes('login') ||
                placeholder.includes('user') || placeholder.includes('email') || field.type === 'email') {
                return field;
            }
        }
        return fields.length > 0 ? fields[0] : null;
    }

    document.addEventListener('focusin', async function(event) {
        let target = event.target;
        if (target.tagName !== 'INPUT') return;

        let hostname = window.location.hostname.replace('www.', '');
        let form = target.closest('form') || document.body;
        let passwordFields = form.querySelectorAll('input[type="password"]');
        let userField = findUserField(form);

        // ১. প্রথমে ব্যাকএন্ডে চেক করা ভল্টে এই ডোমেইনের ক্রেডেনশিয়াল আছে কি না (Login Data Check)
        let hasVaultData = false;
        try {
            let res = await new Promise((resolve) => {
                chrome.runtime.sendMessage({ action: "fetch_get", title: hostname }, (data) => {
                    resolve(data);
                });
            });
            if (res && res.success && res.username) {
                hasVaultData = true;
            }
        } catch (e) {
            console.log("Vault match check error:", e);
        }

        // ২. পেজটি সাইন-আপ নাকি সাইন-ইন তা সুনির্দিষ্টভাবে শনাক্ত করা
        let pageText = document.body.innerText.toLowerCase();
        let isExplicitSignUp = passwordFields.length > 1 || 
                               pageText.includes('sign up') || 
                               pageText.includes('register') ||
                               pageText.includes('create account') ||
                               pageText.includes('signup') ||
                               pageText.includes('confirm password');

        // যদি ভল্টে ডাটা না থাকে এবং সাইন-আপের লক্ষণ থাকে, তবেই এটি রেজিস্টার পেজ হিসেবে গণ্য হবে
        let isSignUp = !hasVaultData && isExplicitSignUp;

        // ৩. সাইন-ইন মোড (লগইন পেজ): ভল্টে ডাটা থাকলে অটো-ফিল করা
        if (!isSignUp && hasVaultData) {
            if ((userField && target === userField && !target.value) || (target.type === 'password' && !target.value)) {
                chrome.runtime.sendMessage({ action: "fetch_get", title: hostname }, (data) => {
                    if (data && data.success) {
                        if (userField && !userField.value && data.username) {
                            setNativeValue(userField, data.username);
                        }
                        if (passwordFields.length > 0 && !passwordFields[0].value && data.password) {
                            setNativeValue(passwordFields[0], data.password);
                        }
                    }
                });
            }
            return; // লগইন ফ্লো শেষ, নিচের সাইন-আপ কোড রান হবে না
        }

        // ৪. সাইন-আপ মোড (রেজিস্ট্রেশন পেজ): ইমেইল বক্সে ফোকাস করলে ড্রপডাউন এবং পাসওয়ার্ড জেনারেট হবে
        if (userField && target === userField && !target.value && isSignUp) {
            chrome.runtime.sendMessage({ action: "fetch_generate" }, (data) => {
                if (data && data.success) {
                    if (passwordFields.length > 0 && !passwordFields[0].value) {
                        setNativeValue(passwordFields[0], data.password);
                        if (passwordFields.length > 1 && !passwordFields[1].value) {
                            setNativeValue(passwordFields[1], data.password);
                        }
                    }
                    showEmailSelector(target, data.emails);
                }
            });
        }
    });

    // প্রি-সেট ইমেইল সিলেক্ট করার ফ্লোটিং ড্রপডাউন বক্স
    function showEmailSelector(inputField, emails) {
        let existingBox = document.getElementById('mrx-email-dropdown');
        if (existingBox) existingBox.remove();

        let box = document.createElement('div');
        box.id = 'mrx-email-dropdown';
        box.style.position = 'absolute';
        box.style.background = '#0d1322';
        box.style.color = '#f1f5f9';
        box.style.border = '1px solid #1e293b';
        box.style.padding = '6px';
        box.style.zIndex = '999999';
        box.style.borderRadius = '8px';
        box.style.boxShadow = '0px 10px 20px rgba(0,0,0,0.5)';
        box.style.fontFamily = 'Segoe UI, sans-serif';
        box.style.fontSize = '13px';

        let rect = inputField.getBoundingClientRect();
        box.style.top = (rect.bottom + window.scrollY + 4) + 'px';
        box.style.left = (rect.left + window.scrollX) + 'px';
        box.style.width = rect.width + 'px';

        emails.forEach(email => {
            let item = document.createElement('div');
            item.innerText = email;
            item.style.padding = '8px 12px';
            item.style.cursor = 'pointer';
            item.style.borderRadius = '6px';
            item.style.transition = 'background 0.2s';
            
            item.onmouseover = () => item.style.background = '#1e293b';
            item.onmouseout = () => item.style.background = 'transparent';
            
            item.onclick = () => {
                setNativeValue(inputField, email);
                box.remove();
            };
            box.appendChild(item);
        });

        document.body.appendChild(box);

        document.addEventListener('click', function closeBox(e) {
            if (!box.contains(e.target) && e.target !== inputField) {
                box.remove();
                document.removeEventListener('click', closeBox);
            }
        });
    }

    // ফর্ম সাবমিট হলে বা সাবমিট বাটন ক্লিক হলে ভল্টে অটো-সেভ করা
    document.addEventListener('submit', function(event) {
        handleSave(event.target);
    });

    document.addEventListener('click', function(event) {
        let btn = event.target.closest('button, input[type="submit"]');
        if (btn) {
            let form = btn.closest('form');
            if (form) {
                setTimeout(() => handleSave(form), 500);
            }
        }
    });

    function handleSave(form) {
        let passwordFields = form.querySelectorAll('input[type="password"]');
        let passField = passwordFields.length > 0 ? passwordFields[passwordFields.length - 1] : null;
        
        let fields = form.querySelectorAll('input[type="text"], input[type="email"], input:not([type])');
        let userField = null;
        for (let field of fields) {
            let nameAttr = (field.name || '').toLowerCase();
            let idAttr = (field.id || '').toLowerCase();
            if (nameAttr.includes('user') || nameAttr.includes('email') || idAttr.includes('user') || idAttr.includes('email') || field.type === 'email') {
                userField = field;
                break;
            }
        }
        if (!userField && fields.length > 0) userField = fields[0];

        if (userField && passField && passField.value && userField.value) {
            let credentialData = {
                title: window.location.hostname.replace('www.', ''),
                username: userField.value,
                password: passField.value
            };

            chrome.runtime.sendMessage({ action: "fetch_save", data: credentialData }, (response) => {
                console.log('MRX-Vault Auto-Saved:', response);
            });
        }
    }
}