// elara poker calculator - main entry point and event handling

// grab the dom elements we need
const analyzeBtn = document.getElementById('analyzeBtn');
const calculateEquityBtn = document.getElementById('calculateEquityBtn');
const preflopBtn = document.getElementById('preflopBtn');

// where we'll show the results
const resultsContainer = document.getElementById('results');
const equityResultsContainer = document.getElementById('equityResults');
const preflopResultsContainer = document.getElementById('preflopResults');

// set up event listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
    analyzeBtn.addEventListener('click', analyzeHand);
    calculateEquityBtn.addEventListener('click', calculateEquity);
    preflopBtn.addEventListener('click', getPreflopAction);
    
    // let people press enter instead of clicking buttons
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const section = this.closest('section');
                if (section.querySelector('.btn-primary')) {
                    section.querySelector('.btn-primary').click();
                } else if (section.querySelector('.btn-secondary')) {
                    section.querySelector('.btn-secondary').click();
                } else if (section.querySelector('.btn-accent')) {
                    section.querySelector('.btn-accent').click();
                }
            }
        });
    });
    
    // Check server health on load
    checkServerHealth().then(isHealthy => {
        if (!isHealthy) {
            // Show a warning if server is not responding
            const warning = document.createElement('div');
            warning.className = 'error';
            warning.style.margin = '20px';
            warning.innerHTML = `
                <strong>Warning:</strong> Cannot connect to the server. 
                Make sure the Flask backend is running on http://localhost:5000
            `;
            document.body.insertBefore(warning, document.body.firstChild);
        }
    });
    
    // Add example button
    const exampleBtn = document.createElement('button');
    exampleBtn.textContent = 'Load Example';
    exampleBtn.className = 'btn btn-accent';
    exampleBtn.style.margin = '20px';
    exampleBtn.onclick = loadExampleData;
    
    const header = document.querySelector('.header');
    header.appendChild(exampleBtn);
});

// analyze hand function - does the full analysis
async function analyzeHand() {
    const heroHand = parseCards(document.getElementById('heroHand').value);
    const board = parseCards(document.getElementById('board').value);
    const position = document.getElementById('position').value;
    const potSize = parseInt(document.getElementById('potSize').value) || 0;
    const currentBet = parseInt(document.getElementById('currentBet').value) || 0;
    
    if (heroHand.length !== 2) {
        showError(resultsContainer, 'Please enter exactly 2 cards for your hand (e.g., "As Kh")');
        return;
    }
    
    showLoading(resultsContainer);
    
    try {
        const result = await analyzeHandAPI(heroHand, board, position, potSize, currentBet);
        
        // Render results
        resultsContainer.innerHTML = renderHandAnalysis(result, heroHand, board);
        
        // Render card displays
        renderCards(heroHand, document.getElementById('heroCardsDisplay'));
        if (board.length > 0) {
            renderCards(board, document.getElementById('boardCardsDisplay'));
        }
        
    } catch (error) {
        showError(resultsContainer, `Failed to analyze hand: ${error.message}`);
    }
}

// equity calculation function - figures out how often you win
async function calculateEquity() {
    const heroHand = parseCards(document.getElementById('equityHeroHand').value);
    const villainRange = document.getElementById('villainRange').value.split(',').map(s => s.trim());
    const board = parseCards(document.getElementById('equityBoard').value);
    const simulations = parseInt(document.getElementById('simulations').value) || 1000;
    
    if (heroHand.length !== 2) {
        showError(equityResultsContainer, 'Please enter exactly 2 cards for your hand (e.g., "As Kh")');
        return;
    }
    
    if (villainRange.length === 0) {
        showError(equityResultsContainer, 'Please enter at least one hand in the opponent range');
        return;
    }
    
    showLoading(equityResultsContainer);
    
    try {
        const result = await calculateEquityAPI(heroHand, villainRange, board, simulations);
        
        // Render results
        equityResultsContainer.innerHTML = renderEquityCalculation(result);
        
    } catch (error) {
        showError(equityResultsContainer, `Failed to calculate equity: ${error.message}`);
    }
}

// preflop action function - tells you what to do preflop
async function getPreflopAction() {
    const position = document.getElementById('preflopPosition').value;
    const holeCards = parseCards(document.getElementById('preflopHoleCards').value);
    
    if (holeCards.length !== 2) {
        showError(preflopResultsContainer, 'Please enter exactly 2 cards for your hand (e.g., "As Kh")');
        return;
    }
    
    showLoading(preflopResultsContainer);
    
    try {
        const result = await getPreflopActionAPI(position, holeCards);
        
        // Render results
        preflopResultsContainer.innerHTML = renderPreflopAction(result);
        
    } catch (error) {
        showError(preflopResultsContainer, `Failed to get preflop action: ${error.message}`);
    }
}