// ব্যাকগ্রাউন্ড থেকে ফ্লাস্ক সার্ভারে রিকোয়েস্ট হ্যান্ডেল করা
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "fetch_generate") {
        fetch('http://127.0.0.1:5000/api/ext/generate')
            .then(res => res.json())
            .then(data => sendResponse(data))
            .catch(err => sendResponse({ success: false }));
        return true; //异步 response এর জন্য জরুরি
    }

    if (request.action === "fetch_get") {
        fetch('http://127.0.0.1:5000/api/ext/get', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: request.title })
        })
        .then(res => res.json())
        .then(data => sendResponse(data))
        .catch(err => sendResponse({ success: false }));
        return true;
    }

    if (request.action === "fetch_save") {
        fetch('http://127.0.0.1:5000/api/ext/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request.data)
        })
        .then(res => res.json())
        .then(data => sendResponse(data))
        .catch(err => sendResponse({ success: false }));
        return true;
    }
});