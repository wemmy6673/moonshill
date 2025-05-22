import random
import re
from datetime import datetime, timedelta
from schemas import generation as generation_schemas


class HumanLikePatterns:
    """Collection of patterns to make messages more human-like"""

    @staticmethod
    def simulate_device_typing(text: str, device: generation_schemas.DeviceType) -> str:
        """Device-specific typing patterns"""
        if device == generation_schemas.DeviceType.MOBILE:
            text = text.replace('.', ' .').replace(',', ' ,')  # Mobile space-before-punctuation
            if random.random() < 0.15:
                text = text.replace('ing', 'in').replace('you', 'u').replace('are', 'r')

        elif device == generation_schemas.DeviceType.DESKTOP:
            if random.random() < 0.1:
                text = re.sub(r'\b(\w{4,})\b', lambda m: m.group(1).capitalize(), text)

        return text

    @staticmethod
    def add_keyboard_typos(text: str, probability: float = 0.1) -> str:
        """Simulate realistic keyboard typos with full QWERTY adjacency mapping"""
        if random.random() > probability:
            return text

        adjacent_keys = {
            'a': ['q', 'w', 's', 'z', 'x'],
            'b': ['v', 'g', 'h', 'n', ' '],
            'c': ['x', 'd', 'f', 'v', ' '],
            'd': ['s', 'e', 'r', 'f', 'c', 'x'],
            'e': ['w', 's', 'd', 'r', '3', '4'],
            'f': ['d', 'r', 't', 'g', 'v', 'c'],
            'g': ['f', 't', 'y', 'h', 'b', 'v'],
            'h': ['g', 'y', 'u', 'j', 'n', 'b'],
            'i': ['u', 'j', 'k', 'o', '8', '9'],
            'j': ['h', 'u', 'i', 'k', 'm', 'n'],
            'k': ['j', 'i', 'o', 'l', ',', 'm'],
            'l': ['k', 'o', 'p', ';', '.', ','],
            'm': ['n', 'j', 'k', ',', ' '],
            'n': ['b', 'h', 'j', 'm', ' '],
            'o': ['i', 'k', 'l', 'p', '9', '0'],
            'p': ['o', 'l', ';', '[', '0', '-'],
            'q': ['1', '2', 'w', 'a', 's'],
            'r': ['e', 'd', 'f', 't', '4', '5'],
            's': ['a', 'w', 'e', 'd', 'x', 'z'],
            't': ['r', 'f', 'g', 'y', '5', '6'],
            'u': ['y', 'h', 'j', 'i', '7', '8'],
            'v': ['c', 'f', 'g', 'b', ' '],
            'w': ['q', 'a', 's', 'e', '2', '3'],
            'x': ['z', 's', 'd', 'c', ' '],
            'y': ['t', 'g', 'h', 'u', '6', '7'],
            'z': ['a', 's', 'x', ' '],
            ' ': ['c', 'v', 'b', 'n', 'm']
        }

        result = []
        for char in text.lower():
            if char in adjacent_keys and random.random() < probability:
                result.append(random.choice(adjacent_keys[char]))
            else:
                result.append(char)
        return ''.join(result)

    @staticmethod
    def add_typos(text: str, probability: float = 0.1) -> str:
        if random.random() > probability:
            return text

        common_typos = {
            'the': 'teh', 'and': 'adn', 'you': 'u', 'your': 'ur', 'are': 'r',
            'for': '4', 'to': '2', 'too': '2', 'be': 'b', 'see': 'c', 'why': 'y',
            'with': 'w/', 'without': 'w/o', 'because': 'cuz', 'though': 'tho',
            'through': 'thru', 'tonight': '2nite', 'today': '2day', 'tomorrow': '2moro',
            'please': 'plz', 'thanks': 'thx', 'thank you': 'ty', 'great': 'gr8',
            'wait': 'w8', 'mate': 'm8', 'later': 'l8r', 'before': 'b4', 'about': 'abt',
            'people': 'ppl', 'probably': 'prob', 'definitely': 'def', 'whatever': 'wtv',
            'what': 'wut', 'want': 'wnt', 'would': 'wld', 'should': 'shld', 'could': 'cld',
            'going to': 'gonna', 'want to': 'wanna', 'got to': 'gotta', 'kind of': 'kinda',
            'sort of': 'sorta', 'right now': 'rn', 'in my opinion': 'imo', 'to be honest': 'tbh',
            'oh my god': 'omg', 'rolling on floor laughing': 'rofl', 'laughing out loud': 'lol'
        }

        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in common_typos and random.random() < probability:
                words[i] = common_typos[word.lower()]

        return ' '.join(words)

    @staticmethod
    def add_emoji_imperfections(text: str, probability: float = 0.15) -> str:
        if random.random() > probability:
            return text

        text = re.sub(r'([\U0001F300-\U0001F9FF])', r' \1 ', text)
        if random.random() < probability:
            extra_emojis = ['😅', '🤔', '💭', '✨', '🔥', '💯', '👀', '🙌']
            text += f" {random.choice(extra_emojis)}"

        return text

    @staticmethod
    def add_casual_punctuation(text: str, probability: float = 0.2) -> str:
        if random.random() > probability:
            return text

        if random.random() < 0.3:
            text = text.replace('.', '...')
        if random.random() < 0.2:
            text = text.replace('!', '!!!')
        if random.random() < 0.2:
            text = text.replace('?', '???')
        if random.random() < 0.15:
            text = text.replace('!', '!?!')
        if random.random() < 0.2:
            text = text.replace('...', '.....')
        if random.random() < 0.1:
            text = text.replace('!', '~!')

        if random.random() < 0.15:
            words = text.split()
            if len(words) > 5:
                pos = random.randint(2, len(words) - 2)
                words.insert(pos, ',')
                text = ' '.join(words)

        return text

    @staticmethod
    def vary_capitalization(text: str, probability: float = 0.1) -> str:
        if random.random() > probability:
            return text

        words = text.split()
        for i, word in enumerate(words):
            if random.random() < probability and len(word) > 3:
                words[i] = word.upper()

        return ' '.join(words)


