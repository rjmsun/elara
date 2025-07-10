const suits = ['♠', '♣', '♥', '♦'];
const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'];
const API_URL = 'http://127.0.0.1:5000'; // URL of the Flask backend

let deck = [];
let playerHand = [];
let botHand = [];
let communityCards = [];
let gamePhase = 'pre-flop';
let pot = 0;
let playerStack = 1000;
let botStack = 1000;
let isPlayerTurn = true;

// --- Core Game Logic ---

function createDeck() {
    deck = [];
    for (let suit of suits) {
        for (let rank of ranks) {
            deck.push({ rank, suit });
        }
    }
}

function shuffleDeck() {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
}

function dealCards() {
    playerHand = [deck.pop(), deck.pop()];
    botHand = [deck.pop(), deck.pop()];
}

function startNewHand() {
    gamePhase = 'pre-flop';
    communityCards = [];
    pot = 0;
    
    // For simplicity, blinds are fixed.
    const smallBlind = 10;
    const bigBlind = 20;
    playerStack -= smallBlind;
    botStack -= bigBlind;
    pot = smallBlind + bigBlind;

    createDeck();
    shuffleDeck();
    dealCards();
    
    updateUI();
    isPlayerTurn = true;
    toggleControls(true);
    document.getElementById('nextHandBtn').style.display = 'none';
    document.getElementById('status').innerHTML = 'New hand. Your turn.';
}

function proceedToNextPhase() {
    isPlayerTurn = true;
    toggleControls(true);
    switch (gamePhase) {
        case 'pre-flop':
            gamePhase = 'flop';
            communityCards.push(deck.pop(), deck.pop(), deck.pop());
            break;
        case 'flop':
            gamePhase = 'turn';
            communityCards.push(deck.pop());
            break;
        case 'turn':
            gamePhase = 'river';
            communityCards.push(deck.pop());
            break;
        case 'river':
            endGame();
            return;
    }
    updateUI();
}

async function endGame() {
    toggleControls(false);

    const response = await fetch(`${API_URL}/evaluate_hands`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            player_hand: playerHand,
            bot_hand: botHand,
            community_cards: communityCards
        })
    });
    const result = await response.json();

    let statusText = '';
    if (result.winner === 'player') {
        playerStack += pot;
        statusText = `You win with a ${result.hand_name}! You won $${pot}.`;
    } else if (result.winner === 'hand2') { // 'hand2' is the bot
        botStack += pot;
        statusText = `Bot wins with a ${result.hand_name}. You lost $${pot}.`;
    } else {
        playerStack += pot / 2;
        botStack += pot / 2;
        statusText = `It's a tie with a ${result.hand_name}! The pot is split.`;
    }

    document.getElementById('status').textContent = statusText;
    renderCards(document.getElementById('bot'), botHand, false); // Reveal bot's cards
    updateUI();
    document.getElementById('nextHandBtn').style.display = 'block';
}

// --- Player Actions ---

function playerFold() {
    botStack += pot;
    document.getElementById('status').textContent = 'You folded. Bot wins the pot.';
    toggleControls(false);
    document.getElementById('nextHandBtn').style.display = 'block';
    updateUI();
}

function playerCheckCall() {
    // For now, we simplify this to just checking and moving to the bot's turn.
    // A full implementation would handle bets.
    isPlayerTurn = false;
    toggleControls(false);
    botTurn();
}

function playerBetRaise() {
    // Simplified action
    const raiseAmount = 50;
    playerStack -= raiseAmount;
    pot += raiseAmount;
    isPlayerTurn = false;
    toggleControls(false);
    updateUI();
    botTurn();
}


// --- Bot Actions ---

async function botTurn() {
    // Here, the bot's decision is driven by the backend.
    // This is a placeholder for a more complex interaction.
    // For now, let's assume the bot checks/calls and we proceed.
    setTimeout(() => {
        document.getElementById('status').textContent = 'Bot checks. Proceeding to next round.';
        proceedToNextPhase();
    }, 1000);
}


// --- UI Updates ---

function renderCards(element, cards, isHidden = false) {
    element.innerHTML = cards.map(card => `
        <div class="card ${isHidden ? 'hidden' : ''}" data-suit="${card.suit}">
            ${isHidden ? '' : card.rank + card.suit}
        </div>
    `).join('');
}

function updateUI() {
    renderCards(document.getElementById('player'), playerHand);
    renderCards(document.getElementById('bot'), botHand, gamePhase !== 'end');
    renderCards(document.getElementById('community'), communityCards);
    document.getElementById('phaseDisplay').textContent = `Phase: ${gamePhase.toUpperCase()} | Pot: $${pot}`;
    document.getElementById('status').innerHTML += `<br>Your Stack: $${playerStack} | Bot Stack: $${botStack}`;
}

function toggleControls(show) {
    document.getElementById('controls').innerHTML = show ? `
        <button onclick="playerCheckCall()">Check/Call</button>
        <button onclick="playerBetRaise()">Bet/Raise</button>
        <button onclick="playerFold()">Fold</button>
    ` : '';
}

// --- Initializer ---
window.onload = () => {
    startNewHand();
};

// Example: Send a hand evaluation request
async function evaluateHand() {
    const heroHand = ['As', 'Ks'];
    const board = ['Ah', '7d', '2c'];
    const data = {
        hero_hand: heroHand,
        board: board,
        hero_position: 'button',
        villain_position: 'big_blind',
        pot_size: 10,
        current_bet: 5,
        action_history: [
            {player: 'villain', action: 'raise', amount: 3, street: 'preflop'},
            {player: 'hero', action: 'call', amount: 3, street: 'preflop'},
            {player: 'villain', action: 'bet', amount: 5, street: 'flop'}
        ]
    };

    const response = await fetch('http://localhost:5000/evaluate_hand', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    const result = await response.json();
    // Now update your HTML with the result
    document.getElementById('output').textContent = JSON.stringify(result, null, 2);
}