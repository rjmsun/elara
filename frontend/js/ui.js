// elara poker calculator - ui functions

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

// Render functions for different result types
function renderHandAnalysis(result, heroHand, board) {
    return `
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
}

function renderEquityCalculation(result) {
    return `
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
}

function renderPreflopAction(result) {
    return `
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
}

function renderRangePartition(result) {
    return `
        <div class="result-item">
            <h3>Range Partition</h3>
            <p><strong>Board:</strong> <span class="value">${result.board.join(' ')}</span></p>
            <p><strong>Villain Range:</strong> <span class="value">${result.villain_range.join(', ')}</span></p>
        </div>
        
        <div class="result-item">
            <h3>Strategic Categories</h3>
            <div class="categories">
                <div class="category">
                    <span class="category-label">Value Hands:</span>
                    <span class="category-value">${result.categories.value}%</span>
                </div>
                <div class="category">
                    <span class="category-label">Marginal Hands:</span>
                    <span class="category-value">${result.categories.marginal}%</span>
                </div>
                <div class="category">
                    <span class="category-label">Flush Draws:</span>
                    <span class="category-value">${result.categories.flush_draw}%</span>
                </div>
                <div class="category">
                    <span class="category-label">Straight Draws:</span>
                    <span class="category-value">${result.categories.straight_draw}%</span>
                </div>
                <div class="category">
                    <span class="category-label">Bluff/Air:</span>
                    <span class="category-value">${result.categories.bluff_air}%</span>
                </div>
            </div>
        </div>
    `;
}

function renderDynamicRange(result) {
    return `
        <div class="result-item">
            <h3>Dynamic Range Filtering</h3>
            <p><strong>Board:</strong> <span class="value">${result.board.join(' ')}</span></p>
            <p><strong>Player Profile:</strong> <span class="value">${result.player_profile}</span></p>
            <p><strong>Original Range Size:</strong> <span class="value">${result.original_range_size} hands</span></p>
            <p><strong>Filtered Range Size:</strong> <span class="value">${result.filtered_range_size} hands</span></p>
        </div>
        
        <div class="result-item">
            <h3>Filtered Range</h3>
            <p><strong>Hands that continue:</strong> <span class="value">${result.filtered_range.join(', ')}</span></p>
        </div>
    `;
}

// Example data loading
function loadExampleData() {
    // Preflop example
    document.getElementById('heroHand').value = 'As Kh';
    document.getElementById('board').value = '';
    document.getElementById('position').value = 'SB';
    document.getElementById('potSize').value = '10';
    document.getElementById('currentBet').value = '5';
    
    // Equity example
    document.getElementById('equityHeroHand').value = 'As Kh';
    document.getElementById('villainRange').value = 'AA,KK,QQ,AKs,AQs';
    document.getElementById('equityBoard').value = '';
    document.getElementById('simulations').value = '1000';
    
    // Preflop example
    document.getElementById('preflopPosition').value = 'SB';
    document.getElementById('preflopHoleCards').value = 'As Kh';
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        parseCards,
        showLoading,
        showError,
        formatCard,
        renderCards,
        renderHandAnalysis,
        renderEquityCalculation,
        renderPreflopAction,
        renderRangePartition,
        renderDynamicRange,
        loadExampleData
    };
}
