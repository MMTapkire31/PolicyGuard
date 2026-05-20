document.addEventListener('DOMContentLoaded', function () {

    // UI elements
    const analyzeBtn = document.getElementById('analyzeBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressLabel = document.getElementById('progressLabel');
    const results = document.getElementById('results');
    const scoreNumber = document.getElementById('scoreNumber');
    const riskBar = document.getElementById('riskBar');
    const toggleBtn = document.getElementById('toggleBtn');
    const sentenceAnalysis = document.getElementById('sentenceAnalysis');
    const sentenceList = document.getElementById('sentenceList');
    const errorEl = document.getElementById('error');

    // Score color
    function scoreColor(score) {
        if (score >= 70) return '#e74c3c';
        if (score >= 40) return '#e67e22';
        return '#2ecc71';
    }

    // Error helper
    function showError(msg) {
        errorEl.style.display = 'block';
        errorEl.textContent = msg;

        progressContainer.style.display = 'none';
        analyzeBtn.disabled = false;
    }

    // Analyze button
    analyzeBtn.addEventListener('click', function () {

        analyzeBtn.disabled = true;

        errorEl.style.display = 'none';
        results.style.display = 'none';

        progressContainer.style.display = 'block';

        progressBar.style.width = '20%';

        progressLabel.textContent = 'Extracting policy text...';

        chrome.tabs.query(
            {
                active: true,
                currentWindow: true
            },

            function (tabs) {

                chrome.tabs.sendMessage(
                    tabs[0].id,
                    { action: 'extractText' },

                    function (response) {

                        if (!response || !response.success) {
                            showError(
                                response?.error ||
                                'Could not extract policy text.'
                            );
                            return;
                        }

                        progressBar.style.width = '50%';

                        progressLabel.textContent =
                            'Analyzing with DistilBERT...';

                        fetch('http://localhost:5000/analyze', {

                            method: 'POST',

                            headers: {
                                'Content-Type': 'application/json'
                            },

                            body: JSON.stringify({
                                text: response.text
                            })
                        })

                        .then(function (res) {
                            return res.json();
                        })

                        .then(function (data) {

                            progressBar.style.width = '100%';

                            progressLabel.textContent = 'Done!';

                            setTimeout(function () {

                                progressContainer.style.display = 'none';

                                displayResults(data);

                                analyzeBtn.disabled = false;

                            }, 500);
                        })

                        .catch(function () {

                            showError(
                                'Could not connect to backend. Is Flask running?'
                            );
                        });
                    }
                );
            }
        );
    });

    // Display results
    function displayResults(data) {

        const score = data.overall_risk_score;

        const color = scoreColor(score);

        scoreNumber.textContent = score + '/100';

        scoreNumber.style.color = color;

        riskBar.style.width = score + '%';

        riskBar.style.background = color;

        sentenceList.innerHTML = '';

        const riskyToShow = data.risky_sentences.filter(function (s) {

            return (
                s.risk_level === 'high' ||
                s.risk_level === 'medium'
            );
        });

        if (riskyToShow.length === 0) {

            sentenceList.innerHTML =
                '<p style="font-size:12px;color:#27ae60">' +
                'No high or medium risk sentences found.' +
                '</p>';
        }

        else {

            riskyToShow.forEach(function (sentence) {

                const card = document.createElement('div');

                card.className =
                    'sentence-card ' + sentence.risk_level;

                card.innerHTML =
                    '<p class="sentence-text">' +
                    sentence.text +
                    '</p>' +

                    '<div class="badges">' +

                    '<span class="badge category">' +
                    sentence.category +
                    '</span>' +

                    '<span class="badge ' +
                    sentence.risk_level +
                    '">' +

                    sentence.risk_level.toUpperCase() +

                    '</span>' +

                    '</div>';

                sentenceList.appendChild(card);
            });
        }

        results.style.display = 'block';
    }

    // Toggle analysis
    toggleBtn.addEventListener('click', function () {

        const isHidden =
            sentenceAnalysis.style.display === 'none';

        sentenceAnalysis.style.display =
            isHidden ? 'block' : 'none';

        toggleBtn.textContent =
            isHidden
                ? 'Hide Sentence Analysis'
                : 'Show Sentence Analysis';
    });

});