class AntiDetectionService:
    """Service for making messages more human-like and avoiding detection"""

    def __init__(self):
        self.patterns = HumanLikePatterns()

    def apply_human_like_patterns(self, text: str, intensity: float = 0.5, device: generation_schemas.DeviceType = generation_schemas.DeviceType.MOBILE) -> str:
        transformations = [
            lambda t: self.patterns.add_typos(t, 0.1 * intensity),
            lambda t: self.patterns.add_emoji_imperfections(t, 0.15 * intensity),
            lambda t: self.patterns.add_casual_punctuation(t, 0.2 * intensity),
            lambda t: self.patterns.vary_capitalization(t, 0.1 * intensity),
            lambda t: self.patterns.simulate_device_typing(t, device),
            lambda t: self.patterns.add_keyboard_typos(t, 0.1 * intensity),
        ]

        random.shuffle(transformations)

        for transform in transformations:
            if random.random() < intensity:
                text = transform(text)

        return text

    def generate_message_style(self, campaign_phase: generation_schemas.CampaignPhase) -> generation_schemas.PostStyle:
        if campaign_phase == generation_schemas.CampaignPhase.EARLY:
            styles = [generation_schemas.PostStyle.THREAD, generation_schemas.PostStyle.QUESTION, generation_schemas.PostStyle.NEWS]
        elif campaign_phase == generation_schemas.CampaignPhase.MID:
            styles = [generation_schemas.PostStyle.MEME, generation_schemas.PostStyle.ANALYSIS, generation_schemas.PostStyle.FUD_RESPONSE]
        else:
            styles = [generation_schemas.PostStyle.THREAD, generation_schemas.PostStyle.ANALYSIS, generation_schemas.PostStyle.FUD_RESPONSE]

        return random.choice(styles)

    def add_random_silence(self, next_post_time: datetime, unit: str = 'days', min_val: int = 1, max_val: int = 3) -> datetime:
        if random.random() < 0.2:
            silence_val = random.randint(min_val, max_val)

            if unit == 'minutes':
                next_post_time += timedelta(minutes=silence_val)
            elif unit == 'hours':
                next_post_time += timedelta(hours=silence_val)
            else:
                next_post_time += timedelta(days=silence_val)

        return next_post_time
