// Extract privacy policy text from webpage

function extractPolicyText() {

    // Get all paragraph text
    const paragraphs = document.querySelectorAll('p');

    // Convert to clean text
    const text = Array.from(paragraphs)

        .map(function (p) {
            return p.innerText.trim();
        })

        .filter(function (t) {
            return t.length > 10;
        })

        .join(' ');

    // If very little text found
    if (!text || text.length < 100) {
        return null;
    }

    return text;
}


// Listen for popup request
chrome.runtime.onMessage.addListener(

    function (request, sender, sendResponse) {

        if (request.action === 'extractText') {

            try {

                const text = extractPolicyText();

                if (text) {

                    sendResponse({
                        success: true,
                        text: text
                    });

                } else {

                    sendResponse({
                        success: false,
                        error: 'No readable text found on this page.'
                    });
                }

            }

            catch (err) {

                sendResponse({
                    success: false,
                    error: err.message
                });
            }
        }

        return true;
    }
);