"""Chatbot tab - AI-powered stock advisor chat interface"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QScrollArea, QFrame, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QTextCursor
from services.chatbot_service import StockChatbot, ChatbotWorker
import logging

logger = logging.getLogger(__name__)


class ChatMessage(QFrame):
    """Individual chat message widget"""
    
    def __init__(self, message: str, is_bot: bool = False, parent=None):
        super().__init__(parent)
        self.is_bot = is_bot
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Message content
        content = QTextEdit()
        content.setReadOnly(True)
        content.setPlainText(message)
        content.setWordWrapMode(3)  # WrapAtWordBoundary
        
        # Style based on sender
        if is_bot:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: 1px solid #0d47a1;
                    border-radius: 8px;
                    margin: 5px 10px 5px 50px;
                    padding: 5px;
                }
            """)
            content.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #87CEEB;
                    border: none;
                    font-size: 10pt;
                }
            """)
            label = QLabel("🤖 Stock Advisor:")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a1a1a;
                    border: 1px solid #0d47a1;
                    border-radius: 8px;
                    margin: 5px 50px 5px 10px;
                    padding: 5px;
                }
            """)
            content.setStyleSheet("""
                QTextEdit {
                    background-color: #1a1a1a;
                    color: #90EE90;
                    border: none;
                    font-size: 10pt;
                }
            """)
            label = QLabel("👤 You:")
        
        label.setFont(QFont("Arial", 9, QFont.Bold))
        
        layout.addWidget(label)
        layout.addWidget(content)
        layout.addStretch()


class ChatbotTab(QWidget):
    """Chatbot interface for stock recommendations and analysis"""
    
    def __init__(self, db, cache):
        super().__init__()
        self.db = db
        self.cache = cache
        self.chatbot = StockChatbot(db, cache)
        self.chat_history = []
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("💬 Stock Advisor ChatBot")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel(
            "Ask me about stock recommendations, buy/sell signals, analysis, portfolio management, "
            "and more! Examples: 'What stocks should I buy?', 'Analyze AAPL', 'When to sell?', "
            "'Portfolio advice', 'Shorting strategies'"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(instructions)
        
        # Chat display area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.chat_scroll.setWidget(self.chat_container)
        
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #0d47a1;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.chat_scroll)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Ask me about stocks... (Press Ctrl+Enter to send)")
        self.message_input.setMaximumHeight(80)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }
        """)
        self.message_input.keyPressEvent = self.handle_key_press
        input_layout.addWidget(self.message_input)
        
        # Send button
        self.send_btn = QPushButton("Send 📤")
        self.send_btn.setMaximumWidth(120)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Status bar
        self.status_label = QLabel("Ready to chat!")
        self.status_label.setStyleSheet("color: #AAAAAA; font-size: 9pt;")
        layout.addWidget(self.status_label)
        
        # Setup worker thread
        self.worker_thread = QThread()
        self.worker = ChatbotWorker(self.chatbot)
        self.worker.moveToThread(self.worker_thread)
        self.worker.response_ready.connect(self.on_response_received)
        self.worker.error_occurred.connect(self.on_error)
        self.worker_thread.start()
        
        # Initial greeting
        self.add_bot_message("👋 Hello! I'm your Stock Advisor ChatBot. Ask me anything about stocks, portfolios, market trends, and investment strategies!")
    
    def handle_key_press(self, event):
        """Handle key press in message input"""
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.message_input, event)
    
    def send_message(self):
        """Send user message and get chatbot response"""
        message = self.message_input.toPlainText().strip()
        
        if not message:
            return
        
        # Add user message to chat
        self.add_user_message(message)
        self.message_input.clear()
        
        # Update status
        self.status_label.setText("🔄 Thinking...")
        self.send_btn.setEnabled(False)
        self.message_input.setEnabled(False)
        
        # Process in background thread
        self.worker.process_message(message)
    
    def on_response_received(self, response: dict):
        """Handle chatbot response"""
        bot_message = response.get("response", "Sorry, I couldn't generate a response.")
        
        self.add_bot_message(bot_message)
        
        # Update status
        stocks_mentioned = response.get("stocks_mentioned", [])
        if stocks_mentioned:
            self.status_label.setText(f"✓ Response ready - Stocks mentioned: {', '.join(stocks_mentioned)}")
        else:
            self.status_label.setText("✓ Response ready")
        
        self.send_btn.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()
    
    def on_error(self, error_msg: str):
        """Handle error in chatbot"""
        self.add_bot_message(f"❌ Error: {error_msg}\n\nPlease try again or rephrase your question.")
        self.status_label.setText("❌ Error occurred")
        self.send_btn.setEnabled(True)
        self.message_input.setEnabled(True)
    
    def add_user_message(self, message: str):
        """Add user message to chat"""
        msg_widget = ChatMessage(message, is_bot=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        self.scroll_to_bottom()
    
    def add_bot_message(self, message: str):
        """Add bot message to chat"""
        msg_widget = ChatMessage(message, is_bot=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """Cleanup thread on close"""
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)
