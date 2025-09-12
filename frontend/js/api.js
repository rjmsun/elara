// elara poker calculator - api functions
const API_BASE_URL = 'http://localhost:5001';

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

// API endpoints
async function analyzeHandAPI(heroHand, board, position, potSize, currentBet) {
    const data = {
        hero_hand: heroHand,
        board: board,
        position: position,
        pot_size: potSize,
        current_bet: currentBet
    };
    return await makeRequest('/analyze_hand', data);
}

async function calculateEquityAPI(heroHand, villainRange, board, simulations) {
    const data = {
        hero_hand: heroHand,
        villain_range: villainRange,
        board: board,
        simulations: simulations
    };
    return await makeRequest('/calculate_equity', data);
}

async function getPreflopActionAPI(position, holeCards) {
    const data = {
        position: position,
        hole_cards: holeCards
    };
    return await makeRequest('/preflop_action', data);
}

async function partitionRange(villainRange, board) {
    const data = {
        villain_range: villainRange,
        board: board
    };
    return await makeRequest('/partition_range', data);
}

async function getDynamicRange(villainRange, board, playerProfile = 'tight') {
    const data = {
        villain_range: villainRange,
        board: board,
        player_profile: playerProfile
    };
    return await makeRequest('/dynamic_range', data);
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        makeRequest,
        checkServerHealth,
        analyzeHandAPI,
        calculateEquityAPI,
        getPreflopActionAPI,
        partitionRange,
        getDynamicRange
    };
}
