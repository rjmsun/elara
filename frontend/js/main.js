// elara poker calculator - frontend javascript
const API_BASE_URL = 'http://localhost:5000';

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
});

// Utility functions
function parseCards(cardString) {
    if (!cardString.trim()) return [];
    return cardString.trim().split(/\s+/).map(card => card.trim());
}

function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

function showError(container, message) {
    container.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

function formatCard(cardStr) {
    const suit = cardStr.slice(-1);
    const rank = cardStr.slice(0, -1);
    const suitSymbols = { 's': '♠', 'h': '♥', 'd': '♦', 'c': '♣' };
    const isRed = suit === 'h' || suit === 'd';
    
    return {
        display: `${rank}${suitSymbols[suit]}`,
        isRed: isRed
    };
}

function renderCards(cards, container) {
    if (!cards || cards.length === 0) {
        container.innerHTML = '<p>No cards</p>';
        return;
    }
    
    const cardElements = cards.map(card => {
        const formatted = formatCard(card);
        return `
            <div class="card ${formatted.isRed ? 'red' : 'black'}">
                ${formatted.display}
            </div>
        `;
    }).join('');
    
    container.innerHTML = `<div class="card-display">${cardElements}</div>`;
}

// API functions
async function makeRequest(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

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
        const data = {
            hero_hand: heroHand,
            board: board,
            position: position,
            pot_size: potSize,
            current_bet: currentBet
        };
        
        const result = await makeRequest('/analyze_hand', data);
        
        // Render results
        resultsContainer.innerHTML = `
            <div class="result-item">
                <h3>Hand Analysis</h3>
                <div class="hand-strength">
                    <span>Hand Strength:</span>
                    <div class="strength-bar">
                        <div class="strength-fill" style="width: ${(result.hand_analysis.strength / 10) * 100}%"></div>
                    </div>
                    <span class="value">${result.hand_analysis.strength}% Equity</span>
                </div>
                <p><strong>Hand Type:</strong> <span class="value">${result.hand_analysis.hand_type || 'Preflop'}</span></p>
                <p><strong>Position:</strong> <span class="value">${result.position}</span></p>
                <p><strong>Pot Size:</strong> <span class="value">${result.pot_size} BB</span></p>
                <p><strong>Current Bet:</strong> <span class="value">${result.current_bet} BB</span></p>
                <p><strong>Pot Odds:</strong> <span class="value">${(result.pot_odds * 100).toFixed(1)}%</span></p>
            </div>
            
            <div class="result-item">
                <h3>Preflop Recommendation</h3>
                <p><strong>Preflop Action:</strong> <span class="value">${result.preflop_recommendation}</span></p>
                <div class="recommendation">${result.recommendation}</div>
            </div>
            
            <div class="result-item">
                <h3>Cards</h3>
                <p><strong>Your Hand:</strong></p>
                <div id="heroCardsDisplay"></div>
                ${board.length > 0 ? `
                    <p><strong>Board:</strong></p>
                    <div id="boardCardsDisplay"></div>
                ` : ''}
            </div>
        `;
        
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
        const data = {
            hero_hand: heroHand,
            villain_range: villainRange,
            board: board,
            simulations: simulations
        };
        
        const result = await makeRequest('/calculate_equity', data);
        
        // Render results
        equityResultsContainer.innerHTML = `
            <div class="result-item">
                <h3>Equity Calculation</h3>
                <p><strong>Your Hand:</strong> <span class="value">${result.hero_hand.join(' ')}</span></p>
                <p><strong>Opponent Range:</strong> <span class="value">${result.villain_range.join(', ')}</span></p>
                ${result.board.length > 0 ? `<p><strong>Board:</strong> <span class="value">${result.board.join(' ')}</span></p>` : ''}
                <p><strong>Simulations:</strong> <span class="value">${result.simulations}</span></p>
                <div class="equity">${(result.equity * 100).toFixed(1)}%</div>
            </div>
            
            <div class="result-item">
                <h3>Interpretation</h3>
                <p>Your hand has <strong>${(result.equity * 100).toFixed(1)}%</strong> equity against the opponent's range.</p>
                ${result.equity > 0.6 ? '<p class="text-success">This is a very strong hand!</p>' : 
                  result.equity > 0.4 ? '<p class="text-warning">This is a decent hand.</p>' : 
                  '<p class="text-danger">This is a weak hand.</p>'}
            </div>
        `;
        
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
        const data = {
            position: position,
            hole_cards: holeCards
        };
        
        const result = await makeRequest('/preflop_action', data);
        
        // Render results
        preflopResultsContainer.innerHTML = `
            <div class="result-item">
                <h3>Preflop Action</h3>
                <p><strong>Position:</strong> <span class="value">${result.position}</span></p>
                <p><strong>Hole Cards:</strong> <span class="value">${result.hole_cards.join(' ')}</span></p>
                <div class="action ${result.action.toLowerCase()}">${result.action}</div>
            </div>
            
            <div class="result-item">
                <h3>Explanation</h3>
                ${result.action === 'RAISE' ? 
                    '<p>This hand is strong enough to raise from this position.</p>' :
                  result.action === 'CALL' ? 
                    '<p>This hand is playable but not strong enough to raise. Consider calling if facing a bet.</p>' :
                    '<p>This hand is too weak to play from this position. Consider folding.</p>'}
            </div>
        `;
        
    } catch (error) {
        showError(preflopResultsContainer, `Failed to get preflop action: ${error.message}`);
    }
}

// Health check function
async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('Server health:', data);
        return true;
    } catch (error) {
        console.error('Server health check failed:', error);
        return false;
    }
}

// Check server health on load
document.addEventListener('DOMContentLoaded', function() {
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
});

// Example usage functions
function loadExampleData() {
    // Preflop example
    document.getElementById('heroHand').value = 'As Kh';
    document.getElementById('board').value = '';
    document.getElementById('position').value = 'BTN';
    document.getElementById('potSize').value = '10';
    document.getElementById('currentBet').value = '5';
    
    // Equity example
    document.getElementById('equityHeroHand').value = 'As Kh';
    document.getElementById('villainRange').value = 'AA,KK,QQ,AKs,AQs';
    document.getElementById('equityBoard').value = '';
    document.getElementById('simulations').value = '1000';
    
    // GTO example
    document.getElementById('gtoPosition').value = 'BTN';
    document.getElementById('gtoHoleCards').value = 'As Kh';
}

// Add example button (optional)
document.addEventListener('DOMContentLoaded', function() {
    const exampleBtn = document.createElement('button');
    exampleBtn.textContent = 'Load Example';
    exampleBtn.className = 'btn btn-accent';
    exampleBtn.style.margin = '20px';
    exampleBtn.onclick = loadExampleData;
    
    const header = document.querySelector('.header');
    header.appendChild(exampleBtn);
});