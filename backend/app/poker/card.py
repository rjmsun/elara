# card class: holds rank, suit, and value
class Card:
    def __init__(self, card_str: str):
        # parse the card string e.g. "As" or "Kh"
        self.rank = card_str[:-1]
        self.suit = card_str[-1]
        self.value = self._get_value()
    
    def _get_value(self):
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                      '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_values.get(self.rank, 0)
    
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
