#!/usr/bin/env python3
"""
AI Chat CLI - Interactive command-line interface for testing AI Chat
====================================================================

Usage:
    python3 ai_chat_cli.py                    # Interactive mode with sample data
    python3 ai_chat_cli.py -f data.csv        # Load a CSV file
    python3 ai_chat_cli.py --analyze          # Quick data quality analysis
    python3 ai_chat_cli.py -v                 # Verbose mode
    python3 ai_chat_cli.py --json             # Output responses in JSON format

Examples:
    # Interactive chat with sample data
    python3 ai_chat_cli.py

    # Analyze a CSV file
    python3 ai_chat_cli.py -f customers.csv --analyze

    # Execute suggested operations automatically
    python3 ai_chat_cli.py -f data.csv --auto-execute
"""

import argparse
import json
import sys
import os
from typing import Optional
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_chat import (
    AIChat, AIChatConfig, AIResponse, AIOperation,
    DataContext, OperationType, create_sample_dataframe,
    AZURE_OPENAI_AVAILABLE
)


class AIChatCLI:
    """Interactive CLI for AI Chat testing"""

    def __init__(
        self,
        verbose: bool = False,
        json_output: bool = False,
        auto_execute: bool = False
    ):
        self.verbose = verbose
        self.json_output = json_output
        self.auto_execute = auto_execute
        self.df: Optional[pd.DataFrame] = None
        self.chat: Optional[AIChat] = None
        self.conversation_history = []

    def log(self, message: str, force: bool = False):
        """Print message if verbose or forced"""
        if self.verbose or force:
            print(message)

    def print_header(self):
        """Print CLI header"""
        print("\n" + "=" * 70)
        print("  FastMig AI Chat CLI - JSON-based LLM Communication")
        print("=" * 70)
        print()

    def print_status(self):
        """Print current status"""
        print("-" * 50)
        print("Status:")
        print(f"  Azure OpenAI Available: {AZURE_OPENAI_AVAILABLE}")
        print(f"  AI Chat Initialized: {self.chat is not None and self.chat.is_available()}")
        if self.df is not None:
            print(f"  Dataset Loaded: {self.df.shape[0]} rows x {self.df.shape[1]} columns")
        else:
            print("  Dataset Loaded: No")
        print(f"  Verbose Mode: {self.verbose}")
        print(f"  JSON Output: {self.json_output}")
        print(f"  Auto-Execute: {self.auto_execute}")
        print("-" * 50)
        print()

    def initialize(self) -> bool:
        """Initialize AI Chat client"""
        self.log("Initializing AI Chat...")

        config = AIChatConfig()
        is_valid, errors = config.validate()

        if not is_valid:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            print("\nPlease set the required environment variables:")
            print("  export AZURE_OPENAI_API_KEY=your_key")
            print("  export AZURE_OPENAI_ENDPOINT=your_endpoint")
            print("  export AZURE_OPENAI_DEPLOYMENT=your_deployment")
            return False

        self.chat = AIChat(config)

        if not self.chat.is_available():
            print("Failed to initialize AI Chat client")
            return False

        self.log("AI Chat initialized successfully")
        return True

    def load_data(self, file_path: Optional[str] = None) -> bool:
        """Load data from file or create sample"""
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith(('.xlsx', '.xls')):
                    self.df = pd.read_excel(file_path)
                elif file_path.endswith('.json'):
                    self.df = pd.read_json(file_path)
                else:
                    print(f"Unsupported file format: {file_path}")
                    return False

                self.log(f"Loaded {len(self.df)} rows from {file_path}")
                return True
            except Exception as e:
                print(f"Error loading file: {e}")
                return False
        else:
            self.log("Creating sample dataset...")
            self.df = create_sample_dataframe()
            self.log(f"Created sample dataset with {len(self.df)} rows")
            return True

    def show_data_preview(self, rows: int = 5):
        """Show data preview"""
        if self.df is None:
            print("No data loaded")
            return

        print("\nData Preview:")
        print("-" * 50)
        print(self.df.head(rows).to_string())
        print("-" * 50)

        print(f"\nShape: {self.df.shape[0]} rows x {self.df.shape[1]} columns")
        print(f"Columns: {', '.join(self.df.columns)}")

        # Show missing values
        missing = self.df.isnull().sum()
        cols_with_missing = missing[missing > 0]
        if len(cols_with_missing) > 0:
            print("\nMissing Values:")
            for col, count in cols_with_missing.items():
                pct = (count / len(self.df)) * 100
                print(f"  {col}: {count} ({pct:.1f}%)")
        print()

    def show_data_context_json(self):
        """Show data context as JSON"""
        if self.df is None:
            print("No data loaded")
            return

        context = DataContext.from_dataframe(self.df)
        print("\nData Context (JSON):")
        print("-" * 50)
        print(context.to_json())
        print("-" * 50)
        print()

    def analyze_data(self) -> Optional[AIResponse]:
        """Run data quality analysis"""
        if self.df is None:
            print("No data loaded")
            return None

        if self.chat is None or not self.chat.is_available():
            print("AI Chat not available")
            return None

        print("\nAnalyzing data quality...")
        response = self.chat.analyze_data_quality(self.df)

        self.display_response(response)
        return response

    def send_message(self, message: str) -> Optional[AIResponse]:
        """Send a message to AI Chat"""
        if self.chat is None or not self.chat.is_available():
            print("AI Chat not available")
            return None

        self.log(f"\nSending: {message}")

        response = self.chat.chat(
            user_message=message,
            df=self.df,
            conversation_history=self.conversation_history
        )

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": message})
        if response.success:
            self.conversation_history.append({
                "role": "assistant",
                "content": response.raw_response
            })

        self.display_response(response)

        # Auto-execute if enabled
        if self.auto_execute and response.success and response.operations:
            self.execute_operations(response.operations)

        return response

    def display_response(self, response: AIResponse):
        """Display AI response"""
        if self.json_output:
            print(response.to_json())
            return

        print("\n" + "=" * 50)
        print("AI Response:")
        print("=" * 50)

        if not response.success:
            print(f"Error: {response.error}")
            return

        print(f"\nMessage: {response.message}")

        if response.operations:
            print(f"\nSuggested Operations ({len(response.operations)}):")
            for i, op in enumerate(response.operations, 1):
                print(f"\n  [{i}] {op.operation.value}")
                if op.column:
                    print(f"      Column: {op.column}")
                if op.parameters:
                    print(f"      Parameters: {json.dumps(op.parameters)}")
                if op.description:
                    print(f"      Description: {op.description}")
                if op.confidence < 1.0:
                    print(f"      Confidence: {op.confidence:.0%}")
                if op.reasoning:
                    print(f"      Reasoning: {op.reasoning}")

        if response.analysis:
            print("\nAnalysis:")
            if 'summary' in response.analysis:
                print(f"  Summary: {response.analysis['summary']}")
            if 'issues_found' in response.analysis:
                print("  Issues Found:")
                for issue in response.analysis['issues_found']:
                    print(f"    - {issue}")
            if 'recommendations' in response.analysis:
                print("  Recommendations:")
                for rec in response.analysis['recommendations']:
                    print(f"    - {rec}")

        if response.usage:
            print(f"\nToken Usage: {response.usage.get('total_tokens', 'N/A')} tokens")

        print("=" * 50)
        print()

    def execute_operations(self, operations: list):
        """Execute suggested operations"""
        if self.df is None:
            print("No data to modify")
            return

        print("\nExecuting operations...")

        for i, op in enumerate(operations, 1):
            if op.operation in (OperationType.ANALYZE, OperationType.NONE):
                continue

            print(f"\n  [{i}] Executing: {op.operation.value}")
            self.df, details = self.chat.execute_operation(self.df, op)

            if details.get('success'):
                print(f"      Success! Rows affected: {details.get('rows_affected', 0)}")
            else:
                print(f"      Failed: {details.get('error', 'Unknown error')}")

        print("\nData after operations:")
        self.show_data_preview()

    def interactive_mode(self):
        """Run interactive chat mode"""
        print("\nInteractive Mode")
        print("-" * 50)
        print("Commands:")
        print("  /help     - Show help")
        print("  /data     - Show data preview")
        print("  /context  - Show data context as JSON")
        print("  /analyze  - Run data quality analysis")
        print("  /execute  - Execute last suggested operations")
        print("  /clear    - Clear conversation history")
        print("  /quit     - Exit")
        print("-" * 50)
        print("\nType your message or command:\n")

        last_response: Optional[AIResponse] = None

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.startswith('/'):
                    cmd = user_input.lower()

                    if cmd in ('/quit', '/exit', '/q'):
                        print("Goodbye!")
                        break
                    elif cmd == '/help':
                        print("\nAvailable commands:")
                        print("  /help     - Show this help")
                        print("  /data     - Show data preview")
                        print("  /context  - Show data context as JSON")
                        print("  /analyze  - Run data quality analysis")
                        print("  /execute  - Execute last suggested operations")
                        print("  /clear    - Clear conversation history")
                        print("  /quit     - Exit\n")
                    elif cmd == '/data':
                        self.show_data_preview()
                    elif cmd == '/context':
                        self.show_data_context_json()
                    elif cmd == '/analyze':
                        last_response = self.analyze_data()
                    elif cmd == '/execute':
                        if last_response and last_response.operations:
                            self.execute_operations(last_response.operations)
                        else:
                            print("No operations to execute")
                    elif cmd == '/clear':
                        self.conversation_history = []
                        print("Conversation history cleared")
                    else:
                        print(f"Unknown command: {cmd}")
                else:
                    last_response = self.send_message(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Use /quit to exit.")
            except EOFError:
                print("\nGoodbye!")
                break

    def run_demo(self):
        """Run a demo of AI Chat capabilities"""
        print("\n" + "=" * 70)
        print("  AI Chat Demo")
        print("=" * 70)

        print("\n1. Showing sample data...")
        self.show_data_preview()

        print("\n2. Showing data context in JSON format...")
        self.show_data_context_json()

        if self.chat and self.chat.is_available():
            print("\n3. Running data quality analysis...")
            self.analyze_data()

            print("\n4. Asking about specific column...")
            self.send_message("What's the best way to handle missing values in the 'age' column?")

            print("\n5. Asking about data cleaning strategy...")
            self.send_message("Suggest a complete data cleaning strategy for this dataset")
        else:
            print("\nAI Chat not available - skipping AI queries")
            print("Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT")

        print("\n" + "=" * 70)
        print("  Demo Complete")
        print("=" * 70 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Chat CLI - Interactive testing for JSON-based LLM communication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ai_chat_cli.py                    # Interactive mode with sample data
  python3 ai_chat_cli.py -f data.csv        # Load a CSV file
  python3 ai_chat_cli.py --analyze          # Quick data quality analysis
  python3 ai_chat_cli.py --demo             # Run demo mode
  python3 ai_chat_cli.py -v --json          # Verbose with JSON output
        """
    )

    parser.add_argument(
        '-f', '--file',
        help='Path to data file (CSV, Excel, or JSON)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output responses in JSON format'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run data quality analysis and exit'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo mode'
    )
    parser.add_argument(
        '--auto-execute',
        action='store_true',
        help='Automatically execute suggested operations'
    )
    parser.add_argument(
        '-m', '--message',
        help='Send a single message and exit'
    )
    parser.add_argument(
        '--show-context',
        action='store_true',
        help='Show data context as JSON and exit'
    )

    args = parser.parse_args()

    # Create CLI instance
    cli = AIChatCLI(
        verbose=args.verbose,
        json_output=args.json,
        auto_execute=args.auto_execute
    )

    # Print header
    if not args.json:
        cli.print_header()

    # Initialize AI Chat
    initialized = cli.initialize()

    # Load data
    cli.load_data(args.file)

    # Print status
    if args.verbose:
        cli.print_status()

    # Handle specific commands
    if args.show_context:
        cli.show_data_context_json()
        return

    if args.demo:
        cli.run_demo()
        return

    if args.analyze:
        if initialized:
            cli.analyze_data()
        else:
            print("Cannot run analysis - AI Chat not initialized")
        return

    if args.message:
        if initialized:
            cli.send_message(args.message)
        else:
            print("Cannot send message - AI Chat not initialized")
        return

    # Default: interactive mode
    if initialized:
        cli.interactive_mode()
    else:
        print("\nAI Chat not available. Please check your configuration.")
        print("You can still view data with --show-context or -f <file>")

        if args.file or not args.json:
            cli.show_data_preview()


if __name__ == "__main__":
    main()
